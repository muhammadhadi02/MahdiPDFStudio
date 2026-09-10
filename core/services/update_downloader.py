import os
import tempfile
import urllib.request


class UpdateDownloader:

    @staticmethod
    def download_update(download_url, progress_callback=None):
        """
        Download file update ke folder temporary.

        progress_callback:
            callback(percent) jika ingin menampilkan progress.
        """

        if not download_url:
            raise ValueError("Download URL tidak tersedia.")

        temp_dir = tempfile.mkdtemp(
            prefix="MahdiPDFStudio_Update_"
        )

        update_path = os.path.join(
            temp_dir,
            "MahdiPDFStudio_new.exe"
        )

        request = urllib.request.Request(
            download_url,
            headers={
                "User-Agent": "MahdiPDFStudio-Updater"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            total_size = response.headers.get(
                "Content-Length"
            )

            if total_size:
                total_size = int(total_size)

            downloaded = 0

            with open(update_path, "wb") as file:

                while True:
                    chunk = response.read(1024 * 1024)

                    if not chunk:
                        break

                    file.write(chunk)

                    downloaded += len(chunk)

                    if (
                        total_size
                        and progress_callback
                    ):
                        percent = int(
                            downloaded
                            * 100
                            / total_size
                        )

                        progress_callback(
                            percent
                        )

        if not os.path.exists(update_path):
            raise RuntimeError(
                "File update gagal dibuat."
            )

        if os.path.getsize(update_path) == 0:
            raise RuntimeError(
                "File update kosong."
            )

        return update_path