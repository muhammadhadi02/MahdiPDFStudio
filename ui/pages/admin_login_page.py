import customtkinter as ctk

from themes.colors import Colors
from themes.spacing import Spacing
from core.services.supabase_service import SupabaseService


class AdminLoginPage(ctk.CTkFrame):

    def __init__(
        self,
        master,
        navigation=None,
        status_bar=None
    ):
        super().__init__(
            master,
            fg_color=Colors.WORKSPACE_BG,
            corner_radius=Spacing.CARD_RADIUS
        )

        self.navigation = navigation
        self.status_bar = status_bar

        self.create_widgets()

    # ==================================================
    # BUILD UI
    # ==================================================

    def create_widgets(self):

        # ==================================================
        # HEADER
        # ==================================================

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=25,
            pady=(20, 10)
        )

        title = ctk.CTkLabel(
            header,
            text="Login Admin",
            font=("Segoe UI", 24, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        title.pack(
            anchor="w"
        )

        subtitle = ctk.CTkLabel(
            header,
            text="Masuk ke panel administrasi.",
            font=("Segoe UI", 13),
            text_color=Colors.TEXT_SECONDARY
        )

        subtitle.pack(
            anchor="w",
            pady=(4, 0)
        )

        # ==================================================
        # LOGIN CARD
        # ==================================================

        card = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=20,
            border_width=1,
            border_color=Colors.BORDER
        )

        card.pack(
            fill="x",
            padx=25,
            pady=20
        )

        form = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        form.pack(
            padx=40,
            pady=40
        )

        # ==================================================
        # EMAIL
        # ==================================================

        email_label = ctk.CTkLabel(
            form,
            text="Email",
            font=("Segoe UI", 13, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        email_label.pack(
            anchor="w",
            pady=(0, 6)
        )

        self.email_entry = ctk.CTkEntry(
            form,
            width=420,
            height=44,
            placeholder_text="Masukkan email admin"
        )

        self.email_entry.pack(
            fill="x",
            pady=(0, 20)
        )

        # ==================================================
        # PASSWORD
        # ==================================================

        password_label = ctk.CTkLabel(
            form,
            text="Password",
            font=("Segoe UI", 13, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        password_label.pack(
            anchor="w",
            pady=(0, 6)
        )

        self.password_entry = ctk.CTkEntry(
            form,
            width=420,
            height=44,
            placeholder_text="Masukkan password",
            show="*"
        )

        self.password_entry.pack(
            fill="x",
            pady=(0, 20)
        )

        # ==================================================
        # LOGIN BUTTON
        # ==================================================

        self.login_button = ctk.CTkButton(
            form,
            text="Login",
            width=420,
            height=44,
            command=self.login
        )

        self.login_button.pack(
            fill="x"
        )

        # ==================================================
        # STATUS
        # ==================================================

        self.status_label = ctk.CTkLabel(
            form,
            text="",
            font=("Segoe UI", 12),
            text_color=Colors.TEXT_SECONDARY
        )

        self.status_label.pack(
            pady=(15, 0)
        )

        # ==================================================
        # ENTER = LOGIN
        # ==================================================

        self.password_entry.bind(
            "<Return>",
            lambda event: self.login()
        )

        # Fokus awal ke email
        self.email_entry.focus()

    # ==================================================
    # LOGIN
    # ==================================================

    def login(self):

        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        # ==================================================
        # VALIDASI INPUT
        # ==================================================

        if not email or not password:

            self.status_label.configure(
                text="Email dan password wajib diisi.",
                text_color="#DC2626"
            )

            return

        # ==================================================
        # DISABLE BUTTON
        # ==================================================

        self.login_button.configure(
            state="disabled",
            text="Memproses..."
        )

        self.status_label.configure(
            text="Memverifikasi akun...",
            text_color=Colors.TEXT_SECONDARY
        )

        try:

            # ==================================================
            # SUPABASE AUTHENTICATION
            # ==================================================

            result = SupabaseService.login(
                email,
                password
            )

            # ==================================================
            # PASTIKAN LOGIN MENGHASILKAN USER
            # ==================================================

            if not result or not result.user:

                self.status_label.configure(
                    text="Login gagal.",
                    text_color="#DC2626"
                )

                return

            # ==================================================
            # CEK ROLE ADMIN
            # ==================================================

            is_admin = SupabaseService.is_admin()

            if not is_admin:

                # Logout kembali karena akun bukan admin
                SupabaseService.logout()

                self.status_label.configure(
                    text="Akun berhasil login, tetapi bukan Admin.",
                    text_color="#DC2626"
                )

                print(
                    "Login ditolak: akun bukan Admin."
                )

                return

            # ==================================================
            # LOGIN ADMIN BERHASIL
            # ==================================================

            self.status_label.configure(
                text="Login Admin berhasil.",
                text_color="#16A34A"
            )

            print(
                "Admin login berhasil:",
                result.user.email
            )

            # ==================================================
            # TAHAP SELANJUTNYA
            # ==================================================
            #
            # ==================================================
            # PINDAH KE ADMIN PANEL
            # ==================================================

            if self.navigation:
                self.navigation.navigate("admin_panel")

        except Exception as error:

            print(
                "Admin login gagal:",
                error
            )

            self.status_label.configure(
                text="Login gagal. Periksa email dan password.",
                text_color="#DC2626"
            )

        finally:

            self.login_button.configure(
                state="normal",
                text="Login"
            )