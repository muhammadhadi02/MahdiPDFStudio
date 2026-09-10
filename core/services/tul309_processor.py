"""
==========================================================
Mahdi PDF Studio
TUL 309 Processor
==========================================================

Mesin pengolahan file Excel TUL 309.

Input:
- Banyak file .xls / .xlsx
- Template TUL 309 yang sama

Output:
- Rekapitulasi seluruh file
- 6 baris per file:
    S
    R
    P
    T
    C
    L

==========================================================
"""

import os
import re
import pandas as pd


class TUL309Processor:
    """
    Processor untuk membaca dan merekap file TUL 309.
    """

    # ==================================================
    # KONFIGURASI BARIS SUMBER
    # ==================================================

    SOURCE_ROWS = {
        "S": [28],
        "R": [45],
        "P": [76],
        "T": [77, 78],
        "C": [79, 80, 81],
        "L": [82, 83, 84],
    }

    # Kolom Excel yang digunakan
    # D = 3
    # E = 4
    # F = 5
    # Q = 16
    SOURCE_COLUMNS = {
        "jumlah_pelanggan": 3,
        "total_daya": 4,
        "total_pemakaian": 5,
        "total_penjualan": 16,
    }

    # ==================================================
    # PUBLIC METHOD
    # ==================================================

    def process_files(self, file_paths):
        """
        Memproses banyak file TUL 309.

        Parameters
        ----------
        file_paths : list
            Daftar path file Excel.

        Returns
        -------
        pandas.DataFrame
            Data hasil rekapitulasi.
        """

        if not file_paths:
            return pd.DataFrame()

        results = []

        for file_path in file_paths:

            try:

                result = self.process_file(
                    file_path
                )

                results.extend(result)

            except Exception as e:

                raise RuntimeError(
                    f"Gagal memproses file:\n"
                    f"{os.path.basename(file_path)}\n\n"
                    f"{e}"
                ) from e

        return pd.DataFrame(results)

    # ==================================================
    # PROCESS SINGLE FILE
    # ==================================================

    def process_file(self, file_path):
        """
        Memproses satu file Excel.

        Menghasilkan 6 record:
        S, R, P, T, C, L
        """

        # ----------------------------------------------
        # Baca Excel tanpa header
        # ----------------------------------------------

        df = pd.read_excel(
            file_path,
            header=None
        )

        # ----------------------------------------------
        # Metadata
        # ----------------------------------------------

        kabupaten = self.get_cell(
            df,
            3,
            2
        )

        keterangan = self.get_last_word(
            self.get_cell(
                df,
                4,
                1
            )
        )

        bulan, tahun = self.parse_month_year(
            self.get_cell(
                df,
                5,
                1
            )
        )

        # ----------------------------------------------
        # Hasil
        # ----------------------------------------------

        results = []

        for tarif, rows in self.SOURCE_ROWS.items():

            values = self.calculate_tariff(
                df,
                rows
            )

            results.append({

                "Kabupaten/Kota": self.clean_text(
                    kabupaten
                ),

                "Bulan": bulan,

                "Tahun": tahun,

                "Golongan Tarif": tarif,

                "Jumlah Pelanggan": values[
                    "jumlah_pelanggan"
                ],

                "Total Daya (VA)": values[
                    "total_daya"
                ],

                "Total Pemakaian kWH": values[
                    "total_pemakaian"
                ],

                "Total Penjualan (Rupiah)": values[
                    "total_penjualan"
                ],

                "Keterangan": keterangan

            })

        return results

    # ==================================================
    # CALCULATE TARIFF
    # ==================================================

    def calculate_tariff(
        self,
        df,
        rows
    ):
        """
        Mengambil dan menjumlahkan nilai
        dari baris sumber.

        rows menggunakan nomor baris Excel,
        sehingga dikurangi 1 untuk pandas.
        """

        total = {
            "jumlah_pelanggan": 0,
            "total_daya": 0,
            "total_pemakaian": 0,
            "total_penjualan": 0
        }

        for excel_row in rows:

            pandas_row = excel_row - 1

            # ------------------------------------------
            # Pastikan baris tersedia
            # ------------------------------------------

            if pandas_row >= len(df):
                continue

            # ------------------------------------------
            # D - Jumlah Pelanggan
            # ------------------------------------------

            total["jumlah_pelanggan"] += self.to_number(
                df.iloc[
                    pandas_row,
                    self.SOURCE_COLUMNS[
                        "jumlah_pelanggan"
                    ]
                ]
            )

            # ------------------------------------------
            # E - Total Daya
            # ------------------------------------------

            total["total_daya"] += self.to_number(
                df.iloc[
                    pandas_row,
                    self.SOURCE_COLUMNS[
                        "total_daya"
                    ]
                ]
            )

            # ------------------------------------------
            # F - Total Pemakaian
            # ------------------------------------------

            total["total_pemakaian"] += self.to_number(
                df.iloc[
                    pandas_row,
                    self.SOURCE_COLUMNS[
                        "total_pemakaian"
                    ]
                ]
            )

            # ------------------------------------------
            # Q - Total Penjualan
            # ------------------------------------------

            total["total_penjualan"] += self.to_number(
                df.iloc[
                    pandas_row,
                    self.SOURCE_COLUMNS[
                        "total_penjualan"
                    ]
                ]
            )

        return total

    # ==================================================
    # GET CELL
    # ==================================================

    @staticmethod
    def get_cell(
        df,
        row,
        column
    ):
        """
        Mengambil isi cell berdasarkan
        nomor baris dan kolom Excel.

        row dan column menggunakan
        indeks Excel 1-based.
        """

        pandas_row = row - 1
        pandas_column = column - 1

        if pandas_row >= len(df):
            return ""

        if pandas_column >= len(df.columns):
            return ""

        return df.iloc[
            pandas_row,
            pandas_column
        ]

    # ==================================================
    # LAST WORD
    # ==================================================

    @staticmethod
    def get_last_word(value):
        """
        Mengambil kata terakhir dari teks.

        Contoh:

        '309 Juni 26 LPB'
            -> LPB

        '309 Juni 26 Normal'
            -> Normal

        '309 Juni 26 Total'
            -> Total
        """

        if pd.isna(value):
            return ""

        text = str(value).strip()

        if not text:
            return ""

        words = text.split()

        return words[-1]

    # ==================================================
    # MONTH & YEAR
    # ==================================================

    @staticmethod
    def parse_month_year(value):
        """
        Mengambil Bulan dan Tahun dari B6.

        Contoh:
            'Juni 2026'
            'Juni 26'
            'Juni 2026 TUL 309'

        Returns:
            bulan, tahun
        """

        if pd.isna(value):
            return "", ""

        text = str(value).strip()

        if not text:
            return "", ""

        # ----------------------------------------------
        # Cari nama bulan
        # ----------------------------------------------

        months = {
            "januari": "Januari",
            "februari": "Februari",
            "maret": "Maret",
            "april": "April",
            "mei": "Mei",
            "juni": "Juni",
            "juli": "Juli",
            "agustus": "Agustus",
            "september": "September",
            "oktober": "Oktober",
            "november": "November",
            "desember": "Desember"
        }

        bulan = ""

        for key, display in months.items():

            if key in text.lower():

                bulan = display
                break

        # ----------------------------------------------
        # Cari tahun
        # ----------------------------------------------

        years = re.findall(
            r"\b(?:19|20)\d{2}\b",
            text
        )

        if years:

            tahun = int(
                years[-1]
            )

        else:

            # Coba tahun 2 digit
            short_years = re.findall(
                r"\b\d{2}\b",
                text
            )

            if short_years:

                short_year = int(
                    short_years[-1]
                )

                tahun = 2000 + short_year

            else:

                tahun = ""

        return bulan, tahun

    # ==================================================
    # NUMBER CONVERTER
    # ==================================================

    @staticmethod
    def to_number(value):
        """
        Mengubah nilai Excel menjadi angka.

        Mendukung:
        - int
        - float
        - string
        - angka dengan separator ribuan
        - angka desimal

        Contoh:
            48,187.729
            48.187,729
            48187.729
        """

        if value is None:
            return 0

        if pd.isna(value):
            return 0

        if isinstance(
            value,
            (int, float)
        ):
            return float(value)

        text = str(value).strip()

        if not text:
            return 0

        # ----------------------------------------------
        # Hapus spasi
        # ----------------------------------------------

        text = text.replace(
            " ",
            ""
        )

        # ----------------------------------------------
        # Format Indonesia:
        # 1.234,56
        # ----------------------------------------------

        if "," in text and "." in text:

            comma_pos = text.rfind(",")
            dot_pos = text.rfind(".")

            if comma_pos > dot_pos:

                # 1.234,56
                text = text.replace(
                    ".",
                    ""
                )

                text = text.replace(
                    ",",
                    "."
                )

            else:

                # 1,234.56
                text = text.replace(
                    ",",
                    ""
                )

        elif "," in text:

            # Jika hanya koma:
            # cek kemungkinan desimal
            parts = text.split(",")

            if len(parts) == 2 and len(
                parts[1]
            ) <= 3:

                text = text.replace(
                    ",",
                    "."
                )

            else:

                text = text.replace(
                    ",",
                    ""
                )

        elif text.count(".") > 1:

            # 1.234.567
            text = text.replace(
                ".",
                ""
            )

        # ----------------------------------------------
        # Hanya ambil angka valid
        # ----------------------------------------------

        try:

            return float(text)

        except ValueError:

            return 0

    # ==================================================
    # CLEAN TEXT
    # ==================================================

    @staticmethod
    def clean_text(value):

        if value is None:
            return ""

        if pd.isna(value):
            return ""

        return str(value).strip()