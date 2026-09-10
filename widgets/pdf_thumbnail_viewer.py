"""
==========================================================
PDF Thumbnail Viewer
==========================================================

Tujuan
-------
Menampilkan preview halaman PDF
dalam bentuk thumbnail yang dapat
di-scroll.

Fitur Saat Ini
--------------
✓ Grid Thumbnail
✓ Scrollable
✓ Nomor Halaman

Fitur Berikutnya
----------------
□ Klik Thumbnail
□ Multi Select
□ Highlight Selection
□ Zoom Preview

Arsitektur
-----------

PDF
 │
 ▼

PyMuPDF
 │
 ▼

Pixmap
 │
 ▼

PIL Image
 │
 ▼

CTkImage
 │
 ▼

Thumbnail Viewer

==========================================================
"""

import customtkinter as ctk
from themes.colors import Colors


class PdfThumbnailViewer(ctk.CTkScrollableFrame):
    """
    Viewer thumbnail halaman PDF.

    Tanggung Jawab
    ---------------

    ✓ Menampilkan thumbnail
    ✓ Menampilkan nomor halaman
    ✓ Mengelola grid thumbnail

    Tidak Bertanggung Jawab
    -----------------------

    ✗ Membaca PDF
    ✗ Render PDF
    ✗ Menyimpan file

    Semua data thumbnail akan
    dikirim dari SplitPage.
    """

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        master
    ):
        """
        Inisialisasi thumbnail viewer.
        """

        super().__init__(
            master,
            height=3,
            fg_color="#F5F8FC",
            corner_radius=14,
        )

        # ==================================================
        # Grid Configuration
        # ==================================================
        #
        # Membuat seluruh kolom memiliki
        # bobot yang sama sehingga thumbnail
        # dapat berada di tengah viewer.
        #
        # ==================================================

        for column in range(4):

            self.grid_columnconfigure(
                column,
                weight=1
            )

        # ==============================================
        # Thumbnail Registry
        # ==============================================
        #
        # Menyimpan seluruh card thumbnail
        # yang sudah dirender.
        #
        # Digunakan untuk:
        #
        # - Clear Viewer
        # - Refresh Viewer
        # - Future Selection
        #
        # ==============================================

        self.thumbnail_images = []
        self.thumbnail_widgets = []
        

    # ==================================================
    # Clear Viewer
    # ==================================================

    def clear(self):
        """
        Menghapus seluruh thumbnail
        dari viewer.
        """

        for widget in self.thumbnail_widgets:

            widget.destroy()

        self.thumbnail_widgets.clear()

    # ==================================================
    # Add Thumbnail
    # ==================================================

    def add_thumbnail(
        self,
        image,
        page_number
    ):
        """
        Menambahkan thumbnail baru.

        Parameters
        ----------
        image : CTkImage

            Thumbnail halaman PDF.

        page_number : int

            Nomor halaman.
        """

        # ==============================================
        # Thumbnail Card
        # ==============================================

        card = ctk.CTkFrame(
            self,
            width=180,
            height=100,

            corner_radius=16,

            fg_color=Colors.CARD_BG,

            border_width=1,

            border_color=Colors.BORDER
        )

        card.grid(
            row=(page_number - 1) // 3,
            column=(page_number - 1) % 3,
            padx=5,
            pady=5,
            sticky=""
        )

        # ==============================================
        # Thumbnail Image
        # ==============================================

        image_label = ctk.CTkLabel(
            card,
            text="",
            image=image
        )

        image_label.pack(
            padx=5,
            pady=(5, 0)
        )

        # ==============================================
        # Page Label
        # ==============================================

        page_label = ctk.CTkLabel(
            card,
            text=f"Page {page_number}",
            font=("Segoe UI", 13)
        )

        page_label.pack(
            pady=5
        )

        self.thumbnail_images.append(image)
        self.thumbnail_widgets.append(
            card
        )