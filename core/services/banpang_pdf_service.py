"""Generator PDF Verifikasi Banpang.

Membuat satu PDF searchable untuk seluruh PBP.

Setiap PBP dibuat menjadi satu halaman:
- Data identitas PBP
- Foto KTP

Foto PBP TIDAK dimasukkan ke PDF.
Foto PBP disimpan terpisah oleh proses pengambilan data.
"""

import io
import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from PIL import Image


class BanpangPDFService:

    PAGE_WIDTH, PAGE_HEIGHT = A4

    @staticmethod
    def _safe_text(value):
        return re.sub(r"\s+", " ", str(value or "")).strip()

    @classmethod
    def _extract_name_nik(cls, value):
        lines = [
            line.strip()
            for line in str(value or "").splitlines()
            if line.strip()
        ]

        if not lines:
            return "", ""

        nik = ""

        for line in lines:
            match = re.search(r"\b\d{16}\b", line)

            if match:
                nik = match.group(0)
                break

        name = lines[0]

        if re.fullmatch(r"\d{16}", name):
            name = ""

        return cls._safe_text(name), nik

    @classmethod
    def row_to_record(cls, row):

        def get(key):
            return row.get(key, "")

        name, nik = cls._extract_name_nik(
            get("nama")
        )

        replacement_name, replacement_nik = (
            cls._extract_name_nik(
                get("nama pengganti / perwakilan")
            )
        )

        if cls._safe_text(
            replacement_name
        ).lower() in {
            "tidak diwakilkan",
            "tidak ada",
            "-",
        }:

            replacement_name = cls._safe_text(
                replacement_name
            )

            replacement_nik = ""

        return {
            "no_pbp": cls._safe_text(
                get("no pbp")
            ),

            "nama_pbp": name,

            "nik_pbp": nik,

            "nama_pengganti": replacement_name,

            "nik_pengganti": replacement_nik,

            "status_pbp": cls._safe_text(
                get("status pbp")
            ),
        }

    @staticmethod
    def _fit_image(
        image_bytes,
        max_width,
        max_height
    ):

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        image.load()

        if image.mode not in (
            "RGB",
            "RGBA"
        ):
            image = image.convert("RGB")

        width, height = image.size

        if width <= 0 or height <= 0:
            raise ValueError(
                "Ukuran foto tidak valid."
            )

        scale = min(
            max_width / width,
            max_height / height,
            1.0
        )

        draw_width = width * scale
        draw_height = height * scale

        return (
            image,
            draw_width,
            draw_height
        )

    @classmethod
    def _draw_photo(
        cls,
        pdf,
        image_bytes,
        x,
        y,
        max_width,
        max_height,
        label
    ):

        if isinstance(
            image_bytes,
            bytearray
        ):
            image_bytes = bytes(
                image_bytes
            )

        elif isinstance(
            image_bytes,
            memoryview
        ):
            image_bytes = image_bytes.tobytes()

        if not image_bytes:

            pdf.setFont(
                "Helvetica",
                11
            )

            pdf.drawCentredString(
                x + max_width / 2,
                y + max_height / 2,
                f"{label} tidak tersedia"
            )

            return

        try:

            if not isinstance(
                image_bytes,
                bytes
            ):

                raise TypeError(
                    f"Data foto harus bytes, "
                    f"bukan {type(image_bytes)}"
                )

            (
                image,
                draw_width,
                draw_height
            ) = cls._fit_image(
                image_bytes,
                max_width,
                max_height
            )

            draw_x = (
                x
                + (
                    max_width
                    - draw_width
                ) / 2
            )

            draw_y = (
                y
                + (
                    max_height
                    - draw_height
                ) / 2
            )

            pdf.drawImage(
                ImageReader(image),
                draw_x,
                draw_y,
                width=draw_width,
                height=draw_height,
                preserveAspectRatio=True,
                mask="auto"
            )

        except Exception as error:

            pdf.setFont(
                "Helvetica",
                10
            )

            pdf.drawCentredString(
                x + max_width / 2,
                y + max_height / 2,
                f"Gagal menampilkan "
                f"{label}: {error}"
            )

    @classmethod
    def create_pdf(
        cls,
        records,
        output_path
    ):
        """Membuat PDF 1 halaman per PBP.

        Isi setiap halaman:
        - Data identitas PBP
        - Foto KTP

        Foto PBP sengaja tidak dimasukkan
        ke dalam PDF.
        """

        if not records:

            raise ValueError(
                "Tidak ada data PBP "
                "untuk dibuat PDF."
            )

        output_path = os.path.abspath(
            output_path
        )

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        # ==========================================================
        # URUTKAN DATA
        # ==========================================================

        ordered_records = list(
            records
        )

        ordered_records.sort(
            key=lambda item:
            item.get(
                "collection_order",
                0
            )
        )

        print(
            "\n=== VALIDASI URUTAN DATA PDF ==="
        )

        seen_no_pbp = set()

        for index, item in enumerate(
            ordered_records,
            start=1
        ):

            no_pbp = cls._safe_text(
                item.get("no pbp")
            )

            target_nik = cls._safe_text(
                item.get("target_nik")
            )

            parsed = cls.row_to_record(
                item
            )

            parsed_nik = cls._safe_text(
                parsed.get("nik_pbp")
            )

            if (
                no_pbp
                and no_pbp in seen_no_pbp
            ):

                raise ValueError(
                    "Duplikat No PBP ditemukan "
                    "sebelum PDF: "
                    f"{no_pbp}"
                )

            if no_pbp:
                seen_no_pbp.add(
                    no_pbp
                )

            if (
                target_nik
                and parsed_nik
                and target_nik != parsed_nik
            ):

                raise ValueError(
                    "NIK PBP tidak konsisten "
                    f"pada urutan {index}: "
                    f"target={target_nik}, "
                    f"data={parsed_nik}"
                )

            print(
                f"{index}. "
                f"No PBP={no_pbp} | "
                f"NIK={target_nik or parsed_nik} | "
                f"KTP="
                f"{len(item.get('foto_ktp_bytes') or b''):,} "
                f"bytes | "
                f"PBP tidak dimasukkan ke PDF"
            )

        # ==========================================================
        # BUAT PDF
        # ==========================================================

        pdf = canvas.Canvas(
            output_path,
            pagesize=A4,
            pageCompression=1
        )

        pdf.setTitle(
            "Verifikasi Banpang"
        )

        pdf.setAuthor(
            "Mahdi PDF Studio"
        )

        pdf.setSubject(
            "Data PBP dan Foto KTP "
            "Verifikasi Banpang"
        )

        margin = 42

        # ==========================================================
        # SATU HALAMAN PER PBP
        # ==========================================================

        for index, item in enumerate(
            ordered_records,
            start=1
        ):

            # PENTING:
            # Data dan Foto KTP berasal
            # dari RECORD PBP yang sama.

            data = cls.row_to_record(
                item
            )

            ktp_bytes = item.get(
                "foto_ktp_bytes"
            )

            # ======================================================
            # HEADER
            # ======================================================

            pdf.setFont(
                "Helvetica-Bold",
                16
            )

            pdf.setFillColorRGB(
                0.12,
                0.16,
                0.23
            )

            pdf.drawString(
                margin,
                cls.PAGE_HEIGHT - 48,
                "VERIFIKASI BANPANG"
            )

            pdf.setFont(
                "Helvetica",
                8.5
            )

            pdf.drawRightString(
                cls.PAGE_WIDTH - margin,
                cls.PAGE_HEIGHT - 47,
                f"PBP {index} | "
                f"No PBP: {data['no_pbp']}"
            )

            pdf.setStrokeColorRGB(
                0.80,
                0.84,
                0.90
            )

            pdf.line(
                margin,
                cls.PAGE_HEIGHT - 62,
                cls.PAGE_WIDTH - margin,
                cls.PAGE_HEIGHT - 62
            )

            # ======================================================
            # DATA IDENTITAS
            # ======================================================

            y = (
                cls.PAGE_HEIGHT
                - 90
            )

            fields = [
                (
                    "Nama PBP",
                    data["nama_pbp"]
                ),

                (
                    "NIK PBP",
                    data["nik_pbp"]
                ),

                (
                    "Nama Pengganti/Perwakilan",
                    data["nama_pengganti"]
                ),

                (
                    "NIK Pengganti/Perwakilan",
                    data["nik_pengganti"]
                ),

                (
                    "Status PBP",
                    data["status_pbp"]
                ),
            ]

            for label, value in fields:

                pdf.setFont(
                    "Helvetica-Bold",
                    9.5
                )

                pdf.setFillColorRGB(
                    0.12,
                    0.16,
                    0.23
                )

                pdf.drawString(
                    margin,
                    y,
                    label
                )

                pdf.setFont(
                    "Helvetica",
                    9.5
                )

                pdf.setFillColorRGB(
                    0.22,
                    0.27,
                    0.36
                )

                pdf.drawString(
                    205,
                    y,
                    value or "-"
                )

                y -= 21

            # ======================================================
            # FOTO KTP
            # ======================================================

            photo_top = y - 8

            photo_bottom = (
                margin + 32
            )

            photo_height = max(
                180,
                photo_top - photo_bottom
            )

            photo_width = (
                cls.PAGE_WIDTH
                - 2 * margin
            )

            pdf.setFont(
                "Helvetica-Bold",
                10
            )

            pdf.setFillColorRGB(
                0.12,
                0.16,
                0.23
            )

            pdf.drawString(
                margin,
                photo_top + 10,
                "Foto KTP"
            )

            pdf.setStrokeColorRGB(
                0.82,
                0.85,
                0.90
            )

            pdf.rect(
                margin,
                photo_bottom,
                photo_width,
                photo_height,
                stroke=1,
                fill=0
            )

            cls._draw_photo(
                pdf,
                ktp_bytes,
                margin + 4,
                photo_bottom + 4,
                photo_width - 8,
                photo_height - 8,
                "Foto KTP"
            )

            # ======================================================
            # FOOTER
            # ======================================================

            pdf.setFont(
                "Helvetica",
                7.5
            )

            pdf.setFillColorRGB(
                0.45,
                0.49,
                0.56
            )

            pdf.drawString(
                margin,
                18,
                "Mahdi PDF Studio — "
                "Dokumen searchable / text layer"
            )

            pdf.drawRightString(
                cls.PAGE_WIDTH - margin,
                18,
                f"Halaman {index}"
            )

            pdf.showPage()

        # ==========================================================
        # SIMPAN
        # ==========================================================

        pdf.save()

        return output_path