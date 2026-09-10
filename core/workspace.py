"""
==========================================================
Mahdi PDF Studio
Workspace
==========================================================

Workspace adalah area kerja utama aplikasi.

Tanggung Jawab
--------------
1. Menampilkan halaman aktif
2. Mengganti halaman ketika navigasi berubah
3. Menyimpan referensi halaman saat ini

Arsitektur
----------

Sidebar / Dashboard
        │
        ▼

Navigation
        │
        ▼

Workspace
        │
        ▼

Page Registry
        │
        ▼

Page Object
        │
        ├── DashboardPage
        ├── MergePage
        ├── SplitPage
        └── (Future Pages)

Keuntungan
-----------
✓ Mudah menambah fitur baru
✓ Tidak perlu if-else panjang
✓ Semua halaman terpusat
✓ Mudah dirawat

==========================================================
"""

import customtkinter as ctk

from ui.pages.dashboard_page import DashboardPage
from ui.pages.merge_page import MergePage
from ui.pages.split_page import SplitPage
from ui.pages.tul309_page import TUL309Page
from ui.pages.monev_piutang_page import MonevPiutangPage
from ui.pages.chat_admin_page import ChatAdminPage
from ui.pages.admin_login_page import AdminLoginPage
from ui.pages.admin_panel_page import AdminPanelPage
from ui.pages.verifikasi_banpang_page import VerifikasiBanpangPage


from themes.colors import Colors
from themes.spacing import Spacing



class Workspace(ctk.CTkFrame):
    """
    Workspace aplikasi.

    Workspace bertindak sebagai "Container"
    yang menampilkan satu halaman aktif
    pada satu waktu.

    Contoh:

        Dashboard
             ↓
        Merge PDF
             ↓
        Split PDF

    Saat halaman berubah:

        Page Lama
             ↓
        Destroy
             ↓
        Buat Page Baru
             ↓
        Tampilkan

    Dengan cara ini penggunaan memori
    lebih efisien dibanding menyimpan
    semua halaman sekaligus.
    """

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(
        self,
        master,
        navigation,
        status_bar
    ):
        """
        Inisialisasi Workspace.

        Parameters
        ----------
        navigation : Navigation
            Controller navigasi aplikasi.

        status_bar : StatusBar
            Panel status di bagian bawah.
        """

        super().__init__(master,corner_radius= Spacing.CARD_RADIUS)

        # ==================================================
        # Shared Components
        # ==================================================
        #
        # Komponen global aplikasi yang
        # dapat digunakan oleh setiap page.
        #
        # ==================================================

        self.navigation = navigation
        self.status_bar = status_bar

        # ==================================================
        # Current Active Page
        # ==================================================
        #
        # Menyimpan halaman yang sedang
        # ditampilkan pada Workspace.
        #
        # Digunakan saat proses pergantian
        # halaman agar page lama bisa dihapus.
        #
        # ==================================================

        self.current_page = None

        # ==================================================
        # Layout Configuration
        # ==================================================

        self.configure(
            fg_color=Colors.WORKSPACE_BG,
            corner_radius=24,
            border_width=1,
            border_color=Colors.BORDER
            
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )

        self.grid_columnconfigure(
            0,
            weight=1
        )

        # ==================================================
        # Page Registry
        # ==================================================
        #
        # Registry seluruh halaman aplikasi.
        #
        # Navigation
        #      ↓
        # Workspace
        #      ↓
        # Registry
        #      ↓
        # Page Object
        #
        # Contoh:
        #
        # navigate("merge")
        #          ↓
        # self.pages["merge"]
        #          ↓
        # MergePage(...)
        #
        # ==================================================

        self.pages = {

            # ==========================================
            # Dashboard
            # ==========================================

            "dashboard": lambda parent:
                DashboardPage(
                    parent,
                    navigation=self.navigation
                ),

            # ==========================================
            # Merge PDF
            # ==========================================

            "merge": lambda parent:
                MergePage(
                    parent,
                    status_bar=self.status_bar
                ),

            # ==========================================
            # Split PDF
            # ==========================================

            "split": lambda parent:
                SplitPage(
                    parent,
                    status_bar=self.status_bar
                ),

            # ==========================================
            # TUL 309
            # ==========================================

            "tul309": lambda parent:
                TUL309Page(
                    parent,
                    status_bar=self.status_bar
                ),

            # ==========================================
            # MONEV PIUTANG
            # ==========================================

            "monev_piutang": lambda parent:
                MonevPiutangPage(
                    parent,
                    status_bar=self.status_bar
                ),

            # ==========================================
            # VERIFIKASI BANPANG
            # ==========================================

            "verifikasi_banpang": lambda parent:
                VerifikasiBanpangPage(
                    parent,
                    status_bar=self.status_bar
                ),

            # ==========================================
            # CHAT ADMIN
            # ==========================================

            "chat_admin": lambda parent:
                ChatAdminPage(
                    parent,
                    status_bar=self.status_bar
                ),

            "admin_login": lambda parent:
                AdminLoginPage(
                    parent,
                    navigation=self.navigation,
                    status_bar=self.status_bar
                ),

            "admin_panel": lambda parent:
                AdminPanelPage(
                    parent,
                    navigation=self.navigation,
                    status_bar=self.status_bar
                ),
            

        }

        # ==================================================
        # Default Startup Page
        # ==================================================
        #
        # Saat aplikasi pertama kali dibuka,
        # Dashboard akan ditampilkan.
        #
        # ==================================================

        self.show_page("dashboard")

    # ==================================================
    # Page Management
    # ==================================================

    def show_page(
        self,
        page_name
    ):
        """
        Menampilkan halaman berdasarkan nama.

        Alur:

            Navigation
                  ↓
            show_page()
                  ↓
            Hapus Page Lama
                  ↓
            Buat Page Baru
                  ↓
            Tampilkan

        Parameters
        ----------
        page_name : str
            Nama halaman yang akan dibuka.

        Contoh:
            "dashboard"
            "merge"
            "split"
        """

        # ==================================================
        # Remove Current Page
        # ==================================================
        #
        # Jika ada halaman yang sedang tampil,
        # hapus terlebih dahulu sebelum
        # membuat halaman baru.
        #
        # ==================================================

        if self.current_page is not None:

            self.current_page.destroy()

        # ==================================================
        # Create New Page
        # ==================================================
        #
        # Ambil factory function dari registry
        # lalu buat instance page baru.
        #
        # ==================================================

        page_factory = self.pages[
            page_name
        ]

        self.current_page = page_factory(
            self
        )

        # ==================================================
        # Render Page
        # ==================================================
        #
        # Menampilkan halaman ke area kerja.
        #
        # ==================================================

        self.current_page.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=15,
            pady=15
        )