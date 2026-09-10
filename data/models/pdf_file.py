"""
==========================================================
Mahdi PDF Studio
PDF File Model
==========================================================

Menyimpan seluruh informasi mengenai sebuah file PDF
yang dipilih pengguna.

Author  : Muhammad Hadi Putra
Version : 1.0

Model ini TIDAK mengandung kode UI.
==========================================================
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class PdfFile:
    """
    Model yang merepresentasikan satu buah file PDF.

    Class ini hanya menyimpan data.
    Tidak ada kode UI di sini.
    """

    # ==========================================================
    # INFORMASI FILE
    # ==========================================================

    # Path lengkap menuju file PDF.
    #
    # Contoh:
    #
    # Path("D:/Dokumen/Laporan.pdf")
    #
    path: Path

    # Nama file saja.
    #
    # Contoh:
    #
    # "Laporan.pdf"
    #
    filename: str

    # Jumlah halaman PDF.
    pages: int

    # Ukuran file dalam BYTE.
    #
    # Contoh:
    #
    # 262680
    #
    filesize: int

    # ==========================================================
    # METADATA
    # ==========================================================

    # True jika PDF terenkripsi.
    encrypted: bool = False

    # True jika file sedang dipilih.
    #
    # Saat ini belum wajib digunakan oleh Merge,
    # tetapi disiapkan untuk fitur berikutnya.
    selected: bool = False

    # Thumbnail PDF.
    #
    # Untuk sementara dapat berupa:
    #
    # None
    # PIL.Image
    # CTkImage
    #
    # Tetapi sebaiknya nanti kita tentukan apakah thumbnail
    # disimpan sebagai PIL.Image atau dibuat oleh FileItem.
    thumbnail: Optional[object] = None

    # ==========================================================
    # PROPERTY
    # ==========================================================

    @property
    def filesize_text(self) -> str:
        """
        Mengubah ukuran file dari BYTE menjadi format
        yang mudah dibaca manusia.

        Contoh:

            1024
            ↓
            1.00 KB

            1500000
            ↓
            1.43 MB
        """

        size = float(self.filesize)

        units = [
            "B",
            "KB",
            "MB",
            "GB",
            "TB",
        ]

        for unit in units:

            if size < 1024:

                return f"{size:.2f} {unit}"

            size /= 1024

        return f"{size:.2f} PB"