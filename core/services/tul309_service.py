"""
==========================================================
Mahdi PDF Studio
TUL 309 Service
==========================================================

Service untuk membaca dan mengolah file Excel TUL 309.

Input:
- Banyak file Excel (.xls / .xlsx)

Informasi yang dibaca:
- C4  : Kabupaten/Kota
- B5  : Keterangan
- B6  : Bulan dan Tahun

Data tarif:
- S : row 28
- R : row 45
- P : row 76
- T : row 77 + 78
- C : row 79 + 80 + 81
- L : row 82 + 83 + 84

Kolom sumber:
- D : Jumlah Pelanggan
- E : Total Daya (VA)
- F : Total Pemakaian kWH
- Q : Total Penjualan (Rupiah)

Output:
- Kabupaten/Kota
- Bulan
- Tahun
- Golongan Tarif
- Jumlah Pelanggan
- Total Daya (VA)
- Total Pemakaian kWH
- Total Penjualan (Rupiah)
- Keterangan

==========================================================
"""

import os
import re

import pandas as pd


class TUL309Service:
    """
    Mesin pengolahan data TUL 309.
    """

    # ==================================================
    # KONFIGURASI BARIS
    # ==================================================

    # Nomor baris Excel -> nomor index pandas (dikurangi 1)
    TARIF_ROWS = {
        "S": [28],
        "R": [45],
        "P": [76],
        "T": [77, 78],
        "C": [79, 80, 81],
        "L": [82, 83, 84],
    }

    # Kolom sumber Excel
    COL_CUSTOMER = 3       # D
    COL_POWER = 4          # E
    COL_USAGE = 5          # F
    COL_SALES = 16         # Q

    # ==================================================
    # PUBLIC METHOD
    # ==================================================

    @classmethod
    def process_files(
        cls,
        file_paths
    ):
        """
        Memproses beberapa file Excel TUL 309.

        Parameters
        ----------
        file_paths : list
            Daftar path file Excel.

        Returns
        -------
        pandas.DataFrame
            Hasil rekap seluruh file.
        """

        all_results = []

        for file_path in file_paths:

            result = cls.process_file(
                file_path
            )

            all_results.extend(
                result
            )

            result_df = pd.DataFrame(
            all_results,
            columns=[
                "Kabupaten/Kota",
                "Bulan",
                "Tahun",
                "Golongan Tarif",
                "Jumlah Pelanggan",
                "Total Daya (VA)",
                "Total Pemakaian kWH",
                "Total Penjualan (Rupiah)",
                "Keterangan"
            ]
        )

        # Tambahkan kolom No
        result_df.insert(
            0,
            "No",
            range(1, len(result_df) + 1)
        )

        return result_df



    # ==================================================
    # PROCESS SINGLE FILE
    # ==================================================

    @classmethod
    def process_file(
        cls,
        file_path
    ):
        """
        Memproses satu file Excel.

        Menghasilkan 6 baris:
        S, R, P, T, C, L
        """

        if not os.path.exists(file_path):

            raise FileNotFoundError(
                f"File tidak ditemukan:\n{file_path}"
            )

        # ----------------------------------------------
        # Baca Excel
        # ----------------------------------------------

        df = cls.read_excel(
            file_path
        )

        # ----------------------------------------------
        # Metadata
        # ----------------------------------------------

        kabupaten = cls.get_cell(
            df,
            4,
            3
        )

        b5 = cls.get_cell(
            df,
            5,
            2
        )

        b6 = cls.get_cell(
            df,
            6,
            2
        )

        # ----------------------------------------------
        # Keterangan
        # ----------------------------------------------

        keterangan = cls.extract_keterangan(
            b5
        )

        # ----------------------------------------------
        # Bulan dan Tahun
        # ----------------------------------------------

        bulan, tahun = cls.extract_month_year(
            b6
        )

        # ----------------------------------------------
        # Hasil file
        # ----------------------------------------------

        results = []

        for tarif, rows in cls.TARIF_ROWS.items():

            values = cls.sum_rows(
                df,
                rows
            )

            results.append({

                "Kabupaten/Kota":
                    str(kabupaten).strip(),

                "Bulan":
                    bulan,

                "Tahun":
                    tahun,

                "Golongan Tarif":
                    tarif,

                "Jumlah Pelanggan":
                    values["pelanggan"],

                "Total Daya (VA)":
                    values["daya"],

                "Total Pemakaian kWH":
                    values["pemakaian"],

                "Total Penjualan (Rupiah)":
                    values["penjualan"],

                "Keterangan":
                    keterangan
            })

        return results

    # ==================================================
    # READ EXCEL
    # ==================================================

    @staticmethod
    def read_excel(
        file_path
    ):
        """
        Membaca file XLS atau XLSX.

        Header=None digunakan karena posisi
        data TUL 309 berdasarkan nomor baris Excel.
        """

        extension = os.path.splitext(
            file_path
        )[1].lower()

        if extension == ".xls":

            return pd.read_excel(
                file_path,
                header=None,
                engine="xlrd"
            )

        return pd.read_excel(
            file_path,
            header=None,
            engine="openpyxl"
        )

    # ==================================================
    # GET CELL
    # ==================================================

    @staticmethod
    def get_cell(
        df,
        excel_row,
        excel_column
    ):
        """
        Mengambil nilai berdasarkan koordinat Excel.

        Contoh:
        C4 -> row 4, column 3
        B5 -> row 5, column 2
        """

        row_index = excel_row - 1
        col_index = excel_column - 1

        try:

            value = df.iloc[
                row_index,
                col_index
            ]

        except IndexError:

            return ""

        if pd.isna(value):

            return ""

        return value

    # ==================================================
    # EXTRACT KETERANGAN
    # ==================================================

    @staticmethod
    def extract_keterangan(
        value
    ):
        """
        Mengambil kata terakhir dari B5.

        Contoh:

        'REKAP LPB'
            -> LPB

        'REKAP NORMAL'
            -> NORMAL

        'REKAP TOTAL'
            -> TOTAL
        """

        text = str(
            value
        ).strip()

        if not text:

            return ""

        words = text.split()

        return words[-1]

    # ==================================================
    # EXTRACT MONTH / YEAR
    # ==================================================

    @staticmethod
    def extract_month_year(
        value
    ):
        """
        Mengambil Bulan dan Tahun dari B6.

        Contoh:
        'Juni 2026'
            -> Juni, 2026

        'Juni 26'
            -> Juni, 2026
        """

        text = str(
            value
        ).strip()

        if not text:

            return "", ""

        # ----------------------------------------------
        # Cari tahun 4 digit
        # ----------------------------------------------

        year_match = re.search(
            r"(20\d{2})",
            text
        )

        if year_match:

            tahun = int(
                year_match.group(1)
            )

        else:

            # ------------------------------------------
            # Cari tahun 2 digit
            # ------------------------------------------

            year_match = re.search(
                r"\b(\d{2})\b",
                text
            )

            if year_match:

                tahun = 2000 + int(
                    year_match.group(1)
                )

            else:

                tahun = ""

        # ----------------------------------------------
        # Daftar bulan
        # ----------------------------------------------

        months = [
            "Januari",
            "Februari",
            "Maret",
            "April",
            "Mei",
            "Juni",
            "Juli",
            "Agustus",
            "September",
            "Oktober",
            "November",
            "Desember"
        ]

        bulan = ""

        text_lower = text.lower()

        for month in months:

            if month.lower() in text_lower:

                bulan = month

                break

        return bulan, tahun

    # ==================================================
    # SUM ROWS
    # ==================================================

    @classmethod
    def sum_rows(
        cls,
        df,
        rows
    ):
        """
        Menjumlahkan baris untuk satu golongan tarif.

        Kolom:
        D = pelanggan
        E = daya
        F = pemakaian
        Q = penjualan
        """

        pelanggan = 0
        daya = 0
        pemakaian = 0
        penjualan = 0

        for excel_row in rows:

            row_index = excel_row - 1

            # ------------------------------------------
            # Jumlah Pelanggan - D
            # ------------------------------------------

            pelanggan += cls.to_number(
                cls.get_dataframe_cell(
                    df,
                    row_index,
                    cls.COL_CUSTOMER
                )
            )

            # ------------------------------------------
            # Total Daya - E
            # ------------------------------------------

            daya += cls.to_number(
                cls.get_dataframe_cell(
                    df,
                    row_index,
                    cls.COL_POWER
                )
            )

            # ------------------------------------------
            # Total Pemakaian - F
            # ------------------------------------------

            pemakaian += cls.to_number(
                cls.get_dataframe_cell(
                    df,
                    row_index,
                    cls.COL_USAGE
                )
            )

            # ------------------------------------------
            # Total Penjualan - Q
            # ------------------------------------------

            penjualan += cls.to_number(
                cls.get_dataframe_cell(
                    df,
                    row_index,
                    cls.COL_SALES
                )
            )

        return {
            "pelanggan": pelanggan,
            "daya": daya,
            "pemakaian": pemakaian,
            "penjualan": penjualan
        }

    # ==================================================
    # DATAFRAME CELL
    # ==================================================

    @staticmethod
    def get_dataframe_cell(
        df,
        row_index,
        column_index
    ):
        """
        Mengambil cell berdasarkan index pandas.
        """

        try:

            value = df.iloc[
                row_index,
                column_index
            ]

        except IndexError:

            return 0

        return value

    # ==================================================
    # NUMBER CONVERSION
    # ==================================================

    @staticmethod
    def to_number(
        value
    ):
        """
        Mengubah berbagai bentuk angka menjadi float.

        Mendukung contoh:

        12345
        12345.67
        '12345.67'
        '48,187.729'
        '1,234,567'
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

        text = str(
            value
        ).strip()

        if not text:

            return 0

        # ----------------------------------------------
        # Hilangkan spasi
        # ----------------------------------------------

        text = text.replace(
            " ",
            ""
        )

        # ----------------------------------------------
        # Hilangkan simbol non angka
        # kecuali titik, koma, minus
        # ----------------------------------------------

        text = re.sub(
            r"[^0-9,.\-]",
            "",
            text
        )

        if not text:

            return 0

        # ----------------------------------------------
        # Format angka
        #
        # Contoh:
        # 48,187.729
        # 1,234,567
        # ----------------------------------------------

        if "," in text and "." in text:

            # Jika titik muncul setelah koma,
            # koma dianggap separator ribuan.
            if text.rfind(".") > text.rfind(","):

                text = text.replace(
                    ",",
                    ""
                )

            else:

                text = text.replace(
                    ".",
                    ""
                )

                text = text.replace(
                    ",",
                    "."
                )

        elif "," in text:

            # Jika koma hanya satu dan diikuti
            # 1-2 digit, kemungkinan decimal.
            parts = text.split(",")

            if (
                len(parts) == 2
                and len(parts[1]) <= 2
            ):

                text = text.replace(
                    ",",
                    "."
                )

            else:

                text = text.replace(
                    ",",
                    ""
                )

        try:

            return float(text)

        except ValueError:

            return 0