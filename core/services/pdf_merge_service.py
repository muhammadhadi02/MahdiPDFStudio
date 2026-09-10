"""
=========================================================
Mahdi PDF Studio
PDF Merge Service
=========================================================

Service untuk menggabungkan beberapa file PDF
menjadi satu dokumen PDF.

Layer Arsitektur:

    MergePage (UI)
            ↓
    PdfMergeService
            ↓
         pypdf

Author : Muhammad Hadi Putra
"""

from pypdf import PdfReader
from pypdf import PdfWriter


class PdfMergeService:
    """
    Service yang bertanggung jawab untuk
    proses penggabungan file PDF.

    Class ini tidak menyimpan state sehingga
    seluruh operasi menggunakan staticmethod.
    """

    @staticmethod
    def merge(files, output_path) -> tuple[bool, str]:
        """
        Menggabungkan beberapa file PDF.

        Returns
        -------
        tuple[bool, str]

        Success:
            (True, "")

        Failed:
            (False, error_message)
        """

        try:

            writer = PdfWriter()

            for pdf in files:

                reader = PdfReader(pdf.path)

                for page in reader.pages:
                    writer.add_page(page)

            with open(output_path, "wb") as file:
                writer.write(file)

            return True, ""

        except Exception as error:

            return False, str(error)