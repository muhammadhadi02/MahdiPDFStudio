"""
====================================================
Mahdi PDF Studio
Feature Card Widget
====================================================

Card fitur dashboard.

Digunakan untuk:

- Merge PDF
- Split PDF
- Compress PDF
- Rotate PDF
- Watermark

Author : Muhammad Hadi Putra
"""

import customtkinter as ctk

from themes.colors import Colors
from themes.fonts import Fonts
from themes.spacing import Spacing
from themes.icons import Icons

ICON_MAP = {
    "merge": Icons.MERGE,
    "split": Icons.SPLIT,
    "excel": Icons.EXCEL,
    "piutang": Icons.PIUTANG,
    "bulog": Icons.BULOG
}

ICON_BACKGROUND = {
    "Merge PDF": Colors.MERGE_BG,
    "Split PDF": Colors.SPLIT_BG,
    "TUL 309": Colors.COMPRESS_BG,
    "Monev Piutang": Colors.ROTATE_BG,
}

class FeatureCard(ctk.CTkFrame):
    """
    Dashboard Feature Card.

    Struktur:

    ┌─────────────────────────────┐
    │ 📄                          │
    │                             │
    │ Merge PDF                   │
    │ Combine multiple PDFs       │
    │                             │
    │                         ○→  │
    └─────────────────────────────┘
    """

    CARD_HEIGHT = Spacing.FEATURE_CARD_HEIGHT

    def __init__(
        self,
        master,
        icon,
        title,
        description,
        command=None
    ):
        super().__init__(master)

        self.icon = icon
        self.title = title
        self.description = description
        self.command = command

        self.configure_card()
        self.create_widgets()

    # ==================================================
    # Card Style
    # ==================================================

    def configure_card(self):

        self.configure(
            height=100,
            corner_radius=Spacing.CARD_RADIUS,
            fg_color=Colors.CARD_BG,
            border_width=1,
            border_color=Colors.BORDER_CARD
        )

        self.grid_propagate(False)

        # Icon
        self.grid_columnconfigure(
            0,
            weight=0
        )

        # Text
        self.grid_columnconfigure(
            1,
            weight=1
        )

        # Arrow
        self.grid_columnconfigure(
            2,
            weight=0
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            1,
            weight=1
        )

    # ==================================================
    # Widgets
    # ==================================================

    def create_widgets(self):

        # ==================================================
        # Icon
        # ==================================================

        icon_container = ctk.CTkFrame(
            self,
            width=56,
            height=56,
            corner_radius=Spacing.ICON_RADIUS,
            fg_color=ICON_BACKGROUND.get(
                self.title,
                Colors.MERGE_BG
            )
        )

        icon_container.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(15,10),
            pady=15
        )

        icon_container.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_container,
            text="",
            image=ICON_MAP[self.icon]
        )

        icon_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # ==================================================
        # Title
        # ==================================================

        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=Fonts.CARD_TITLE,
            text_color=Colors.TEXT_PRIMARY,
            justify="left"
        )

        title_label.grid(
            row=0,
            column=1,           
            sticky="sw",
            pady=0
        )

        # ==================================================
        # Description
        # ==================================================

        description_label = ctk.CTkLabel(
            self,
            text=self.description,
            font=Fonts.CARD_DESCRIPTION,
            justify="left",
            wraplength=260,
            text_color=Colors.TEXT_SECONDARY
        )

        description_label.grid(
            row=1,
            column=1,
            sticky="nw",
            pady=0
        )



        # ==================================================
        # Action Button
        # ==================================================

        action_button = ctk.CTkButton(
            self,
            text="→",
            width=36,
            height=36,
            corner_radius=15,
            font=Fonts.ARROW_BUTTON,
            fg_color=Colors.ARROW_BG,
            text_color=Colors.PRIMARY,
            border_width=1,
            border_color=Colors.ARROW_BORDER,
            hover_color=Colors.BORDER_LIGHT,
            command=self.command
        )

        action_button.grid(
            row=0,
            column=2,
            rowspan=2,
            padx=(15,15)
        )