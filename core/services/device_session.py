#File ini akan membuat identitas unik untuk instalasi/perangkat aplikasi.


import os
import uuid


class DeviceSession:

    APP_FOLDER = "MahdiPDFStudio"
    SESSION_FILE = "device_id.txt"

    @classmethod
    def get_app_data_dir(cls):
        """
        Mengambil folder AppData/Roaming untuk aplikasi.
        """

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
    def get_device_id(cls):
        """
        Mengambil Device ID.
        Jika belum ada, buat ID baru.
        """

        session_file = os.path.join(
            cls.get_app_data_dir(),
            cls.SESSION_FILE
        )

        # ==============================================
        # Device ID sudah ada
        # ==============================================

        if os.path.exists(session_file):

            try:

                with open(
                    session_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    device_id = file.read().strip()

                if device_id:
                    return device_id

            except Exception:
                pass

        # ==============================================
        # Buat Device ID baru
        # ==============================================

        device_id = str(
            uuid.uuid4()
        )

        try:

            with open(
                session_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(device_id)

        except Exception as error:

            print(
                "Gagal menyimpan Device ID:",
                error
            )

        return device_id