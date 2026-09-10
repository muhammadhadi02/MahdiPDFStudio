import ctypes


class WindowStyle:

    DWMWA_CAPTION_COLOR = 35
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_WINDOW_CORNER_PREFERENCE = 33

    @staticmethod
    def apply_fluent_style(window):

        hwnd = window.winfo_id()

        # ====================================
        # Caption Color
        # #ECF2FE
        # BGR format
        # ====================================

        caption_color = ctypes.c_int(
            0xFEF2EC
        )

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            WindowStyle.DWMWA_CAPTION_COLOR,
            ctypes.byref(caption_color),
            ctypes.sizeof(caption_color)
        )

        # ====================================
        # Rounded Corner
        # ====================================

        corner = ctypes.c_int(2)

        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            WindowStyle.DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(corner),
            ctypes.sizeof(corner)
        )