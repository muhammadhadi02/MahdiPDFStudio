"""
==========================================================
Mahdi PDF Studio
Merge Page
==========================================================

Halaman untuk menggabungkan beberapa file PDF menjadi satu
dokumen PDF.

==========================================================
"""

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from pypdf import PdfReader

from data.models.pdf_file import PdfFile
from widgets.file_list_widget import FileListWidget
from widgets.primary_button import PrimaryButton
from widgets.merge_summary_card import MergeSummaryCard

from themes.colors import Colors
from themes.fonts import Fonts
from themes.icons import Icons

from core.services.pdf_merge_service import PdfMergeService


class MergePage(ctk.CTkFrame):

    # ==========================================================
    # LAYOUT CONSTANT
    # ==========================================================

    FILE_LIST_HEIGHT = 395

    FILE_LIST_PADX = 30

    # Warna area kosong / area daftar file
    FILE_AREA_BG = Colors.MERGE_BG

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self, master, status_bar):

        super().__init__(
            master,
            fg_color=Colors.WORKSPACE_BG,
        )

        self.status_bar = status_bar

        # ======================================================
        # BUILD UI
        # ======================================================

        self.configure_layout()

        self.create_header()

        self.create_file_section()

        self.update_info_panel()

    # ==========================================================
    # LAYOUT
    # ==========================================================

    def configure_layout(self):

        # ------------------------------------------------------
        # HEADER
        # ------------------------------------------------------

        self.grid_rowconfigure(
            0,
            weight=0,
        )

        # ------------------------------------------------------
        # FILE SECTION
        # ------------------------------------------------------

        self.grid_rowconfigure(
            1,
            weight=0,
        )

        # ------------------------------------------------------
        # SPACE / BOTTOM
        # ------------------------------------------------------

        self.grid_rowconfigure(
            2,
            weight=1,
        )

        self.grid_columnconfigure(
            0,
            weight=1,
        )

    # ==========================================================
    # HEADER
    # ==========================================================

    def create_header(self):

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 0),
        )

        # ------------------------------------------------------
        # HEADER GRID
        # ------------------------------------------------------

        header_frame.grid_columnconfigure(
            0,
            weight=0,
        )

        header_frame.grid_columnconfigure(
            1,
            weight=1,
        )

        header_frame.grid_columnconfigure(
            2,
            weight=0,
        )

        # ======================================================
        # SUMMARY CARD
        # ======================================================

        self.summary_card = MergeSummaryCard(
            header_frame
        )

        self.summary_card.grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="ne",
            padx=(20, 0),
        )

        # ======================================================
        # ICON BOX
        # ======================================================

        icon_box = ctk.CTkFrame(
            header_frame,
            width=80,
            height=80,
            corner_radius=24,
            fg_color=Colors.MERGE_BG,
        )

        icon_box.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(0, 20),
        )

        icon_box.grid_propagate(False)

        # ======================================================
        # MERGE ICON
        # ======================================================

        icon_label = ctk.CTkLabel(
            icon_box,
            text="",
            image=Icons.MERGE_LOGO,
        )

        icon_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        # ======================================================
        # TITLE
        # ======================================================

        title = ctk.CTkLabel(
            header_frame,
            text="Merge PDF",
            font=Fonts.PAGE_TITLE,
            text_color=Colors.TEXT_PRIMARY,
        )

        title.grid(
            row=0,
            column=1,
            sticky="sw",
            pady=(0, 2),
        )

        # ======================================================
        # SUBTITLE
        # ======================================================

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Gabungkan beberapa file PDF menjadi satu dokumen.",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
        )

        subtitle.grid(
            row=1,
            column=1,
            sticky="nw",
        )

    # ==========================================================
    # FILE SECTION
    # ==========================================================

    def create_file_section(self):

        """
        ==========================================================
        FILE SECTION

        Struktur:

        ┌───────────────────────────────────────────────┐
        │                                               │
        │        AREA FILE / EMPTY STATE                │
        │                                               │
        │                                               │
        ├───────────────────────────────────────────────┤
        │                                  [Merge PDF]  │
        └───────────────────────────────────────────────┘

        Outer  : putih
        Inner  : #F5F8FC
        ==========================================================
        """

        # ======================================================
        # OUTER CONTAINER
        # ======================================================

        self.file_section = ctk.CTkFrame(
            self,
            fg_color=Colors.WORKSPACE_BG,
    
        )

        self.file_section.grid(
            row=1,
            column=0,
            padx=self.FILE_LIST_PADX,
            pady=(10, 10),
            sticky="ew",
        )

        # ------------------------------------------------------
        # GRID
        # ------------------------------------------------------

        self.file_section.grid_rowconfigure(
            0,
            weight=0,
        )

        self.file_section.grid_rowconfigure(
            1,
            weight=0,
        )

        self.file_section.grid_columnconfigure(
            0,
            weight=1,
        )

        # ======================================================
        # FILE LIST AREA
        # ======================================================

        self.file_list = FileListWidget(
            self,
            on_change=self.update_info_panel,
            on_add_file=self.on_add_pdf,
        )

        # ------------------------------------------------------
        # UKURAN
        # ------------------------------------------------------

        self.file_list.configure(
            height=self.FILE_LIST_HEIGHT,
            fg_color=self.FILE_AREA_BG,
            corner_radius=14,
            border_width = 1
        )

        self.file_list.grid_propagate(
            False
        )

        # ======================================================
        # MASUKKAN FILE LIST KE OUTER CONTAINER
        # ======================================================

        self.file_list.grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
            sticky="ew",
            in_=self.file_section,
        )

        # ======================================================
        # BOTTOM BAR
        # ======================================================

        bottom = ctk.CTkFrame(
            self.file_section,
            fg_color="transparent",
        )

        bottom.grid(
            row=1,
            column=0,
            padx=0,
            pady=(0, 5),
            sticky="ew",
        )

        bottom.grid_rowconfigure(
            0,
            weight=1,
        )

        bottom.grid_columnconfigure(
            0,
            weight=1,
        )

        # ======================================================
        # MERGE BUTTON
        # ======================================================

        self.merge_button = PrimaryButton(
            bottom,
            text="Merge PDF",
            command=self.on_merge_pdf,
        )

        self.merge_button.grid(
            row=0,
            column=0,
            padx=(0, 0),
            pady=0,
            sticky="e",
        )

        # ======================================================
        # INITIAL STATE
        # ======================================================

        self._set_merge_button_state(
            False
        )

    # ==========================================================
    # ADD PDF
    # ==========================================================

    def on_add_pdf(self, filepaths=None):

        # ------------------------------------------------------
        # FILE DIALOG
        # ------------------------------------------------------

        if filepaths is None:

            filepaths = filedialog.askopenfilenames(
                title="Pilih File PDF",
                filetypes=[
                    ("PDF Files", "*.pdf"),
                ],
            )

        # User cancel
        if not filepaths:
            return

        # ------------------------------------------------------
        # PROCESS FILES
        # ------------------------------------------------------

        self.add_pdf_files(
            filepaths
        )

    # ==========================================================
    # VALIDATE + ADD PDF
    # ==========================================================

    def add_pdf_files(self, filepaths):

        # Jika hanya satu file
        if isinstance(
            filepaths,
            (str, Path),
        ):
            filepaths = [filepaths]

        # ======================================================
        # CURRENT PATHS
        # ======================================================

        current_paths = {
            str(
                pdf.path.resolve()
            ).lower()

            for pdf in self.file_list.get_files()
        }

        # ======================================================
        # TEMPORARY DATA
        # ======================================================

        new_pdfs = []

        added = 0
        skipped = 0
        failed = 0

        errors = []

        # ======================================================
        # LOOP
        # ======================================================

        for filepath in filepaths:

            try:

                path = Path(filepath)

                # ------------------------------------------------
                # CHECK EXIST
                # ------------------------------------------------

                if (
                    not path.exists()
                    or not path.is_file()
                ):

                    skipped += 1

                    errors.append(
                        f"File tidak ditemukan: {path}"
                    )

                    continue

                # ------------------------------------------------
                # CHECK EXTENSION
                # ------------------------------------------------

                if path.suffix.lower() != ".pdf":

                    skipped += 1

                    errors.append(
                        f"Bukan file PDF: {path.name}"
                    )

                    continue

                # ------------------------------------------------
                # CHECK DUPLICATE
                # ------------------------------------------------

                resolved = str(
                    path.resolve()
                ).lower()

                if resolved in current_paths:

                    skipped += 1

                    continue

                # ------------------------------------------------
                # READ PDF
                # ------------------------------------------------

                reader = PdfReader(
                    str(path)
                )

                # ------------------------------------------------
                # CHECK ENCRYPTED
                # ------------------------------------------------

                if reader.is_encrypted:

                    failed += 1

                    errors.append(
                        f"PDF terenkripsi: {path.name}"
                    )

                    continue

                # ------------------------------------------------
                # PAGE COUNT
                # ------------------------------------------------

                total_pages = len(
                    reader.pages
                )

                if total_pages <= 0:

                    failed += 1

                    errors.append(
                        f"PDF tidak memiliki halaman: {path.name}"
                    )

                    continue

                # ------------------------------------------------
                # CREATE MODEL
                # ------------------------------------------------

                pdf = PdfFile(
                    path=path,
                    filename=path.name,
                    pages=total_pages,
                    filesize=path.stat().st_size,
                )

                # ------------------------------------------------
                # ADD TO BATCH
                # ------------------------------------------------

                new_pdfs.append(
                    pdf
                )

                current_paths.add(
                    resolved
                )

                added += 1

            except Exception as error:

                failed += 1

                errors.append(
                    f"{Path(filepath).name}: {error}"
                )

        # ======================================================
        # ADD BATCH
        # ======================================================

        if new_pdfs:

            self.file_list.add_files(
                new_pdfs
            )

        # ======================================================
        # STATUS BAR
        # ======================================================

        if added:

            status = (
                f"{added} file PDF berhasil ditambahkan"
            )

            if skipped or failed:

                status += (
                    f" • {skipped + failed} dilewati"
                )

            self.status_bar.set_status(
                status
            )

        elif skipped or failed:

            self.status_bar.set_status(
                "Tidak ada file PDF baru yang ditambahkan"
            )

        # ======================================================
        # ERROR MESSAGE
        # ======================================================

        if errors and (failed or skipped):

            important_errors = [
                error
                for error in errors
                if not error.startswith(
                    "Bukan file PDF:"
                )
            ]

            if important_errors:

                messagebox.showwarning(
                    "Sebagian File Tidak Ditambahkan",
                    "\n".join(
                        important_errors[:8]
                    ),
                )

    # ==========================================================
    # UPDATE SUMMARY + BUTTON
    # ==========================================================

    def update_info_panel(self):

        files = self.file_list.get_files()

        total_files = len(
            files
        )

        total_pages = sum(
            pdf.pages
            for pdf in files
        )

        total_size = sum(
            pdf.filesize
            for pdf in files
        )

        # ======================================================
        # SUMMARY
        # ======================================================

        self.summary_card.update_summary(
            total_files,
            total_pages,
            total_size / (1024 * 1024),
        )

        # ======================================================
        # BUTTON
        # ======================================================

        self._set_merge_button_state(
            total_files > 0
        )

    # ==========================================================
    # MERGE BUTTON STATE
    # ==========================================================

    def _set_merge_button_state(
        self,
        enabled,
    ):

        if enabled:

            self.merge_button.configure(
                state="normal",
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_HOVER,
            )

        else:

            self.merge_button.configure(
                state="disabled",
                fg_color=Colors.TEXT_MUTED,
                hover_color=Colors.TEXT_MUTED,
            )

    # ==========================================================
    # MERGE PDF
    # ==========================================================

    def on_merge_pdf(self):

        # ======================================================
        # GET FILES
        # ======================================================

        files = self.file_list.get_files()

        # ======================================================
        # CHECK EMPTY
        # ======================================================

        if not files:

            messagebox.showwarning(
                "Peringatan",
                "Belum ada file PDF yang dipilih.",
            )

            return

        # ======================================================
        # SAVE DIALOG
        # ======================================================

        output_path = filedialog.asksaveasfilename(
            title="Simpan Hasil Merge",
            defaultextension=".pdf",
            filetypes=[
                ("PDF Files", "*.pdf"),
            ],
        )

        if not output_path:
            return

        # ======================================================
        # RESOLVE OUTPUT
        # ======================================================

        output = Path(
            output_path
        ).resolve()

        # ======================================================
        # INPUT PATHS
        # ======================================================

        input_paths = {
            Path(
                pdf.path
            ).resolve()

            for pdf in files
        }

        # ======================================================
        # PREVENT OVERWRITE
        # ======================================================

        if output in input_paths:

            messagebox.showwarning(
                "Lokasi Tidak Valid",
                "File output tidak boleh sama "
                "dengan salah satu file input.",
            )

            return

        # ======================================================
        # STATUS
        # ======================================================

        self.status_bar.set_status(
            "Menggabungkan PDF..."
        )

        self.update_idletasks()

        # ======================================================
        # CALL SERVICE
        # ======================================================

        success, error_message = (
            PdfMergeService.merge(
                files=files,
                output_path=str(output),
            )
        )

        # ======================================================
        # RESULT
        # ======================================================

        if success:

            self.status_bar.set_status(
                "PDF berhasil digabung"
            )

            messagebox.showinfo(
                "Sukses",
                f"PDF berhasil digabung.\n\n"
                f"Lokasi:\n{output}",
            )

        else:

            self.status_bar.set_status(
                "Gagal menggabungkan PDF"
            )

            messagebox.showerror(
                "Gagal",
                f"Terjadi kesalahan:\n\n"
                f"{error_message}",
            )