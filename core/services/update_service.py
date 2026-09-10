"""
==========================================================
Mahdi PDF Studio
Update Service
==========================================================

Bertugas mengecek apakah tersedia versi aplikasi terbaru.

Tahap awal:
- Membaca versi aplikasi lokal
- Mengecek versi terbaru dari server
- Membandingkan versi
- Belum melakukan download/update EXE
==========================================================
"""

import urllib.request
import json

from version import APP_VERSION


class UpdateService:
    """
    Service untuk mengecek update Mahdi PDF Studio.
    """

    # ==================================================
    # Konfigurasi
    # ==================================================

    # Untuk sementara URL masih dikosongkan.
    # Nanti kita isi dengan GitHub Releases/API.
    UPDATE_URL = ""

    # ==================================================
    # Version Comparison
    # ==================================================

    @staticmethod
    def parse_version(version):
        """
        Mengubah versi:

            1.2.3

        menjadi:

            (1, 2, 3)
        """

        try:
            parts = str(version).strip().lstrip("v").split(".")

            return tuple(
                int(part)
                for part in parts
            )

        except Exception:
            return (0, 0, 0)

    @classmethod
    def is_newer_version(cls, latest_version):
        """
        Mengecek apakah latest_version lebih baru
        daripada versi aplikasi saat ini.
        """

        current = cls.parse_version(
            APP_VERSION
        )

        latest = cls.parse_version(
            latest_version
        )

        return latest > current

    # ==================================================
    # Check Update
    # ==================================================

    @classmethod
    def check_for_update(cls):
        """
        Mengecek update dari server.

        Return:

            None
                Jika gagal / tidak ada update.

            dict
                Jika tersedia update.
        """

        if not cls.UPDATE_URL:
            return None

        try:
            request = urllib.request.Request(
                cls.UPDATE_URL,
                headers={
                    "User-Agent":
                    "MahdiPDFStudio-Updater"
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=5
            ) as response:

                data = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

            latest_version = str(
                data.get("version", "")
            ).strip()

            if not latest_version:
                return None

            if not cls.is_newer_version(
                latest_version
            ):
                return None

            return {
                "current_version": APP_VERSION,
                "latest_version": latest_version,
                "download_url": data.get(
                    "download_url"
                ),
                "release_notes": data.get(
                    "release_notes",
                    []
                ),
            }

        except Exception as error:

            print(
                "Update check gagal:",
                error
            )

            return None