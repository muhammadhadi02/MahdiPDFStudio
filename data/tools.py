"""
==========================================================
Mahdi PDF Studio
Tool Registry
==========================================================

Berisi daftar seluruh tool yang akan
ditampilkan pada Dashboard.

Author : Muhammad Hadi Putra
"""

from data.models.tool_info import ToolInfo
from themes.fonts   import Fonts
from themes.colors   import Colors

TOOLS = [

    ToolInfo(

        id="merge",

        icon="merge",

        title="Merge PDF",

        description="Gabungkan beberapa file PDF.",

        page="merge"

    ),

    ToolInfo(

        id="split",

        icon="split",

        title="Split PDF",

        description="Pisahkan halaman PDF.",

        page="split"

    ),

    ToolInfo(

        id="tul309",

        icon="excel",

        title="TUL 309",

        description="Gabungkan file Excel TUL 309",

        page="tul309"

    ),

    ToolInfo(

        id="monev_piutang",

        icon="piutang",

        title="Monev Piutang",

        description="Gabungkan file Excel Piutang",

        page="monev_piutang"

    ),

    ToolInfo(

        id="verifikasi_banpang",

        icon="bulog",

        title="Verifikasi Banpang",

        description="Otomatisasi pengambilan dan verifikasi data Banpang",

        page="verifikasi_banpang"

    )

]