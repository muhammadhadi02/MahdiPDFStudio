"""
==========================================================
Mahdi PDF Studio
Split PDF Page
==========================================================

Halaman untuk melakukan proses pemisahan PDF.

Fitur:
✓ Split Per Halaman
✓ Split Halaman Pilihan
✓ PDF Preview Card
✓ PDF Thumbnail Viewer
✓ Empty State Preview
✓ Status Bar Integration

==========================================================
"""

import fitz

from PIL import Image
from customtkinter import CTkImage

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from pypdf import PdfReader

from widgets.primary_button import PrimaryButton
from widgets.pdf_preview_card import PdfPreviewCard
from widgets.pdf_thumbnail_viewer import PdfThumbnailViewer

from core.services.page_parser import PageParser
from core.services.pdf_split_service import PdfSplitService

from themes.colors import Colors
from themes.fonts import Fonts
from themes.icons import Icons


class SplitPage(ctk.CTkFrame):

    # ==========================================================
    # LAYOUT CONSTANT
    # ==========================================================

    FILE_LIST_HEIGHT = 395

    # ==========================================================
    # CONSTRUCTOR
    # ==========================================================

    def __init__(
        self,
        master,
        status_bar
    ):

        super().__init__(
            master,
            fg_color=Colors.WORKSPACE_BG,
        )

        self.status_bar = status_bar

        # ======================================================
        # STATE
        # ======================================================

        self.pdf_path = None
        self.total_pages = 0

        self.split_mode = ctk.StringVar(
            value="page"
        )

        # ======================================================
        # BUILD UI
        # ======================================================

        self.configure_layout()

        self.create_header()

        self.create_content()

    # ==========================================================
    # LAYOUT
    # ==========================================================

    def configure_layout(self):

        self.grid_rowconfigure(
            0,
            weight=0
        )

        self.grid_rowconfigure(
            1,
            weight=1
        )

        self.grid_columnconfigure(
            0,
            weight=1
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
            pady=(0, 10),
        )

        # ------------------------------------------------------
        # HEADER GRID
        # ------------------------------------------------------

        header_frame.grid_columnconfigure(
            0,
            weight=0
        )

        header_frame.grid_columnconfigure(
            1,
            weight=1
        )

        header_frame.grid_columnconfigure(
            2,
            weight=0
        )

        # ======================================================
        # SUMMARY / PDF INFO CARD
        # ======================================================

        self.preview_card = PdfPreviewCard(
            header_frame
        )

        self.preview_card.grid(
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
        # SPLIT ICON
        # ======================================================

        icon_label = ctk.CTkLabel(
            icon_box,
            text="",
            image=Icons.SPLIT_LOGO,
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
            text="Split PDF",
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
            text="Pisahkan halaman PDF menjadi beberapa file.",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
        )

        subtitle.grid(
            row=1,
            column=1,
            sticky="nw",
        )

    # ==========================================================
    # MAIN CONTENT
    # ==========================================================

    def create_content(self):

        # ======================================================
        # OUTER CONTAINER
        # ======================================================

        container = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color=Colors.BORDER,
        )

        container.grid(
            row=1,
            column=0,
            padx=30,
            pady=(0, 10),
            sticky="nsew",
        )

        container.grid_rowconfigure(
            0,
            weight=1
        )

        # ======================================================
        # FIXED LEFT COLUMN
        # ======================================================

        container.grid_columnconfigure(
            0,
            minsize=350,
            weight=0
        )

        container.grid_columnconfigure(
            1,
            weight=1
        )

        # ======================================================
        # LEFT CONTROL PANEL
        # ======================================================

        left_panel = ctk.CTkFrame(
            container,
            width=350,
            fg_color="#FFFFFF",
        )

        left_panel.grid(
            row=0,
            column=0,
            sticky="ns",
            padx=(25, 10),
            pady=25,
        )

        left_panel.grid_propagate(False)

        # ======================================================
        # PILIH PDF BUTTON
        # ======================================================

        self.select_button = PrimaryButton(
            left_panel,
            text="Pilih PDF",
            command=self.on_select_pdf
        )

        self.select_button.pack(
            padx=15,
            pady=(10, 20),
            anchor = "w",
        )

        # ======================================================
        # DIVIDER
        # ======================================================

        divider = ctk.CTkFrame(
            left_panel,
            height=1,
            width=220,
            fg_color=Colors.BORDER,
        )

        divider.pack(
            anchor="w",
            padx=15,
            pady=(0, 20)
        )

        # ======================================================
        # METODE SPLIT
        # ======================================================

        mode_title = ctk.CTkLabel(
            left_panel,
            text="Metode Split",
            font=Fonts.SECTION_HEADING,
            text_color=Colors.TEXT_PRIMARY,
        )

        mode_title.pack(
            anchor="w",
            padx=15,
            pady=(0, 12)
        )

        # ======================================================
        # SPLIT PER HALAMAN
        # ======================================================

        self.page_radio = ctk.CTkRadioButton(
            left_panel,
            text="Per Halaman",
            variable=self.split_mode,
            value="page",
            command=self.update_mode_ui,
        )

        self.page_radio.pack(
            anchor="w",
            padx=20,
            pady=5
        )

        # ======================================================
        # HALAMAN PILIHAN
        # ======================================================

        self.range_radio = ctk.CTkRadioButton(
            left_panel,
            text="Halaman Pilihan",
            variable=self.split_mode,
            value="range",
            command=self.update_mode_ui,
        )

        self.range_radio.pack(
            anchor="w",
            padx=20,
            pady=5
        )

        # ======================================================
        # RANGE ENTRY
        # ======================================================

        self.range_entry = ctk.CTkEntry(
            left_panel,
            width=100,
            height=38,
            placeholder_text="1-5,8,10-12",
        )

        self.range_entry.bind(
            "<KeyRelease>",
            self.on_range_typing
        )

        self.range_entry.pack(
            anchor="w",
            padx=50,
            pady=(8, 5)
        )

        self.range_entry.pack_forget()

        # ======================================================
        # HELP TEXT
        # ======================================================

        self.range_help = ctk.CTkLabel(
            left_panel,
            text=(
                "Contoh: 1-5,8,10-12\n"
                "Maka akan jadi 3 file PDF yaitu:\n"
                "1. 1-5.pdf\n"
                "2. 8.pdf\n"
                "3. 10-12.pdf"
            ),
            justify="left",
            anchor="w",
            wraplength=240,
            font=Fonts.HELP_TEXT,
            text_color=Colors.TEXT_SECONDARY,
        )

        self.range_help.pack(
            anchor="w",
            padx=50,
            pady=(0, 10)
        )

        self.range_help.pack_forget()

        # ======================================================
        # SPLIT BUTTON
        # ======================================================

        self.split_button = PrimaryButton(
            left_panel,
            text="Split PDF",
            command=self.on_split_pdf,
        )

        self.split_button.pack(
            anchor="w",
            padx=15,
            pady=(20, 10)
        )

        # ======================================================
        # RIGHT PREVIEW AREA
        # ======================================================

        right_panel = ctk.CTkFrame(
            container,
            fg_color="#F5F8FC",
            corner_radius=14,
        )

        right_panel.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(10, 25),
            pady=25,
        )

        right_panel.grid_rowconfigure(
            0,
            weight=1
        )

        right_panel.grid_columnconfigure(
            0,
            weight=1
        )

        # ======================================================
        # THUMBNAIL VIEWER
        # ======================================================

        self.thumbnail_viewer = PdfThumbnailViewer(
            right_panel
        )

        self.thumbnail_viewer.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ======================================================
        # EMPTY STATE
        # ======================================================
        #
        # Ditampilkan ketika belum ada PDF.
        #
        # Saat PDF dipilih:
        #     empty state -> hilang
        #     thumbnail   -> tampil
        #
        # ======================================================

        self.empty_preview = ctk.CTkFrame(
            right_panel,
            fg_color="#F5F8FC",
            corner_radius=14,
        )

        self.empty_preview.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.96,
            relheight=0.92,
            anchor="center",
        )

        # ======================================================
        # EMPTY CONTENT
        # ======================================================

        empty_content = ctk.CTkFrame(
            self.empty_preview,
            fg_color="transparent",
        )

        empty_content.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        # ======================================================
        # EMPTY ICON
        # ======================================================

        empty_icon = ctk.CTkLabel(
            empty_content,
            text="",
            image=Icons.PDF_EMPTY,
        )

        empty_icon.pack(
            pady=(0, 12)
        )

        # ======================================================
        # EMPTY TITLE
        # ======================================================

        empty_title = ctk.CTkLabel(
            empty_content,
            text="Belum ada PDF dipilih",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            ),
            text_color=Colors.TEXT_PRIMARY,
        )

        empty_title.pack()

        # ======================================================
        # EMPTY SUBTITLE
        # ======================================================

        empty_subtitle = ctk.CTkLabel(
            empty_content,
            text="Pilih file PDF untuk melihat preview halaman.",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
            justify="center",
        )

        empty_subtitle.pack(
            pady=(8, 0)
        )

        # ======================================================
        # INITIAL STATE
        # ======================================================

        self.update_split_button(
            has_pdf=False
        )

        self.update_mode_ui()

    # ==========================================================
    # SELECT PDF
    # ==========================================================

    def on_select_pdf(self):

        filepath = filedialog.askopenfilename(
            title="Pilih PDF",
            filetypes=[
                ("PDF Files", "*.pdf")
            ]
        )

        if not filepath:
            return

        self.pdf_path = Path(
            filepath
        )

        # ======================================================
        # READ PDF
        # ======================================================

        try:

            reader = PdfReader(
                filepath
            )

            total_pages = len(
                reader.pages
            )

        except Exception as error:

            self.pdf_path = None
            self.total_pages = 0

            # Tampilkan kembali empty state
            self.empty_preview.place(
                relx=0.5,
                rely=0.5,
                relwidth=0.96,
                relheight=0.92,
                anchor="center",
            )

            messagebox.showerror(
                "Gagal Membaca PDF",
                str(error)
            )

            return

        # ======================================================
        # FILE SIZE
        # ======================================================

        file_size_mb = (
            self.pdf_path.stat().st_size
            /
            (1024 * 1024)
        )

        # ======================================================
        # UPDATE SUMMARY CARD
        # ======================================================

        self.preview_card.update_pdf(
            filename=self.pdf_path.name,
            pages=total_pages,
            size_mb=file_size_mb
        )

        # ======================================================
        # LOAD THUMBNAILS
        # ======================================================

        self.load_thumbnails(
            filepath
        )

        # ======================================================
        # HIDE EMPTY STATE
        # ======================================================

        self.empty_preview.place_forget()

        # ======================================================
        # SAVE METADATA
        # ======================================================

        self.total_pages = total_pages

        # ======================================================
        # ENABLE BUTTON
        # ======================================================

        self.update_split_button(
            has_pdf=True
        )

        # ======================================================
        # STATUS
        # ======================================================

        self.status_bar.set_status(
            f"PDF dipilih : {self.pdf_path.name}"
        )

    # ==========================================================
    # SPLIT PDF
    # ==========================================================

    def on_split_pdf(self):

        # ======================================================
        # VALIDATE PDF
        # ======================================================

        if self.pdf_path is None:

            messagebox.showwarning(
                "PDF Belum Dipilih",
                "Silakan pilih PDF terlebih dahulu."
            )

            return

        selected_mode = self.split_mode.get()

        # ======================================================
        # SPLIT PER PAGE
        # ======================================================

        if selected_mode == "page":

            output_folder = filedialog.askdirectory(
                title="Pilih Folder Output"
            )

            if not output_folder:
                return

            self.status_bar.set_status(
                "Memproses split PDF..."
            )

            success, message = (
                PdfSplitService.split_per_page(
                    self.pdf_path,
                    output_folder
                )
            )

            if success:

                messagebox.showinfo(
                    "Berhasil",
                    f"{message}\n\n"
                    f"Folder Output:\n{output_folder}"
                )

                self.status_bar.set_status(
                    message
                )

            else:

                messagebox.showerror(
                    "Gagal",
                    message
                )

                self.status_bar.set_status(
                    "Proses split gagal"
                )

        # ======================================================
        # SPLIT RANGE
        # ======================================================

        elif selected_mode == "range":

            page_groups = (
                self.range_entry.get()
                .strip()
            )

            if not page_groups:

                messagebox.showwarning(
                    "Input Kosong",
                    "Masukkan halaman yang ingin dipisahkan."
                )

                return

            try:

                groups = PageParser.parse_groups(
                    page_groups,
                    self.total_pages
                )

            except ValueError as error:

                messagebox.showwarning(
                    "Format Salah",
                    str(error)
                )

                return

            output_folder = filedialog.askdirectory(
                title="Pilih Folder Output"
            )

            if not output_folder:
                return

            self.status_bar.set_status(
                "Memproses split PDF..."
            )

            success, message = (
                PdfSplitService.split_groups(
                    self.pdf_path,
                    output_folder,
                    groups
                )
            )

            if success:

                messagebox.showinfo(
                    "Berhasil",
                    message
                )

                self.status_bar.set_status(
                    message
                )

            else:

                messagebox.showerror(
                    "Gagal",
                    message
                )

                self.status_bar.set_status(
                    "Proses split gagal"
                )

        # ======================================================
        # OTHER MODE
        # ======================================================

        else:

            messagebox.showinfo(
                "Coming Soon",
                "Mode split ini akan dibuat pada Episode berikutnya."
            )

    # ==========================================================
    # SPLIT BUTTON STATE
    # ==========================================================

    def update_split_button(
        self,
        has_pdf
    ):

        if has_pdf:

            self.split_button.configure(
                state="normal",
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_HOVER
            )

        else:

            self.split_button.configure(
                state="disabled",
                fg_color=Colors.TEXT_MUTED,
                hover_color=Colors.TEXT_MUTED
            )

    # ==========================================================
    # RANGE TYPING
    # ==========================================================

    def on_range_typing(
        self,
        event
    ):

        value = (
            self.range_entry
            .get()
            .strip()
        )

        if value:

            self.split_mode.set(
                "range"
            )

            self.update_mode_ui()

    # ==========================================================
    # UPDATE MODE UI
    # ==========================================================

    def update_mode_ui(self):

        selected_mode = (
            self.split_mode.get()
        )

        if selected_mode == "range":

            self.range_entry.pack(
                anchor="w",
                padx=50,
                pady=(8, 5),
                before=self.split_button
            )

            self.range_help.pack(
                anchor="w",
                padx=50,
                pady=(0, 10),
                before=self.split_button
            )

        else:

            self.range_entry.pack_forget()

            self.range_help.pack_forget()

    # ==========================================================
    # LOAD PDF THUMBNAILS
    # ==========================================================

    def load_thumbnails(
        self,
        pdf_path
    ):

        self.thumbnail_viewer.clear()

        pdf = fitz.open(
            pdf_path
        )

        # ======================================================
        # LOAD ALL PAGES
        # ======================================================

        max_pages = len(pdf)

        for page_index in range(
            max_pages
        ):

            page = pdf.load_page(
                page_index
            )

            pix = page.get_pixmap(
                matrix=fitz.Matrix(
                    0.25,
                    0.25
                )
            )

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples
            )

            thumbnail = CTkImage(
                light_image=image,
                dark_image=image,
                size=(150, 210)
            )

            self.thumbnail_viewer.add_thumbnail(
                thumbnail,
                page_index + 1
            )

        pdf.close()