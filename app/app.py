"""
==========================================================
Mahdi PDF Studio
Main Application
==========================================================

Entry Point aplikasi.

Tanggung Jawab:
1. Membuat window utama aplikasi
2. Mengatur layout utama
3. Menghubungkan komponen global
4. Menyediakan Navigation, Workspace,
   InfoPanel, dan StatusBar

Struktur Layout:

┌──────────┬────────────────────────────┐
│ Sidebar  │         Workspace          │
├──────────┴────────────────────────────┤
│              StatusBar                │
└───────────────────────────────────────┘

Author : Muhammad Hadi Putra
"""

import customtkinter as ctk
from version import APP_NAME, APP_VERSION

from core.navigation import Navigation
from core.workspace import Workspace

from ui.sidebar import Sidebar
from ui.statusbar import StatusBar

from themes.window_style import WindowStyle


class MahdiPDFStudio(ctk.CTk):
    """
    Window utama aplikasi.

    Komponen:

        Sidebar
            │
            ▼

        Navigation
            │
            ▼

        Workspace
            │
            ▼

          Pages

    Workspace akan menampilkan:
    - Dashboard
    - Merge PDF
    - Split PDF
    - Compress PDF
    - Rotate PDF

    Sedangkan InfoPanel dan StatusBar
    bersifat global sehingga dapat
    digunakan oleh seluruh halaman.
    """

    # ==================================================
    # Application Configuration
    # ==================================================
    #
    # Menyimpan ukuran default aplikasi.
    #
    # Keuntungan:
    # - Mudah diubah di satu tempat
    # - Menghindari magic number
    #
    # ==================================================

    APP_WIDTH = 1200
    APP_HEIGHT = 650

    def __init__(self):
        super().__init__()

        from themes.colors import Colors

        self.configure(
            fg_color=Colors.APP_BG
        )

        # ==================================================
        # Theme
        # ==================================================
        #
        # Mengatur tema global aplikasi.
        #
        # appearance_mode:
        #     light / dark / system
        #
        # color_theme:
        #     blue / green / dark-blue
        #
        # ==================================================

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # ==================================================
        # Window
        # ==================================================
        #
        # Mengatur informasi dasar window.
        #
        # geometry:
        #     ukuran awal saat aplikasi dibuka
        #
        # minsize:
        #     ukuran minimum yang diizinkan
        #
        # ==================================================

        self.title(f"{APP_NAME} v{APP_VERSION}")

        self.geometry(
            f"{self.APP_WIDTH}x{self.APP_HEIGHT}"
        )

        self.minsize(1200, 700)

        # ==================================================
        # Layout Configuration
        # ==================================================
        #
        # Grid utama aplikasi:
        #
        # Column 0 : Sidebar
        # Column 1 : Workspace
        # Column 2 : InfoPanel
        #
        # Row 0    : Konten utama
        # Row 1    : StatusBar
        #
        # Workspace diberi weight=1 agar
        # mengambil seluruh ruang yang tersedia.
        #
        # ==================================================

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # ==================================================
        # Core Components
        # ==================================================
        #
        # Navigation bertugas mengatur
        # perpindahan halaman.
        #
        # Sidebar
        #     ↓
        # Navigation
        #     ↓
        # Workspace
        #
        # ==================================================

        self.navigation = Navigation()

        # ==================================================
        # Sidebar
        # ==================================================
        #
        # Menu navigasi aplikasi.
        #
        # Berisi:
        # - Dashboard
        # - Merge PDF
        # - Split PDF
        # - Compress PDF
        # - Rotate PDF
        #
        # ==================================================

        self.sidebar = Sidebar(self,navigation=self.navigation)

        self.navigation.sidebar = self.sidebar

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(20, 10),
            pady=20
        )


        # ==================================================
        # Status Bar
        # ==================================================
        #
        # Menampilkan status aplikasi.
        #
        # Contoh:
        # - Ready
        # - 3 file berhasil ditambahkan
        # - Menggabungkan PDF...
        # - PDF berhasil digabung
        #
        # ==================================================

        self.status_bar = StatusBar(self)

        self.status_bar.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew"
        )

        # ==================================================
        # Workspace
        # ==================================================
        #
        # Area kerja utama aplikasi.
        #
        # Workspace bertugas menampilkan
        # halaman aktif berdasarkan
        # perintah dari Navigation.
        #
        # ==================================================

        self.workspace = Workspace(
            self,
            navigation=self.navigation,
            status_bar=self.status_bar
        )

        self.workspace.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=20,
            pady=20
        )

        # ==================================================
        # Hubungkan Navigation ke Workspace
        # ==================================================
        #
        # Navigation perlu mengetahui
        # Workspace mana yang harus
        # dikontrol.
        #
        # ==================================================

        self.navigation.set_workspace(
            self.workspace
        )

        # ==================================================
        # Center Window
        # ==================================================
        #
        # Menunggu window selesai dirender,
        # kemudian memposisikannya ke tengah.
        #
        # Menggunakan after() agar ukuran
        # window sudah stabil saat dihitung.
        #
        # ==================================================

        self.after(
            100,
            self.center_window
        )

        self.after(
            200,
            lambda: WindowStyle.apply_fluent_style(
                self
            )
        )

    # ======================================================
    # Window Utilities
    # ======================================================

    def center_window(self):
        """
        Menempatkan window di tengah layar.

        Rumus:

            x = (screen_width - window_width) / 2
            y = (screen_height - window_height) / 2

        Contoh:

            Screen : 1920 x 1080
            Window : 1400 x 850

            x = 260
            y = 115

        Hasil:
            Window muncul di tengah layar.
        """

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Hitung posisi horizontal
        x = (
            screen_width - self.APP_WIDTH
        ) // 2

        # Hitung posisi vertikal
        y = (
            screen_height - self.APP_HEIGHT
        ) // 2

        self.geometry(
            f"{self.APP_WIDTH}x{self.APP_HEIGHT}+{x}+{y}"
        )


if __name__ == "__main__":

    app = MahdiPDFStudio()

    app.mainloop()