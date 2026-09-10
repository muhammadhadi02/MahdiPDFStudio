"""
==========================================================
Mahdi PDF Studio
TkinterDnD Backend
==========================================================

Backend teknis untuk native Drag & Drop.

CATATAN PENTING
---------------
Aplikasi Mahdi PDF Studio saat ini menggunakan:

    customtkinter.CTk

sebagai root window.

Karena itu kita TIDAK memaksa root aplikasi berubah menjadi
TkinterDnD.Tk. Sebagai gantinya, modul tkinterdnd2 di-load ke
Tk interpreter yang sudah dibuat oleh CustomTkinter menggunakan:

    TkinterDnD._require(root)

Setelah modul TkDnD berhasil di-load, method DnD yang disediakan
tkinterdnd2 dapat digunakan oleh widget CustomTkinter.

"""

from pathlib import Path


class TkinterDnDBackend:
    """
    Backend paling bawah untuk Drag & Drop.

    Tanggung jawab kelas ini hanya:
        1. Memuat library native tkdnd.
        2. Mendaftarkan widget sebagai drop target.
        3. Menerima event Drop.
        4. Mengubah event.data menjadi list path.
        5. Mengirim list path ke callback.
        6. Memberikan feedback visual saat drag masuk/keluar.

    Kelas ini TIDAK mengetahui:
        - PDF
        - PdfFile
        - MergePage
        - PdfMergeService

    Dengan demikian backend tetap reusable untuk fitur lain.
    """

    def __init__(self, widget, callback):
        # Widget yang akan menerima file drop.
        self.widget = widget

        # Callback akan dipanggil setelah file berhasil di-drop.
        # Contoh:
        #     callback(["C:/a.pdf", "C:/b.pdf"])
        self.callback = callback

        # Menandakan apakah widget sudah terdaftar sebagai
        # drop target.
        self._registered = False

    # ==========================================================
    # LOAD TKDND
    # ==========================================================

    @staticmethod
    def _ensure_tkdnd_loaded(widget):
        """
        Memuat extension native tkdnd ke root Tk yang sudah ada.

        Kenapa method ini penting?
        --------------------------
        Error yang muncul sebelumnya:

            invalid command name "tkdnd::drop_target"

        berarti Python mengenal method:

            drop_target_register()

        tetapi extension native Tcl:

            tkdnd

        belum dimuat ke interpreter Tk.

        tkinterdnd2 menyediakan fungsi internal _require()
        untuk melakukan proses tersebut.

        Kita mengambil root dari widget dengan:

            widget.winfo_toplevel()

        sehingga tidak perlu mengganti root CustomTkinter aplikasi.
        """

        try:
            # Import modul utama tkinterdnd2.
            from tkinterdnd2 import TkinterDnD
        except ImportError as exc:
            raise RuntimeError(
                "Library tkinterdnd2 belum terpasang.\n\n"
                "Install dengan:\n"
                "python -m pip install tkinterdnd2"
            ) from exc

        # Ambil root window yang sebenarnya.
        root = widget.winfo_toplevel()

        # Kita simpan flag sendiri supaya _require() tidak dipanggil
        # berulang kali untuk setiap FileItem.
        if getattr(root, "_mahdi_tkdnd_loaded", False):
            return

        try:
            # _require() melakukan:
            #   1. mencari folder tkdnd sesuai OS
            #   2. menambahkan folder tersebut ke auto_path
            #   3. menjalankan "package require tkdnd"
            #
            # Inilah langkah yang sebelumnya belum dilakukan.
            version = TkinterDnD._require(root)

            # Simpan status sukses pada root.
            root._mahdi_tkdnd_loaded = True
            root._mahdi_tkdnd_version = version

        except Exception as exc:
            raise RuntimeError(
                "tkdnd gagal dimuat ke Tk interpreter.\n\n"
                f"Detail: {exc}"
            ) from exc

    # ==========================================================
    # REGISTER
    # ==========================================================

    def register(self):
        """
        Mengaktifkan Drag & Drop pada widget.

        Urutannya:

            widget
              ↓
        load tkdnd extension
              ↓
        register DND_Files
              ↓
        bind event Drop
              ↓
        widget siap menerima file
        """

        try:
            # DND_FILES adalah tipe data standar tkinterdnd2
            # untuk file yang di-drag dari Windows Explorer.
            from tkinterdnd2 import DND_FILES

            # Pastikan extension native tkdnd sudah aktif.
            self._ensure_tkdnd_loaded(self.widget)

            # Setelah import tkinterdnd2, DnDWrapper memasang
            # method DnD ke BaseWidget Tkinter.
            if not hasattr(self.widget, "drop_target_register"):
                raise RuntimeError(
                    "Widget belum memiliki dukungan Drag & Drop."
                )

            # Daftarkan widget sebagai target file.
            self.widget.drop_target_register(DND_FILES)

            # Event saat file benar-benar dilepas.
            self.widget.dnd_bind(
                "<<Drop>>",
                self._on_drop
            )

            # Event saat cursor/file masuk ke area target.
            self.widget.dnd_bind(
                "<<DropEnter>>",
                self._on_drag_enter
            )

            # Event saat cursor/file keluar dari area target.
            self.widget.dnd_bind(
                "<<DropLeave>>",
                self._on_drag_leave
            )

            self._registered = True

        except Exception as exc:
            self._registered = False

            # Ubah semua error DnD menjadi RuntimeError agar
            # DragDropManager dapat menangani kegagalan tanpa
            # membuat halaman Merge crash.
            if isinstance(exc, RuntimeError):
                raise

            raise RuntimeError(
                f"Gagal mengaktifkan Drag & Drop: {exc}"
            ) from exc

    # ==========================================================
    # UNREGISTER
    # ==========================================================

    def unregister(self):
        """
        Melepas widget dari Drag & Drop.

        Ini penting karena FileListWidget sering melakukan refresh:

            FileItem lama
                 ↓
              destroy
                 ↓
            FileItem baru

        Binding DnD lama harus dilepas terlebih dahulu.
        """

        if not self._registered:
            return

        # Lepaskan binding event.
        try:
            self.widget.dnd_bind("<<Drop>>", "")
            self.widget.dnd_bind("<<DropEnter>>", "")
            self.widget.dnd_bind("<<DropLeave>>", "")
        except Exception:
            pass

        # Lepaskan widget dari daftar drop target tkdnd.
        try:
            self.widget.drop_target_unregister()
        except Exception:
            pass

        self._registered = False

    # ==========================================================
    # DROP EVENT
    # ==========================================================

    def _on_drop(self, event):
        """
        Dipanggil ketika user melepaskan file pada widget.

        event.data dari tkinterdnd2 bukan list Python biasa.
        Contohnya dapat terlihat seperti:

            {C:/Data PDF/Laporan Januari.pdf}
            {C:/Data PDF/Laporan Februari.pdf}

        Karena path bisa mengandung spasi, kita tidak boleh
        menggunakan:

            event.data.split(" ")

        """

        paths = self._parse_drop_data(event.data)

        if paths and self.callback:
            # Kirim hasil parsing ke layer berikutnya.
            self.callback(paths)

        # Memberitahu TkDnD bahwa event sudah ditangani.
        return "break"

    # ==========================================================
    # DRAG ENTER
    # ==========================================================

    def _on_drag_enter(self, event):
        """
        Feedback visual ketika file masuk ke area drop.

        Border diubah menjadi warna primary supaya user tahu
        bahwa area tersebut menerima file.
        """

        try:
            from themes.colors import Colors

            self.widget.configure(
                border_color=Colors.PRIMARY
            )
        except Exception:
            # Feedback visual tidak boleh membuat DnD gagal.
            pass

        return "copy"

    # ==========================================================
    # DRAG LEAVE
    # ==========================================================

    def _on_drag_leave(self, event):
        """
        Mengembalikan border ke warna normal ketika file keluar.
        """

        try:
            from themes.colors import Colors

            self.widget.configure(
                border_color=Colors.BORDER_HERO
            )
        except Exception:
            pass

        return "copy"

    # ==========================================================
    # PARSE DROP DATA
    # ==========================================================

    @staticmethod
    def _parse_drop_data(data):
        """
        Mengubah event.data menjadi list path Python.

        Contoh:

            input:
                {C:/Data PDF/A.pdf} {C:/Data PDF/B.pdf}

            output:
                [
                    "C:/Data PDF/A.pdf",
                    "C:/Data PDF/B.pdf"
                ]

        Kita menggunakan tk.splitlist(), bukan split(" "),
        karena Tcl sudah memahami aturan quoting/path Windows.
        """

        if not data:
            return []

        raw = str(data).strip()

        if not raw:
            return []

        try:
            # tkinter._default_root biasanya menunjuk root aplikasi.
            import tkinter

            root = tkinter._default_root

            if root is not None:
                items = root.tk.splitlist(raw)
            else:
                items = (raw,)

        except Exception:
            # Fallback sederhana jika Tcl list parser tidak tersedia.
            items = (raw,)

        # Normalisasi setiap path menjadi string.
        return [
            str(Path(item))
            for item in items
            if str(item).strip()
        ]

    # ==========================================================
    # DESTROY
    # ==========================================================

    def destroy(self):
        """
        Alias sederhana agar manager dapat memanggil cleanup.
        """

        self.unregister()
