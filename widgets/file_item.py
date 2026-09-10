"""
==========================================================
Mahdi PDF Studio
File Item - Thumbnail Card
==========================================================

Widget untuk menampilkan satu file PDF dalam bentuk
thumbnail card.

Tanggung jawab FileItem:

1. Menampilkan thumbnail PDF.
2. Menampilkan nama file.
3. Menampilkan tombol hapus.
4. Mendeteksi click.
5. Mendeteksi drag.
6. Mengirim event drag ke FileListWidget.
7. Memberikan visual feedback saat hover.
8. Memberikan visual feedback saat drag.
9. Mengubah cursor sesuai kondisi.

FileItem TIDAK menentukan urutan file.

Pengaturan urutan dilakukan oleh:

    FileListWidget

==========================================================

KONSEP INTERAKSI
==========================================================

NORMAL:

    ┌──────────────────────┐
    │                      │
    │                      │
    │      THUMBNAIL       │
    │                      │
    │                      │
    │    nama_file.pdf     │
    └──────────────────────┘

    Tombol X  : hidden
    Cursor    : arrow
    Border    : normal


HOVER CARD:

    ┌──────────────────────┐
    │                  ┌──┐│
    │                  │× ││
    │                  └──┘│
    │      THUMBNAIL       │
    │                      │
    │    nama_file.pdf     │
    └──────────────────────┘

    Tombol X  : visible
    Cursor    : fleur
    Border    : primary


HOVER TOMBOL X:

    ┌──────────────────────┐
    │                  ┌──┐│
    │                  │× ││
    │                  └──┘│
    │      THUMBNAIL       │
    │                      │
    │    nama_file.pdf     │
    └──────────────────────┘

    Tombol X  : visible
    Cursor    : hand2
    Drag      : disabled


DRAG:

    Mouse Press
         │
         ▼
    Simpan posisi awal
         │
         ▼
    Mouse Motion
         │
         ▼
    Sudah melewati threshold?
       /       \
     Tidak      Ya
      │          │
      │          ▼
      │      Mulai Drag
      │          │
      │          ├── border primary
      │          ├── cursor fleur
      │          └── callback
      │
      ▼
    tetap klik

==========================================================

Author : Muhammad Hadi Putra
Version: 5.0
==========================================================
"""

from pathlib import Path

import customtkinter as ctk

from themes.colors import Colors


class FileItem(ctk.CTkFrame):
    """
    ==========================================================
    THUMBNAIL CARD
    ==========================================================

    Satu FileItem mewakili satu file PDF.

    FileItem bertanggung jawab terhadap:

        UI
        Mouse event
        Hover event
        Drag event
        Visual feedback
        Cursor

    FileItem TIDAK mengubah:

        self.files

    Perubahan urutan tetap dilakukan oleh
    FileListWidget.
    """

    # ==========================================================
    # UKURAN CARD
    # ==========================================================

    CARD_WIDTH = 190
    CARD_HEIGHT = 250

    # ==========================================================
    # UKURAN THUMBNAIL
    # ==========================================================

    THUMBNAIL_WIDTH = 160
    THUMBNAIL_HEIGHT = 205

    # ==========================================================
    # DRAG THRESHOLD
    # ==========================================================

    #
    # Mouse harus bergerak minimal 5 pixel sebelum
    # klik dianggap sebagai drag.
    #

    DRAG_THRESHOLD = 5

    # ==========================================================
    # HOVER DELAY
    # ==========================================================

    #
    # Delay kecil ketika mouse keluar dari widget.
    #
    # Tujuannya agar tombol X tidak flicker ketika mouse
    # berpindah dari:
    #
    #     thumbnail
    #          ↓
    #     filename
    #          ↓
    #     delete button
    #
    # Nilai dalam milliseconds.
    #

    HOVER_LEAVE_DELAY = 30

    def __init__(
        self,
        master,
        pdf,
        order=1,
        on_delete=None,
        on_drag_start=None,
        on_drag_motion=None,
        on_drag_end=None,
    ):
        """
        Parameters
        ----------
        master:
            Parent widget.

        pdf:
            Object PdfFile.

        order:
            Nomor urutan file.

        on_delete:
            Callback untuk menghapus file.

        on_drag_start:
            Dipanggil ketika drag dimulai.

        on_drag_motion:
            Dipanggil terus selama mouse bergerak.

        on_drag_end:
            Dipanggil ketika mouse dilepas.
        """

        super().__init__(
            master,

            width=self.CARD_WIDTH,
            height=self.CARD_HEIGHT,

            corner_radius=16,

            fg_color=Colors.CARD_BG,

            border_width=1,

            border_color=Colors.BORDER_CARD,
        )

        # ======================================================
        # DATA
        # ======================================================

        self.pdf = pdf

        self.order = order

        # ======================================================
        # CALLBACK
        # ======================================================

        self.on_delete = on_delete

        self.on_drag_start = on_drag_start

        self.on_drag_motion = on_drag_motion

        self.on_drag_end = on_drag_end

        # ======================================================
        # DRAG STATE
        # ======================================================

        #
        # Posisi mouse ketika pertama kali ditekan.
        #

        self._drag_start_x = 0
        self._drag_start_y = 0

        #
        # Posisi cursor relatif terhadap card.
        #
        # Digunakan FileListWidget untuk memposisikan ghost
        # agar tidak loncat ketika drag dimulai.
        #

        self._grab_offset_x = 0
        self._grab_offset_y = 0

        #
        # True hanya ketika drag benar-benar dimulai.
        #

        self._dragging = False

        # ======================================================
        # HOVER STATE
        # ======================================================

        #
        # True ketika mouse berada di area card.
        #

        self._hovered = False

        #
        # ID timer pengecekan mouse keluar.
        #

        self._hover_check_id = None

        # ======================================================
        # BORDER NORMAL
        # ======================================================

        self._normal_border_width = 1

        self._normal_border_color = (
            Colors.BORDER_CARD
        )

        # ======================================================
        # BORDER HOVER
        # ======================================================

        self._hover_border_width = 1

        self._hover_border_color = (
            Colors.PRIMARY
        )

        # ======================================================
        # BORDER DRAG
        # ======================================================

        self._drag_border_width = 2

        self._drag_border_color = (
            Colors.PRIMARY
        )

        # ======================================================
        # UKURAN CARD TETAP
        # ======================================================

        #
        # Jangan biarkan isi thumbnail menentukan ukuran card.
        #

        self.grid_propagate(False)

        # ======================================================
        # GRID
        # ======================================================

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            0,
            weight=1,
        )

        # ======================================================
        # BUILD UI
        # ======================================================

        self.create_widgets()

        # ======================================================
        # ENABLE EVENTS
        # ======================================================

        #
        # Event dipasang setelah seluruh widget selesai dibuat.
        #

        self._bind_drag_events_recursive(
            self
        )

        # ======================================================
        # INITIAL CURSOR
        # ======================================================

        self._set_drag_cursor(
            False
        )

    # ==========================================================
    # UI
    # ==========================================================

    def create_widgets(self):
        """
        Membuat seluruh isi thumbnail card.
        """

        self.create_thumbnail()

        self.create_delete_button()

        self.create_filename()

    # ==========================================================
    # THUMBNAIL
    # ==========================================================

    def create_thumbnail(self):
        """
        Membuat preview halaman pertama PDF.
        """

        image = self._load_pdf_thumbnail()

        # ======================================================
        # THUMBNAIL BERHASIL
        # ======================================================

        if image is not None:

            self.thumbnail_label = ctk.CTkLabel(
                self,

                text="",

                image=image,

                fg_color="transparent",
            )

            #
            # Simpan reference image.
            #

            self.thumbnail_label.image = image

        # ======================================================
        # THUMBNAIL GAGAL
        # ======================================================

        else:

            self.thumbnail_label = ctk.CTkLabel(
                self,

                text="📄",

                font=(
                    "Segoe UI Emoji",
                    54,
                ),

                text_color=Colors.TEXT_PRIMARY,

                fg_color="transparent",
            )

            self.thumbnail_label.image = None

        # ======================================================
        # POSISI THUMBNAIL
        # ======================================================

        self.thumbnail_label.grid(
            row=0,
            column=0,

            padx=15,

            pady=(18, 5),

            sticky="n",
        )

    # ==========================================================
    # DELETE BUTTON
    # ==========================================================

    def create_delete_button(self):
        """
        ==========================================================
        DELETE BUTTON
        ==========================================================

        Tombol X:

            INITIAL
                ↓
            hidden

            HOVER CARD
                ↓
            visible

            HOVER OUT
                ↓
            hidden

        Tombol X tidak menerima event drag.
        """

        self.delete_button = ctk.CTkButton(
            self,

            text="×",

            width=20,
            height=20,

            corner_radius=15,

            # Warna normal tombol
            fg_color=Colors.DANGER,

            # Warna SELURUH tombol ketika hover
            hover_color=Colors.DANGER,

            text_color="white",

            font=(
                "Segoe UI",
                18,
                "bold",
            ),

            # Cursor saat berada di tombol
            cursor="hand2",

            command=self._delete_clicked,
        )

        # ======================================================
        # INITIAL STATE
        # ======================================================

        #
        # Jangan langsung place.
        #
        # Tombol baru muncul ketika hover.
        #

        self.delete_button.place_forget()

    # ==========================================================
    # FILE NAME
    # ==========================================================

    def create_filename(self):
        """
        Menampilkan nama file di bagian bawah card.
        """

        filename = self.pdf.filename

        display_name = self._shorten_filename(
            filename,
            max_length=24,
        )

        self.filename_label = ctk.CTkLabel(
            self,

            text=display_name,

            font=(
                "Segoe UI",
                11,
            ),

            text_color=Colors.TEXT_PRIMARY,

            anchor="center",

            justify="center",

            wraplength=170,
        )

        self.filename_label.grid(
            row=1,
            column=0,

            padx=10,

            pady=(0, 10),

            sticky="ew",
        )

    # ==========================================================
    # LOAD PDF THUMBNAIL
    # ==========================================================

    def _load_pdf_thumbnail(self):
        """
        ==========================================================
        PDF → THUMBNAIL
        ==========================================================

        Alur:

            PDF
             ↓
            PyMuPDF
             ↓
            halaman pertama
             ↓
            render
             ↓
            PIL
             ↓
            resize
             ↓
            CTkImage
        """

        # ======================================================
        # IMPORT FITZ
        # ======================================================

        try:

            import fitz

        except ImportError:

            return None

        # ======================================================
        # PROSES PDF
        # ======================================================

        try:

            from PIL import Image

            path = Path(
                self.pdf.path
            )

            # --------------------------------------------------
            # FILE TIDAK ADA
            # --------------------------------------------------

            if not path.exists():

                return None

            # --------------------------------------------------
            # BUKA PDF
            # --------------------------------------------------

            document = fitz.open(
                str(path)
            )

            # --------------------------------------------------
            # PDF KOSONG
            # --------------------------------------------------

            if document.page_count == 0:

                document.close()

                return None

            # --------------------------------------------------
            # HALAMAN PERTAMA
            # --------------------------------------------------

            page = document.load_page(
                0
            )

            # --------------------------------------------------
            # RENDER
            # --------------------------------------------------

            matrix = fitz.Matrix(
                1.5,
                1.5,
            )

            pixmap = page.get_pixmap(
                matrix=matrix,

                alpha=False,
            )

            # --------------------------------------------------
            # PIL
            # --------------------------------------------------

            image = Image.frombytes(
                "RGB",

                (
                    pixmap.width,
                    pixmap.height,
                ),

                pixmap.samples,
            )

            # --------------------------------------------------
            # CLOSE PDF
            # --------------------------------------------------

            document.close()

            # --------------------------------------------------
            # RESIZE
            # --------------------------------------------------

            image.thumbnail(
                (
                    self.THUMBNAIL_WIDTH,
                    self.THUMBNAIL_HEIGHT,
                ),

                Image.Resampling.LANCZOS,
            )

            # --------------------------------------------------
            # CTK IMAGE
            # --------------------------------------------------

            return ctk.CTkImage(
                light_image=image,

                dark_image=image,

                size=image.size,
            )

        except Exception:

            return None

    # ==========================================================
    # DELETE
    # ==========================================================

    def _delete_clicked(self):
        """
        ==========================================================
        DELETE CLICK
        ==========================================================

        Tombol X ditekan.

        FileItem menyerahkan proses delete ke parent.

        Tombol ini tidak boleh memicu drag.
        """

        if self.on_delete:

            self.on_delete()

    # ==========================================================
    # HOVER ENTER
    # ==========================================================

    def _on_hover_enter(
        self,
        event=None,
    ):
        """
        ==========================================================
        HOVER ENTER
        ==========================================================

        Ketika mouse masuk area FileItem:

            1. Set hovered = True
            2. Tampilkan tombol X
            3. Ubah border
            4. Ubah cursor menjadi fleur
        """

        self._hovered = True

        # ======================================================
        # CANCEL LEAVE TIMER
        # ======================================================

        if self._hover_check_id is not None:

            try:

                self.after_cancel(
                    self._hover_check_id
                )

            except Exception:

                pass

            self._hover_check_id = None

        # ======================================================
        # VISUAL
        # ======================================================

        #
        # Ketika sedang drag, visual drag lebih prioritas.
        #

        if not self._dragging:

            self._set_hover_visual(
                True
            )

    # ==========================================================
    # HOVER LEAVE
    # ==========================================================

    def _on_hover_leave(
        self,
        event=None,
    ):
        """
        ==========================================================
        HOVER LEAVE
        ==========================================================

        Tidak langsung menyembunyikan tombol.

        Kita menunggu sebentar dan mengecek apakah mouse
        benar-benar sudah keluar dari seluruh card.
        """

        # ======================================================
        # CANCEL TIMER LAMA
        # ======================================================

        if self._hover_check_id is not None:

            try:

                self.after_cancel(
                    self._hover_check_id
                )

            except Exception:

                pass

        # ======================================================
        # BUAT TIMER BARU
        # ======================================================

        self._hover_check_id = self.after(
            self.HOVER_LEAVE_DELAY,
            self._check_mouse_outside,
        )

    # ==========================================================
    # CHECK MOUSE OUTSIDE
    # ==========================================================

    def _check_mouse_outside(self):
        """
        Mengecek apakah cursor benar-benar sudah keluar
        dari seluruh area FileItem.
        """

        self._hover_check_id = None

        try:

            # ==================================================
            # POSISI CURSOR
            # ==================================================

            x = self.winfo_pointerx()

            y = self.winfo_pointery()

            # ==================================================
            # POSISI CARD
            # ==================================================

            left = self.winfo_rootx()

            top = self.winfo_rooty()

            right = (
                left
                + self.winfo_width()
            )

            bottom = (
                top
                + self.winfo_height()
            )

            # ==================================================
            # CEK
            # ==================================================

            inside = (
                left <= x <= right
                and
                top <= y <= bottom
            )

            # ==================================================
            # MASIH DI DALAM CARD
            # ==================================================

            if inside:

                self._hovered = True

                if not self._dragging:

                    self._set_hover_visual(
                        True
                    )

            # ==================================================
            # SUDAH KELUAR
            # ==================================================

            else:

                self._hovered = False

                if not self._dragging:

                    self._set_hover_visual(
                        False
                    )

        except Exception:

            pass

    # ==========================================================
    # HOVER VISUAL
    # ==========================================================

    def _set_hover_visual(
        self,
        hovered,
    ):
        """
        ==========================================================
        HOVER VISUAL
        ==========================================================

        Hover ON:

            border  → PRIMARY
            cursor  → fleur
            X       → visible

        Hover OFF:

            border  → normal
            cursor  → arrow
            X       → hidden
        """

        try:

            if hovered:

                # ==================================================
                # BORDER
                # ==================================================

                self.configure(
                    border_width=(
                        self._hover_border_width
                    ),

                    border_color=(
                        self._hover_border_color
                    ),
                )

                # ==================================================
                # DELETE BUTTON
                # ==================================================

                self.delete_button.place(
                    relx=1.0,

                    x=-10,

                    y=10,

                    anchor="ne",
                )

                self.delete_button.lift()

                # ==================================================
                # CURSOR
                # ==================================================

                self._set_drag_cursor(
                    True
                )

            else:

                # ==================================================
                # BORDER
                # ==================================================

                self.configure(
                    border_width=(
                        self._normal_border_width
                    ),

                    border_color=(
                        self._normal_border_color
                    ),
                )

                # ==================================================
                # DELETE BUTTON
                # ==================================================

                self.delete_button.place_forget()

                # ==================================================
                # CURSOR
                # ==================================================

                self._set_drag_cursor(
                    False
                )

        except Exception:

            pass

    # ==========================================================
    # SET DRAG CURSOR
    # ==========================================================

    def _set_drag_cursor(
        self,
        enabled,
    ):
        """
        ==========================================================
        CURSOR
        ==========================================================

        enabled=True:

            fleur

        enabled=False:

            arrow

        Tombol delete mempunyai cursor sendiri:

            hand2
        """

        cursor = (
            "fleur"
            if enabled
            else "arrow"
        )

        widgets = [
            self,

            getattr(
                self,
                "thumbnail_label",
                None,
            ),

            getattr(
                self,
                "filename_label",
                None,
            ),
        ]

        for widget in widgets:

            if widget is None:

                continue

            try:

                widget.configure(
                    cursor=cursor
                )

            except Exception:

                pass

        # ======================================================
        # DELETE BUTTON
        # ======================================================

        try:

            self.delete_button.configure(
                cursor="hand2"
            )

        except Exception:

            pass

    # ==========================================================
    # MOUSE PRESS
    # ==========================================================

    def _drag_press(self, event):
        """
        ==========================================================
        MOUSE PRESS
        ==========================================================


        Hanya menyimpan posisi mouse awal.

        Posisi ini akan digunakan oleh FileListWidget
        untuk menghitung perpindahan ghost.

    
        """

        # ======================================================
        # POSISI MOUSE GLOBAL
        # ======================================================

        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

        # ======================================================
        # RESET DRAG
        # ======================================================

        self._dragging = False

        # ======================================================
        # HOVER
        # ======================================================

        self._hovered = True

        self._set_drag_cursor(
            True
        )


    # ==========================================================
    # MOUSE MOTION
    # ==========================================================

    def _drag_motion(
        self,
        event,
    ):
        """
        ==========================================================
        MOUSE MOTION
        ==========================================================

        Method ini adalah sumber utama event drag.

        Flow:

            Mouse bergerak
                 ↓
            hitung jarak
                 ↓
            threshold tercapai?
                 ↓
               Ya
                 ↓
            aktifkan drag
                 ↓
            panggil on_drag_start()
                 ↓
            panggil on_drag_motion()
        """

        # ======================================================
        # HITUNG PERGERAKAN
        # ======================================================

        dx = abs(
            event.x_root
            - self._drag_start_x
        )

        dy = abs(
            event.y_root
            - self._drag_start_y
        )

        # ======================================================
        # BELUM DRAG
        # ======================================================

        if not self._dragging:

            # --------------------------------------------------
            # BELUM MELEWATI THRESHOLD
            # --------------------------------------------------

            if (
                dx < self.DRAG_THRESHOLD
                and
                dy < self.DRAG_THRESHOLD
            ):

                return

            # --------------------------------------------------
            # RESMI MENJADI DRAG
            # --------------------------------------------------

            self._dragging = True

            # --------------------------------------------------
            # VISUAL DRAG
            # --------------------------------------------------

            self._set_drag_visual(
                True
            )

            # --------------------------------------------------
            # CALLBACK START
            # --------------------------------------------------

            if self.on_drag_start:

                self.on_drag_start(
                    self,
                    event,
                )

        # ======================================================
        # SELAMA DRAG
        # ======================================================

        if self._dragging:

            if self.on_drag_motion:

                #
                # Callback penting.
                #
                # FileListWidget menggunakan event ini untuk:
                #
                #   1. menggerakkan ghost
                #   2. mencari target
                #   3. menggeser thumbnail
                #

                self.on_drag_motion(
                    self,
                    event,
                )

    # ==========================================================
    # MOUSE RELEASE
    # ==========================================================

    def _drag_release(
        self,
        event,
    ):
        """
        ==========================================================
        MOUSE RELEASE
        ==========================================================

        Jika benar-benar drag:

            on_drag_end()

        Jika hanya klik:

            tidak melakukan apa-apa.
        """

        # ======================================================
        # JIKA DRAG
        # ======================================================

        if self._dragging:

            if self.on_drag_end:

                self.on_drag_end(
                    self,
                    event,
                )

        # ======================================================
        # RESET DRAG
        # ======================================================

        self._dragging = False

        # ======================================================
        # RESET VISUAL
        # ======================================================

        self._set_drag_visual(
            False
        )

    # ==========================================================
    # DRAG VISUAL
    # ==========================================================

    def _set_drag_visual(
        self,
        dragging,
    ):
        """
        ==========================================================
        DRAG VISUAL
        ==========================================================

        DRAGGING:

            border  = PRIMARY
            width   = 2
            cursor  = fleur
            X       = visible

        SELESAI:

            jika mouse masih berada di card:

                gunakan hover visual

            jika mouse sudah keluar:

                gunakan normal visual
        """

        try:

            # ==================================================
            # DRAG ON
            # ==================================================

            if dragging:

                self.configure(
                    border_width=(
                        self._drag_border_width
                    ),

                    border_color=(
                        self._drag_border_color
                    ),
                )

                # --------------------------------------------------
                # TOMBOL X TETAP TERLIHAT
                # --------------------------------------------------

                self.delete_button.place(
                    relx=1.0,

                    x=-10,

                    y=10,

                    anchor="ne",
                )

                self.delete_button.lift()

                # --------------------------------------------------
                # CURSOR
                # --------------------------------------------------

                self._set_drag_cursor(
                    True
                )

                return

            # ==================================================
            # DRAG OFF
            # ==================================================

            #
            # Setelah drag selesai, kita cek apakah cursor
            # masih berada di card.
            #

            try:

                x = self.winfo_pointerx()

                y = self.winfo_pointery()

                left = self.winfo_rootx()

                top = self.winfo_rooty()

                right = (
                    left
                    + self.winfo_width()
                )

                bottom = (
                    top
                    + self.winfo_height()
                )

                still_inside = (
                    left <= x <= right
                    and
                    top <= y <= bottom
                )

            except Exception:

                still_inside = False

            # ==================================================
            # MASIH HOVER
            # ==================================================

            if still_inside:

                self._hovered = True

                self._set_hover_visual(
                    True
                )

            # ==================================================
            # SUDAH KELUAR
            # ==================================================

            else:

                self._hovered = False

                self._set_hover_visual(
                    False
                )

        except Exception:

            pass

    # ==========================================================
    # BIND EVENT
    # ==========================================================

    def _bind_drag_events_recursive(
        self,
        widget,
    ):
        """
        ==========================================================
        BIND EVENT
        ==========================================================

        Event dipasang ke seluruh area card:

            FileItem
            ├── Thumbnail
            ├── Filename
            └── Delete Button

        Tetapi tombol Delete Button:

            ✓ hover
            ✓ cursor hand2

            ✗ drag
        """

        # ======================================================
        # HOVER EVENTS
        # ======================================================

        #
        # Hover dipasang ke semua widget.
        #
        # Dengan demikian ketika mouse berada pada thumbnail,
        # filename, atau area tombol, state hover tetap aktif.
        #

        widget.bind(
            "<Enter>",
            self._on_hover_enter,
            add="+",
        )

        widget.bind(
            "<Leave>",
            self._on_hover_leave,
            add="+",
        )

        # ======================================================
        # DRAG EVENTS
        # ======================================================

        #
        # Delete button dikecualikan dari drag.
        #

        if widget is not self.delete_button:

            # --------------------------------------------------
            # PRESS
            # --------------------------------------------------

            widget.bind(
                "<ButtonPress-1>",
                self._drag_press,
                add="+",
            )

            # --------------------------------------------------
            # MOTION
            # --------------------------------------------------

            widget.bind(
                "<B1-Motion>",
                self._drag_motion,
                add="+",
            )

            # --------------------------------------------------
            # RELEASE
            # --------------------------------------------------

            widget.bind(
                "<ButtonRelease-1>",
                self._drag_release,
                add="+",
            )

        # ======================================================
        # CHILDREN
        # ======================================================

        for child in widget.winfo_children():

            self._bind_drag_events_recursive(
                child
            )

    # ==========================================================
    # HELPER
    # ==========================================================

    @staticmethod
    def _shorten_filename(
        filename,
        max_length=24,
    ):
        """
        ==========================================================
        SHORTEN FILENAME
        ==========================================================

        Contoh:

            dokumen_perjanjian_pln_2026.pdf

        menjadi:

            dokumen_perjanj...pdf
        """

        # ------------------------------------------------------
        # TIDAK PERLU DIPOTONG
        # ------------------------------------------------------

        if len(filename) <= max_length:

            return filename

        # ------------------------------------------------------
        # AMBIL EXTENSION
        # ------------------------------------------------------

        path = Path(
            filename
        )

        suffix = path.suffix

        # ------------------------------------------------------
        # HITUNG RUANG
        # ------------------------------------------------------

        available = (
            max_length
            - len(suffix)
            - 3
        )

        # ------------------------------------------------------
        # SAFETY
        # ------------------------------------------------------

        if available < 1:

            return filename[
                :max_length
            ]

        # ------------------------------------------------------
        # GABUNG
        # ------------------------------------------------------

        return (
            filename[:available]
            + "..."
            + suffix
        )

    # ==========================================================
    # UPDATE ORDER
    # ==========================================================

    def update_order(
        self,
        order,
    ):
        """
        Mengubah nomor urutan internal FileItem.
        """

        self.order = order