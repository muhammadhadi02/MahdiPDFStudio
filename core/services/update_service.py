import urllib.request
import json
from version import APP_VERSION


class UpdateService:
    UPDATE_URL = (
        "https://wqeaftswaiglrtpoxtfq.supabase.co/"
        "storage/v1/object/public/updates/version.json"
    )

    @staticmethod
    def parse_version(version):
        try:
            parts = str(version).strip().lstrip("v").split(".")
            return tuple(int(part) for part in parts)
        except Exception:
            return (0, 0, 0)

    @classmethod
    def is_newer_version(cls, latest_version):
        current = cls.parse_version(APP_VERSION)
        latest = cls.parse_version(latest_version)
        return latest > current

    @classmethod
    def check_for_update(cls):
        try:
            request = urllib.request.Request(
                cls.UPDATE_URL,
                headers={
                    "User-Agent": "MahdiPDFStudio-Updater"
                }
            )

            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )

            latest_version = str(
                data.get("version", "")
            ).strip()

            if not latest_version:
                return None

            if not cls.is_newer_version(latest_version):
                return None

            return {
                "current_version": APP_VERSION,
                "latest_version": latest_version,
                "download_url": data.get("download_url"),
                "release_notes": data.get(
                    "release_notes", []
                ),
            }

        except Exception as error:
            print("Update check gagal:", error)
            return None 