"""
==========================================================
Mahdi PDF Studio
MONEV PIUTANG Page
==========================================================

Halaman untuk menggabungkan beberapa file Excel
MONEV PIUTANG menjadi satu file.

==========================================================
"""

import os

import customtkinter as ctk
from tkinter import filedialog, messagebox

from core.services.gabung_excel_service import GabungExcelService

from themes.colors import Colors
from themes.fonts import Fonts
from themes.icons import Icons


class MonevPiutangPage(ctk.CTkFrame):

    # ==================================================
    # LAYOUT CONSTANT
    # ==================================================

    FILE_LIST_HEIGHT = 395

    # ==================================================
    # INITIALIZATION
    # ==================================================

    def __init__(
        self,
        master,
        status_bar=None
    ):

        super().__init__(
            master,
            fg_color=Colors.WORKSPACE_BG,
        )

        self.selected_files = []

        self.status_bar = status_bar

        self.configure_layout()
        self.create_header()
        self.create_file_section()

        self.update_info_panel()

    # ==================================================
    # LAYOUT
    # ==================================================

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

    # ==================================================
    # HEADER
    # ==================================================

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

        # ==================================================
        # SUMMARY CARD
        # ==================================================

        summary_card = ctk.CTkFrame(
            header_frame,
            width=350,
            height=110,
            corner_radius=16,
            fg_color="#FFFFFF",
            border_width=1,
            border_color=Colors.BORDER,
        )

        summary_card.grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="ne",
            padx=(20, 0),
        )

        summary_card.grid_propagate(False)

        summary_title = ctk.CTkLabel(
            summary_card,
            text="▥  Ringkasan",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color=Colors.TEXT_PRIMARY,
        )

        summary_title.pack(
            anchor="w",
            padx=22,
            pady=(5, 5),
        )

        # ==================================================
        # SUMMARY DATA
        # ==================================================

        summary_container = ctk.CTkFrame(
            summary_card,
            fg_color="transparent",
        )

        summary_container.pack(
            fill="x",
            padx=22,
            pady=(2, 2),
        )

        summary_container.grid_columnconfigure(
            0,
            weight=1
        )

        summary_container.grid_columnconfigure(
            1,
            weight=1
        )

        self.total_file_label = ctk.CTkLabel(
            summary_container,
            text="Total File : 0",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
        )

        self.total_file_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 15),
        )

        self.total_data_label = ctk.CTkLabel(
            summary_container,
            text="Total Data : 0",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
            anchor="e",
        )

        self.total_data_label.grid(
            row=0,
            column=1,
            sticky="e",
            padx=(15, 0),
        )

        # ==================================================
        # ICON BOX
        # ==================================================

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

        icon_label = ctk.CTkLabel(
            icon_box,
            text="",
            image=Icons.PIUTANG_LOGO,
        )

        icon_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        # ==================================================
        # TITLE
        # ==================================================

        title = ctk.CTkLabel(
            header_frame,
            text="MONEV PIUTANG",
            font=Fonts.PAGE_TITLE,
            text_color=Colors.TEXT_PRIMARY,
        )

        title.grid(
            row=0,
            column=1,
            sticky="sw",
            pady=(0, 2),
        )

        # ==================================================
        # SUBTITLE
        # ==================================================

        subtitle = ctk.CTkLabel(
            header_frame,
            text=(
                "Gabungkan beberapa file Excel PIUTANG "
                "menjadi satu dokumen."
            ),
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
        )

        subtitle.grid(
            row=1,
            column=1,
            sticky="nw",
        )

    # ==================================================
    # FILE SECTION
    # ==================================================

    def create_file_section(self):

        # ==================================================
        # OUTER CARD
        # ==================================================

        section = ctk.CTkFrame(
            self,
            fg_color=Colors.WORKSPACE_BG,

        )

        section.grid(
            row=1,
            column=0,
            padx=30,
            pady=(10, 0),
            sticky="nsew",
        )

        section.grid_columnconfigure(
            0,
            weight=1
        )

        section.grid_rowconfigure(
            1,
            weight=1
        )

        # ==================================================
        # FILE LIST CONTAINER
        # ==================================================

        self.file_list_container = ctk.CTkFrame(
            section,
            fg_color="transparent",
        )

        self.file_list_container.grid(
            row=1,
            column=0,
            padx=25,
            pady=(10, 10),
            sticky="nsew",
        )

        self.file_list_container.grid_columnconfigure(
            0,
            weight=1
        )

        self.file_list_container.grid_rowconfigure(
            0,
            weight=1
        )

        # ==================================================
        # SCROLLABLE FILE LIST
        # ==================================================

        self.file_list_frame = ctk.CTkScrollableFrame(
            self.file_list_container,
            fg_color=Colors.WORKSPACE_BG,
            corner_radius=14,
        )

        self.file_list_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.file_list_frame.grid_columnconfigure(
            0,
            weight=1
        )

        # ==================================================
        # EMPTY STATE
        # ==================================================

        self.empty_state = ctk.CTkFrame(
            self.file_list_container,
            fg_color=Colors.MERGE_BG,
            corner_radius=14,
        )

        self.empty_state.place(
            relx=0.5,
            rely=0.5,
            relwidth=0.96,
            relheight=0.90,
            anchor="center",
        )

        # ==================================================
        # EMPTY CONTENT
        # ==================================================

        empty_content = ctk.CTkFrame(
            self.empty_state,
            fg_color="transparent",
            width=600,
            height=320,
        )

        empty_content.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        empty_content.pack_propagate(False)

        # ==================================================
        # EMPTY ICON
        # ==================================================

        empty_icon = ctk.CTkLabel(
            empty_content,
            text="",
            image=Icons.EXCEL_EMPTY,
        )

        empty_icon.pack(
            pady=(0, 10)
        )

        # ==================================================
        # EMPTY TITLE
        # ==================================================

        empty_title = ctk.CTkLabel(
            empty_content,
            text="Belum ada file Excel",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color=Colors.TEXT_PRIMARY,
        )

        empty_title.pack()

        # ==================================================
        # EMPTY DESCRIPTION
        # ==================================================

        empty_subtitle = ctk.CTkLabel(
            empty_content,
            text=(
                "Belum ada file Excel MONEV PIUTANG yang ditambahkan.\n"
                "Klik tombol \"Tambah File\" untuk memilih file."
            ),
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
            justify="center",
        )

        empty_subtitle.pack(
            pady=(6, 18)
        )

        # ==================================================
        # BUTTON AREA
        # ==================================================

        button_frame = ctk.CTkFrame(
            section,
            fg_color="transparent",
        )

        button_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 20),
        )

        button_frame.grid_columnconfigure(
            0,
            weight=0
        )

        button_frame.grid_columnconfigure(
            1,
            weight=0
        )

        button_frame.grid_columnconfigure(
            2,
            weight=1
        )

        button_frame.grid_columnconfigure(
            3,
            weight=0
        )

        # ==================================================
        # TAMBAH FILE
        # ==================================================

        self.add_button = ctk.CTkButton(
            button_frame,
            text="+  Tambah File",
            width=170,
            height=48,
            corner_radius=10,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=self.add_files,
        )

        self.add_button.grid(
            row=0,
            column=0,
            sticky="w",
        )

        # ==================================================
        # HAPUS SEMUA
        # ==================================================

        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Hapus Semua",
            width=170,
            height=48,
            corner_radius=10,
            fg_color="#FFFFFF",
            hover_color="#F5F8FC",
            border_width=1,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(
                size=14
            ),
            command=self.clear_files,
        )

        self.clear_button.grid(
            row=0,
            column=1,
            padx=(15, 0),
            sticky="w",
        )

        # ==================================================
        # PROCESS
        # ==================================================

        self.process_button = ctk.CTkButton(
            button_frame,
            text="PROSES MONEV PIUTANG",
            width=230,
            height=48,
            corner_radius=10,
            fg_color=Colors.TEXT_MUTED,
            hover_color=Colors.TEXT_MUTED,
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=self.process_files,
        )

        self.process_button.grid(
            row=0,
            column=3,
            sticky="e",
        )

    # ==================================================
    # ADD FILE
    # ==================================================

    def add_files(self):

        files = filedialog.askopenfilenames(
            title="Pilih File Excel MONEV PIUTANG",
            filetypes=[
                (
                    "Excel Files",
                    "*.xls *.xlsx"
                )
            ],
        )

        if not files:
            return

        added = 0

        for file_path in files:

            if file_path not in self.selected_files:

                self.selected_files.append(
                    file_path
                )

                added += 1

        self.refresh_file_list()

        if self.status_bar is not None and added:

            self.status_bar.set_status(
                f"{added} file Excel berhasil ditambahkan"
            )

    # ==================================================
    # REFRESH FILE LIST
    # ==================================================

    def refresh_file_list(self):

        for widget in self.file_list_frame.winfo_children():

            widget.destroy()

        if not self.selected_files:

            self.empty_state.place(
                relx=0.5,
                rely=0.5,
                relwidth=0.96,
                relheight=0.90,
                anchor="center",
            )

        else:

            self.empty_state.place_forget()

            for index, file_path in enumerate(
                self.selected_files,
                start=1
            ):

                self.create_file_item(
                    index,
                    file_path
                )

        self.update_info_panel()

    # ==================================================
    # FILE ITEM
    # ==================================================

    def create_file_item(
        self,
        index,
        file_path
    ):

        item = ctk.CTkFrame(
            self.file_list_frame,
            fg_color="#F8FAFC",
            corner_radius=10,
            border_width=1,
            border_color=Colors.BORDER,
        )

        item.pack(
            fill="x",
            padx=15,
            pady=6,
        )

        # ==================================================
        # COLUMN CONFIGURATION
        # ==================================================

        item.grid_columnconfigure(
            0,
            weight=0
        )

        item.grid_columnconfigure(
            1,
            weight=0
        )

        item.grid_columnconfigure(
            2,
            weight=1
        )

        item.grid_columnconfigure(
            3,
            weight=0
        )

        # ==================================================
        # NUMBER
        # ==================================================

        number = ctk.CTkLabel(
            item,
            text=str(index),
            width=35,
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=Colors.TEXT_SECONDARY,
        )

        number.grid(
            row=0,
            column=0,
            padx=(12, 5),
            pady=12,
        )

        # ==================================================
        # EXCEL ICON
        # ==================================================

        icon = ctk.CTkLabel(
            item,
            text="",
            image=Icons.EXCEL,
        )

        icon.grid(
            row=0,
            column=1,
            sticky="w",
            padx=(5, 10),
            pady=12,
        )

        # ==================================================
        # FILE NAME
        # ==================================================

        filename = ctk.CTkLabel(
            item,
            text=os.path.basename(file_path),
            anchor="w",
            justify="left",
            font=ctk.CTkFont(
                size=13
            ),
            text_color=Colors.TEXT_PRIMARY,
        )

        filename.grid(
            row=0,
            column=2,
            sticky="w",
            padx=(5, 10),
            pady=12,
        )

        # ==================================================
        # REMOVE
        # ==================================================

        remove_button = ctk.CTkButton(
            item,
            text="×",
            width=35,
            height=30,
            corner_radius=8,
            fg_color="transparent",
            hover_color="#FEE2E2",
            text_color="#DC2626",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            command=lambda path=file_path:
                self.remove_file(path),
        )

        remove_button.grid(
            row=0,
            column=3,
            padx=(5, 10),
            pady=10,
        )

    # ==================================================
    # REMOVE FILE
    # ==================================================

    def remove_file(
        self,
        file_path
    ):

        if file_path in self.selected_files:

            self.selected_files.remove(
                file_path
            )

        self.refresh_file_list()

        self.update_status(
            f"{len(self.selected_files)} file Excel dipilih."
        )

    # ==================================================
    # CLEAR FILES
    # ==================================================

    def clear_files(self):

        if not self.selected_files:
            return

        confirm = messagebox.askyesno(
            "Hapus Semua",
            "Apakah Anda yakin ingin menghapus semua file?",
            parent=self
        )

        if not confirm:
            return

        self.selected_files.clear()

        self.refresh_file_list()

        self.update_status(
            "Daftar file MONEV PIUTANG dikosongkan"
        )

    # ==================================================
    # UPDATE INFO
    # ==================================================

    def update_info_panel(self):

        total_files = len(
            self.selected_files
        )

        self.total_file_label.configure(
            text=f"Total File : {total_files}"
        )

        self.total_data_label.configure(
            text="Total Data : 0"
        )

        if total_files > 0:

            self.process_button.configure(
                state="normal",
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_HOVER,
            )

        else:

            self.process_button.configure(
                state="disabled",
                fg_color=Colors.TEXT_MUTED,
                hover_color=Colors.TEXT_MUTED,
            )

    # ==================================================
    # PROCESS
    # ==================================================

    def process_files(self):

        if not self.selected_files:

            messagebox.showwarning(
                "MONEV PIUTANG",
                "Silakan tambahkan file Excel terlebih dahulu.",
                parent=self
            )

            return

        confirm = messagebox.askyesno(
            "Proses MONEV PIUTANG",
            (
                f"Proses {len(self.selected_files)} "
                "file Excel?"
            ),
            parent=self
        )

        if not confirm:
            return

        try:

            # ==================================================
            # PROCESS DATA
            # ==================================================

            self.update_status(
                "Sedang memproses MONEV PIUTANG..."
            )

            result_df = GabungExcelService.process_files(
                self.selected_files
            )

            if result_df.empty:

                messagebox.showwarning(
                    "Data Kosong",
                    "Tidak ada data yang dapat diproses.",
                    parent=self
                )

                return

            # ==================================================
            # UPDATE SUMMARY
            # ==================================================

            self.total_data_label.configure(
                text=f"Total Data : {len(result_df)}"
            )

            # ==================================================
            # SAVE DIALOG
            # ==================================================

            output_path = filedialog.asksaveasfilename(
                title="Simpan Hasil MONEV PIUTANG",
                defaultextension=".xlsx",
                filetypes=[
                    (
                        "Excel Workbook",
                        "*.xlsx"
                    )
                ],
                initialfile="MONEV_PIUTANG.xlsx",
            )

            if not output_path:

                self.update_status(
                    "Proses MONEV PIUTANG dibatalkan."
                )

                return

            # ==================================================
            # EXPORT
            # ==================================================

            GabungExcelService.export_to_excel(
                result_df,
                output_path,
            )

            self.update_status(
                "MONEV PIUTANG berhasil diproses."
            )

            messagebox.showinfo(
                "MONEV PIUTANG Berhasil",
                (
                    "MONEV PIUTANG berhasil diproses.\n\n"
                    f"Jumlah file : {len(self.selected_files)}\n"
                    f"Jumlah data : {len(result_df)}\n\n"
                    f"File disimpan di:\n{output_path}"
                ),
                parent=self
            )

        except Exception as error:

            self.update_status(
                "Terjadi kesalahan saat memproses MONEV PIUTANG."
            )

            messagebox.showerror(
                "MONEV PIUTANG - Error",
                (
                    "Terjadi kesalahan saat memproses "
                    "file Excel.\n\n"
                    f"{error}"
                ),
                parent=self
            )

    # ==================================================
    # STATUS BAR
    # ==================================================

    def update_status(
        self,
        message
    ):

        if self.status_bar is None:
            return

        try:

            self.status_bar.set_status(
                message
            )

        except AttributeError:

            pass