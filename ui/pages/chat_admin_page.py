"""
==========================================================
Mahdi PDF Studio
Chat Admin Page
==========================================================

Halaman komunikasi antara User dan Admin.

USER BIASA
----------
Nama + No. HP
      ↓
Mulai Chat
      ↓
Conversation
      ↓
Chat dengan Admin

ADMIN
-----
Login Admin menggunakan Supabase Authentication.

Catatan:
- User biasa TIDAK menggunakan login Supabase.
- Identitas user disimpan melalui conversation.
- conversation_id dan access_token digunakan
  untuk mengakses percakapan.
==========================================================
"""

import customtkinter as ctk
from core.services.chat_session import ChatSession
from core.services.secure_storage import SecureStorage
from core.services.device_session import DeviceSession
from core.services.supabase_service import SupabaseService
import threading
import asyncio

from core.services.realtime_service import RealtimeService

from themes.colors import Colors
from themes.spacing import Spacing


class ChatAdminPage(ctk.CTkFrame):

    def __init__(
        self,
        master,
        status_bar=None
    ):
        super().__init__(
            master,
            fg_color=Colors.WORKSPACE_BG,
            corner_radius=Spacing.CARD_RADIUS
        )

        self.status_bar = status_bar

        # ==================================================
        # Conversation State
        # ==================================================

        self.conversation_id = None
        self.access_token = None

        # ==================================================
        # Realtime State
        # ==================================================

        self.realtime_service = None
        self.realtime_thread = None
        self.realtime_loop = None

        self.user_name = ""
        self.user_phone = ""

        # ==================================================
        # Restore Previous Chat Session
        # ==================================================

        self.restore_session()

    # ==================================================
    # RESTORE SESSION
    # ==================================================

    def restore_session(self):

        session = ChatSession.load_session()

        if not session:
            self.create_start_ui()
            return

        conversation_id = session.get(
            "conversation_id"
        )

        user_name = session.get(
            "user_name",
            ""
        )

        user_phone = session.get(
            "user_phone",
            ""
        )

        access_token = (
            SecureStorage.load_access_token()
        )

        device_id = DeviceSession.get_device_id()

        if not conversation_id or not access_token:

            ChatSession.clear_session()
            SecureStorage.clear_access_token()

            self.create_start_ui()

            return

        try:

            is_valid = (
                SupabaseService
                .validate_conversation_session(
                    conversation_id=conversation_id,
                    access_token=access_token,
                    device_id=device_id
                )
            )

            if not is_valid:

                ChatSession.clear_session()
                SecureStorage.clear_access_token()

                self.create_start_ui()

                return

        except Exception as error:

            print(
                "Gagal memvalidasi Chat Session:",
                error
            )

            ChatSession.clear_session()
            SecureStorage.clear_access_token()

            self.create_start_ui()

            return

        self.conversation_id = conversation_id
        self.access_token = access_token

        self.user_name = user_name
        self.user_phone = user_phone

        self.create_chat_ui()

    # ==================================================
    # START UI
    # ==================================================

    def create_start_ui(self):

        container = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=20,
            border_width=1,
            border_color=Colors.BORDER
        )

        container.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        # ==================================================
        # Title
        # ==================================================

        title = ctk.CTkLabel(
            container,
            text="Chat Admin",
            font=("Segoe UI", 24, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        title.pack(
            padx=60,
            pady=(35, 8)
        )

        # ==================================================
        # Subtitle
        # ==================================================

        subtitle = ctk.CTkLabel(
            container,
            text="Silakan isi data Anda untuk memulai percakapan.",
            font=("Segoe UI", 12),
            text_color=Colors.TEXT_SECONDARY
        )

        subtitle.pack(
            padx=60,
            pady=(0, 25)
        )

        # ==================================================
        # Nama
        # ==================================================

        name_label = ctk.CTkLabel(
            container,
            text="Nama",
            font=("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        name_label.pack(
            anchor="w",
            padx=60,
            pady=(0, 5)
        )

        self.name_entry = ctk.CTkEntry(
            container,
            width=360,
            height=44,
            placeholder_text="Masukkan nama Anda"
        )

        self.name_entry.pack(
            padx=60,
            pady=(0, 12)
        )

        # ==================================================
        # No HP
        # ==================================================

        phone_label = ctk.CTkLabel(
            container,
            text="No. HP",
            font=("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        phone_label.pack(
            anchor="w",
            padx=60,
            pady=(0, 5)
        )

        self.phone_entry = ctk.CTkEntry(
            container,
            width=360,
            height=44,
            placeholder_text="Contoh: 081234567890"
        )

        self.phone_entry.pack(
            padx=60,
            pady=(0, 18)
        )

        # ==================================================
        # Start Chat Button
        # ==================================================

        self.start_button = ctk.CTkButton(
            container,
            text="Mulai Chat",
            width=360,
            height=44,
            command=self.start_chat
        )

        self.start_button.pack(
            padx=60,
            pady=(0, 10)
        )

        # ==================================================
        # Status
        # ==================================================

        self.start_status = ctk.CTkLabel(
            container,
            text="",
            font=("Segoe UI", 11),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=360
        )

        self.start_status.pack(
            padx=60,
            pady=(0, 30)
        )

    # ==================================================
    # START CHAT
    # ==================================================

    def start_chat(self):

        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        # ==================================================
        # Validation
        # ==================================================

        if not name:

            self.start_status.configure(
                text="Nama wajib diisi.",
                text_color="#DC2626"
            )

            return

        if not phone:

            self.start_status.configure(
                text="No. HP wajib diisi.",
                text_color="#DC2626"
            )

            return

        # ==================================================
        # Disable Button
        # ==================================================

        self.start_button.configure(
            state="disabled",
            text="Membuat Chat..."
        )

        self.start_status.configure(
            text="Menghubungkan ke Admin...",
            text_color=Colors.TEXT_SECONDARY
        )

        try:

            # ==================================================
            # Create Conversation
            # ==================================================

            result = SupabaseService.create_conversation(
                name,
                phone
            )

            if not result:

                raise Exception(
                    "Conversation tidak berhasil dibuat."
                )

            # ==================================================
            # Ambil Conversation Data
            # ==================================================

            conversation = result[0]

            self.conversation_id = conversation[
                "conversation_id"
            ]

            self.access_token = conversation[
                "access_token"
            ]

            self.user_name = name
            self.user_phone = phone

            # ==================================================
            # Simpan Chat Session
            # ==================================================

            ChatSession.save_session(
                conversation_id=self.conversation_id,
                user_name=self.user_name,
                user_phone=self.user_phone
            )

            # ==================================================
            # Simpan Access Token secara aman
            # ==================================================

            token_saved = SecureStorage.save_access_token(
                self.access_token
            )

            if not token_saved:

                raise Exception(
                    "Access token gagal disimpan secara aman."
                )

            # ==================================================
            # Tampilkan Chat
            # ==================================================

            self.create_chat_ui()

        except Exception as error:

            print(
                "Gagal membuat conversation:",
                error
            )

            self.start_status.configure(
                text=f"Gagal memulai chat:\n{error}",
                text_color="#DC2626"
            )

            self.start_button.configure(
                state="normal",
                text="Mulai Chat"
            )

    # ==================================================
    # CHAT UI
    # ==================================================

    def create_chat_ui(self):

        # ==================================================
        # Bersihkan UI
        # ==================================================

        for widget in self.winfo_children():
            widget.destroy()

        # ==================================================
        # Header
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

        # ==================================================
        # Title
        # ==================================================

        title = ctk.CTkLabel(
            header,
            text="Chat Admin",
            font=("Segoe UI", 24, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        title.pack(
            anchor="w"
        )

        # ==================================================
        # User Information
        # ==================================================

        subtitle = ctk.CTkLabel(
            header,
            text=f"{self.user_name}  •  {self.user_phone}",
            font=("Segoe UI", 13),
            text_color=Colors.TEXT_SECONDARY
        )

        subtitle.pack(
            anchor="w",
            pady=(4, 0)
        )

        # ==================================================
        # Chat Container
        # ==================================================

        self.chat_container = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=20,
            border_width=1,
            border_color=Colors.BORDER
        )

        self.chat_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        # ==================================================
        # Load Conversation
        # ==================================================

        self.load_messages()

        # ==================================================
        # Input Area
        # ==================================================

        input_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        input_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

        # ==================================================
        # Message Entry
        # ==================================================

        self.message_entry = ctk.CTkEntry(
            input_frame,
            height=44,
            placeholder_text="Tulis pesan untuk Admin..."
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        # ==================================================
        # Send Button
        # ==================================================

        self.send_button = ctk.CTkButton(
            input_frame,
            text="Kirim",
            width=90,
            height=44,
            command=self.send_message
        )

        self.send_button.pack(
            side="right"
        )

        # ==================================================
        # Enter = Send
        # ==================================================

        self.message_entry.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        # ==================================================
        # Focus
        # ==================================================

        self.message_entry.focus_set()

        # ==================================================
        # Start User Realtime
        # ==================================================

        self.start_user_realtime()

    # ==================================================
    # LOAD MESSAGES
    # ==================================================

    def load_messages(self):

        if not self.conversation_id:
            return

        if not self.access_token:
            return

        try:

            device_id = DeviceSession.get_device_id()

            messages = (
                SupabaseService.get_conversation_messages(
                    conversation_id=self.conversation_id,
                    access_token=self.access_token,
                    device_id=device_id
                )
            )

            # ==================================================
            # Empty Conversation
            # ==================================================

            if not messages:

                self.show_empty_state()

                return

            # ==================================================
            # Render Messages
            # ==================================================

            for message in messages:

                self.render_message(
                    message
                )

        except Exception as error:

            print(
                "Gagal mengambil pesan:",
                error
            )

            self.show_error_state(
                str(error)
            )

    # ==================================================
    # EMPTY STATE
    # ==================================================

    def show_empty_state(self):

        self.empty_label = ctk.CTkLabel(
            self.chat_container,
            text="Belum ada pesan",
            font=("Segoe UI", 18, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        self.empty_label.pack(
            pady=(120, 5)
        )

        self.empty_info = ctk.CTkLabel(
            self.chat_container,
            text="Silakan kirim pesan untuk memulai percakapan.",
            font=("Segoe UI", 12),
            text_color=Colors.TEXT_SECONDARY
        )

        self.empty_info.pack(
            pady=(0, 20)
        )

    # ==================================================
    # ERROR STATE
    # ==================================================

    def show_error_state(self, message):

        error_label = ctk.CTkLabel(
            self.chat_container,
            text="Gagal memuat percakapan.",
            font=("Segoe UI", 16, "bold"),
            text_color="#DC2626"
        )

        error_label.pack(
            pady=(100, 5)
        )

        detail_label = ctk.CTkLabel(
            self.chat_container,
            text=message,
            font=("Segoe UI", 11),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=600
        )

        detail_label.pack(
            pady=(0, 20)
        )

    # ==================================================
    # RENDER MESSAGE
    # ==================================================

    def render_message(self, message):

        sender_type = message.get(
            "sender_type",
            "user"
        )

        message_text = message.get(
            "message",
            ""
        )

        sender_name = message.get(
            "sender_name",
            ""
        )

        # ==================================================
        # Remove Empty State
        # ==================================================

        if hasattr(self, "empty_label"):

            self.empty_label.destroy()
            self.empty_info.destroy()

            del self.empty_label
            del self.empty_info

        # ==================================================
        # Message Row
        # ==================================================

        row = ctk.CTkFrame(
            self.chat_container,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=10,
            pady=5
        )

        # ==================================================
        # User Message
        # ==================================================

        if sender_type == "user":

            bubble = ctk.CTkFrame(
                row,
                fg_color=Colors.PRIMARY,
                corner_radius=15
            )

            bubble.pack(
                side="right",
                padx=(100, 5)
            )

            if sender_name:

                sender_label = ctk.CTkLabel(
                    bubble,
                    text=sender_name,
                    font=("Segoe UI", 10, "bold"),
                    text_color="#DBEAFE"
                )

                sender_label.pack(
                    anchor="e",
                    padx=15,
                    pady=(8, 0)
                )

            message_label = ctk.CTkLabel(
                bubble,
                text=message_text,
                font=("Segoe UI", 13),
                text_color="white",
                wraplength=500,
                justify="left"
            )

            message_label.pack(
                padx=15,
                pady=10
            )

        # ==================================================
        # Admin Message
        # ==================================================

        else:

            bubble = ctk.CTkFrame(
                row,
                fg_color=Colors.BORDER_LIGHT,
                corner_radius=15
            )

            bubble.pack(
                side="left",
                padx=(5, 100)
            )

            if sender_name:

                sender_label = ctk.CTkLabel(
                    bubble,
                    text=sender_name,
                    font=("Segoe UI", 10, "bold"),
                    text_color=Colors.TEXT_SECONDARY
                )

                sender_label.pack(
                    anchor="w",
                    padx=15,
                    pady=(8, 0)
                )

            message_label = ctk.CTkLabel(
                bubble,
                text=message_text,
                font=("Segoe UI", 13),
                text_color=Colors.TEXT_PRIMARY,
                wraplength=500,
                justify="left"
            )

            message_label.pack(
                padx=15,
                pady=10
            )

        # ==================================================
        # Scroll to Bottom
        # ==================================================

        self.after(
            50,
            self.scroll_to_bottom
        )

    # ==================================================
    # SCROLL TO BOTTOM
    # ==================================================

    def scroll_to_bottom(self):

        try:

            self.chat_container._parent_canvas.yview_moveto(
                1.0
            )

        except Exception:
            pass

    # ==================================================
    # START USER REALTIME
    # ==================================================

    def start_user_realtime(self):

        try:

            # ==================================================
            # CEGAH REALTIME START LEBIH DARI SATU KALI
            # ==================================================

            if (
                self.realtime_thread
                and self.realtime_thread.is_alive()
            ):

                print(
                    "Realtime User sudah berjalan."
                )

                return

            # ==================================================
            # VALIDASI CONVERSATION
            # ==================================================

            if not self.conversation_id:

                print(
                    "Realtime User: Conversation ID tidak tersedia."
                )

                return

            # ==================================================
            # AMBIL ANONYMOUS AUTH SESSION
            # ==================================================

            session = (
                SupabaseService.ensure_anonymous_session()
            )

            if not session:

                print(
                    "Realtime User: Anonymous Auth session tidak tersedia."
                )

                return

            auth_access_token = (
                session.access_token
            )

            if not auth_access_token:

                print(
                    "Realtime User: JWT Auth tidak tersedia."
                )

                return

            # ==================================================
            # DEVICE ID
            # ==================================================

            device_id = (
                DeviceSession.get_device_id()
            )

            # ==================================================
            # START BACKGROUND THREAD
            # ==================================================

            self.realtime_thread = threading.Thread(
                target=self._run_user_realtime,
                args=(
                    self.conversation_id,
                    auth_access_token,
                    device_id
                ),
                daemon=True
            )

            self.realtime_thread.start()

            print(
                "Realtime User: Background thread dimulai."
            )

        except Exception as error:

            print(
                "Gagal memulai Realtime User:",
                error
            )

    # ==================================================
    # RUN USER REALTIME
    # ==================================================

    def _run_user_realtime(
        self,
        conversation_id,
        access_token,
        device_id
    ):

        try:

            self.realtime_loop = asyncio.new_event_loop()

            asyncio.set_event_loop(
                self.realtime_loop
            )

            self.realtime_service = RealtimeService()

            self.realtime_loop.run_until_complete(
                self.realtime_service.connect_user(
                    conversation_id,
                    access_token,
                    self.handle_user_realtime_message
                )
            )

            self.realtime_loop.run_forever()

        except Exception as error:

            print(
                "Realtime User error:",
                error
            )

        finally:

            try:

                self.realtime_loop.close()

            except Exception:
                pass

    # ==================================================
    # HANDLE USER REALTIME MESSAGE
    # ==================================================

    def handle_user_realtime_message(
        self,
        payload
    ):

        try:

            print(
                "\n=== USER REALTIME CALLBACK ==="
            )

            print(
                payload
            )

            data = payload.get(
                "payload",
                {}
            )

            conversation_id = data.get(
                "conversation_id"
            )

            sender_type = data.get(
                "sender_type"
            )

            message = data.get(
                "message"
            )

            if not conversation_id:
                return

            if conversation_id != self.conversation_id:
                return

            if sender_type != "admin":
                return

            if not message:
                return

            self.after(
                0,
                lambda: self.render_message(
                    data
                )
            )

        except Exception as error:

            print(
                "Gagal memproses Realtime User:",
                error
            )

    # ==================================================
    # SEND MESSAGE
    # ==================================================

    def send_message(self):

        message = (
            self.message_entry
            .get()
            .strip()
        )

        if not message:
            return

        # ==================================================
        # Pastikan Conversation Ada
        # ==================================================

        if not self.conversation_id:

            print(
                "Conversation ID tidak tersedia."
            )

            return

        if not self.access_token:

            print(
                "Conversation Access Token tidak tersedia."
            )

            return

        # ==================================================
        # Disable Button
        # ==================================================

        self.send_button.configure(
            state="disabled",
            text="Mengirim..."
        )

        try:

            # ==================================================
            # DEVICE ID
            # ==================================================

            device_id = (
                DeviceSession.get_device_id()
            )

            print(
                "\n========================================"
            )

            print(
                "=== USER SEND MESSAGE ==="
            )

            print(
                "Conversation ID:",
                self.conversation_id
            )

            print(
                "Device ID:",
                device_id
            )

            print(
                "Message:",
                message
            )

            print(
                "========================================"
            )

            # ==================================================
            # VALIDASI CONVERSATION
            # ==================================================

            validation = (
                SupabaseService
                .validate_conversation_session(
                    self.conversation_id,
                    self.access_token,
                    device_id
                )
            )

            print(
                "=== VALIDASI CONVERSATION SESSION ==="
            )

            print(
                validation
            )

            if not validation:

                raise Exception(
                    "Conversation session tidak valid."
                )

            # ==================================================
            # PASTIKAN OWNERSHIP AUTH USER
            # ==================================================

            recovery = (
                SupabaseService
                .restore_conversation_owner(
                    self.conversation_id,
                    self.access_token,
                    device_id
                )
            )

            print(
                "=== RECOVERY CONVERSATION OWNER ==="
            )

            print(
                recovery
            )

            # ==================================================
            # SIMPAN PESAN KE SUPABASE
            # ==================================================

            result = (
                SupabaseService
                .send_conversation_message(
                    self.conversation_id,
                    self.access_token,
                    message,
                    device_id
                )
            )

            # ==================================================
            # RENDER PESAN USER
            # ==================================================

            if result:

                if isinstance(result, list):

                    message_data = result[0]

                else:

                    message_data = result

                self.render_message(
                    message_data
                )

            # ==================================================
            # REALTIME BROADCAST USER → ADMIN
            # ==================================================

            self.broadcast_user_message(
                conversation_id=self.conversation_id,
                message=message,
                sender_type="user",
                sender_name=self.user_name
            )

            # ==================================================
            # CLEAR INPUT
            # ==================================================

            self.message_entry.delete(
                0,
                "end"
            )

        except Exception as error:

            print(
                "Gagal mengirim pesan:",
                error
            )

            self.show_send_error(
                str(error)
            )

        finally:

            self.send_button.configure(
                state="normal",
                text="Kirim"
            )

    # ==================================================
    # BROADCAST USER MESSAGE
    # ==================================================

    def broadcast_user_message(
        self,
        conversation_id,
        message,
        sender_type="user",
        sender_name=None
    ):

        if not conversation_id:

            print(
                "Broadcast User: Conversation ID tidak tersedia."
            )

            return

        if not message:

            print(
                "Broadcast User: Pesan tidak tersedia."
            )

            return

        if not self.realtime_service:

            print(
                "Broadcast User: Realtime Service belum tersedia."
            )

            return

        if not self.realtime_loop:

            print(
                "Broadcast User: Realtime Loop belum tersedia."
            )

            return

        # ==================================================
        # Jalankan Broadcast pada Realtime Loop User
        # ==================================================

        try:

            future = (
                asyncio.run_coroutine_threadsafe(
                    self.realtime_service.broadcast_message(
                        conversation_id,
                        message,
                        sender_type,
                        sender_name or self.user_name
                    ),
                    self.realtime_loop
                )
            )

            def check_result():

                try:

                    result = future.result()

                    if result:

                        print(
                            "Broadcast User berhasil dikirim."
                        )

                    else:

                        print(
                            "Broadcast User gagal dikirim."
                        )

                except Exception as error:

                    print(
                        "Broadcast User error:",
                        error
                    )

            threading.Thread(
                target=check_result,
                daemon=True
            ).start()

        except Exception as error:

            print(
                "Gagal menjalankan Broadcast User:",
                error
            )

    # ==================================================
    # SEND ERROR
    # ==================================================

    def show_send_error(self, message):

        error_label = ctk.CTkLabel(
            self,
            text=f"Gagal mengirim pesan: {message}",
            font=("Segoe UI", 11),
            text_color="#DC2626"
        )

        error_label.pack(
            pady=(0, 5)
        )

        self.after(
            4000,
            error_label.destroy
        )