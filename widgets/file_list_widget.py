"""
==========================================================
Mahdi PDF Studio
File List Widget - Smooth Thumbnail Drag
==========================================================

Widget utama untuk mengelola daftar PDF pada Merge PDF.

FITUR
----------------------------------------------------------

1. Empty State
2. Thumbnail PDF
3. Tombol tambah PDF
4. Tombol hapus semua
5. Hapus satu file
6. Windows Explorer Drag & Drop
7. Drag thumbnail untuk reorder
8. Ghost card mengikuti mouse
9. Card lain langsung bergeser
10. Tidak melakukan refresh() selama drag
11. Toolbar selalu terlihat
12. Scrollbar tetap tersedia
13. Jumlah file tidak menghilangkan toolbar
14. Ghost mempunyai ukuran sama dengan FileItem
15. Posisi ghost mempertahankan titik pegangan mouse
16. Koordinat ghost menggunakan ROOT/SCREEN coordinate
17. Debug first-move ghost

==========================================================
PRINSIP DRAG
==========================================================

                MOUSE ROOT
                    │
                    ▼
          mouse_root - grab_offset
                    │
                    ▼
             EXPECTED ROOT
                    │
                    ▼
       dikonversi ke koordinat
          parent ghost
                    │
                    ▼
              ghost.place()

PENTING:

Jangan menggunakan:

    FileListWidget root
    sebagai basis posisi ghost.

Karena FileItem berada di dalam:

    CTkScrollableFrame
        └── internal scroll frame

sehingga coordinate system dapat berbeda.

==========================================================

Author : Muhammad Hadi Putra
Version: 4.2
"""

import customtkinter as ctk
from tkinter import messagebox

from data.models.pdf_file import PdfFile
from widgets.file_item import FileItem

from core.services.dragdrop.manager import DragDropManager

from themes.colors import Colors
from themes.fonts import Fonts
from themes.icons import Icons


class FileListWidget(ctk.CTkFrame):

    # ==========================================================
    # GRID
    # ==========================================================

    THUMBNAIL_COLUMNS = 4

    # ==========================================================
    # SPACING
    # ==========================================================

    ITEM_PAD_X = 12
    ITEM_PAD_Y = 12

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        master,
        on_change=None,
        on_add_file=None,
    ):

        super().__init__(
            master,

            fg_color=Colors.HERO_BG,

            corner_radius=25,

            border_width=1,

            border_color=Colors.BORDER_HERO,
        )

        # ======================================================
        # CALLBACK
        # ======================================================

        self.on_change = on_change

        self.on_add_file = on_add_file

        # ======================================================
        # DATA
        # ======================================================

        self.files: list[PdfFile] = []

        # ======================================================
        # DRAG STATE
        # ======================================================

        self._dragged_item = None

        self._dragged_index = None

        self._drop_index = None

        # ======================================================
        # GRAB OFFSET
        # ======================================================

        #
        # Posisi cursor relatif terhadap pojok kiri atas
        # FileItem ketika drag dimulai.
        #

        self._grab_offset_x = 0

        self._grab_offset_y = 0

        # ======================================================
        # DRAG MOUSE ROOT
        # ======================================================

        #
        # Posisi mouse ROOT terakhir.
        #
        # Digunakan untuk debug dan validasi.
        #

        self._last_mouse_root_x = None

        self._last_mouse_root_y = None

        # ======================================================
        # EXPECTED GHOST ROOT
        # ======================================================

        #
        # Posisi ghost yang SEHARUSNYA berdasarkan:
        #
        # mouse_root - grab_offset
        #

        self._expected_ghost_root_x = None

        self._expected_ghost_root_y = None

        # ======================================================
        # GHOST
        # ======================================================

        self._ghost = None

        self._ghost_parent = None

        self._ghost_width = 0

        self._ghost_height = 0

        # ======================================================
        # THUMBNAIL AREA
        # ======================================================

        self.thumbnail_area = None

        # ======================================================
        # LAYOUT
        # ======================================================

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            0,
            weight=0,
        )

        self.grid_rowconfigure(
            1,
            weight=1,
        )

        # ======================================================
        # WINDOWS DRAG & DROP
        # ======================================================

        self.dragdrop = DragDropManager(
            widget=self,

            callback=self._on_drop_files,
        )

        # ======================================================
        # INITIAL RENDER
        # ======================================================

        self.refresh()

    # ==========================================================
    # DATA API
    # ==========================================================

    def add_file(
        self,
        pdf: PdfFile,
    ):

        if not isinstance(
            pdf,
            PdfFile,
        ):

            raise TypeError(
                "pdf harus berupa PdfFile"
            )

        self.files.append(pdf)

        self.refresh()

        self.notify_change()

    # ==========================================================

    def add_files(
        self,
        pdfs,
    ):

        valid_files = [
            pdf
            for pdf in pdfs
            if isinstance(
                pdf,
                PdfFile,
            )
        ]

        if not valid_files:

            return

        self.files.extend(
            valid_files
        )

        self.refresh()

        self.notify_change()

    # ==========================================================

    def delete_file(
        self,
        index,
    ):

        if not (
            0 <= index < len(self.files)
        ):

            return

        pdf = self.files[index]

        answer = messagebox.askyesno(
            "Hapus File",

            (
                "Apakah Anda yakin ingin "
                "menghapus:\n\n"
                f"{pdf.filename}?"
            ),
        )

        if not answer:

            return

        self.files.pop(index)

        self.refresh()

        self.notify_change()

    # ==========================================================

    def clear(self):

        if not self.files:

            return

        answer = messagebox.askyesno(
            "Hapus Semua File",

            (
                "Apakah Anda yakin ingin "
                "menghapus seluruh file PDF?"
            ),
        )

        if not answer:

            return

        self.files.clear()

        self.refresh()

        self.notify_change()

    # ==========================================================

    def get_files(self):

        return list(
            self.files
        )

    # ==========================================================
    # REFRESH
    # ==========================================================

    def refresh(self):
        """
        ==========================================================
        REFRESH
        ==========================================================

        Refresh hanya dilakukan ketika data berubah.

        TIDAK boleh dipanggil selama drag motion.
        """

        # ======================================================
        # HAPUS GHOST
        # ======================================================

        self._destroy_ghost()

        # ======================================================
        # RESET DRAG
        # ======================================================

        self._dragged_item = None

        self._dragged_index = None

        self._drop_index = None

        self._ghost_parent = None

        self._expected_ghost_root_x = None

        self._expected_ghost_root_y = None

        # ======================================================
        # RESET WINDOWS DROP
        # ======================================================

        try:

            self.dragdrop.unregister_all()

        except Exception:

            pass

        # ======================================================
        # HAPUS UI LAMA
        # ======================================================

        for widget in self.winfo_children():

            widget.destroy()

        # ======================================================
        # RESET REFERENCE
        # ======================================================

        self.thumbnail_area = None

        # ======================================================
        # EMPTY STATE
        # ======================================================

        if not self.files:

            self._build_empty_state()

            return

        # ======================================================
        # FILE STATE
        # ======================================================

        self._build_file_state()

    # ==========================================================
    # EMPTY STATE
    # ==========================================================

    def _build_empty_state(self):

        surface = ctk.CTkFrame(
            self,

            fg_color="transparent",
        )

        surface.grid(
            row=0,
            column=0,

            rowspan=2,

            sticky="nsew",
        )

        surface.grid_rowconfigure(
            0,
            weight=1,
        )

        surface.grid_columnconfigure(
            0,
            weight=1,
        )

        content = ctk.CTkFrame(
            surface,

            fg_color="transparent",
        )

        content.grid(
            row=0,
            column=0,
        )

        # ======================================================
        # ICON
        # ======================================================

        icon = ctk.CTkLabel(
            content,
            text="",
            image=Icons.PDF_EMPTY,
        )

        icon.pack(
            pady=(0, 10)
        )

        # ======================================================
        # TITLE
        # ======================================================

        title = ctk.CTkLabel(
            content,

            text="Drop PDF Disini",

            font=(
                "Segoe UI",
                24,
                "bold",
            ),

            text_color=Colors.TEXT_PRIMARY,
        )

        title.pack(
            pady=(0, 6)
        )

        # ======================================================
        # SUBTITLE
        # ======================================================

        subtitle = ctk.CTkLabel(
            content,

            text="atau klik tombol Tambah PDF",

            font=Fonts.PAGE_SUBTITLE,

            text_color=Colors.TEXT_SECONDARY,
        )

        subtitle.pack(
            pady=(0, 16)
        )

        # ======================================================
        # ADD BUTTON
        # ======================================================

        add_button = ctk.CTkButton(
            content,

            text="+ Tambah PDF",

            command=self.on_add_file,

            width=155,

            height=42,

            corner_radius=12,

            fg_color=Colors.PRIMARY,

            hover_color=Colors.PRIMARY_HOVER,

            font=Fonts.BUTTON,
        )

        add_button.pack()

        # ======================================================
        # WINDOWS DROP TARGET
        # ======================================================

        for widget in (
            surface,
            content,
            icon,
            title,
            subtitle,
            add_button,
        ):

            self.dragdrop.register(
                widget
            )

    # ==========================================================
    # FILE STATE
    # ==========================================================

    def _build_file_state(self):

        # ======================================================
        # TOOLBAR
        # ======================================================

        toolbar = ctk.CTkFrame(
            self,

            fg_color="transparent",
        )

        toolbar.grid(
            row=0,
            column=0,

            sticky="ew",

            padx=12,

            pady=(10, 6),
        )

        toolbar.grid_columnconfigure(
            0,
            weight=1,
        )

        # ======================================================
        # BUTTON GROUP
        # ======================================================

        button_group = ctk.CTkFrame(
            toolbar,

            fg_color="transparent",
        )

        button_group.grid(
            row=0,
            column=0,

            sticky="e",
        )

        # ======================================================
        # ADD
        # ======================================================

        add_button = ctk.CTkButton(
            button_group,

            text="+",

            width=48,

            height=38,

            corner_radius=12,

            fg_color="transparent",

            hover_color=Colors.PRIMARY_HOVER,

            border_color=Colors.PRIMARY_ACTIVE,

            border_width=1,

            text_color=Colors.PRIMARY_ACTIVE,

            font=(
                "Segoe UI",
                25,
                "bold",
            ),

            command=self.on_add_file,
        )

        add_button.pack(
            side="left",

            padx=(0, 6),
        )

        # ======================================================
        # CLEAR
        # ======================================================

        clear_button = ctk.CTkButton(
            button_group,

            text="🗑",

            width=38,

            height=38,

            corner_radius=12,

            fg_color="transparent",

            hover_color=Colors.DANGER_HOVER,

            border_width=1,

            border_color=Colors.DANGER,

            text_color=Colors.DANGER,

            font=(
                "Segoe UI Emoji",
                16,
            ),

            command=self.clear,
        )

        clear_button.pack(
            side="left"
        )

        # ======================================================
        # SCROLLABLE AREA
        # ======================================================

        self.thumbnail_area = ctk.CTkScrollableFrame(
            self,

            fg_color="transparent",

            corner_radius=0,

            scrollbar_button_color=Colors.PRIMARY,

            scrollbar_button_hover_color=Colors.PRIMARY_HOVER,
        )

        self.thumbnail_area.grid(
            row=1,
            column=0,

            sticky="nsew",

            padx=12,

            pady=(4, 12),
        )

        # ======================================================
        # GRID COLUMNS
        # ======================================================

        for column in range(
            self.THUMBNAIL_COLUMNS
        ):

            self.thumbnail_area.grid_columnconfigure(
                column,

                weight=1,

                uniform="thumbnail",
            )

        # ======================================================
        # CREATE FILE ITEMS
        # ======================================================

        for index, pdf in enumerate(
            self.files
        ):

            row = (
                index
                // self.THUMBNAIL_COLUMNS
            )

            column = (
                index
                % self.THUMBNAIL_COLUMNS
            )

            item = FileItem(
                self.thumbnail_area,

                pdf=pdf,

                order=index + 1,

                on_delete=lambda i=index:
                    self.delete_file(i),

                on_drag_start=self._on_drag_start,

                on_drag_motion=self._on_drag_motion,

                on_drag_end=self._on_drag_end,
            )

            item.grid(
                row=row,

                column=column,

                padx=self.ITEM_PAD_X,

                pady=self.ITEM_PAD_Y,

                sticky="n",
            )

            self.dragdrop.register(
                item
            )

        # ======================================================
        # DROP TARGET
        # ======================================================

        self.dragdrop.register(
            self.thumbnail_area
        )

    # ==========================================================
    # WINDOWS EXPLORER DROP
    # ==========================================================

    def _on_drop_files(
        self,
        filepaths,
    ):

        if self.on_add_file:

            self.on_add_file(
                filepaths
            )

    # ==========================================================
    # DRAG START
    # ==========================================================

    def _on_drag_start(
        self,
        item,
        event,
    ):
        """
        ==========================================================
        DRAG START
        ==========================================================

        Sangat penting:

        1. Ambil posisi card.
        2. Ambil posisi mouse.
        3. Hitung grab offset.
        4. Buat ghost.
        5. Hide card.
        6. Update slot.
        7. Posisikan ghost berdasarkan ROOT.
        """

        if item not in self._get_file_items():

            return

        # ======================================================
        # INDEX
        # ======================================================

        try:

            self._dragged_index = (
                self.files.index(
                    item.pdf
                )
            )

        except ValueError:

            return

        # ======================================================
        # STATE
        # ======================================================

        self._dragged_item = item

        self._drop_index = (
            self._dragged_index
        )

        # ======================================================
        # PASTIKAN GEOMETRY TERBARU
        # ======================================================

        self.update_idletasks()

        item.update_idletasks()

        # ======================================================
        # MOUSE ROOT
        # ======================================================

        mouse_root_x = event.x_root

        mouse_root_y = event.y_root

        self._last_mouse_root_x = (
            mouse_root_x
        )

        self._last_mouse_root_y = (
            mouse_root_y
        )

        # ======================================================
        # CARD ROOT
        # ======================================================

        card_root_x = (
            item.winfo_rootx()
        )

        card_root_y = (
            item.winfo_rooty()
        )

        # ======================================================
        # CARD SIZE
        # ======================================================

        card_width = (
            item.winfo_width()
        )

        card_height = (
            item.winfo_height()
        )

        # ======================================================
        # GRAB OFFSET
        # ======================================================

        self._grab_offset_x = (
            mouse_root_x
            - card_root_x
        )

        self._grab_offset_y = (
            mouse_root_y
            - card_root_y
        )

        # ======================================================
        # EXPECTED ROOT
        # ======================================================

        expected_root_x = (
            mouse_root_x
            - self._grab_offset_x
        )

        expected_root_y = (
            mouse_root_y
            - self._grab_offset_y
        )

        self._expected_ghost_root_x = (
            expected_root_x
        )

        self._expected_ghost_root_y = (
            expected_root_y
        )

        # ======================================================
        # DEBUG
        # ======================================================

        print("\n")

        print("=" * 70)

        print(
            "                    DEBUG DRAG START"
        )

        print("=" * 70)

        print(
            f"FILE INDEX       : "
            f"{self._dragged_index + 1}"
        )

        print(
            f"FILE NAME        : "
            f"{item.pdf.filename}"
        )

        print("-" * 70)

        print(
            f"MOUSE ROOT       : "
            f"X={mouse_root_x}, "
            f"Y={mouse_root_y}"
        )

        print(
            f"CARD ROOT        : "
            f"X={card_root_x}, "
            f"Y={card_root_y}"
        )

        print(
            f"CARD SIZE        : "
            f"W={card_width}, "
            f"H={card_height}"
        )

        print("-" * 70)

        print(
            f"GRAB OFFSET      : "
            f"X={self._grab_offset_x}, "
            f"Y={self._grab_offset_y}"
        )

        print("-" * 70)

        print(
            f"EXPECTED ROOT    : "
            f"X={expected_root_x}, "
            f"Y={expected_root_y}"
        )

        print("=" * 70)

        # ======================================================
        # CREATE GHOST
        # ======================================================

        self._create_ghost(
            item
        )

        # ======================================================
        # HIDE ORIGINAL
        # ======================================================

        item.grid_remove()

        # ======================================================
        # UPDATE SLOT
        # ======================================================

        self._update_drag_layout()

        # ======================================================
        # POSISI GHOST
        # ======================================================

        self._move_ghost(
            event
        )

        # ======================================================
        # DEBUG FIRST MOVE
        # ======================================================

        self.after(
            10,
            self._debug_compare_ghost,
        )

    # ==========================================================
    # DEBUG GHOST
    # ==========================================================

    def _debug_compare_ghost(self):
        """
        ==========================================================
        DEBUG GHOST

        Membandingkan:

            EXPECTED ROOT
            ACTUAL GHOST ROOT

        BUKAN lagi membandingkan dengan posisi FileItem.

        FileItem memang boleh sudah bergeser setelah
        _update_drag_layout().
        """

        if self._ghost is None:

            return

        if (
            self._expected_ghost_root_x
            is None
        ):

            return

        if (
            self._expected_ghost_root_y
            is None
        ):

            return

        try:

            # ==================================================
            # ACTUAL GHOST ROOT
            # ==================================================

            actual_root_x = (
                self._ghost.winfo_rootx()
            )

            actual_root_y = (
                self._ghost.winfo_rooty()
            )

            # ==================================================
            # DIFFERENCE
            # ==================================================

            diff_x = (
                actual_root_x
                - self._expected_ghost_root_x
            )

            diff_y = (
                actual_root_y
                - self._expected_ghost_root_y
            )

            print(
                "\n"
                "[GHOST ROOT COMPARE]\n"
                f"EXPECTED ROOT : "
                f"({self._expected_ghost_root_x}, "
                f"{self._expected_ghost_root_y})\n"
                f"ACTUAL ROOT   : "
                f"({actual_root_x}, "
                f"{actual_root_y})\n"
                f"DIFF          : "
                f"({diff_x}, "
                f"{diff_y})\n"
            )

        except Exception as e:

            print(
                "[GHOST DEBUG ERROR]",
                e,
            )

    # ==========================================================
    # DRAG MOTION
    # ==========================================================

    def _on_drag_motion(
        self,
        item,
        event,
    ):

        if self._dragged_item is None:

            return

        if item is not self._dragged_item:

            return

        # ======================================================
        # SIMPAN MOUSE ROOT
        # ======================================================

        self._last_mouse_root_x = (
            event.x_root
        )

        self._last_mouse_root_y = (
            event.y_root
        )

        # ======================================================
        # GHOST
        # ======================================================

        self._move_ghost(
            event
        )

        # ======================================================
        # TARGET
        # ======================================================

        target_index = (
            self._calculate_target_index(
                event.x_root,
                event.y_root,
            )
        )

        if target_index is None:

            return

        # ======================================================
        # TARGET TIDAK BERUBAH
        # ======================================================

        if (
            target_index
            == self._drop_index
        ):

            return

        # ======================================================
        # UPDATE TARGET
        # ======================================================

        self._drop_index = (
            target_index
        )

        # ======================================================
        # UPDATE GRID
        # ======================================================

        self._update_drag_layout()

    # ==========================================================
    # DRAG END
    # ==========================================================

    def _on_drag_end(
        self,
        item,
        event,
    ):

        if self._dragged_item is None:

            return

        old_index = (
            self._dragged_index
        )

        new_index = (
            self._drop_index
        )

        if (
            old_index is None
            or
            new_index is None
        ):

            self._cancel_drag()

            return

        # ======================================================
        # UPDATE DATA
        # ======================================================

        if old_index != new_index:

            pdf = self.files.pop(
                old_index
            )

            self.files.insert(
                new_index,
                pdf,
            )

        # ======================================================
        # CLEAN GHOST
        # ======================================================

        self._destroy_ghost()

        # ======================================================
        # RESET DRAG STATE
        # ======================================================

        self._dragged_item = None

        self._dragged_index = None

        self._drop_index = None

        self._expected_ghost_root_x = None

        self._expected_ghost_root_y = None

        # ======================================================
        # RENDER SEKALI
        # ======================================================

        self.refresh()

        self.notify_change()

    # ==========================================================
    # CANCEL DRAG
    # ==========================================================

    def _cancel_drag(self):

        self._destroy_ghost()

        self._dragged_item = None

        self._dragged_index = None

        self._drop_index = None

        self._expected_ghost_root_x = None

        self._expected_ghost_root_y = None

        self.refresh()

    # ==========================================================
    # CREATE GHOST
    # ==========================================================

    def _create_ghost(
        self,
        item,
    ):
        """
        ==========================================================
        CREATE GHOST
        ==========================================================

        Ghost WAJIB dibuat pada parent yang sama dengan FileItem.

        Kenapa?

            FileItem
                │
                └── item.master

            Ghost
                │
                └── item.master

        Dengan begitu koordinat:

            FileItem
            Ghost
            grid
            place

        berada pada coordinate system yang sama.
        """

        # ======================================================
        # HAPUS GHOST LAMA
        # ======================================================

        self._destroy_ghost()

        # ======================================================
        # PARENT YANG SAMA DENGAN FILE ITEM
        # ======================================================

        ghost_parent = item.master

        if ghost_parent is None:

            return

        # ======================================================
        # UPDATE GEOMETRY
        # ======================================================

        self.update_idletasks()

        item.update_idletasks()

        ghost_parent.update_idletasks()

        # ======================================================
        # UKURAN AKTUAL FILE ITEM
        # ======================================================

        ghost_width = item.winfo_width()

        ghost_height = item.winfo_height()

        # ======================================================
        # FALLBACK
        # ======================================================

        if ghost_width <= 1:

            ghost_width = FileItem.CARD_WIDTH

        if ghost_height <= 1:

            ghost_height = FileItem.CARD_HEIGHT

        # ======================================================
        # SIMPAN UKURAN
        # ======================================================

        self._ghost_width = ghost_width

        self._ghost_height = ghost_height

        # ======================================================
        # CREATE GHOST
        # ======================================================

        ghost = ctk.CTkFrame(
            ghost_parent,

            width=ghost_width,

            height=ghost_height,

            corner_radius=16,

            fg_color=Colors.CARD_BG,

            border_width=2,

            border_color=Colors.PRIMARY,
        )

        ghost.grid_propagate(False)

        ghost.pack_propagate(False)

        # ======================================================
        # THUMBNAIL
        # ======================================================

        image = getattr(
            item.thumbnail_label,
            "image",
            None,
        )

        if image is not None:

            ghost_thumbnail = ctk.CTkLabel(
                ghost,

                text="",

                image=image,

                fg_color="transparent",
            )

            ghost_thumbnail.place(
                relx=0.5,

                x=0,

                y=18,

                anchor="n",
            )

        else:

            ghost_thumbnail = ctk.CTkLabel(
                ghost,

                text="📄",

                font=(
                    "Segoe UI Emoji",
                    54,
                ),

                text_color=Colors.TEXT_PRIMARY,

                fg_color="transparent",
            )

            ghost_thumbnail.place(
                relx=0.5,

                y=18,

                anchor="n",
            )

        # ======================================================
        # FILE NAME
        # ======================================================

        display_name = (
            FileItem._shorten_filename(
                item.pdf.filename,
                max_length=24,
            )
        )

        ghost_filename = ctk.CTkLabel(
            ghost,

            text=display_name,

            font=(
                "Segoe UI",
                11,
            ),

            text_color=Colors.TEXT_PRIMARY,

            anchor="center",

            justify="center",

            wraplength=max(
                100,
                ghost_width - 20,
            ),
        )

        ghost_filename.place(
            relx=0.5,

            rely=1.0,

            y=-10,

            anchor="s",
        )

        # ======================================================
        # SIMPAN REFERENCE
        # ======================================================

        self._ghost = ghost

        self._ghost_parent = ghost_parent

        # ======================================================
        # INITIAL POSITION
        # ======================================================

        ghost.place(
            x=0,
            y=0,
        )

        ghost.lift()


    # ==========================================================
    # MOVE GHOST
    # ==========================================================

    def _move_ghost(
        self,
        event,
    ):
        """
        ==========================================================
        MOVE GHOST
        ==========================================================

        Coordinate flow:

            Mouse ROOT
                ↓
            - Grab Offset
                ↓
            Expected Ghost ROOT
                ↓
            - Ghost Parent ROOT
                ↓
            Ghost LOCAL
                ↓
            ghost.place()
        """

        if self._ghost is None:

            return

        if self._ghost_parent is None:

            return

        try:

            # ==================================================
            # MOUSE ROOT
            # ==================================================

            mouse_root_x = event.x_root

            mouse_root_y = event.y_root

            # ==================================================
            # EXPECTED GHOST ROOT
            # ==================================================

            expected_root_x = (
                mouse_root_x
                - self._grab_offset_x
            )

            expected_root_y = (
                mouse_root_y
                - self._grab_offset_y
            )

            # ==================================================
            # SIMPAN UNTUK DEBUG
            # ==================================================

            self._expected_ghost_root_x = (
                expected_root_x
            )

            self._expected_ghost_root_y = (
                expected_root_y
            )

            # ==================================================
            # GHOST PARENT ROOT
            # ==================================================

            parent_root_x = (
                self._ghost_parent.winfo_rootx()
            )

            parent_root_y = (
                self._ghost_parent.winfo_rooty()
            )

            # ==================================================
            # ROOT → LOCAL PARENT
            # ==================================================

            local_x = (
                expected_root_x
                - parent_root_x
            )

            local_y = (
                expected_root_y
                - parent_root_y
            )

            # ==================================================
            # MOVE
            # ==================================================

            self._ghost.place(
                x=int(local_x),

                y=int(local_y),
            )

            # ==================================================
            # FRONT
            # ==================================================

            self._ghost.lift()

        except Exception as e:

            print(
                "[GHOST MOVE ERROR]",
                e,
            )

    # ==========================================================
    # CALCULATE TARGET
    # ==========================================================

    def _calculate_target_index(
        self,
        x_root,
        y_root,
    ):
        """
        ==========================================================
        CALCULATE TARGET INDEX
        ==========================================================

        Menghasilkan posisi FINAL dalam self.files.
        """

        items = (
            self._get_file_items()
        )

        visible_items = [
            item
            for item in items
            if item is not self._dragged_item
        ]

        if not visible_items:

            return self._dragged_index

        # ======================================================
        # SORT GRID
        # ======================================================

        visible_items.sort(
            key=lambda widget: (
                int(
                    widget.grid_info().get(
                        "row",
                        0,
                    )
                ),

                int(
                    widget.grid_info().get(
                        "column",
                        0,
                    )
                ),
            )
        )

        # ======================================================
        # CHECK CARD
        # ======================================================

        for position, widget in enumerate(
            visible_items
        ):

            try:

                left = (
                    widget.winfo_rootx()
                )

                top = (
                    widget.winfo_rooty()
                )

                width = (
                    widget.winfo_width()
                )

                height = (
                    widget.winfo_height()
                )

                right = (
                    left + width
                )

                bottom = (
                    top + height
                )

                # ==================================================
                # MOUSE DI DALAM CARD
                # ==================================================

                if (
                    left <= x_root <= right
                    and
                    top <= y_root <= bottom
                ):

                    middle_x = (
                        left
                        + width / 2
                    )

                    if x_root < middle_x:

                        target = position

                    else:

                        target = (
                            position + 1
                        )

                    # ==================================================
                    # FINAL INDEX
                    # ==================================================

                    return max(
                        0,

                        min(
                            target,

                            len(
                                self.files
                            ) - 1,
                        ),
                    )

            except Exception:

                continue

        # ======================================================
        # TIDAK DI ATAS CARD
        # ======================================================

        return self._drop_index

    # ==========================================================
    # UPDATE DRAG LAYOUT
    # ==========================================================

    def _update_drag_layout(self):
        """
        ==========================================================
        UPDATE DRAG LAYOUT
        ==========================================================

        Tidak melakukan refresh().

        Tidak membuat FileItem baru.

        Hanya mengubah posisi grid.
        """

        if self._dragged_item is None:

            return

        if self._drop_index is None:

            return

        # ======================================================
        # GET ITEMS
        # ======================================================

        items = (
            self._get_file_items()
        )

        # ======================================================
        # REMOVE DRAGGED
        # ======================================================

        remaining = [
            item
            for item in items
            if item is not self._dragged_item
        ]

        # ======================================================
        # SORT DATA ORDER
        # ======================================================

        remaining.sort(
            key=lambda item:
                self.files.index(
                    item.pdf
                )
        )

        # ======================================================
        # CREATE LOGICAL ORDER
        # ======================================================

        ordered_items = list(
            remaining
        )

        # ======================================================
        # INSERT EMPTY SLOT
        # ======================================================

        insertion_index = max(
            0,

            min(
                self._drop_index,

                len(
                    ordered_items
                ),
            ),
        )

        ordered_items.insert(
            insertion_index,

            None,
        )

        # ======================================================
        # GRID
        # ======================================================

        for slot, widget in enumerate(
            ordered_items
        ):

            if widget is None:

                continue

            row = (
                slot
                // self.THUMBNAIL_COLUMNS
            )

            column = (
                slot
                % self.THUMBNAIL_COLUMNS
            )

            try:

                widget.grid(
                    row=row,

                    column=column,

                    padx=self.ITEM_PAD_X,

                    pady=self.ITEM_PAD_Y,

                    sticky="n",
                )

            except Exception:

                pass

        # ======================================================
        # GHOST FRONT
        # ======================================================

        if self._ghost is not None:

            self._ghost.lift()

    # ==========================================================
    # GET FILE ITEMS
    # ==========================================================

    def _get_file_items(self):

        result = []

        def scan(widget):

            for child in (
                widget.winfo_children()
            ):

                if isinstance(
                    child,
                    FileItem,
                ):

                    result.append(
                        child
                    )

                scan(child)

        scan(self)

        return result

    # ==========================================================
    # DESTROY GHOST
    # ==========================================================

    def _destroy_ghost(self):

        if self._ghost is None:

            return

        try:

            self._ghost.destroy()

        except Exception:

            pass

        self._ghost = None

        self._ghost_parent = None

        self._ghost_width = 0

        self._ghost_height = 0

    # ==========================================================
    # CALLBACK
    # ==========================================================

    def notify_change(self):

        if self.on_change:

            self.on_change()

    # ==========================================================
    # DESTROY
    # ==========================================================

    def destroy(self):

        try:

            self._destroy_ghost()

        except Exception:

            pass

        try:

            self.dragdrop.destroy()

        except Exception:

            pass

        super().destroy()