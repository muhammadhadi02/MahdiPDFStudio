"""
=========================================================
Mahdi PDF Studio
Quick Tools Section
=========================================================

Section yang menampilkan fitur utama aplikasi.

Dashboard hanya mengetahui daftar tool
dari TOOLS sehingga bersifat dinamis.

Author : Muhammad Hadi Putra
"""

import customtkinter as ctk

from widgets.feature_card import FeatureCard
from data.tools import TOOLS
from themes.fonts import Fonts
from themes.colors import Colors


class QuickToolsSection(ctk.CTkFrame):
    """
    Quick Tools Dashboard.

    Struktur:

    Quick Tools

    ┌─────────────┐ ┌─────────────┐
    │ Merge PDF   │ │ Split PDF   │
    └─────────────┘ └─────────────┘

    ┌─────────────┐ ┌─────────────┐
    │ Compress    │ │ Rotate      │
    └─────────────┘ └─────────────┘
    """

    def __init__(
        self,
        master,
        navigation
    ):
        super().__init__(
            master,
            fg_color="transparent"
        )

        self.navigation = navigation

        self.configure_layout()

        self.create_widgets()

    # ==================================================
    # Layout
    # ==================================================

    def configure_layout(self):

        self.grid_columnconfigure(
            0,
            weight=1
        )

    # ==================================================
    # Widgets
    # ==================================================

    def create_widgets(self):

        self.create_header()

        self.create_cards()

    # ==================================================
    # Header
    # ==================================================

    def create_header(self):

        title = ctk.CTkLabel(
            self,
            text="Quick Tools",
            font=Fonts.SECTION_TITLE_QUICK,
            text_color=Colors.TEXT_PRIMARY
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 0)
        )

    # ==================================================
    # Cards
    # ==================================================

    def create_cards(self):

        cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        cards_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        cards_frame.grid_columnconfigure(
            0,
            weight=1
        )

        cards_frame.grid_columnconfigure(
            1,
            weight=1
        )

        dashboard_tools = [
            tool for tool in TOOLS
            if tool.page != "verifikasi_banpang"
        ]

        for index, tool in enumerate(dashboard_tools):

            row = index // 2
            col = index % 2

            card = FeatureCard(
                cards_frame,
                icon=tool.icon,
                title=tool.title,
                description=tool.description,
                command=lambda page=tool.page:
                    self.navigation.navigate(page)
            )

            card.grid(
                row=row,
                column=col,
                padx=(0,0),
                pady=15,
                sticky="nsew"
            )