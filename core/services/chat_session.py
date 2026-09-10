#untuk data session non-rahasia.

import json
import os


class ChatSession:

    APP_FOLDER = "MahdiPDFStudio"
    SESSION_FILE = "chat_session.json"

    @classmethod
    def get_app_data_dir(cls):
        appdata = os.getenv("APPDATA")

        if not appdata:
            appdata = os.path.expanduser("~")

        folder = os.path.join(
            appdata,
            cls.APP_FOLDER
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        return folder

    @classmethod
    def get_session_file(cls):
        return os.path.join(
            cls.get_app_data_dir(),
            cls.SESSION_FILE
        )

    @classmethod
    def save_session(
        cls,
        conversation_id,
        user_name,
        user_phone
    ):
        session = {
            "conversation_id": conversation_id,
            "user_name": user_name,
            "user_phone": user_phone
        }

        session_file = cls.get_session_file()

        with open(
            session_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                session,
                file,
                ensure_ascii=False,
                indent=4
            )

    @classmethod
    def load_session(cls):

        session_file = cls.get_session_file()

        if not os.path.exists(session_file):
            return None

        try:

            with open(
                session_file,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except Exception as error:

            print(
                "Gagal membaca Chat Session:",
                error
            )

            return None

    @classmethod
    def clear_session(cls):

        session_file = cls.get_session_file()

        if os.path.exists(session_file):

            try:
                os.remove(session_file)

            except Exception as error:

                print(
                    "Gagal menghapus Chat Session:",
                    error
                )