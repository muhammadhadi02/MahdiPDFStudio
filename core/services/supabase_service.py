from supabase import create_client, Client
from core.services.device_session import DeviceSession
from core.services.secure_storage import SecureStorage

class SupabaseService:
    SUPABASE_URL = "https://wqeaftswaiglrtpoxtfq.supabase.co"
    SUPABASE_KEY = "sb_publishable_SykYZbzDtMQmo3CxsvbD3A_aQlTez_S"

    _client: Client | None = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._client is None:
            cls._client = create_client(
                cls.SUPABASE_URL,
                cls.SUPABASE_KEY
            )

        return cls._client

    @classmethod
    def sign_in_anonymously(cls):
        client = cls.get_client()
        result = client.auth.sign_in_anonymously()
        return result

    @classmethod
    def ensure_anonymous_session(cls):
        client = cls.get_client()

        # ==================================================
        # 1. CEK SESSION YANG SUDAH ADA DI MEMORY
        # ==================================================

        try:
            session = client.auth.get_session()

            if (
                session
                and session.user
                and session.access_token
            ):
                # --------------------------------------------------
                # Penting:
                # get_session() dapat melakukan refresh otomatis.
                # Kalau session berubah, simpan pasangan token terbaru.
                # --------------------------------------------------

                if session.refresh_token:
                    SecureStorage.save_auth_session(
                        session.access_token,
                        session.refresh_token
                    )

                print(
                    "Anonymous Auth session aktif."
                )

                print(
                    "Anonymous Auth User ID:",
                    session.user.id
                )

                return session

        except Exception as error:

            print(
                "Gagal membaca Anonymous Auth session:",
                error
            )

        # ==================================================
        # 2. COBA RESTORE DARI SECURE STORAGE
        # ==================================================

        saved_session = (
            SecureStorage.load_auth_session()
        )

        if saved_session:

            access_token = (
                saved_session.get(
                    "access_token"
                )
            )

            refresh_token = (
                saved_session.get(
                    "refresh_token"
                )
            )

            if access_token and refresh_token:

                try:

                    restored = (
                        client.auth.set_session(
                            access_token,
                            refresh_token
                        )
                    )

                    # set_session() mengembalikan AuthResponse.
                    # Session berada di restored.session.

                    if (
                        restored
                        and restored.session
                        and restored.session.user
                        and restored.session.access_token
                    ):

                        new_session = (
                            restored.session
                        )

                        # --------------------------------------------------
                        # Sangat penting:
                        # Supabase dapat memberikan refresh token BARU.
                        # Simpan token BARU tersebut.
                        # --------------------------------------------------

                        SecureStorage.save_auth_session(
                            new_session.access_token,
                            new_session.refresh_token
                        )

                        print(
                            "Anonymous Auth session berhasil direstore."
                        )

                        print(
                            "Anonymous Auth User ID:",
                            new_session.user.id
                        )

                        return new_session

                except Exception as error:

                    print(
                        "Gagal restore Anonymous Auth session:",
                        error
                    )

                    # Jangan langsung membuat user baru
                    # tanpa membersihkan token lama.
                    SecureStorage.clear_auth_session()

        # ==================================================
        # 3. TIDAK ADA SESSION VALID
        #    BUAT ANONYMOUS USER BARU
        # ==================================================

        print(
            "Membuat Anonymous Auth User baru..."
        )

        result = (
            client.auth.sign_in_anonymously()
        )

        if (
            not result
            or not result.session
            or not result.user
        ):

            raise Exception(
                "Gagal membuat Anonymous Auth session."
            )

        new_session = (
            result.session
        )

        # ==================================================
        # 4. SIMPAN SESSION BARU
        # ==================================================

        SecureStorage.save_auth_session(
            new_session.access_token,
            new_session.refresh_token
        )

        print(
            "Anonymous Auth User baru berhasil dibuat."
        )

        print(
            "Anonymous Auth User ID:",
            new_session.user.id
        )

        return new_session

    @classmethod
    def login(cls, email: str, password: str):
        client = cls.get_client()

        result = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        return result

    @classmethod
    def logout(cls):
        client = cls.get_client()
        client.auth.sign_out()

    @classmethod
    def get_current_user(cls):
        client = cls.get_client()
        return client.auth.get_user()

    @classmethod
    def is_admin(cls):
        client = cls.get_client()

        result = (
            client
            .rpc("is_admin")
            .execute()
        )

        return result.data

    @classmethod
    def get_all_conversations(cls):
        client = cls.get_client()

        result = (
            client.table("conversations")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return result.data

    @classmethod
    def get_messages(cls, limit: int = 100):
        client = cls.get_client()

        result = (
            client.table("messages")
            .select("*")
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )

        return result.data

    @classmethod
    def send_message(
        cls,
        message: str,
        sender_type: str,
        sender_name: str,
        user_id: str
    ):
        client = cls.get_client()

        result = (
            client.table("messages")
            .insert({
                "user_id": user_id,
                "sender_type": sender_type,
                "sender_name": sender_name,
                "message": message
            })
            .execute()
        )

        return result.data

    @classmethod
    def create_conversation(
        cls,
        name: str,
        phone: str
    ):
        client = cls.get_client()

        session = cls.ensure_anonymous_session()

        if not session or not session.user:
            raise Exception(
                "Anonymous Auth session tidak tersedia."
            )

        device_id = DeviceSession.get_device_id()

        result = (
            client
            .rpc(
                "create_conversation",
                {
                    "p_name": name,
                    "p_phone": phone,
                    "p_device_id": device_id
                }
            )
            .execute()
        )

        return result.data

    @classmethod
    def validate_conversation_session(
        cls,
        conversation_id: str,
        access_token: str,
        device_id: str
    ):
        client = cls.get_client()

        result = (
            client
            .rpc(
                "validate_conversation_session",
                {
                    "p_conversation_id": conversation_id,
                    "p_access_token": access_token,
                    "p_device_id": device_id
                }
            )
            .execute()
        )

        return result.data

    @classmethod
    def restore_conversation_owner(
        cls,
        conversation_id: str,
        access_token: str,
        device_id: str
    ):
        client = cls.get_client()

        result = client.rpc(
            "restore_conversation_owner",
            {
                "p_conversation_id": conversation_id,
                "p_access_token": access_token,
                "p_device_id": device_id
            }
        ).execute()

        return result.data

    @classmethod
    def send_conversation_message(
        cls,
        conversation_id: str,
        access_token: str,
        message: str,
        device_id: str
    ):
        client = cls.get_client()

        result = (
            client
            .rpc(
                "send_conversation_message",
                {
                    "p_conversation_id": conversation_id,
                    "p_access_token": access_token,
                    "p_message": message,
                    "p_device_id": device_id
                }
            )
            .execute()
        )

        return result.data

    @classmethod
    def get_conversation_messages(
        cls,
        conversation_id: str,
        access_token: str,
        device_id: str
    ):
        client = cls.get_client()

        result = (
            client
            .rpc(
                "get_conversation_messages",
                {
                    "p_conversation_id": conversation_id,
                    "p_access_token": access_token,
                    "p_device_id": device_id
                }
            )
            .execute()
        )

        return result.data

    @classmethod
    def get_admin_conversation_messages(
        cls,
        conversation_id: str
    ):
        client = cls.get_client()

        result = (
            client
            .table("messages")
            .select("*")
            .eq("conversation_id", conversation_id)
            .order("created_at", desc=False)
            .execute()
        )

        return result.data

    @classmethod
    def send_admin_message(
        cls,
        conversation_id: str,
        message: str
    ):
        client = cls.get_client()

        result = (
            client
            .table("messages")
            .insert({
                "conversation_id": conversation_id,
                "sender_type": "admin",
                "sender_name": "Admin",
                "message": message
            })
            .execute()
        )

        return result.data