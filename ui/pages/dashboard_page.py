"""
dashboard_page.py
--------------------------------------------------
Dashboard utama Mahdi PDF Studio

Author : Muhammad Hadi Putra
"""

import customtkinter as ctk

from ui.sections.hero_section import HeroSection
from ui.sections.quick_tools_section import QuickToolsSection


class DashboardPage(ctk.CTkFrame):

    def __init__(
        self,
        master,
        navigation
    ):
        super().__init__(master)

        self.configure(
            fg_color="transparent"
        )

        self.navigation = navigation

        self.configure_layout()

        self.create_header()

        self.create_quick_tools()

        #self.create_recent_files()

        #self.create_drop_zone()

    # ==================================================
    # Layout
    # ==================================================

    def configure_layout(self):

        self.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            99,
            weight=1
        )

    # ==================================================
    # Header
    # ==================================================

    def create_header(self):

            hero = HeroSection(
            self,
            navigation=self.navigation
            )

            hero.grid(
                row=0,
                column=0,
                padx=30,
                pady=30,
                sticky="ew"
            )

    # ==================================================
    # Quick Tools
    # ==================================================

    def create_quick_tools(self):

        section = QuickToolsSection(
            self,
            navigation=self.navigation
        )

        section.grid(
            row=1,
            column=0,
            padx=30,
            pady=(10,30),
            sticky="ew"
        )

    # ==================================================
    # Recent Files
    # ==================================================

    def create_recent_files(self):

        label = ctk.CTkLabel(
            self,
            text="Recent Files",
            font=("Segoe UI", 18)
        )

        label.grid(
            row=3,
            column=0,
            pady=20
        )

    # ==================================================
    # Drop Zone
    # ==================================================

    def create_drop_zone(self):

        label = ctk.CTkLabel(
            self,
            text="Drag & Drop PDF Here",
            width=500,
            height=180,
            corner_radius=15,
            fg_color="#2B2B2B"
        )

        label.grid(
            row=4,
            column=0,
            pady=30
        )