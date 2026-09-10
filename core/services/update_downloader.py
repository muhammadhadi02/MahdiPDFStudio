import os
import tempfile
import urllib.request


class UpdateDownloader:

    USER_AGENT = "MahdiPDFStudio-Updater"

    # ======================================================
    # DOWNLOAD GENERIC FILE
    # ======================================================

    @staticmethod
    def download_file(
        download_url,
        filename,
        progress_callback=None
    ):
        """
        Download file ke temporary directory.

        Parameters:
            download_url
                URL file yang akan di-download.

            filename
                Nama file hasil download.

            progress_callback
                Callback progress 0-100.
        """

        if not download_url:

            raise ValueError(
                "Download URL tidak tersedia."
            )

        # --------------------------------------------------
        # Temporary Directory
        # --------------------------------------------------

        temp_dir = tempfile.mkdtemp(
            prefix="MahdiPDFStudio_Update_"
        )

        file_path = os.path.join(
            temp_dir,
            filename
        )

        # --------------------------------------------------
        # Request
        # --------------------------------------------------

        request = urllib.request.Request(
            download_url,
            headers={
                "User-Agent": (
                    UpdateDownloader.USER_AGENT
                )
            }
        )

        # --------------------------------------------------
        # Download
        # --------------------------------------------------

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            total_size = response.headers.get(
                "Content-Length"
            )

            if total_size:

                total_size = int(
                    total_size
                )

            downloaded = 0

            with open(
                file_path,
                "wb"
            ) as file:

                while True:

                    chunk = response.read(
                        1024 * 1024
                    )

                    if not chunk:

                        break

                    file.write(
                        chunk
                    )

                    downloaded += len(
                        chunk
                    )

                    # ------------------------------------------
                    # Progress
                    # ------------------------------------------

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

        # --------------------------------------------------
        # Validate
        # --------------------------------------------------

        if not os.path.exists(
            file_path
        ):

            raise RuntimeError(
                "File download gagal dibuat."
            )

        if os.path.getsize(
            file_path
        ) == 0:

            raise RuntimeError(
                "File download kosong."
            )

        # Pastikan progress terakhir 100%.

        if progress_callback:

            progress_callback(
                100
            )

        return file_path

    # ======================================================
    # DOWNLOAD APPLICATION UPDATE
    # ======================================================

    @staticmethod
    def download_update(
        download_url,
        progress_callback=None
    ):
        """
        Download EXE aplikasi terbaru.
        """

        return (
            UpdateDownloader.download_file(
                download_url,
                "MahdiPDFStudio_new.exe",
                progress_callback
            )
        )

    # ======================================================
    # DOWNLOAD UPDATER
    # ======================================================

    @staticmethod
    def download_updater(
        updater_url
    ):
        """
        Download MahdiPDFStudioUpdater.exe.

        File ini hanya diperlukan oleh aplikasi
        ketika proses instalasi update akan dilakukan.
        """

        return (
            UpdateDownloader.download_file(
                updater_url,
                "MahdiPDFStudioUpdater.exe"
            )
        )