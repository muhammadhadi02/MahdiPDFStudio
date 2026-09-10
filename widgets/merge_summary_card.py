"""
==========================================================
Mahdi PDF Studio
Merge Summary Card
==========================================================

Widget ringkasan untuk fitur Merge PDF.

Digunakan Oleh
--------------

✓ Merge PDF

Menampilkan
------------

✓ Total File
✓ Total Halaman
✓ Total Ukuran

Tidak Bertanggung Jawab
-----------------------

✗ Memilih file
✗ Membaca PDF
✗ Merge PDF

Widget ini hanya menampilkan
ringkasan data yang diberikan
oleh MergePage.

==========================================================
"""

import customtkinter as ctk
from themes.colors import Colors


class MergeSummaryCard(ctk.CTkFrame):
    """
    Ringkasan statistik Merge PDF.
    """

    def __init__(
        self,
        master
    ):
        super().__init__(
            master,
            width=220,
            height=140,
            corner_radius=12
        )

        self.pack_propagate(False)

        self.create_widgets()

        self.configure(
            fg_color=Colors.CARD_BG,
            border_width=1,
            border_color=Colors.BORDER
        )

    # ==================================================
    # Build UI
    # ==================================================

    def create_widgets(self):

        title = ctk.CTkLabel(
            self,
            text="📊 Ringkasan",
            font=("Segoe UI", 15, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        title.pack(
            anchor="w",
            padx=15,
            pady=(10,6)
        )

        self.files_label = ctk.CTkLabel(
            self,
            text="Total File : 0",
            text_color=Colors.TEXT_SECONDARY
        )

        self.files_label.pack(
            anchor="w",
            padx=15,
            pady=(0,4)
        )

        self.pages_label = ctk.CTkLabel(
            self,
            text="Total Halaman : 0",
            text_color=Colors.TEXT_SECONDARY
        )

        self.pages_label.pack(
            anchor="w",
            padx=15,
            pady=(0,4)
        )

        self.size_label = ctk.CTkLabel(
            self,
            text="Total Ukuran : 0 MB",
            text_color=Colors.TEXT_SECONDARY
        )

        self.size_label.pack(
            anchor="w",
            padx=15,
            pady=(0,4)
        )

    # ==================================================
    # Update Summary
    # ==================================================

    def update_summary(
        self,
        files_count,
        total_pages,
        total_size_mb
    ):
        """
        Update statistik merge.
        """

        self.files_label.configure(
            text=f"Total File : {files_count}"
        )

        self.pages_label.configure(
            text=f"Total Halaman : {total_pages}"
        )

        self.size_label.configure(
            text=f"Total Ukuran : {total_size_mb:.2f} MB"
        )

    # ==================================================
    # Reset Summary
    # ==================================================

    def reset(self):

        self.update_summary(
            0,
            0,
            0
        )