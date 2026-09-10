"""
==========================================================
Mahdi PDF Studio
PDF Split Service
==========================================================

Service Layer untuk proses Split PDF.

Tanggung Jawab
--------------
✓ Membaca PDF
✓ Membuat PDF baru
✓ Menyimpan hasil split

Tidak Bertanggung Jawab
-----------------------
✗ Menampilkan UI
✗ Dialog Save
✗ StatusBar

Semua UI ditangani oleh SplitPage.

Arsitektur
----------

SplitPage
    │
    ▼

PdfSplitService
    │
    ▼

Output PDF

==========================================================
"""

from pathlib import Path

from pypdf import PdfReader
from pypdf import PdfWriter


class PdfSplitService:
    """
    Service pemisahan PDF.
    """

    @staticmethod
    def split_per_page(
        pdf_path,
        output_folder
    ):
        """
        Split PDF menjadi satu file
        untuk setiap halaman.

        Contoh:

        laporan.pdf

        ↓

        laporan_1.pdf
        laporan_2.pdf
        laporan_3.pdf
        """

        try:

            reader = PdfReader(
                pdf_path
            )

            source_name = Path(
                pdf_path
            ).stem

            total_pages = len(
                reader.pages
            )

            for page_index in range(
                total_pages
            ):

                writer = PdfWriter()

                writer.add_page(
                    reader.pages[
                        page_index
                    ]
                )

                output_file = (
                    Path(output_folder)
                    /
                    f"{source_name}_{page_index + 1}.pdf"
                )

                with open(
                    output_file,
                    "wb"
                ) as pdf_file:

                    writer.write(
                        pdf_file
                    )

            return (
                True,
                f"Berhasil split {total_pages} halaman"
            )

        except Exception as error:

            return (
                False,
                str(error)
            )
        

    @staticmethod
    def split_range(
        pdf_path,
        output_file,
        start_page,
        end_page
    ):
        """
        Split PDF berdasarkan rentang.

        Contoh:

            1-5

        menghasilkan:

            output.pdf
        """

        try:

            reader = PdfReader(
                pdf_path
            )

            writer = PdfWriter()

            for page_index in range(
                start_page - 1,
                end_page
            ):

                writer.add_page(
                    reader.pages[
                        page_index
                    ]
                )

            with open(
                output_file,
                "wb"
            ) as pdf_file:

                writer.write(
                    pdf_file
                )

            return (
                True,
                "Split rentang berhasil"
            )

        except Exception as error:

            return (
                False,
                str(error)
            )
        
    
    @staticmethod
    def split_groups(
        pdf_path,
        output_folder,
        groups
    ):
        """
        Membuat beberapa PDF berdasarkan
        grup halaman hasil parser.

        Contoh:

        groups = [
            (2,2),
            (3,5)
        ]

        Output:

        File_1.pdf
        File_2.pdf
        """

        try:

            from pathlib import Path
            from pypdf import (
                PdfReader,
                PdfWriter
            )

            reader = PdfReader(
                str(pdf_path)
            )

            source_name = Path(
                pdf_path
            ).stem

            created_files = []

            for index, (
                start_page,
                end_page
            ) in enumerate(groups, start=1):

                writer = PdfWriter()

                for page_number in range(
                    start_page,
                    end_page + 1
                ):

                    writer.add_page(
                        reader.pages[
                            page_number - 1
                        ]
                    )

                output_file = (
                    Path(output_folder)
                    /
                    f"{source_name}_{index}.pdf"
                )

                with open(
                    output_file,
                    "wb"
                ) as pdf_file:

                    writer.write(
                        pdf_file
                    )

                created_files.append(
                    output_file.name
                )

            return (
                True,
                f"{len(created_files)} file berhasil dibuat."
            )

        except Exception as error:

            return (
                False,
                str(error)
            )