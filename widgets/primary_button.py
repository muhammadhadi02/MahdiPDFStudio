"""
====================================================
Mahdi PDF Studio
Primary Button Widget
====================================================

Widget tombol utama yang digunakan di seluruh aplikasi.

Contoh:
    - Open
    - Save
    - Merge
    - Export
    - Browse
"""

import customtkinter as ctk
from themes.colors import Colors
from themes.fonts import Fonts
from themes.spacing import Spacing


class PrimaryButton(ctk.CTkButton):
    """
    Tombol utama aplikasi.
    """

    def __init__(
        self,
        master,
        text,
        command=None,
        width=150,
        height=42
    ):

        super().__init__(master)

        self.button_text = text
        self.command = command
        self.width = width
        self.height = height

        self.configure_button()

    # ==================================================
    # Configuration
    # ==================================================

    def configure_button(self):
        """
        Mengatur tampilan tombol.
        """

        self.configure(
            text=self.button_text,
            command=self.command,
            width=self.width,
            height=self.height,

            corner_radius=Spacing.BUTTON_RADIUS,

            font=Fonts.BUTTON,

            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,

            text_color=Colors.MENU_ACTIVE_TEXT,

            cursor="hand2"
        )