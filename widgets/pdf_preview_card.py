"""
==========================================================
Mahdi PDF Studio
PDF Preview Card
==========================================================

Widget reusable untuk menampilkan
informasi PDF yang dipilih user.

Digunakan oleh:

- Split PDF
- Compress PDF
- Rotate PDF
- Watermark PDF

==========================================================

Tanggung Jawab
--------------

✓ Menampilkan metadata PDF
✓ Menampilkan nama file
✓ Menampilkan ukuran file
✓ Menampilkan status file

Tidak Bertanggung Jawab
-----------------------

✗ Membaca PDF
✗ Memproses PDF
✗ Menyimpan PDF

==========================================================
"""

import customtkinter as ctk
from themes.colors import Colors


class PdfPreviewCard(ctk.CTkFrame):
    """
    Card informasi PDF.
    """

    def __init__(
        self,
        master
    ):
        super().__init__(
            master,
            corner_radius=12,
            width=250,
            height=110
        )

        self.pack_propagate(False)
        self.create_widgets()
        
        self.configure(
            fg_color=Colors.CARD_BG,
            border_width=1,
            border_color=Colors.BORDER
        )
        

    # ==================================================
    # Build UI
    # ==================================================

    def create_widgets(self):

        # ==================================================
        # File Name
        # ==================================================

        self.file_label = ctk.CTkLabel(
            self,
            text="📄 Belum ada PDF dipilih",
            font=("Segoe UI", 14, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        self.file_label.pack(
            anchor="w",
            padx=20,
            pady=(15, 8)
        )

        # ==================================================
        # Metadata
        # ==================================================

        self.pages_label = ctk.CTkLabel(
            self,
            text="Pages : -",
            text_color=Colors.TEXT_PRIMARY
        )

        self.pages_label.pack(
            anchor="w",
            padx=20,
            pady=(0,2)
        )

        self.size_label = ctk.CTkLabel(
            self,
            text="Size : -",
            text_color=Colors.TEXT_PRIMARY
        )

        self.size_label.pack(
            anchor="w",
            padx=20,
            pady=(0,2)
        )

        

    # ==================================================
    # Update Card
    # ==================================================

    def update_pdf(
        self,
        filename,
        pages,
        size_mb
    ):
        """
        Update informasi PDF.
        """

        self.file_label.configure(
            text=self.shorten_filename(
                filename
            )
        )

        self.pages_label.configure(
            text=f"Pages : {pages}"
        )

        self.size_label.configure(
            text=f"Size : {size_mb:.2f} MB"
        )

        

    # ==================================================
    # Reset Card
    # ==================================================

    def reset(self):

        self.file_label.configure(
            text="📄 Belum ada PDF dipilih"
        )

        self.pages_label.configure(
            text="Pages : -"
        )

        self.size_label.configure(
            text="Size : -"
        )

        self.status_label.configure(
            text="Status : Waiting"
        )

    def shorten_filename(
        self,
        filename,
        max_length=20
    ):

        if len(filename) <= max_length:
            return filename

        return filename[:max_length] + "..."