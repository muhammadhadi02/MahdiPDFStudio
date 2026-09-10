import customtkinter as ctk
import threading
import urllib.request

from themes.colors import Colors


class StatusBar(ctk.CTkFrame):

    CHECK_INTERVAL = 15000  # 15 detik

    def __init__(self, master):
        super().__init__(
            master,
            height=35,
            fg_color=Colors.CARD_BG
        )

        self.grid_propagate(False)

        # ==================================================
        # Status aplikasi
        # ==================================================

        self.label = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
            text_color=Colors.TEXT_SECONDARY
        )

        self.label.pack(
            side="left",
            fill="y",
            padx=10
        )

        # ==================================================
        # Status Internet
        # ==================================================

        self.connection_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.connection_frame.pack(
            side="right",
            fill="y",
            padx=12
        )

        self.connection_dot = ctk.CTkLabel(
            self.connection_frame,
            text="●",
            font=ctk.CTkFont(size=13),
            text_color="#9CA3AF"
        )

        self.connection_dot.pack(
            side="left",
            padx=(0, 5)
        )

        self.connection_label = ctk.CTkLabel(
            self.connection_frame,
            text="Checking...",
            font=ctk.CTkFont(size=12),
            text_color=Colors.TEXT_SECONDARY
        )

        self.connection_label.pack(
            side="left"
        )

        # ==================================================
        # Background checker
        # ==================================================

        self._stop_event = threading.Event()

        self._check_connection()

    # ======================================================
    # Internet Connection
    # ======================================================

    def _check_connection(self):

        thread = threading.Thread(
            target=self._connection_worker,
            daemon=True
        )

        thread.start()

        self.after(
            self.CHECK_INTERVAL,
            self._check_connection
        )

    def _connection_worker(self):

        online = False

        try:
            urllib.request.urlopen(
                "https://www.google.com/generate_204",
                timeout=3
            )

            online = True

        except Exception:
            online = False

        # Jangan update Tkinter langsung dari thread.
        self.after(
            0,
            lambda: self._update_connection_status(online)
        )

    def _update_connection_status(self, online):

        if online:

            self.connection_dot.configure(
                text_color="#22C55E"
            )

            self.connection_label.configure(
                text="Internet Terhubung",
                text_color="#16A34A"
            )

        else:

            self.connection_dot.configure(
                text_color="#9CA3AF"
            )

            self.connection_label.configure(
                text="Internet Tidak Terhubung",
                text_color="#6B7280"
            )

    # ======================================================
    # Application Status
    # ======================================================

    def set_status(self, message):

        self.label.configure(
            text=message
        )

    # ======================================================
    # Cleanup
    # ======================================================

    def destroy(self):

        self._stop_event.set()

        super().destroy()