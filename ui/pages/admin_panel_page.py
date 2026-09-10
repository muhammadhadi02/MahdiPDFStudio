import customtkinter as ctk
import threading
import asyncio

from core.services.realtime_service import RealtimeService
from core.services.supabase_service import SupabaseService

from themes.colors import Colors
from themes.spacing import Spacing


class AdminPanelPage(ctk.CTkFrame):

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

        # ==================================================
        # Conversation yang sedang dipilih
        # ==================================================

        self.selected_conversation_id = None

        # ==================================================
        # Realtime State
        # ==================================================

        self.realtime_service = None
        self.realtime_thread = None
        self.realtime_loop = None

        self.create_widgets()
        self.load_conversations()

        self.start_realtime()

    # ==================================================
    # REALTIME ADMIN
    # ==================================================

    def start_realtime(self):
        """
        Memulai koneksi Realtime Admin
        di background thread.

        Admin tidak lagi menggunakan channel
        'admin_messages' karena project Supabase
        menggunakan Private Only.

        Realtime conversation akan diaktifkan
        ketika Admin memilih conversation.
        """

        try:

            session = (
                SupabaseService
                .get_client()
                .auth
                .get_session()
            )

            if not session:

                print(
                    "Realtime: Session Admin tidak ditemukan."
                )

                return

            access_token = session.access_token

            if not access_token:

                print(
                    "Realtime: Access token Admin "
                    "tidak ditemukan."
                )

                return

            self.realtime_thread = threading.Thread(
                target=self._run_realtime,
                args=(access_token,),
                daemon=True
            )

            self.realtime_thread.start()

            print(
                "Realtime: Background thread dimulai."
            )

        except Exception as error:

            print(
                "Gagal memulai Realtime:",
                error
            )

    def _run_realtime(
        self,
        access_token
    ):
        """
        Menjalankan asyncio event loop
        khusus untuk Realtime Admin.
        """

        try:

            self.realtime_loop = (
                asyncio.new_event_loop()
            )

            asyncio.set_event_loop(
                self.realtime_loop
            )

            self.realtime_service = (
                RealtimeService()
            )

            # ==================================================
            # HANYA BUAT CLIENT REALTIME ADMIN
            # ==================================================

            self.realtime_loop.run_until_complete(
                self.realtime_service.connect_admin(
                    access_token
                )
            )

            self.realtime_loop.run_forever()

        except Exception as error:

            print(
                "Realtime Admin error:",
                error
            )

        finally:

            try:

                self.realtime_loop.close()

            except Exception:

                pass

    # ==================================================
    # SUBSCRIBE CONVERSATION ADMIN
    # ==================================================

    def subscribe_conversation_realtime(
        self,
        conversation_id
    ):
        """
        Subscribe Admin ke private channel
        conversation tertentu.
        """

        if not conversation_id:

            print(
                "Realtime Admin: Conversation ID "
                "tidak tersedia."
            )

            return

        if not self.realtime_service:

            print(
                "Realtime Admin: Realtime Service "
                "belum tersedia."
            )

            return

        if not self.realtime_loop:

            print(
                "Realtime Admin: Realtime Loop "
                "belum tersedia."
            )

            return

        future = asyncio.run_coroutine_threadsafe(
            self.realtime_service.subscribe_admin_conversation(
                conversation_id,
                self.handle_realtime_message
            ),
            self.realtime_loop
        )

        def check_result():

            try:

                future.result()

                print(
                    "Realtime Admin conversation berhasil "
                    "diproses:",
                    conversation_id
                )

            except Exception as error:

                print(
                    "Realtime Admin conversation error:",
                    error
                )

        threading.Thread(
            target=check_result,
            daemon=True
        ).start()

    # ==================================================
    # REALTIME MESSAGE CALLBACK
    # ==================================================

    def handle_realtime_message(
        self,
        payload
    ):
        """
        Callback ketika ada pesan User
        dari Supabase Realtime Broadcast.
        """

        try:

            print(
                "\n========================================"
            )

            print(
                "=== REALTIME ADMIN MESSAGE ==="
            )

            print(
                "Payload:",
                payload
            )

            print(
                "========================================"
            )

            data = payload.get(
                "payload",
                {}
            )

            if not data:

                return

            sender_type = data.get(
                "sender_type"
            )

            conversation_id = data.get(
                "conversation_id"
            )

            message = data.get(
                "message"
            )

            # ==================================================
            # HANYA PESAN USER
            # ==================================================

            if sender_type != "user":

                return

            if not conversation_id:

                return

            if not message:

                return

            print(
                "Pesan User diterima Realtime:",
                message
            )

            # ==================================================
            # HANYA UPDATE CHAT YANG SEDANG DIPILIH
            # ==================================================

            if (
                conversation_id
                != self.selected_conversation_id
            ):

                return

            # ==================================================
            # UPDATE UI DI MAIN THREAD
            # ==================================================

            self.after(
                0,
                self.load_conversation_messages
            )

        except Exception as error:

            print(
                "Gagal memproses Realtime message:",
                error
            )

    # ==================================================
    # BROADCAST ADMIN -> USER
    # ==================================================

    def _broadcast_to_user(
        self,
        conversation_id,
        message
    ):
        """
        Mengirim Broadcast Admin ke channel conversation
        melalui event loop Realtime Admin.
        """

        if not self.realtime_service:

            print(
                "Broadcast gagal: Realtime Service "
                "belum tersedia."
            )

            return

        if not self.realtime_loop:

            print(
                "Broadcast gagal: Realtime Loop "
                "belum tersedia."
            )

            return

        future = asyncio.run_coroutine_threadsafe(
            self.realtime_service.broadcast_message(
                conversation_id,
                message
            ),
            self.realtime_loop
        )

        def check_result():

            try:

                result = future.result()

                if result:

                    print(
                        "Broadcast Admin berhasil dikirim."
                    )

                else:

                    print(
                        "Broadcast Admin tidak dikirim."
                    )

            except Exception as error:

                print(
                    "Broadcast Admin gagal:",
                    error
                )

        threading.Thread(
            target=check_result,
            daemon=True
        ).start()

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
            text="Admin Panel",
            font=("Segoe UI", 24, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        title.pack(
            anchor="w"
        )

        subtitle = ctk.CTkLabel(
            header,
            text="Kelola percakapan pengguna dengan Admin.",
            font=("Segoe UI", 13),
            text_color=Colors.TEXT_SECONDARY
        )

        subtitle.pack(
            anchor="w",
            pady=(4, 0)
        )

        # ==================================================
        # MAIN CONTAINER
        # ==================================================

        main_container = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=20,
            border_width=1,
            border_color=Colors.BORDER
        )

        main_container.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        # ==================================================
        # LEFT - CONVERSATION LIST
        # ==================================================

        conversation_panel = ctk.CTkFrame(
            main_container,
            fg_color="transparent",
            width=300
        )

        conversation_panel.pack(
            side="left",
            fill="y",
            padx=15,
            pady=15
        )

        conversation_panel.pack_propagate(False)

        conversation_title = ctk.CTkLabel(
            conversation_panel,
            text="Percakapan",
            font=("Segoe UI", 16, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        conversation_title.pack(
            anchor="w",
            padx=10,
            pady=(5, 10)
        )

        # ==================================================
        # SEARCH
        # ==================================================

        self.search_entry = ctk.CTkEntry(
            conversation_panel,
            height=40,
            placeholder_text="Cari pengguna..."
        )

        self.search_entry.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        # ==================================================
        # CONVERSATION LIST
        # ==================================================

        self.conversation_list = ctk.CTkScrollableFrame(
            conversation_panel,
            fg_color=Colors.WORKSPACE_BG,
            corner_radius=12
        )

        self.conversation_list.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        # ==================================================
        # SEPARATOR
        # ==================================================

        separator = ctk.CTkFrame(
            main_container,
            width=1,
            fg_color=Colors.BORDER
        )

        separator.pack(
            side="left",
            fill="y",
            pady=20
        )

        # ==================================================
        # RIGHT - CHAT AREA
        # ==================================================

        chat_panel = ctk.CTkFrame(
            main_container,
            fg_color="transparent"
        )

        chat_panel.pack(
            side="left",
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        # ==================================================
        # CHAT HEADER
        # ==================================================

        chat_header = ctk.CTkFrame(
            chat_panel,
            fg_color=Colors.WORKSPACE_BG,
            corner_radius=12
        )

        chat_header.pack(
            fill="x"
        )

        self.chat_user_label = ctk.CTkLabel(
            chat_header,
            text="Pilih percakapan",
            font=("Segoe UI", 15, "bold"),
            text_color=Colors.TEXT_PRIMARY
        )

        self.chat_user_label.pack(
            anchor="w",
            padx=15,
            pady=(12, 2)
        )

        self.chat_phone_label = ctk.CTkLabel(
            chat_header,
            text="",
            font=("Segoe UI", 11),
            text_color=Colors.TEXT_SECONDARY
        )

        self.chat_phone_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 12)
        )

        # ==================================================
        # CHAT MESSAGE AREA
        # ==================================================

        self.chat_container = ctk.CTkScrollableFrame(
            chat_panel,
            fg_color=Colors.CARD_BG,
            corner_radius=12
        )

        self.chat_container.pack(
            fill="both",
            expand=True,
            pady=(10, 10)
        )

        # ==================================================
        # INITIAL CHAT EMPTY STATE
        # ==================================================

        self.show_chat_empty_state()

        # ==================================================
        # MESSAGE INPUT
        # ==================================================

        input_frame = ctk.CTkFrame(
            chat_panel,
            fg_color="transparent"
        )

        input_frame.pack(
            fill="x"
        )

        self.message_entry = ctk.CTkEntry(
            input_frame,
            height=44,
            placeholder_text="Tulis balasan..."
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

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
    # CHAT EMPTY STATE
    # ==================================================

    def show_chat_empty_state(self):

        for widget in self.chat_container.winfo_children():

            widget.destroy()

        empty_label = ctk.CTkLabel(
            self.chat_container,
            text="Pilih percakapan untuk melihat pesan.",
            font=("Segoe UI", 13),
            text_color=Colors.TEXT_SECONDARY
        )

        empty_label.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

    # ==================================================
    # LOAD CONVERSATIONS
    # ==================================================

    def load_conversations(self):

        try:

            conversations = (
                SupabaseService
                .get_all_conversations()
            )

            # ==================================================
            # HAPUS DAFTAR LAMA
            # ==================================================

            for widget in (
                self.conversation_list
                .winfo_children()
            ):

                widget.destroy()

            if not conversations:

                empty_label = ctk.CTkLabel(
                    self.conversation_list,
                    text="Belum ada percakapan.",
                    font=("Segoe UI", 12),
                    text_color=Colors.TEXT_SECONDARY
                )

                empty_label.pack(
                    pady=30
                )

                return

            # ==================================================
            # TAMPILKAN CONVERSATION
            # ==================================================

            for conversation in conversations:

                name = conversation.get(
                    "name",
                    "Tanpa Nama"
                )

                phone = conversation.get(
                    "phone",
                    ""
                )

                item = ctk.CTkButton(
                    self.conversation_list,
                    text=f"{name}\n{phone}",
                    anchor="w",
                    height=60,
                    fg_color="transparent",
                    text_color=Colors.TEXT_PRIMARY,
                    hover_color=Colors.BORDER_LIGHT,
                    command=lambda c=conversation:
                        self.select_conversation(c)
                )

                item.pack(
                    fill="x",
                    padx=5,
                    pady=3
                )

        except Exception as error:

            print(
                "Gagal mengambil conversations:",
                error
            )

            for widget in (
                self.conversation_list
                .winfo_children()
            ):

                widget.destroy()

            error_label = ctk.CTkLabel(
                self.conversation_list,
                text="Gagal memuat percakapan.",
                font=("Segoe UI", 12),
                text_color="#DC2626"
            )

            error_label.pack(
                pady=30
            )

    # ==================================================
    # SELECT CONVERSATION
    # ==================================================

    def select_conversation(
        self,
        conversation
    ):

        self.selected_conversation_id = (
            conversation.get("id")
        )

        name = conversation.get(
            "name",
            "Tanpa Nama"
        )

        phone = conversation.get(
            "phone",
            ""
        )

        # ==================================================
        # UPDATE CHAT HEADER
        # ==================================================

        self.chat_user_label.configure(
            text=name
        )

        self.chat_phone_label.configure(
            text=phone
        )

        print(
            "Conversation dipilih:",
            self.selected_conversation_id
        )

        # ==================================================
        # LOAD MESSAGES
        # ==================================================

        self.load_conversation_messages()

        # ==================================================
        # SUBSCRIBE REALTIME
        # ==================================================

        self.subscribe_conversation_realtime(
            self.selected_conversation_id
        )

    # ==================================================
    # LOAD CONVERSATION MESSAGES
    # ==================================================

    def load_conversation_messages(self):

        if not self.selected_conversation_id:

            return

        try:

            messages = (
                SupabaseService
                .get_admin_conversation_messages(
                    self.selected_conversation_id
                )
            )

            # ==================================================
            # HAPUS PESAN LAMA
            # ==================================================

            for widget in (
                self.chat_container
                .winfo_children()
            ):

                widget.destroy()

            # ==================================================
            # BELUM ADA PESAN
            # ==================================================

            if not messages:

                empty_label = ctk.CTkLabel(
                    self.chat_container,
                    text="Belum ada pesan.",
                    font=("Segoe UI", 13),
                    text_color=Colors.TEXT_SECONDARY
                )

                empty_label.pack(
                    pady=30
                )

                return

            # ==================================================
            # TAMPILKAN PESAN
            # ==================================================

            for message in messages:

                self.render_admin_message(
                    message
                )

            # ==================================================
            # SCROLL KE PESAN TERAKHIR
            # ==================================================

            self.after(
                100,
                self.scroll_chat_to_bottom
            )

        except Exception as error:

            print(
                "Gagal mengambil pesan:",
                error
            )

            for widget in (
                self.chat_container
                .winfo_children()
            ):

                widget.destroy()

            error_label = ctk.CTkLabel(
                self.chat_container,
                text="Gagal memuat pesan.",
                font=("Segoe UI", 12),
                text_color="#DC2626"
            )

            error_label.pack(
                pady=30
            )

    # ==================================================
    # SCROLL CHAT TO BOTTOM
    # ==================================================

    def scroll_chat_to_bottom(self):

        try:

            self.chat_container._parent_canvas.yview_moveto(
                1.0
            )

        except Exception as error:

            print(
                "Gagal scroll chat:",
                error
            )

    # ==================================================
    # RENDER MESSAGE
    # ==================================================

    def render_admin_message(
        self,
        message
    ):

        sender_type = message.get(
            "sender_type",
            "user"
        )

        sender_name = message.get(
            "sender_name",
            "User"
        )

        message_text = message.get(
            "message",
            ""
        )

        # ==================================================
        # ADMIN MESSAGE
        # ==================================================

        if sender_type == "admin":

            anchor = "e"
            bubble_color = "#2563EB"
            text_color = "white"

        # ==================================================
        # USER MESSAGE
        # ==================================================

        else:

            anchor = "w"
            bubble_color = Colors.WORKSPACE_BG
            text_color = Colors.TEXT_PRIMARY

        # ==================================================
        # MESSAGE FRAME
        # ==================================================

        message_frame = ctk.CTkFrame(
            self.chat_container,
            fg_color="transparent"
        )

        message_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        # ==================================================
        # MESSAGE BUBBLE
        # ==================================================

        bubble = ctk.CTkFrame(
            message_frame,
            fg_color=bubble_color,
            corner_radius=14
        )

        bubble.pack(
            anchor=anchor
        )

        # ==================================================
        # SENDER
        # ==================================================

        sender_label = ctk.CTkLabel(
            bubble,
            text=sender_name,
            font=("Segoe UI", 10, "bold"),
            text_color=text_color
        )

        sender_label.pack(
            anchor="w",
            padx=12,
            pady=(8, 0)
        )

        # ==================================================
        # MESSAGE TEXT
        # ==================================================

        message_label = ctk.CTkLabel(
            bubble,
            text=message_text,
            font=("Segoe UI", 12),
            text_color=text_color,
            wraplength=450,
            justify="left"
        )

        message_label.pack(
            anchor="w",
            padx=12,
            pady=(3, 8)
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

        if not self.selected_conversation_id:

            print(
                "Belum ada percakapan yang dipilih."
            )

            return

        try:

            # ==================================================
            # SIMPAN PESAN ADMIN KE DATABASE
            # ==================================================

            SupabaseService.send_admin_message(
                conversation_id=(
                    self.selected_conversation_id
                ),
                message=message
            )

            # ==================================================
            # BROADCAST KE USER
            # ==================================================

            self._broadcast_to_user(
                conversation_id=(
                    self.selected_conversation_id
                ),
                message=message
            )

            # ==================================================
            # CLEAR INPUT
            # ==================================================

            self.message_entry.delete(
                0,
                "end"
            )

            # ==================================================
            # REFRESH CHAT ADMIN
            # ==================================================

            self.load_conversation_messages()

        except Exception as error:

            print(
                "Gagal mengirim pesan admin:",
                error
            )