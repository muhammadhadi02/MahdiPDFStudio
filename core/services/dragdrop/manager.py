"""
==========================================================
Mahdi PDF Studio
DragDropManager
==========================================================

Manager untuk mengelola beberapa widget sebagai drop target.
"""

from .tkinterdnd_backend import TkinterDnDBackend


class DragDropManager:
    """
    Mengelola banyak widget yang menerima Drag & Drop.

    Contoh pada Merge PDF:

        FileListWidget
             │
             ├── Empty State
             ├── FileItem 1
             ├── FileItem 2
             └── FileItem 3

    Semua widget tersebut dapat menjadi drop target.

    Manager menyimpan backend masing-masing widget agar:
        - mudah register
        - mudah unregister
        - mudah cleanup
    """

    def __init__(self, widget=None, callback=None):
        # Callback utama ketika file dijatuhkan.
        self.callback = callback

        # Satu widget mempunyai satu backend.
        self.backends = []

        # Status global apakah DnD berhasil diaktifkan.
        self.available = True

        # Jika widget diberikan saat constructor,
        # langsung daftarkan sebagai target.
        if widget is not None:
            self.register(widget)

    # ==========================================================
    # REGISTER
    # ==========================================================

    def register(self, widget):
        """
        Mendaftarkan widget baru sebagai drop target.

        Jika DnD gagal:
            - aplikasi TIDAK crash
            - File Dialog tetap dapat digunakan
            - available menjadi False
        """

        # Hindari widget yang sama didaftarkan berkali-kali.
        for backend in self.backends:
            if backend.widget is widget:
                return backend

        backend = TkinterDnDBackend(
            widget=widget,
            callback=self.callback
        )

        try:
            backend.register()

        except RuntimeError as exc:
            # Drag & Drop adalah fitur tambahan.
            # Jangan biarkan kegagalannya menghentikan aplikasi.
            #
            # Ini juga melindungi MergePage dari error seperti:
            #   invalid command name "tkdnd::drop_target"
            self.available = False

            print(
                "[DragDropManager] "
                f"Drag & Drop tidak aktif: {exc}"
            )

            return None

        # Jika berhasil, simpan backend.
        self.backends.append(backend)
        self.available = True

        return backend

    # ==========================================================
    # UNREGISTER ALL
    # ==========================================================

    def unregister_all(self):
        """
        Melepas seluruh widget dari DnD.

        Dipanggil ketika FileListWidget melakukan refresh.
        """

        for backend in self.backends:
            backend.unregister()

        self.backends.clear()

    # ==========================================================
    # DESTROY
    # ==========================================================

    def destroy(self):
        """
        Membersihkan seluruh binding sebelum manager dihancurkan.
        """

        self.unregister_all()
