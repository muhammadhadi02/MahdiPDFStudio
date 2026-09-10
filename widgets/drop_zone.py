"""
==========================================================
Mahdi PDF Studio
Drop Zone Widget
==========================================================

Area drag & drop file.

Author : Muhammad Hadi Putra
"""

import customtkinter as ctk

from themes.colors import Colors
from themes.icons import Icons


class DropZone(ctk.CTkFrame):
    """
    Area untuk drag & drop file.

    Saat ini:
        - Menampilkan instruksi
        - Siap untuk integrasi tkinterdnd2

    Nantinya:
        - Drag file
        - Highlight saat hover
        - Validasi ekstensi file
    """

    def __init__(self, master):
        super().__init__(master)

        self.configure(
            height=120,
            corner_radius=25,
            fg_color=Colors.HERO_BG,
            border_width=2,
            border_color=Colors.DROPZONE_BORDER
        )

        self.create_widgets()

    def create_widgets(self):

        # ======================================================
        # ICON
        # ======================================================

        icon = ctk.CTkLabel(
            self,
            text="",
            image=Icons.PDF_EMPTY,
        )

        icon.pack(
            pady=(15, 5)
        )

        # ======================================================
        # TITLE
        # ======================================================

        title = ctk.CTkLabel(
            self,
            text="Drag & Drop File Here",
            font=("Segoe UI", 16, "bold")
        )

        title.pack()

        # ======================================================
        # SUBTITLE
        # ======================================================

        subtitle = ctk.CTkLabel(
            self,
            text="atau klik tombol Tambah File",
            font=("Segoe UI", 12),
            text_color=Colors.TEXT_SECONDARY
        )

        subtitle.pack(
            pady=(0, 15)
        )