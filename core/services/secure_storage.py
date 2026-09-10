#menyimpan access_token secara aman.

#Kita akan menggunakan Windows Credential Manager, bukan memasukkan token ke chat_session.json.

import ctypes
import ctypes.wintypes
import base64


class SecureStorage:

    TARGET_NAME = "MahdiPDFStudio.ChatAdmin"

    @classmethod
    def save_access_token(cls, token: str):
        if not token:
            return False

        data = token.encode("utf-8")

        encoded = base64.b64encode(data)

        try:
            # Windows DPAPI
            crypt32 = ctypes.windll.crypt32

            class DATA_BLOB(ctypes.Structure):
                _fields_ = [
                    ("cbData", ctypes.wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_byte))
                ]

            buffer = (ctypes.c_byte * len(encoded))(*encoded)

            input_blob = DATA_BLOB(
                len(encoded),
                ctypes.cast(
                    buffer,
                    ctypes.POINTER(ctypes.c_byte)
                )
            )

            output_blob = DATA_BLOB()

            result = crypt32.CryptProtectData(
                ctypes.byref(input_blob),
                cls.TARGET_NAME,
                None,
                None,
                None,
                0,
                ctypes.byref(output_blob)
            )

            if not result:
                return False

            encrypted = ctypes.string_at(
                output_blob.pbData,
                output_blob.cbData
            )

            ctypes.windll.kernel32.LocalFree(output_blob.pbData)

            # Simpan hasil terenkripsi
            import os

            appdata = os.getenv("APPDATA")

            if not appdata:
                appdata = os.path.expanduser("~")

            folder = os.path.join(
                appdata,
                "MahdiPDFStudio"
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            file_path = os.path.join(
                folder,
                "chat_token.dat"
            )

            with open(
                file_path,
                "wb"
            ) as file:

                file.write(encrypted)

            return True

        except Exception as error:

            print(
                "Gagal menyimpan access token:",
                error
            )

            return False

    @classmethod
    def load_access_token(cls):

        try:

            import os

            appdata = os.getenv("APPDATA")

            if not appdata:
                appdata = os.path.expanduser("~")

            file_path = os.path.join(
                appdata,
                "MahdiPDFStudio",
                "chat_token.dat"
            )

            if not os.path.exists(file_path):
                return None

            with open(
                file_path,
                "rb"
            ) as file:

                encrypted = file.read()

            crypt32 = ctypes.windll.crypt32

            class DATA_BLOB(ctypes.Structure):
                _fields_ = [
                    ("cbData", ctypes.wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_byte))
                ]

            buffer = (ctypes.c_byte * len(encrypted))(*encrypted)

            input_blob = DATA_BLOB(
                len(encrypted),
                ctypes.cast(
                    buffer,
                    ctypes.POINTER(ctypes.c_byte)
                )
            )

            output_blob = DATA_BLOB()

            result = crypt32.CryptUnprotectData(
                ctypes.byref(input_blob),
                None,
                None,
                None,
                None,
                0,
                ctypes.byref(output_blob)
            )

            if not result:
                return None

            decrypted = ctypes.string_at(
                output_blob.pbData,
                output_blob.cbData
            )

            ctypes.windll.kernel32.LocalFree(output_blob.pbData)

            decoded = base64.b64decode(
                decrypted
            )

            return decoded.decode("utf-8")

        except Exception as error:

            print(
                "Gagal membaca access token:",
                error
            )

            return None

    @classmethod
    def clear_access_token(cls):

        try:

            import os

            appdata = os.getenv("APPDATA")

            if not appdata:
                appdata = os.path.expanduser("~")

            file_path = os.path.join(
                appdata,
                "MahdiPDFStudio",
                "chat_token.dat"
            )

            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as error:

            print(
                "Gagal menghapus access token:",
                error
            )


    @classmethod
    def save_auth_session(cls, access_token: str, refresh_token: str):
        if not access_token or not refresh_token:
            return False

        try:
            import json

            session_data = json.dumps({
                "access_token": access_token,
                "refresh_token": refresh_token
            })

            return cls._save_encrypted_file(
                "auth_session.dat",
                session_data
            )

        except Exception as error:
            print("Gagal menyimpan Auth Session:", error)
            return False

    @classmethod
    def load_auth_session(cls):
        try:
            import json

            session_data = cls._load_encrypted_file(
                "auth_session.dat"
            )

            if not session_data:
                return None

            return json.loads(session_data)

        except Exception as error:
            print("Gagal membaca Auth Session:", error)
            return None

    @classmethod
    def clear_auth_session(cls):
        try:
            import os

            appdata = os.getenv("APPDATA")
            if not appdata:
                appdata = os.path.expanduser("~")

            file_path = os.path.join(
                appdata,
                "MahdiPDFStudio",
                "auth_session.dat"
            )

            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as error:
            print("Gagal menghapus Auth Session:", error)

    @classmethod
    def _save_encrypted_file(cls, file_name: str, text: str):
        if not text:
            return False

        try:
            import os

            data = text.encode("utf-8")
            encoded = base64.b64encode(data)

            crypt32 = ctypes.windll.crypt32

            class DATA_BLOB(ctypes.Structure):
                _fields_ = [
                    ("cbData", ctypes.wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_byte))
                ]

            buffer = (ctypes.c_byte * len(encoded))(*encoded)

            input_blob = DATA_BLOB(
                len(encoded),
                ctypes.cast(
                    buffer,
                    ctypes.POINTER(ctypes.c_byte)
                )
            )

            output_blob = DATA_BLOB()

            result = crypt32.CryptProtectData(
                ctypes.byref(input_blob),
                cls.TARGET_NAME,
                None,
                None,
                None,
                0,
                ctypes.byref(output_blob)
            )

            if not result:
                return False

            encrypted = ctypes.string_at(
                output_blob.pbData,
                output_blob.cbData
            )

            ctypes.windll.kernel32.LocalFree(
                output_blob.pbData
            )

            appdata = os.getenv("APPDATA")

            if not appdata:
                appdata = os.path.expanduser("~")

            folder = os.path.join(
                appdata,
                "MahdiPDFStudio"
            )

            os.makedirs(
                folder,
                exist_ok=True
            )

            file_path = os.path.join(
                folder,
                file_name
            )

            with open(
                file_path,
                "wb"
            ) as file:

                file.write(encrypted)

            return True

        except Exception as error:

            print(
                "Gagal menyimpan encrypted file:",
                error
            )

            return False

    @classmethod
    def _load_encrypted_file(cls, file_name: str):

        try:
            import os

            appdata = os.getenv("APPDATA")

            if not appdata:
                appdata = os.path.expanduser("~")

            file_path = os.path.join(
                appdata,
                "MahdiPDFStudio",
                file_name
            )

            if not os.path.exists(file_path):
                return None

            with open(
                file_path,
                "rb"
            ) as file:

                encrypted = file.read()

            crypt32 = ctypes.windll.crypt32

            class DATA_BLOB(ctypes.Structure):
                _fields_ = [
                    ("cbData", ctypes.wintypes.DWORD),
                    ("pbData", ctypes.POINTER(ctypes.c_byte))
                ]

            buffer = (ctypes.c_byte * len(encrypted))(*encrypted)

            input_blob = DATA_BLOB(
                len(encrypted),
                ctypes.cast(
                    buffer,
                    ctypes.POINTER(ctypes.c_byte)
                )
            )

            output_blob = DATA_BLOB()

            result = crypt32.CryptUnprotectData(
                ctypes.byref(input_blob),
                None,
                None,
                None,
                None,
                0,
                ctypes.byref(output_blob)
            )

            if not result:
                return None

            decrypted = ctypes.string_at(
                output_blob.pbData,
                output_blob.cbData
            )

            ctypes.windll.kernel32.LocalFree(
                output_blob.pbData
            )

            decoded = base64.b64decode(
                decrypted
            )

            return decoded.decode("utf-8")

        except Exception as error:

            print(
                "Gagal membaca encrypted file:",
                error
            )

            return None