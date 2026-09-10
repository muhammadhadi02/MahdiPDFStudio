"""
hero_section.py
----------------------------------------------------
Hero Section Dashboard

Menampilkan identitas aplikasi dan
shortcut ke fitur utama.

Author : Muhammad Hadi Putra
"""

import customtkinter as ctk
from PIL import Image
from pathlib import Path

from themes.colors import Colors
from themes.fonts import Fonts
from themes.spacing import Spacing


BASE_DIR = Path(__file__).resolve().parents[2]

logo_path = (
    BASE_DIR /
    "assets" /
    "logo" /
    "logo.png"
)


class HeroSection(ctk.CTkFrame):
    """
    Hero banner dashboard.

    Struktur:

    ┌──────────────────────────────────────┐
    │ LOGO │ Title                         │
    │      │ Subtitle                      │
    │      │ Status                        │
    │      │               │
    └──────────────────────────────────────┘
    """

    def __init__(
        self,
        master,
        navigation
    ):
        super().__init__(master)

        self.navigation = navigation

        self.configure_card()

        self.create_widgets()

    # ==================================================
    # Card Style
    # ==================================================

    def configure_card(self):

        self.configure(
            height=190,
            corner_radius=Spacing.CARD_RADIUS,
            fg_color=Colors.HERO_BG,
            border_width=1,
            border_color=Colors.BORDER_HERO
        )

        self.grid_propagate(False)

        self.grid_rowconfigure(
            0,
            weight=1
        )

        self.grid_columnconfigure(
            0,
            weight=1
        )

    # ==================================================
    # Widgets
    # ==================================================

    def create_widgets(self):

        # ==========================================
        # Main Content
        # ==========================================

        content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        content.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        content.grid_columnconfigure(
            0,
            weight=0
        )

        content.grid_columnconfigure(
            1,
            weight=0
        )

        # ==========================================
        # Logo Container
        # ==========================================

        logo_container = ctk.CTkFrame(
            content,
            width=120,
            height=120,
            corner_radius=24,
            fg_color=Colors.LOGO_CARD_BG,
            border_color=Colors.LOGO_CARD_BORDER,
            border_width=1
        )

        logo_container.grid(
            row=0,
            column=0,
            rowspan=3,
            padx=(0, 36),
            sticky="ns"
        )

        logo_container.grid_propagate(False)

        # ==========================================
        # Logo
        # ==========================================

        image = Image.open(logo_path)

        self.logo = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=(90, 90)
        )

        logo_label = ctk.CTkLabel(
            logo_container,
            text="",
            image=self.logo
        )

        logo_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # ==========================================
        # Text Container
        # ==========================================

        text_frame = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        text_frame.grid(
            row=0,
            column=1,
            sticky="w"
        )

        # ==========================================
        # Title
        # ==========================================

        title = ctk.CTkLabel(
            text_frame,
            text="Mahdi PDF Studio",
            font=Fonts.HERO_TITLE,
            text_color=Colors.TEXT_PRIMARY
        )

        title.pack(
            anchor="w"
        )

        # ==========================================
        # Subtitle
        # ==========================================

        subtitle = ctk.CTkLabel(
            text_frame,
            text="Modern PDF Toolkit for Everyday Productivity",
            font=Fonts.HERO_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY
        )

        subtitle.pack(
            anchor="w",
            pady=(8, 12)
        )

        # ==========================================
        # Status
        # ==========================================

        status = ctk.CTkLabel(
            text_frame,
            text="⚡ Fast   •   🔒 Secure   •   💻 Offline",
            font=("Segoe UI", 14),
            text_color=Colors.TEXT_SECONDARY
        )

        status.pack(
            anchor="w"
        )