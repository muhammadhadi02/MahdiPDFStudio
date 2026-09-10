"""
==========================================================
Mahdi PDF Studio
Updater
==========================================================

Program kecil yang bertugas mengganti executable
Mahdi PDF Studio setelah aplikasi utama ditutup.

Alur:

MahdiPDFStudio.exe
        |
        | download update
        v
MahdiPDFStudio_new.exe
        |
        | jalankan updater
        v
MahdiPDFStudioUpdater.exe
        |
        | tunggu aplikasi utama tertutup
        v
hapus / backup EXE lama
        |
        v
pasang EXE baru
        |
        v
jalankan kembali aplikasi
==========================================================
"""

import os
import sys
import time
import shutil
import subprocess


# ==========================================================
# KONFIGURASI
# ==========================================================

WAIT_INTERVAL = 0.5
MAX_WAIT_SECONDS = 30

BACKUP_EXTENSION = ".backup"


# ==========================================================
# LOG
# ==========================================================

def log(message):
    """
    Menampilkan log sederhana.
    """

    print(
        f"[Mahdi PDF Studio Updater] {message}"
    )


# ==========================================================
# ARGUMENT
# ==========================================================

def get_arguments():
    """
    Mengambil argument dari command line.

    Format:

    updater.exe
        <update_file>
        <target_exe>
    """

    if len(sys.argv) < 3:

        raise ValueError(
            "Argument updater tidak lengkap.\n\n"
            "Format:\n"
            "updater.exe <update_file> <target_exe>"
        )

    update_file = os.path.abspath(
        sys.argv[1]
    )

    target_exe = os.path.abspath(
        sys.argv[2]
    )

    return (
        update_file,
        target_exe
    )


# ==========================================================
# VALIDASI FILE
# ==========================================================

def validate_files(
    update_file,
    target_exe
):
    """
    Memastikan file update tersedia.
    """

    log(
        f"File update: {update_file}"
    )

    log(
        f"Target EXE : {target_exe}"
    )

    if not os.path.exists(update_file):

        raise FileNotFoundError(
            "File update tidak ditemukan:\n"
            f"{update_file}"
        )

    if os.path.getsize(update_file) <= 0:

        raise RuntimeError(
            "File update kosong."
        )

    target_folder = os.path.dirname(
        target_exe
    )

    if not os.path.exists(target_folder):

        raise FileNotFoundError(
            "Folder aplikasi tidak ditemukan:\n"
            f"{target_folder}"
        )


# ==========================================================
# TUNGGU APLIKASI UTAMA TERTUTUP
# ==========================================================

def wait_for_target_to_close(
    target_exe
):
    """
    Menunggu sampai executable utama
    tidak lagi digunakan oleh Windows.

    Kita tidak langsung melakukan replace.

    Updater akan mencoba membuka target
    dengan mode read/write.

    Jika masih terkunci, berarti aplikasi
    kemungkinan masih berjalan.
    """

    log(
        "Menunggu aplikasi utama ditutup..."
    )

    start_time = time.time()

    while True:

        elapsed = (
            time.time() - start_time
        )

        if elapsed >= MAX_WAIT_SECONDS:

            raise TimeoutError(
                "Aplikasi utama tidak tertutup "
                f"dalam {MAX_WAIT_SECONDS} detik."
            )

        if not os.path.exists(target_exe):

            log(
                "EXE utama sudah tidak ditemukan."
            )

            return

        try:

            with open(
                target_exe,
                "r+b"
            ):

                pass

            log(
                "EXE utama sudah tidak terkunci."
            )

            return

        except PermissionError:

            time.sleep(
                WAIT_INTERVAL
            )

        except OSError:

            time.sleep(
                WAIT_INTERVAL
            )


# ==========================================================
# BACKUP EXE LAMA
# ==========================================================

def create_backup(
    target_exe
):
    """
    Membuat backup EXE lama sebelum diganti.

    Contoh:

    MahdiPDFStudio.exe
    ->
    MahdiPDFStudio.exe.backup
    """

    if not os.path.exists(
        target_exe
    ):

        log(
            "EXE lama tidak ditemukan. "
            "Backup dilewati."
        )

        return None

    backup_path = (
        target_exe
        + BACKUP_EXTENSION
    )

    try:

        if os.path.exists(
            backup_path
        ):

            os.remove(
                backup_path
            )

        shutil.copy2(
            target_exe,
            backup_path
        )

        log(
            f"Backup dibuat: {backup_path}"
        )

        return backup_path

    except Exception as error:

        raise RuntimeError(
            "Gagal membuat backup EXE lama."
        ) from error


# ==========================================================
# PASANG UPDATE
# ==========================================================

def install_update(
    update_file,
    target_exe
):
    """
    Mengganti EXE lama dengan EXE baru.
    """

    log(
        "Memasang update..."
    )

    if not os.path.exists(
        update_file
    ):

        raise FileNotFoundError(
            "File update tidak ditemukan."
        )

    target_folder = os.path.dirname(
        target_exe
    )

    # ------------------------------------------------------
    # Temporary EXE
    # ------------------------------------------------------

    temporary_target = os.path.join(
        target_folder,
        "MahdiPDFStudio_installing.exe"
    )

    # ------------------------------------------------------
    # Hapus temporary lama jika ada
    # ------------------------------------------------------

    if os.path.exists(
        temporary_target
    ):

        try:

            os.remove(
                temporary_target
            )

        except Exception as error:

            raise RuntimeError(
                "Tidak dapat membersihkan "
                "file temporary updater."
            ) from error

    # ------------------------------------------------------
    # Copy update ke folder aplikasi
    # ------------------------------------------------------

    shutil.copy2(
        update_file,
        temporary_target
    )

    log(
        "File update berhasil disalin."
    )

    # ------------------------------------------------------
    # Pastikan file temporary ada
    # ------------------------------------------------------

    if not os.path.exists(
        temporary_target
    ):

        raise RuntimeError(
            "File temporary update gagal dibuat."
        )

    if os.path.getsize(
        temporary_target
    ) <= 0:

        raise RuntimeError(
            "File temporary update kosong."
        )

    # ------------------------------------------------------
    # Hapus EXE lama
    # ------------------------------------------------------

    if os.path.exists(
        target_exe
    ):

        try:

            os.remove(
                target_exe
            )

        except Exception as error:

            raise RuntimeError(
                "Gagal menghapus EXE lama."
            ) from error

    # ------------------------------------------------------
    # Rename temporary menjadi EXE utama
    # ------------------------------------------------------

    try:

        os.replace(
            temporary_target,
            target_exe
        )

    except Exception as error:

        raise RuntimeError(
            "Gagal memasang EXE terbaru."
        ) from error

    log(
        "Update berhasil dipasang."
    )


# ==========================================================
# JALANKAN APLIKASI KEMBALI
# ==========================================================

def restart_application(
    target_exe
):
    """
    Menjalankan kembali Mahdi PDF Studio.
    """

    if not os.path.exists(
        target_exe
    ):

        raise FileNotFoundError(
            "EXE terbaru tidak ditemukan "
            "setelah proses update."
        )

    log(
        "Menjalankan kembali Mahdi PDF Studio..."
    )

    subprocess.Popen(
        [
            target_exe
        ],
        cwd=os.path.dirname(
            target_exe
        ),
        close_fds=True
    )


# ==========================================================
# CLEANUP
# ==========================================================

def cleanup(
    update_file
):
    """
    Menghapus file update sementara.
    """

    try:

        if os.path.exists(
            update_file
        ):

            os.remove(
                update_file
            )

            log(
                "File update sementara dihapus."
            )

    except Exception as error:

        log(
            f"Gagal menghapus file sementara: {error}"
        )


# ==========================================================
# MAIN
# ==========================================================

def main():

    update_file = None

    try:

        log(
            "Updater dimulai."
        )

        # --------------------------------------------------
        # Ambil argument
        # --------------------------------------------------

        (
            update_file,
            target_exe
        ) = get_arguments()

        # --------------------------------------------------
        # Validasi
        # --------------------------------------------------

        validate_files(
            update_file,
            target_exe
        )

        # --------------------------------------------------
        # Tunggu aplikasi utama
        # --------------------------------------------------

        wait_for_target_to_close(
            target_exe
        )

        # --------------------------------------------------
        # Backup EXE lama
        # --------------------------------------------------

        create_backup(
            target_exe
        )

        # --------------------------------------------------
        # Install update
        # --------------------------------------------------

        install_update(
            update_file,
            target_exe
        )

        # --------------------------------------------------
        # Hapus file update
        # --------------------------------------------------

        cleanup(
            update_file
        )

        # --------------------------------------------------
        # Jalankan kembali aplikasi
        # --------------------------------------------------

        restart_application(
            target_exe
        )

        log(
            "Proses updater selesai."
        )

    except Exception as error:

        log(
            "UPDATE GAGAL"
        )

        log(
            f"Error: {error}"
        )

        # Jangan langsung tutup console ketika
        # dijalankan manual untuk testing.
        #
        # Saat nanti sudah menjadi EXE updater,
        # bagian ini akan kita ubah menjadi
        # UI error dialog.

        if getattr(
            sys,
            "frozen",
            False
        ):

            time.sleep(5)

        return 1

    return 0


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )