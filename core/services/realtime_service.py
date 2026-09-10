import asyncio

from supabase import acreate_client
from realtime import RealtimeSubscribeStates


class RealtimeService:

    SUPABASE_URL = (
        "https://wqeaftswaiglrtpoxtfq.supabase.co"
    )

    SUPABASE_KEY = (
        "sb_publishable_SykYZbzDtMQmo3CxsvbD3A_aQlTez_S"
    )

    def __init__(self):
        self.client = None

        # Channel yang sedang digunakan untuk user/admin
        self.channel = None

        # Khusus subscription Admin ke conversation
        self.admin_conversation_channel = None

        # Conversation yang sedang disubscribe Admin
        self.admin_conversation_id = None

    async def connect_admin(self, access_token):

        if not access_token:
            raise Exception(
                "Access token Admin tidak tersedia."
            )

        self.client = await acreate_client(
            self.SUPABASE_URL,
            self.SUPABASE_KEY
        )

        print("Menghubungkan Realtime Admin...")

        await self.client.realtime.set_auth(
            access_token
        )

        print("Access token Admin berhasil dipasang.")
        print("Realtime Admin siap.")

    async def connect_user(
        self,
        conversation_id,
        access_token,
        callback
    ):

        if not conversation_id:
            raise Exception(
                "Conversation ID User tidak tersedia."
            )

        if not access_token:
            raise Exception(
                "Access token User tidak tersedia."
            )

        self.client = await acreate_client(
            self.SUPABASE_URL,
            self.SUPABASE_KEY
        )

        print("Menghubungkan Realtime User...")

        await self.client.realtime.set_auth(
            access_token
        )

        print("Access token User berhasil dipasang.")

        channel_name = (
            f"conversation:{conversation_id}"
        )

        print("User Channel:", channel_name)

        def handle_broadcast(payload):

            print("\n========================================")
            print("=== REALTIME ADMIN MESSAGE ===")
            print(
                "Admin Channel Object:",
                id(channel)
            )
            print(
                "Admin Conversation ID:",
                conversation_id
            )
            print("Payload:", payload)
            print("========================================")

            if callback:

                try:

                    callback(payload)

                except Exception as error:

                    print(
                        "Callback Admin error:",
                        error
                    )

            if callback:

                try:
                    callback(payload)

                except Exception as error:

                    print(
                        "Callback User error:",
                        error
                    )

        def handle_user_status(
            status,
            error
        ):

            print("\n=== REALTIME USER SUBSCRIBE ===")
            print("Status:", status)
            print("Error:", error)

            if (
                status
                == RealtimeSubscribeStates.SUBSCRIBED
            ):

                print(
                    "Realtime User berhasil subscribe!"
                )

        channel = self.client.channel(
            channel_name,
            params={
                "config": {
                    "private": True
                }
            }
        )

        self.channel = channel

        await (
            channel
            .on_broadcast(
                event="message",
                callback=handle_broadcast
            )
            .subscribe(handle_user_status)
        )

        print(
            "Realtime User: proses subscribe selesai."
        )

    async def subscribe_admin_conversation(
        self,
        conversation_id,
        callback
    ):

        if not self.client:
            raise Exception(
                "Realtime Admin belum terhubung."
            )

        if not conversation_id:
            raise Exception(
                "Conversation ID tidak tersedia."
            )

        # ==================================================
        # CEK APAKAH SUDAH SUBSCRIBE CONVERSATION YANG SAMA
        # ==================================================

        if (
            self.admin_conversation_id
            == conversation_id
            and self.admin_conversation_channel
        ):

            print(
                "Realtime Admin: conversation sudah "
                "disubscribe, tidak membuat subscription baru."
            )

            return

        # ==================================================
        # HENTIKAN SUBSCRIPTION ADMIN SEBELUMNYA
        # ==================================================

        if self.admin_conversation_channel:

            print(
                "Realtime Admin: menghentikan "
                "subscription conversation sebelumnya..."
            )

            try:

                await (
                    self.admin_conversation_channel
                    .unsubscribe()
                )

            except Exception as error:

                print(
                    "Gagal unsubscribe conversation sebelumnya:",
                    error
                )

            self.admin_conversation_channel = None
            self.admin_conversation_id = None

        # ==================================================
        # BUAT CHANNEL BARU
        # ==================================================

        channel_name = (
            f"conversation:{conversation_id}"
        )

        print("\n=== ADMIN SUBSCRIBE CONVERSATION ===")
        print("Channel:", channel_name)

        channel = self.client.channel(
            channel_name,
            params={
                "config": {
                    "private": True
                }
            }
        )

        self.admin_conversation_channel = channel
        self.admin_conversation_id = conversation_id

        # ==================================================
        # CALLBACK MESSAGE
        # ==================================================

        def handle_broadcast(payload):

            print("\n========================================")
            print("=== REALTIME ADMIN MESSAGE ===")
            print("Payload:", payload)
            print("========================================")

            if callback:

                try:

                    callback(payload)

                except Exception as error:

                    print(
                        "Callback Admin error:",
                        error
                    )

        # ==================================================
        # CALLBACK STATUS
        # ==================================================

        def handle_status(
            status,
            error
        ):

            print(
                "\n=== REALTIME ADMIN SUBSCRIBE ==="
            )

            print("Status:", status)
            print("Error:", error)

            if (
                status
                == RealtimeSubscribeStates.SUBSCRIBED
            ):

                print(
                    "Realtime Admin conversation "
                    "berhasil subscribe!"
                )

        # ==================================================
        # SUBSCRIBE
        # ==================================================

        await (
            channel
            .on_broadcast(
                event="message",
                callback=handle_broadcast
            )
            .subscribe(handle_status)
        )

        print(
            "Realtime Admin conversation: "
            "proses subscribe selesai."
        )

    async def broadcast_message(
        self,
        conversation_id,
        message,
        sender_type="admin",
        sender_name="Admin"
    ):

        if not self.client:
            raise Exception(
                "Realtime Client belum terhubung."
            )

        if not conversation_id:
            raise Exception(
                "Conversation ID tidak tersedia."
            )

        if not message:
            raise Exception(
                "Pesan tidak tersedia."
            )

        if sender_type not in (
            "admin",
            "user"
        ):

            raise Exception(
                "Sender type tidak valid."
            )

        if not sender_name:

            sender_name = (
                "Admin"
                if sender_type == "admin"
                else "User"
            )

        channel_name = (
            f"conversation:{conversation_id}"
        )

        print("\n=== REALTIME BROADCAST ===")
        print("Channel:", channel_name)
        print("Sender Type:", sender_type)
        print("Sender Name:", sender_name)
        print("Message:", message)

        channel = self.client.channel(
            channel_name,
            params={
                "config": {
                    "private": True
                }
            }
        )

        subscribe_event = asyncio.Event()

        subscribe_success = False

        def handle_broadcast_status(
            status,
            error
        ):

            nonlocal subscribe_success

            print(
                "\n=== REALTIME BROADCAST SUBSCRIBE ==="
            )

            print("Status:", status)
            print("Error:", error)

            if (
                status
                == RealtimeSubscribeStates.SUBSCRIBED
            ):

                subscribe_success = True

                print(
                    "Channel Broadcast berhasil subscribe!"
                )

            else:

                subscribe_success = False

            try:

                subscribe_event.set()

            except Exception:

                pass

        channel = channel.on_broadcast(
            event="message",
            callback=lambda payload: print(
                "\n=== BROADCAST CALLBACK ===\n",
                payload
            )
        )

        await channel.subscribe(
            handle_broadcast_status
        )

        try:

            await asyncio.wait_for(
                subscribe_event.wait(),
                timeout=10
            )

        except asyncio.TimeoutError:

            print(
                "Timeout menunggu status "
                "subscribe Broadcast."
            )

            subscribe_success = False

        if not subscribe_success:

            print(
                "Broadcast dibatalkan karena "
                "subscribe private channel gagal."
            )

            try:

                await channel.unsubscribe()

            except Exception:

                pass

            return False

        broadcast_payload = {

            "conversation_id":
                conversation_id,

            "sender_type":
                sender_type,

            "sender_name":
                sender_name,

            "message":
                message
        }

        print(
            "\n=== MENGIRIM REALTIME BROADCAST ==="
        )

        print(
            "Payload:",
            broadcast_payload
        )

        await channel.send_broadcast(
            "message",
            broadcast_payload
        )

        print(
            "Realtime Broadcast berhasil dikirim."
        )

        try:

            await channel.unsubscribe()

        except Exception as error:

            print(
                "Gagal unsubscribe channel broadcast:",
                error
            )

        return True

    async def disconnect(self):

        # ==================================================
        # DISCONNECT ADMIN CONVERSATION CHANNEL
        # ==================================================

        if self.admin_conversation_channel:

            try:

                await (
                    self.admin_conversation_channel
                    .unsubscribe()
                )

            except Exception as error:

                print(
                    "Gagal unsubscribe "
                    "Admin conversation:",
                    error
                )

            self.admin_conversation_channel = None
            self.admin_conversation_id = None

        # ==================================================
        # DISCONNECT CHANNEL UMUM
        # ==================================================

        if self.channel:

            try:

                await self.channel.unsubscribe()

            except Exception as error:

                print(
                    "Gagal unsubscribe Realtime:",
                    error
                )

            self.channel = None

        # ==================================================
        # DISCONNECT CLIENT
        # ==================================================

        if self.client:

            try:

                await self.client.realtime.disconnect()

            except Exception as error:

                print(
                    "Gagal disconnect Realtime:",
                    error
                )

            self.client = None

        print("Realtime dihentikan.")