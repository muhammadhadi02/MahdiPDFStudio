"""
==========================================================
Mahdi PDF Studio
Sidebar
==========================================================

Sidebar merupakan navigasi utama aplikasi.

Tanggung Jawab
--------------

1. Menampilkan identitas aplikasi
2. Menampilkan menu navigasi
3. Menampilkan active state
4. Meneruskan aksi navigasi ke Navigation Controller

Tidak Bertanggung Jawab
-----------------------

✗ Menampilkan halaman
✗ Mengelola Workspace
✗ Menjalankan fitur PDF

Arsitektur
----------

User
 │
 ▼
Sidebar
 │
 ▼
Navigation
 │
 ▼
Workspace
 │
 ▼
Page

Struktur Sidebar
----------------

Brand
 ├─ Logo
 ├─ Mahdi PDF
 └─ Studio

Dashboard

PDF Tools
 ├─ Merge PDF
 ├─ Split PDF
 ├─ Compress PDF
 └─ Rotate PDF

Utility
 ├─ Settings
 └─ About

Footer
 └─ Version

Author : Muhammad Hadi Putra
"""

import customtkinter as ctk

from data.tools import TOOLS

from themes.colors import Colors
from themes.fonts import Fonts
from themes.spacing import Spacing
from themes.icons import Icons

TOOL_ICONS = {
                    "merge": Icons.MERGE,
                    "split": Icons.SPLIT,
                    "excel": Icons.EXCEL,
                    "piutang": Icons.PIUTANG,
                    "admin": Icons.ADMIN,
                    "bulog": Icons.BULOG
                }

from PIL import Image
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

logo_path = (
    BASE_DIR /
    "assets" /
    "logo" /
    "logo.png"
)

class Sidebar(ctk.CTkFrame):
    """
    Sidebar navigasi utama aplikasi.

    Filosofi:
    ----------
    Sidebar berfungsi sebagai pusat navigasi.

    Dashboard dipisahkan dari PDF Tools
    agar hirarki aplikasi lebih jelas.

    Keuntungan:
    ------------
    ✓ Lebih profesional
    ✓ Mudah dikembangkan
    ✓ Mendukung banyak fitur baru
    ✓ Konsisten dengan desktop app modern
    """

    SIDEBAR_WIDTH = 240

    def __init__(
        self,
        master,
        navigation
    ):
        super().__init__(
            master,
            width=self.SIDEBAR_WIDTH,
            corner_radius= Spacing.CARD_RADIUS,
            
        )

        
        self.navigation = navigation

        # Registry tombol navigasi

        self.configure(
            fg_color=Colors.SIDEBAR_BG,
            border_width=1,
            border_color=Colors.BORDER_SIDEBAR
        )

        self.buttons = {}

        self.pack_propagate(False)

        self.create_widgets()

    # ==================================================
    # Build UI
    # ==================================================

    def create_widgets(self):

        self.create_brand_section()

        self.create_dashboard_section()

        self.create_tools_section()

        self.create_chat_section()

        self.create_footer_section()

        # Default startup page
        self.set_active(
            "dashboard"
        )

    # ==================================================
    # Brand Section
    # ==================================================

    def create_brand_section(self):

        brand_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        brand_frame.pack(
            fill="x",
            padx=18,
            pady=(16, 18)
        )

        self.logo = ctk.CTkImage(
            light_image=Image.open(logo_path),
            dark_image=Image.open(logo_path),
            size=(40, 40)
        )

        # Container horizontal
        header_frame = ctk.CTkFrame(
            brand_frame,
            fg_color="transparent"
        )

        header_frame.pack(
            fill="x"
        )

        logo = ctk.CTkLabel(
            header_frame,
            text="",
            image=self.logo
        )

        logo.pack(
            side="left",
            padx=(0, 10)
        )

        text_frame = ctk.CTkFrame(
            header_frame,
            fg_color="transparent"
        )

        text_frame.pack(
            side="left",
            fill="y"
        )

        title = ctk.CTkLabel(
            text_frame,
            text="Mahdi PDF",
            font=("Segoe UI", 15, "bold"),
            anchor="w"
        )

        title.pack(
            anchor="w"
        )

        subtitle = ctk.CTkLabel(
            text_frame,
            text="Studio",
            font=("Segoe UI", 11),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )

        subtitle.pack(
            anchor="w"
        )

    # ==================================================
    # Dashboard Section
    # ==================================================

    def create_dashboard_section(self):

        self.dashboard_button = ctk.CTkButton(
            self,
            text="Dashboard",
            image=Icons.DASHBOARD,
            compound="left",
            anchor="w",
            height=40,
            command=lambda:
                self.navigate("dashboard")
        )

        self.dashboard_button.pack(
            fill="x",
            padx=20
            
        )

        self.buttons[
            "dashboard"
        ] = self.dashboard_button

    # ==================================================
    # PDF Tools Section
    # ==================================================

    def create_tools_section(self):

        tools_label = ctk.CTkLabel(
            self,
            text="PDF TOOLS",
            font=("Segoe UI", 11, "bold"),
            text_color=Colors.TEXT_SECONDARY
        )

        tools_label.pack(
            anchor="w",
            padx=20,
            pady=(5, 8)
        )

        for tool in TOOLS:

            button = ctk.CTkButton(
                self,
                text=tool.title,
                image=TOOL_ICONS[tool.icon],
                compound="left",
                anchor="w",
                height=38,
                command=lambda page=tool.page:
                    self.navigate(page)
            )

            button.pack(
                fill="x",
                padx=20,
                pady=2
            )

            self.buttons[
                tool.page
            ] = button


    # ==================================================
    # Chat Admin Section
    # ==================================================

    def create_chat_section(self):

        separator = ctk.CTkFrame(
            self,
            height=1,
            fg_color=Colors.BORDER
        )

        separator.pack(
            fill="x",
            padx=20,
            pady=(10, 8)
        )

        chat_label = ctk.CTkLabel(
            self,
            text="COMMUNICATION",
            font=("Segoe UI", 11, "bold"),
            text_color=Colors.TEXT_SECONDARY
        )

        chat_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 8)
        )

        chat_button = ctk.CTkButton(
            self,
            text="Chat Admin",
            image=Icons.ADMIN,
            compound="left",
            anchor="w",
            height=38,
            command=lambda:
                self.navigate("chat_admin")
        )

        chat_button.pack(
            fill="x",
            padx=20,
            pady=2
        )

        self.buttons[
            "chat_admin"
        ] = chat_button

        # ----------------------------------------------
        # Login Admin
        # ----------------------------------------------

        admin_login_button = ctk.CTkButton(
            self,
            text="Login Admin",
            image=Icons.ADMIN,
            compound="left",
            anchor="w",
            height=38,
            fg_color="transparent",
            text_color=Colors.TEXT_PRIMARY,
            hover_color=Colors.BORDER_LIGHT,
            command=lambda: self.navigate("admin_login")
        )

        admin_login_button.pack(
            fill="x",
            padx=20,
            pady=(8, 2)
        )

        self.buttons[
            "login_admin"
        ] = admin_login_button

    


    # ==================================================
    # Footer Section
    # ==================================================

    def create_footer_section(self):

        footer_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=80
        )

        footer_frame.pack(
            side="bottom",
            fill="x",
            padx=8,
            pady=(0, 12)
        )

        separator = ctk.CTkFrame(
            footer_frame,
            height=2,
            corner_radius=0,
            fg_color=Colors.DIVIDER
        )

        separator.pack(
            fill="x",
            padx=16,

        )

        app_name = ctk.CTkLabel(
            footer_frame,
            text="Mahdi PDF Studio",
            font=("Segoe UI", 11, "bold"),
            text_color=Colors.TEXT_SECONDARY
        )

        app_name.pack()

        version = ctk.CTkLabel(
            footer_frame,
            text="Version 1.0.0",
            font=("Segoe UI", 10),
            text_color=Colors.TEXT_MUTED
        )

        version.pack(pady=(0, 4))

    # ==================================================
    # Navigation
    # ==================================================

    def navigate(
        self,
        page_name
    ):
        """
        Menjalankan navigasi halaman.

        Alur:
        User
            ↓
        Sidebar
            ↓
        Navigation
            ↓
        Workspace
            ↓
        Page
        """

        self.navigation.navigate(
            page_name
        )

        self.set_active(
            page_name
        )

    # ==================================================
    # Active State
    # ==================================================

    def set_active(
        self,
        page_name
    ):
        """
        Mengubah active state tombol.

        Aturan:
        --------

        ✓ Hanya satu tombol aktif
        ✓ Tombol aktif berwarna biru
        ✓ Tombol lain berwarna netral
        """

        # Reset seluruh tombol

        for button in self.buttons.values():

            button.configure(
                fg_color="transparent",
                hover_color=Colors.BORDER_LIGHT,
                text_color=Colors.TEXT_PRIMARY
            )

        # Aktifkan tombol terpilih

        if page_name in self.buttons:

            self.buttons[
                page_name
            ].configure(
                fg_color=Colors.PRIMARY,
                text_color=Colors.MENU_ACTIVE_TEXT,
                hover_color=Colors.PRIMARY_HOVER
            )