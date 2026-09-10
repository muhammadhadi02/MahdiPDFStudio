"""
==========================================================
Mahdi PDF Studio
main.py

Entry Point aplikasi.

File ini sengaja dibuat sangat kecil.
Semua proses aplikasi berada pada folder app/.
==========================================================
"""

from app.app import MahdiPDFStudio


def main():
    """
    Membuat dan menjalankan aplikasi.
    """

    app = MahdiPDFStudio()

    app.mainloop()


if __name__ == "__main__":
    main()