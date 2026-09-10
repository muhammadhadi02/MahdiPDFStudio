import customtkinter as ctk

from themes.colors import Colors
from themes.fonts import Fonts


class EmptyDropZone(ctk.CTkFrame):

    def __init__(
        self,
        master,
        on_add_file
    ):
        super().__init__(
            master,
            fg_color="Colors.HERO_BG",
            corner_radius=24,
            border_width=1,
            border_color=Colors.BORDER_HERO,
            width=700,
            height=500
        )

        self.grid_propagate(False)

        self.on_add_file = on_add_file

        self.build_ui()

    def build_ui(self):

        icon = ctk.CTkLabel(
            self,
            text="📄",
            font=("Segoe UI Emoji", 64)
        )

        icon.pack(
            pady=(5, 10)
        )

        title = ctk.CTkLabel(
            self,
            text="Drop PDF Disini",
            font=Fonts.PAGE_TITLE,
            text_color=Colors.TEXT_PRIMARY,
        )

        title.pack(
            pady=(0,10),
            padx=10
        )

        subtitle = ctk.CTkLabel(
            self,
            text="atau",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY
        )

        subtitle.pack(
            pady=(0, 15)
        )

        add_button = ctk.CTkButton(
            self,
            text="+ Tambah PDF",
            command=self.on_add_file,
            height=42,
            corner_radius=12,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            font=Fonts.BUTTON
        )

        add_button.pack(
            pady=(0, 10)
        )