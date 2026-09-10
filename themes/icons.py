from pathlib import Path
from PIL import Image
import customtkinter as ctk

BASE_DIR = Path(__file__).resolve().parent.parent
ICONS_DIR = BASE_DIR / "assets" / "icons"
LOGO_DIR = BASE_DIR / "assets" / "logo"


def load_icon(filename, size=(20, 20)):
    image = Image.open(ICONS_DIR / filename)
    return ctk.CTkImage(
        light_image=image,
        dark_image=image,
        size=size
    )


def load_icon_logo(filename, size=(60, 60)):
    image = Image.open(ICONS_DIR / filename)
    return ctk.CTkImage(
        light_image=image,
        dark_image=image,
        size=size
    )


def load_logo(filename, size=(150, 150)):
    image = Image.open(LOGO_DIR / filename)
    return ctk.CTkImage(
        light_image=image,
        dark_image=image,
        size=size
    )



class Icons:

    DASHBOARD = load_icon("dashboard.png")

    MERGE = load_icon("merge.png")

    SPLIT = load_icon("split.png")

    EXCEL = load_icon("excel.png")

    COMPRESS = load_icon("compress.png")

    ROTATE = load_icon("rotate.png")

    PIUTANG = load_icon("piutang.png")

    BULOG = load_icon("bulog.png")

    ADMIN = load_icon("admin.png")

    SETTINGS = load_icon("settings.png")

    ABOUT = load_icon("about.png")

    MERGE_LOGO = load_icon_logo("merge_logo.png")

    PIUTANG_LOGO = load_icon_logo("piutang.png")

    TUL_LOGO = load_icon_logo("excel.png")

    SPLIT_LOGO = load_icon_logo("split.png")

    EXCEL_EMPTY = load_logo("excel_logo.png")

    PDF_EMPTY = load_logo("pdf.png")

    BULOG_LOGO = load_icon_logo("verify.png")