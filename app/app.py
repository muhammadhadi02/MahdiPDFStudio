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
   dan StatusBar

Struktur Layout:

┌──────────┬────────────────────────────┐
│ Sidebar  │         Workspace          │
├──────────┴────────────────────────────┤
│              StatusBar                │
└───────────────────────────────────────┘

Author : Muhammad Hadi Putra
"""

import os
import sys
import threading
import subprocess
import customtkinter as ctk

from version import APP_NAME, APP_VERSION

from core.navigation import Navigation
from core.workspace import Workspace

from ui.sidebar import Sidebar
from ui.statusbar import StatusBar

from themes.window_style import WindowStyle

from core.services.update_service import UpdateService
from core.services.update_downloader import UpdateDownloader


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

    Workspace akan menampilkan halaman aplikasi.
    """

    # ==================================================
    # Application Configuration
    # ==================================================

    APP_WIDTH = 1200
    APP_HEIGHT = 650

    # ==================================================
    # Constructor
    # ==================================================

    def __init__(self):
        super().__init__()

        from themes.colors import Colors

        self.configure(
            fg_color=Colors.APP_BG
        )

        # ==================================================
        # Theme
        # ==================================================

        ctk.set_appearance_mode(
            "light"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        # ==================================================
        # Window
        # ==================================================

        self.title(
            f"{APP_NAME} v{APP_VERSION}"
        )

        self.geometry(
            f"{self.APP_WIDTH}x{self.APP_HEIGHT}"
        )

        self.minsize(
            1200,
            700
        )

        # ==================================================
        # Update State
        # ==================================================

        self.update_dialog = None
        self.update_progress_bar = None
        self.update_progress_label = None
        self.update_status_label = None

        # Menyimpan informasi update aktif.
        self.current_update_info = None

        # Menandakan aplikasi sedang melakukan
        # proses update.
        self.is_updating = False

        # ==================================================
        # Layout Configuration
        # ==================================================

        self.grid_rowconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            1,
            weight=0
        )

        self.grid_columnconfigure(
            0,
            weight=0
        )

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_columnconfigure(
            2,
            weight=0
        )

        # ==================================================
        # Core Components
        # ==================================================

        self.navigation = Navigation()

        # ==================================================
        # Sidebar
        # ==================================================

        self.sidebar = Sidebar(
            self,
            navigation=self.navigation
        )

        self.navigation.sidebar = (
            self.sidebar
        )

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

        self.status_bar = StatusBar(
            self
        )

        self.status_bar.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew"
        )

        # ==================================================
        # Workspace
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

        self.navigation.set_workspace(
            self.workspace
        )

        # ==================================================
        # Center Window
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

        # ==================================================
        # Check Update
        # ==================================================

        self.after(
            1000,
            self.check_for_updates
        )

    # ======================================================
    # UPDATE CHECKER
    # ======================================================

    def check_for_updates(self):
        """
        Mengecek update di background agar UI
        tidak freeze.
        """

        def worker():

            result = (
                UpdateService.check_for_update()
            )

            if result:

                self.after(
                    0,
                    lambda info=result:
                        self.show_update_notification(
                            info
                        )
                )

        thread = threading.Thread(
            target=worker,
            daemon=True
        )

        thread.start()

    # ======================================================
    # UPDATE NOTIFICATION
    # ======================================================

    def show_update_notification(
        self,
        update_info
    ):
        """
        Menampilkan dialog ketika versi baru
        tersedia.
        """

        # Jangan membuka dialog update kedua
        # jika dialog sebelumnya masih ada.

        if (
            self.update_dialog is not None
            and self.update_dialog.winfo_exists()
        ):
            return

        self.current_update_info = (
            update_info
        )

        dialog = ctk.CTkToplevel(
            self
        )

        dialog.title(
            "Update Tersedia"
        )

        dialog.geometry(
            "460x320"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            self
        )

        dialog.grab_set()

        # ==================================================
        # Center Dialog
        # ==================================================

        dialog.update_idletasks()

        x = (
            self.winfo_x()
            + (
                self.winfo_width()
                - dialog.winfo_width()
            ) // 2
        )

        y = (
            self.winfo_y()
            + (
                self.winfo_height()
                - dialog.winfo_height()
            ) // 2
        )

        dialog.geometry(
            f"+{x}+{y}"
        )

        # ==================================================
        # Container
        # ==================================================

        container = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=24
        )

        # ==================================================
        # Title
        # ==================================================

        title = ctk.CTkLabel(
            container,
            text="Update Tersedia",
            font=(
                "Segoe UI",
                20,
                "bold"
            ),
            anchor="w"
        )

        title.pack(
            fill="x"
        )

        # ==================================================
        # Description
        # ==================================================

        description = ctk.CTkLabel(
            container,
            text=(
                "Versi baru Mahdi PDF Studio "
                "tersedia."
            ),
            font=(
                "Segoe UI",
                13
            ),
            anchor="w",
            justify="left"
        )

        description.pack(
            fill="x",
            pady=(8, 18)
        )

        # ==================================================
        # Version Information
        # ==================================================

        version_frame = ctk.CTkFrame(
            container,
            corner_radius=12
        )

        version_frame.pack(
            fill="x"
        )

        current_label = ctk.CTkLabel(
            version_frame,
            text=(
                f"Versi saat ini    "
                f"{update_info['current_version']}"
            ),
            font=(
                "Segoe UI",
                12
            ),
            anchor="w"
        )

        current_label.pack(
            fill="x",
            padx=16,
            pady=(12, 4)
        )

        latest_label = ctk.CTkLabel(
            version_frame,
            text=(
                f"Versi terbaru     "
                f"{update_info['latest_version']}"
            ),
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            anchor="w"
        )

        latest_label.pack(
            fill="x",
            padx=16,
            pady=(4, 12)
        )

        # ==================================================
        # Release Notes
        # ==================================================

        release_notes = update_info.get(
            "release_notes",
            []
        )

        if release_notes:

            notes_text = "\n".join(
                f"• {note}"
                for note in release_notes
            )

            notes_label = ctk.CTkLabel(
                container,
                text=notes_text,
                font=(
                    "Segoe UI",
                    11
                ),
                anchor="w",
                justify="left"
            )

            notes_label.pack(
                fill="x",
                pady=(14, 0)
            )

        # ==================================================
        # Buttons
        # ==================================================

        button_frame = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            side="bottom",
            pady=(18, 0)
        )

        later_button = ctk.CTkButton(
            button_frame,
            text="Nanti",
            width=110,
            height=38,
            fg_color="transparent",
            border_width=1,
            command=dialog.destroy
        )

        later_button.pack(
            side="right",
            padx=(8, 0)
        )

        update_button = ctk.CTkButton(
            button_frame,
            text="Update",
            width=110,
            height=38,
            command=lambda:
                self.start_update(
                    update_info,
                    dialog
                )
        )

        update_button.pack(
            side="right"
        )

        # Simpan reference dialog

        self.update_dialog = dialog

        # Bersihkan reference ketika dialog ditutup

        def on_close():

            try:

                dialog.grab_release()

            except Exception:

                pass

            dialog.destroy()

            self.update_dialog = None

        dialog.protocol(
            "WM_DELETE_WINDOW",
            on_close
        )

    # ======================================================
    # UPDATE DOWNLOAD PROGRESS
    # ======================================================

    def show_download_progress(
        self,
        update_info
    ):
        """
        Menampilkan dialog progress ketika update
        sedang diunduh.
        """

        dialog = ctk.CTkToplevel(
            self
        )

        dialog.title(
            "Mengunduh Update"
        )

        dialog.geometry(
            "500x330"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            self
        )

        dialog.grab_set()

        # ==================================================
        # Center Dialog
        # ==================================================

        dialog.update_idletasks()

        x = (
            self.winfo_x()
            + (
                self.winfo_width()
                - dialog.winfo_width()
            ) // 2
        )

        y = (
            self.winfo_y()
            + (
                self.winfo_height()
                - dialog.winfo_height()
            ) // 2
        )

        dialog.geometry(
            f"+{x}+{y}"
        )

        # ==================================================
        # Main Container
        # ==================================================

        container = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        container.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=28
        )

        # ==================================================
        # Update Icon
        # ==================================================

        icon = ctk.CTkLabel(
            container,
            text="↓",
            font=(
                "Segoe UI",
                34,
                "bold"
            ),
            text_color="#2563EB"
        )

        icon.pack(
            pady=(0, 4)
        )

        # ==================================================
        # Title
        # ==================================================

        title = ctk.CTkLabel(
            container,
            text="Update sedang diunduh",
            font=(
                "Segoe UI",
                21,
                "bold"
            ),
            text_color="#111827"
        )

        title.pack()

        # ==================================================
        # Description
        # ==================================================

        description = ctk.CTkLabel(
            container,
            text=(
                "Mahdi PDF Studio sedang menyiapkan "
                "versi terbaru."
            ),
            font=(
                "Segoe UI",
                12
            ),
            text_color="#64748B"
        )

        description.pack(
            pady=(6, 18)
        )

        # ==================================================
        # Version
        # ==================================================

        version_frame = ctk.CTkFrame(
            container,
            corner_radius=12,
            fg_color="#F1F5F9"
        )

        version_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        version_label = ctk.CTkLabel(
            version_frame,
            text=(
                f"{update_info['current_version']}"
                f"   →   "
                f"{update_info['latest_version']}"
            ),
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            text_color="#334155"
        )

        version_label.pack(
            pady=10
        )

        # ==================================================
        # Percentage
        # ==================================================

        self.update_progress_label = (
            ctk.CTkLabel(
                container,
                text="0%",
                font=(
                    "Segoe UI",
                    12,
                    "bold"
                ),
                text_color="#2563EB"
            )
        )

        self.update_progress_label.pack(
            anchor="e",
            pady=(0, 5)
        )

        # ==================================================
        # Progress Bar
        # ==================================================

        self.update_progress_bar = (
            ctk.CTkProgressBar(
                container,
                height=12,
                corner_radius=6,
                progress_color="#2563EB",
                fg_color="#E2E8F0"
            )
        )

        self.update_progress_bar.pack(
            fill="x"
        )

        self.update_progress_bar.set(
            0
        )

        # ==================================================
        # Status
        # ==================================================

        self.update_status_label = (
            ctk.CTkLabel(
                container,
                text=(
                    "Menghubungkan ke server update..."
                ),
                font=(
                    "Segoe UI",
                    11
                ),
                text_color="#64748B",
                anchor="w"
            )
        )

        self.update_status_label.pack(
            fill="x",
            pady=(12, 0)
        )

        # ==================================================
        # Simpan Reference
        # ==================================================

        self.update_dialog = dialog

        return dialog

    # ======================================================
    # UPDATE DOWNLOAD PROGRESS
    # ======================================================

    def update_download_progress(
        self,
        percent
    ):
        """
        Memperbarui progress bar download.

        Method ini dijalankan pada main thread
        menggunakan self.after().
        """

        try:

            if (
                self.update_progress_bar
                is None
            ):
                return

            percent = max(
                0,
                min(
                    100,
                    int(percent)
                )
            )

            self.update_progress_bar.set(
                percent / 100
            )

            self.update_progress_label.configure(
                text=f"{percent}%"
            )

            if percent < 100:

                self.update_status_label.configure(
                    text="Mengunduh update...",
                    text_color="#64748B"
                )

            else:

                self.update_status_label.configure(
                    text=(
                        "Download selesai. "
                        "Menyiapkan update..."
                    ),
                    text_color="#16A34A"
                )

        except Exception as error:

            print(
                "Gagal memperbarui progress update:",
                error
            )

    # ======================================================
    # START UPDATE DOWNLOAD
    # ======================================================

    def start_update(
        self,
        update_info,
        dialog
    ):
        """
        Memulai proses download update
        di background thread.
        """

        download_url = (
            update_info.get(
                "download_url"
            )
        )

        if not download_url:

            print(
                "URL update tidak tersedia."
            )

            return

        # ==================================================
        # Tutup Dialog Update
        # ==================================================

        try:

            dialog.grab_release()

        except Exception:

            pass

        try:

            dialog.destroy()

        except Exception:

            pass

        # ==================================================
        # Status
        # ==================================================

        self.is_updating = True

        # ==================================================
        # Tampilkan Progress Dialog
        # ==================================================

        self.show_download_progress(
            update_info
        )

        print(
            "Memulai download update..."
        )

        print(
            "Versi terbaru :",
            update_info[
                "latest_version"
            ]
        )

        # ==================================================
        # Progress Callback
        # ==================================================

        def progress_callback(
            percent
        ):

            try:

                self.after(
                    0,
                    lambda p=percent:
                        self.update_download_progress(
                            p
                        )
                )

            except Exception:

                pass

        # ==================================================
        # Background Worker
        # ==================================================

        def worker():

            try:

                update_path = (
                    UpdateDownloader.download_update(
                        download_url,
                        progress_callback
                    )
                )

                self.after(
                    0,
                    lambda path=update_path:
                        self.update_download_finished(
                            path
                        )
                )

            except Exception as error:

                self.after(
                    0,
                    lambda err=error:
                        self.update_download_failed(
                            err
                        )
                )

        thread = threading.Thread(
            target=worker,
            daemon=True
        )

        thread.start()

    # ======================================================
    # FIND UPDATER EXE
    # ======================================================

    def get_updater_path(self):
        """
        Mencari lokasi MahdiPDFStudioUpdater.exe.

        Ketika aplikasi sudah menjadi EXE:

            MahdiPDFStudio.exe
            MahdiPDFStudioUpdater.exe

        berada dalam folder yang sama.

        Ketika dijalankan dari source code,
        updater dicari di folder dist.
        """

        # ==================================================
        # Mode EXE
        # ==================================================

        if getattr(
            sys,
            "frozen",
            False
        ):

            base_dir = os.path.dirname(
                sys.executable
            )

            updater_path = os.path.join(
                base_dir,
                "MahdiPDFStudioUpdater.exe"
            )

            return updater_path

        # ==================================================
        # Mode Source Code
        # ==================================================

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(
                    __file__
                )
            )
        )

        updater_path = os.path.join(
            project_root,
            "dist",
            "MahdiPDFStudioUpdater.exe"
        )

        return updater_path

    # ======================================================
    # GET TARGET EXE
    # ======================================================

    def get_target_exe_path(self):
        """
        Menentukan executable yang akan diganti.

        Dalam mode EXE:

            target = MahdiPDFStudio.exe

        Dalam mode source:

            tidak boleh menggunakan Python executable.
        """

        if getattr(
            sys,
            "frozen",
            False
        ):

            return os.path.abspath(
                sys.executable
            )

        return None

    # ======================================================
    # START EXTERNAL UPDATER
    # ======================================================

    def launch_updater(
        self,
        update_path
    ):
        """
        Menjalankan MahdiPDFStudioUpdater.exe.

        Updater menerima dua argument:

            1. File update
            2. Target EXE

        Setelah updater berjalan,
        aplikasi utama akan ditutup.
        """

        updater_path = (
            self.get_updater_path()
        )

        target_exe = (
            self.get_target_exe_path()
        )

        # ==================================================
        # Validasi Mode
        # ==================================================

        if target_exe is None:

            self.show_update_error(
                "Updater belum dapat melakukan "
                "instalasi ketika aplikasi dijalankan "
                "dari source code.\n\n"
                "Build dan jalankan "
                "MahdiPDFStudio.exe untuk melakukan "
                "test auto-update sebenarnya."
            )

            return False

        # ==================================================
        # Validasi Updater
        # ==================================================

        if not os.path.exists(
            updater_path
        ):

            self.show_update_error(
                "MahdiPDFStudioUpdater.exe "
                "tidak ditemukan.\n\n"
                f"Lokasi yang dicari:\n"
                f"{updater_path}"
            )

            return False

        # ==================================================
        # Validasi Update
        # ==================================================

        if not os.path.exists(
            update_path
        ):

            self.show_update_error(
                "File update tidak ditemukan.\n\n"
                f"{update_path}"
            )

            return False

        # ==================================================
        # Jalankan Updater
        # ==================================================

        try:

            print(
                "Menjalankan updater:"
            )

            print(
                updater_path
            )

            print(
                "Update file:"
            )

            print(
                update_path
            )

            print(
                "Target EXE:"
            )

            print(
                target_exe
            )

            subprocess.Popen(
                [
                    updater_path,
                    update_path,
                    target_exe
                ],
                cwd=os.path.dirname(
                    updater_path
                ),
                close_fds=True
            )

            return True

        except Exception as error:

            self.show_update_error(
                "Gagal menjalankan updater.\n\n"
                f"Error:\n{error}"
            )

            return False

    # ======================================================
    # UPDATE DOWNLOAD FINISHED
    # ======================================================

    def update_download_finished(
        self,
        update_path
    ):
        """
        Dipanggil ketika file update selesai
        diunduh.
        """

        print(
            "DOWNLOAD UPDATE BERHASIL"
        )

        print(
            "File update:",
            update_path
        )

        try:

            if (
                self.update_progress_bar
                is not None
            ):

                self.update_progress_bar.set(
                    1
                )

            if (
                self.update_progress_label
                is not None
            ):

                self.update_progress_label.configure(
                    text="100%"
                )

            if (
                self.update_status_label
                is not None
            ):

                self.update_status_label.configure(
                    text=(
                        "Download selesai. "
                        "Menyiapkan pemasangan..."
                    ),
                    text_color="#16A34A"
                )

            # ==================================================
            # Tunggu sebentar agar user melihat 100%
            # ==================================================

            self.after(
                700,
                lambda path=update_path:
                    self.install_downloaded_update(
                        path
                    )
            )

        except Exception as error:

            print(
                "Gagal memperbarui status selesai:",
                error
            )

    # ======================================================
    # INSTALL DOWNLOADED UPDATE
    # ======================================================

    def install_downloaded_update(
        self,
        update_path
    ):
        """
        Menjalankan updater setelah download selesai.
        """

        try:

            success = (
                self.launch_updater(
                    update_path
                )
            )

            if not success:

                self.is_updating = False

                return

            # ==================================================
            # Tutup Progress Dialog
            # ==================================================

            try:

                if (
                    self.update_dialog
                    is not None
                    and self.update_dialog.winfo_exists()
                ):

                    self.update_dialog.grab_release()

                    self.update_dialog.destroy()

            except Exception:

                pass

            self.update_dialog = None

            # ==================================================
            # Tutup Aplikasi Utama
            # ==================================================

            print(
                "Updater berhasil dijalankan."
            )

            print(
                "Menutup Mahdi PDF Studio..."
            )

            self.after(
                200,
                self.destroy
            )

        except Exception as error:

            self.is_updating = False

            self.show_update_error(
                "Gagal memulai proses update.\n\n"
                f"Error:\n{error}"
            )

    # ======================================================
    # UPDATE DOWNLOAD FAILED
    # ======================================================

    def update_download_failed(
        self,
        error
    ):
        """
        Dipanggil ketika download update gagal.
        """

        print(
            "DOWNLOAD UPDATE GAGAL"
        )

        print(
            "Error:",
            error
        )

        self.is_updating = False

        try:

            if (
                self.update_status_label
                is not None
            ):

                self.update_status_label.configure(
                    text=(
                        "Download update gagal."
                    ),
                    text_color="#DC2626"
                )

            if (
                self.update_progress_label
                is not None
            ):

                self.update_progress_label.configure(
                    text="Gagal",
                    text_color="#DC2626"
                )

            # Jangan langsung menutup dialog.
            # User dapat melihat error status.

        except Exception as ui_error:

            print(
                "Gagal memperbarui UI error:",
                ui_error
            )

    # ======================================================
    # UPDATE ERROR DIALOG
    # ======================================================

    def show_update_error(
        self,
        message
    ):
        """
        Menampilkan dialog error update.
        """

        try:

            error_dialog = ctk.CTkToplevel(
                self
            )

            error_dialog.title(
                "Update Gagal"
            )

            error_dialog.geometry(
                "460x260"
            )

            error_dialog.resizable(
                False,
                False
            )

            error_dialog.transient(
                self
            )

            error_dialog.grab_set()

            # ==================================================
            # Center
            # ==================================================

            error_dialog.update_idletasks()

            x = (
                self.winfo_x()
                + (
                    self.winfo_width()
                    - error_dialog.winfo_width()
                ) // 2
            )

            y = (
                self.winfo_y()
                + (
                    self.winfo_height()
                    - error_dialog.winfo_height()
                ) // 2
            )

            error_dialog.geometry(
                f"+{x}+{y}"
            )

            # ==================================================
            # Container
            # ==================================================

            container = ctk.CTkFrame(
                error_dialog,
                fg_color="transparent"
            )

            container.pack(
                fill="both",
                expand=True,
                padx=28,
                pady=24
            )

            # ==================================================
            # Icon
            # ==================================================

            icon = ctk.CTkLabel(
                container,
                text="!",
                font=(
                    "Segoe UI",
                    30,
                    "bold"
                ),
                text_color="#DC2626"
            )

            icon.pack(
                pady=(0, 4)
            )

            # ==================================================
            # Title
            # ==================================================

            title = ctk.CTkLabel(
                container,
                text="Update Gagal",
                font=(
                    "Segoe UI",
                    19,
                    "bold"
                ),
                text_color="#111827"
            )

            title.pack()

            # ==================================================
            # Message
            # ==================================================

            message_label = ctk.CTkLabel(
                container,
                text=message,
                font=(
                    "Segoe UI",
                    11
                ),
                text_color="#64748B",
                justify="center",
                wraplength=390
            )

            message_label.pack(
                pady=(12, 18)
            )

            # ==================================================
            # Button
            # ==================================================

            close_button = ctk.CTkButton(
                container,
                text="Tutup",
                width=110,
                height=36,
                command=error_dialog.destroy
            )

            close_button.pack()

        except Exception as error:

            print(
                "Gagal menampilkan dialog update:",
                error
            )

    # ======================================================
    # WINDOW UTILITIES
    # ======================================================

    def center_window(self):
        """
        Menempatkan window di tengah layar.
        """

        screen_width = (
            self.winfo_screenwidth()
        )

        screen_height = (
            self.winfo_screenheight()
        )

        x = (
            screen_width
            - self.APP_WIDTH
        ) // 2

        y = (
            screen_height
            - self.APP_HEIGHT
        ) // 2

        self.geometry(
            f"{self.APP_WIDTH}"
            f"x{self.APP_HEIGHT}"
            f"+{x}+{y}"
        )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    app = MahdiPDFStudio()

    app.mainloop()