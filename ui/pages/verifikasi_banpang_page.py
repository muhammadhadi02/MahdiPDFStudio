"""
Mahdi PDF Studio - Verifikasi Banpang

Workflow sederhana:
1. Buka Website
2. Persiapan Filter Manual
3. Pengambilan Data & Pembuatan PDF
4. Prompt Verifikasi
5. Hasil

Catatan:
- Semua filter Banpang dilakukan manual langsung pada website.
- User disarankan memilih Baris per halaman = 100.
- Tahap pengambilan saat ini membaca tabel PBP yang sudah tampil.
- Mekanisme pengambilan foto dan generator PDF akan menggunakan data
  yang sudah terkumpul pada tahap berikutnya.
"""

import os
import re
import threading
import traceback
import webbrowser
import customtkinter as ctk
from tkinter import filedialog

from themes.colors import Colors
from themes.fonts import Fonts
from themes.icons import Icons
from core.services.banpang_browser_service import BanpangBrowserService
from core.services.banpang_pdf_service import BanpangPDFService


# ==========================================================
# PROMPT VERIFIKASI CHATGPT
# ==========================================================

PROMPT_VERIFIKASI = {

    # ==========================================================
    # NORMAL
    # ==========================================================
    "Normal": """
ANDA BERTUGAS SEBAGAI VERIFIKATOR DATA BANTUAN PANGAN (BANPANG).

Lakukan verifikasi secara OBJEKTIF, DETAIL, INDIVIDUAL, DAN BERDASARKAN BUKTI yang terdapat pada PDF yang saya upload.

KHUSUS UNTUK:
STATUS PBP = "NORMAL"

============================================================
TUJUAN VERIFIKASI
============================================================

Memastikan:

1. Identitas PBP pada data sesuai dengan KTP PBP.
2. Nama PBP sesuai dengan nama pada KTP.
3. NIK PBP sesuai dengan NIK pada KTP.
4. KTP PBP tersedia dan dapat diidentifikasi sebagai KTP FISIK ASLI secara visual.

============================================================
ATURAN SUMBER DATA
============================================================

1. PDF adalah SATU-SATUNYA sumber bukti.
2. Jangan menggunakan asumsi atau pengetahuan dari luar PDF.
3. Jangan mencari informasi tambahan di internet.
4. Jangan mengarang data yang tidak terlihat.
5. Jangan memperbaiki atau menormalisasi nama, NIK, alamat, Kecamatan, atau data lainnya.
6. Jika tulisan kurang jelas, jangan menebak.
7. Jika bukti tidak cukup untuk menentukan hasil → PERLU VERIFIKASI.

============================================================
PEMERIKSAAN NAMA
============================================================

Bandingkan:

Nama PBP pada Data
VS
Nama pada KTP PBP.

Kategori:

- SESUAI
- BERBEDA
- TIDAK DAPAT DIVERIFIKASI

Jika terdapat perbedaan nama yang jelas → TIDAK LOLOS.

Jangan menganggap nama sama hanya karena terlihat mirip.

============================================================
PEMERIKSAAN NIK
============================================================

Bandingkan:

NIK PBP pada Data
VS
NIK pada KTP PBP.

Ketentuan:

1. NIK harus terdiri dari 16 digit.
2. Semua digit harus sama.
3. Jika terdapat 1 digit saja yang berbeda → TIDAK LOLOS.
4. Jika beberapa digit berbeda → TIDAK LOLOS.
5. Tampilkan posisi digit yang berbeda jika dapat dibaca dengan jelas.
6. Jika NIK tidak terbaca → PERLU VERIFIKASI.
7. Jangan menebak digit yang tidak terlihat.

============================================================
PEMERIKSAAN KTP PBP
============================================================

KTP PBP WAJIB tersedia.

Periksa secara VISUAL apakah dokumen merupakan KTP FISIK ASLI.

Kategori:

- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

Jika KTP berupa fotokopi → TIDAK LOLOS.

Jika KTP tidak tersedia → TIDAK LOLOS.

Jika KTP tersedia tetapi tidak dapat ditentukan secara visual → PERLU VERIFIKASI.

Jangan menyatakan "ASLI" hanya karena terdapat gambar KTP.
Penilaian harus berdasarkan tampilan visual dokumen KTP pada PDF.

============================================================
PENTING: PEMERIKSAAN VISUAL PDF
============================================================

WAJIB memeriksa gambar/dokumen yang tertanam di dalam PDF secara visual.

Jangan hanya mengandalkan text layer PDF.

Khusus KTP:
- baca nama secara visual;
- baca NIK secara visual;
- periksa bentuk/tampilan KTP;
- tentukan apakah terlihat sebagai KTP fisik asli, fotokopi, tidak ada, atau tidak terbaca.

============================================================
HASIL AKHIR
============================================================

Gunakan HANYA tiga hasil:

1. LOLOS
2. TIDAK LOLOS
3. PERLU VERIFIKASI

LOLOS jika seluruh persyaratan wajib terpenuhi.

TIDAK LOLOS jika terdapat pelanggaran persyaratan yang dapat dibuktikan dengan jelas.

PERLU VERIFIKASI jika bukti tidak cukup atau tidak dapat dibaca dengan jelas.

============================================================
FORMAT OUTPUT
============================================================

Buat tabel:

No | No PBP | Nama PBP | Nama KTP | Detail Nama | NIK PBP | NIK KTP | Detail NIK | KTP PBP | HASIL | ALASAN

Setiap PBP harus diverifikasi INDIVIDUAL.

Jangan menggabungkan beberapa PBP menjadi satu pemeriksaan.

Pada ALASAN, jelaskan bukti yang menyebabkan hasil tersebut.

============================================================
RECHECK
============================================================

Sebelum memberikan hasil akhir, lakukan pemeriksaan ulang untuk memastikan:

- Nama sudah dibandingkan dengan benar.
- NIK sudah dibandingkan digit per digit.
- Jumlah digit NIK sudah diperiksa.
- Status KTP sudah diperiksa secara visual.
- Tidak ada data yang ditebak.
- Tidak ada PBP yang terlewat.
- Tidak ada hasil LOLOS ketika bukti sebenarnya tidak cukup.
""",

    # ==========================================================
    # PERWAKILAN 1 KK
    # ==========================================================
    "Perwakilan 1 KK": """
ANDA BERTUGAS SEBAGAI VERIFIKATOR DATA BANTUAN PANGAN (BANPANG).

Lakukan verifikasi secara OBJEKTIF, DETAIL, INDIVIDUAL, DAN BERDASARKAN BUKTI yang terdapat pada PDF yang saya upload.

KHUSUS UNTUK:
STATUS PBP = "PERWAKILAN 1 KK"

============================================================
TUJUAN VERIFIKASI
============================================================

Memastikan bahwa:

1. Data PBP dapat diidentifikasi.
2. Data Perwakilan dapat diidentifikasi.
3. Nama Perwakilan sesuai dengan KTP Perwakilan.
4. NIK Perwakilan sesuai dengan KTP Perwakilan.
5. KTP Perwakilan tersedia dan secara visual merupakan KTP FISIK ASLI.
6. PBP tercantum sebagai anggota dalam KK.
7. Perwakilan tercantum sebagai anggota dalam KK.
8. PBP dan Perwakilan berada dalam KK yang SAMA.
9. Nomor KK yang menjadi bukti untuk PBP dan Perwakilan adalah sama.

============================================================
ATURAN PENTING TENTANG KK
============================================================

Untuk kategori PERWAKILAN 1 KK:

KK adalah BUKTI UTAMA untuk membuktikan bahwa PBP dan Perwakilan berada dalam satu keluarga/KK.

Perhatikan bahwa pada PDF, dokumen KK yang terlihat dapat merupakan:

"KK PERWAKILAN"

Jika hanya satu dokumen KK yang terlihat dan dokumen tersebut adalah KK Perwakilan, maka gunakan dokumen tersebut sebagai bukti.

Namun, PBP HARUS benar-benar tercantum sebagai anggota dalam KK tersebut agar dapat dinyatakan PERWAKILAN 1 KK.

Jangan menyimpulkan satu KK hanya berdasarkan:

- nama keluarga;
- hubungan keluarga yang diasumsikan;
- alamat yang sama;
- Kecamatan yang sama;
- Kabupaten yang sama;
- kemiripan nama.

Nomor KK adalah bukti utama.

============================================================
PEMERIKSAAN DATA PERWAKILAN
============================================================

Bandingkan:

Nama Perwakilan pada Data
VS
Nama Perwakilan pada KTP.

Kategori:

- SESUAI
- BERBEDA
- TIDAK DAPAT DIVERIFIKASI

Jika berbeda secara jelas → TIDAK LOLOS.

============================================================
PEMERIKSAAN NIK PERWAKILAN
============================================================

Bandingkan:

NIK Perwakilan pada Data
VS
NIK Perwakilan pada KTP.

Ketentuan:

1. NIK harus 16 digit.
2. Semua digit harus sama.
3. Perbedaan satu digit saja → TIDAK LOLOS.
4. Jika beberapa digit berbeda → TIDAK LOLOS.
5. Jika NIK tidak terbaca → PERLU VERIFIKASI.
6. Jangan menebak digit.

============================================================
PEMERIKSAAN KTP PERWAKILAN
============================================================

KTP Perwakilan WAJIB tersedia.

Periksa secara VISUAL.

Kategori:

- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

Jika KTP berupa fotokopi → TIDAK LOLOS.

Jika KTP tidak tersedia → TIDAK LOLOS.

Jika tersedia tetapi tidak dapat ditentukan secara visual → PERLU VERIFIKASI.

Jangan menyatakan KTP "ASLI" hanya karena terdapat gambar KTP.

============================================================
PEMERIKSAAN KK
============================================================

WAJIB memeriksa gambar KK secara VISUAL.

Jangan hanya mengandalkan text layer PDF.

Dari KK, periksa:

1. Nomor KK.
2. Nama-nama anggota keluarga.
3. NIK anggota jika terlihat.
4. Nama PBP.
5. Nama Perwakilan.
6. Hubungan keluarga jika tercantum.
7. Alamat jika tercantum.
8. Kecamatan jika tercantum.

============================================================
PEMERIKSAAN PBP DALAM KK
============================================================

Cari nama PBP secara langsung pada daftar anggota KK.

Kategori:

- ADA
- TIDAK ADA
- TIDAK DAPAT DIVERIFIKASI

Jika PBP jelas tercantum → ADA.

Jika PBP jelas tidak tercantum setelah seluruh daftar anggota KK terbaca → TIDAK ADA → TIDAK LOLOS.

Jika daftar KK tidak terbaca atau bukti tidak cukup → TIDAK DAPAT DIVERIFIKASI → PERLU VERIFIKASI.

Jika NIK PBP pada KK terlihat, bandingkan dengan NIK PBP pada data.

Kategori:

- SESUAI
- BERBEDA
- TIDAK TERSEDIA / TIDAK TERBACA

Perbedaan NIK yang jelas → TIDAK LOLOS.

Jika NIK tidak terlihat pada KK, jangan menganggap berbeda. Kehadiran NIK pada KK bukan syarat terpisah jika nama PBP dan keanggotaan dalam KK dapat dibuktikan dengan jelas.

============================================================
PEMERIKSAAN PERWAKILAN DALAM KK
============================================================

Cari nama Perwakilan secara langsung pada daftar anggota KK.

Kategori:

- ADA
- TIDAK ADA
- TIDAK DAPAT DIVERIFIKASI

Jika Perwakilan jelas tercantum → ADA.

Jika Perwakilan jelas tidak tercantum → TIDAK ADA → TIDAK LOLOS.

Jika tidak dapat dibaca → PERLU VERIFIKASI.

Jika NIK Perwakilan pada KK terlihat, bandingkan dengan NIK Perwakilan pada data.

Kategori:

- SESUAI
- BERBEDA
- TIDAK TERSEDIA / TIDAK TERBACA

Perbedaan NIK yang jelas → TIDAK LOLOS.

============================================================
PEMERIKSAAN NOMOR KK
============================================================

Baca nomor KK secara VISUAL.

Catat:

KK PBP
KK Perwakilan

Jika hanya satu KK Perwakilan yang terlihat dan PBP juga tercantum dalam KK tersebut, maka:

KK PBP = nomor KK yang terlihat
KK Perwakilan = nomor KK yang terlihat

Detail KK:

- NOMOR KK SAMA
- NOMOR KK BERBEDA
- NOMOR KK TIDAK DAPAT DIVERIFIKASI

Untuk kategori PERWAKILAN 1 KK:

NOMOR KK BERBEDA → TIDAK LOLOS.

NOMOR KK TIDAK DAPAT DIVERIFIKASI → PERLU VERIFIKASI.

Jangan menebak nomor KK yang buram/tidak terbaca.

============================================================
KTP PBP
============================================================

KTP PBP TIDAK WAJIB untuk kategori PERWAKILAN 1 KK.

Jadi:

- KTP PBP tidak ada → bukan otomatis TIDAK LOLOS.
- KTP PBP fotokopi → bukan otomatis TIDAK LOLOS.
- KTP PBP ada → dapat digunakan sebagai bukti tambahan.
- Jangan menjadikan KTP PBP sebagai syarat wajib.

Fokus utama adalah:

PBP + Perwakilan + KTP Perwakilan + KK.

============================================================
HASIL AKHIR
============================================================

Gunakan HANYA:

- LOLOS
- TIDAK LOLOS
- PERLU VERIFIKASI

LOLOS jika:

1. Nama Perwakilan = KTP.
2. NIK Perwakilan = KTP.
3. NIK 16 digit dan sesuai.
4. KTP Perwakilan tersedia.
5. KTP Perwakilan secara visual merupakan KTP fisik asli.
6. PBP tercantum dalam KK.
7. Perwakilan tercantum dalam KK.
8. Nomor KK sama.
9. Tidak ada bukti yang bertentangan.

TIDAK LOLOS jika salah satu persyaratan wajib terbukti gagal.

PERLU VERIFIKASI jika bukti tidak cukup atau tidak terbaca.

============================================================
FORMAT OUTPUT
============================================================

Buat tabel:

No | No PBP | Nama PBP | NIK PBP | Nama Perwakilan | Nama KTP Perwakilan | Detail Nama | NIK Perwakilan | NIK KTP Perwakilan | Detail NIK | KK PBP | KK Perwakilan | Detail KK | PBP dalam KK | NIK PBP dalam KK | Perwakilan dalam KK | NIK Perwakilan dalam KK | KTP Perwakilan | HASIL | ALASAN

============================================================
DETAIL KK
============================================================

Gunakan:

- NOMOR KK SAMA
- NOMOR KK BERBEDA
- NOMOR KK TIDAK DAPAT DIVERIFIKASI

============================================================
RECHECK
============================================================

Sebelum hasil akhir, pastikan:

1. PBP benar-benar tercantum dalam KK.
2. Perwakilan benar-benar tercantum dalam KK.
3. Nomor KK sudah dibaca secara visual.
4. Nomor KK PBP dan Perwakilan sama.
5. Tidak menggunakan alamat/nama keluarga sebagai pengganti nomor KK.
6. Nama Perwakilan sudah dibandingkan dengan KTP.
7. NIK sudah dibandingkan digit per digit.
8. KTP Perwakilan sudah diperiksa secara visual.
9. Tidak ada data yang ditebak.
10. Setiap PBP diperiksa individual.
""",

    # ==========================================================
    # PERWAKILAN BEDA KK
    # ==========================================================
    "Perwakilan Beda KK": """
ANDA BERTUGAS SEBAGAI VERIFIKATOR DATA BANTUAN PANGAN (BANPANG).

Lakukan verifikasi secara OBJEKTIF, DETAIL, INDIVIDUAL, DAN BERDASARKAN BUKTI yang terdapat pada PDF yang saya upload.

KHUSUS UNTUK:
STATUS PBP = "PERWAKILAN BEDA KK"

============================================================
TUJUAN VERIFIKASI
============================================================

Memastikan bahwa:

1. Data PBP dapat diidentifikasi.
2. Data Perwakilan dapat diidentifikasi.
3. Nama Perwakilan sesuai dengan KTP Perwakilan.
4. NIK Perwakilan sesuai dengan KTP Perwakilan.
5. KTP Perwakilan tersedia dan secara visual merupakan KTP FISIK ASLI.
6. Kecamatan PBP dapat diverifikasi.
7. Kecamatan Perwakilan dapat diverifikasi.
8. Kecamatan PBP dan Kecamatan Perwakilan SAMA.

============================================================
ATURAN UTAMA BEDA KK
============================================================

PBP dan Perwakilan BOLEH berada dalam KK yang BERBEDA.

Jadi:

KK BERBEDA = DIPERBOLEHKAN.

Perbedaan nomor KK TIDAK BOLEH dijadikan alasan TIDAK LOLOS.

Fokus utama verifikasi kategori ini adalah:

PBP
+
Perwakilan
+
KTP Perwakilan
+
Kecamatan PBP
+
Kecamatan Perwakilan.

============================================================
ATURAN KK
============================================================

KK merupakan BUKTI PENDUKUNG, bukan syarat bahwa nomor KK harus sama.

Pada PDF, dokumen KK yang terlihat umumnya merupakan:

"KK PERWAKILAN"

Jika KK yang terlihat adalah KK Perwakilan, catat nomor KK tersebut sebagai:

KK Perwakilan.

Jangan otomatis menganggap nomor tersebut sebagai KK PBP.

Jika KK PBP tidak tersedia dalam PDF:

KK PBP = TIDAK TERSEDIA.

Jangan mengarang atau menebak KK PBP.

Jika nomor KK Perwakilan terlihat jelas, tuliskan nomor KK tersebut.

============================================================
PEMERIKSAAN NAMA PERWAKILAN
============================================================

Bandingkan:

Nama Perwakilan pada Data
VS
Nama pada KTP Perwakilan.

Kategori:

- SESUAI
- BERBEDA
- TIDAK DAPAT DIVERIFIKASI

Jika berbeda secara jelas → TIDAK LOLOS.

Jangan melakukan normalisasi atau asumsi nama.

============================================================
PEMERIKSAAN NIK PERWAKILAN
============================================================

Bandingkan:

NIK Perwakilan pada Data
VS
NIK pada KTP Perwakilan.

Ketentuan:

1. NIK harus 16 digit.
2. Semua digit harus sama.
3. Perbedaan satu digit saja → TIDAK LOLOS.
4. Beberapa digit berbeda → TIDAK LOLOS.
5. Jika NIK tidak terbaca → PERLU VERIFIKASI.
6. Jangan menebak digit yang tidak terlihat.
7. Jika ada perbedaan, tuliskan posisi digit yang berbeda jika dapat ditentukan.

============================================================
PEMERIKSAAN KTP PERWAKILAN
============================================================

KTP Perwakilan WAJIB tersedia.

Periksa secara VISUAL apakah merupakan KTP FISIK ASLI.

Kategori:

- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

Jika KTP fotokopi → TIDAK LOLOS.

Jika KTP tidak ada → TIDAK LOLOS.

Jika KTP tersedia tetapi tidak dapat ditentukan secara visual → PERLU VERIFIKASI.

Jangan menyatakan "ASLI" hanya karena gambar KTP tersedia.

============================================================
PEMERIKSAAN KECAMATAN PBP
============================================================

Ambil Kecamatan PBP dari data/dokumen yang tersedia pada PDF.

Kecamatan harus dapat dibaca secara langsung.

Jangan menyimpulkan Kecamatan dari:

- Kabupaten;
- Provinsi;
- alamat yang tidak lengkap;
- kode wilayah;
- nama Desa/Nagari saja;
- asumsi geografis.

Kategori:

- DAPAT DIVERIFIKASI
- TIDAK DAPAT DIVERIFIKASI

Jika Kecamatan PBP tidak dapat dibaca dengan jelas → PERLU VERIFIKASI.

============================================================
PEMERIKSAAN KECAMATAN PERWAKILAN
============================================================

Verifikasi Kecamatan Perwakilan berdasarkan dokumen yang tersedia, terutama KTP Perwakilan dan/atau dokumen pendukung yang jelas.

Kecamatan harus dapat dibaca secara langsung.

Jangan menyimpulkan Kecamatan dari Kabupaten, Provinsi, alamat yang tidak lengkap, atau asumsi geografis.

Kategori:

- DAPAT DIVERIFIKASI
- TIDAK DAPAT DIVERIFIKASI

Jika Kecamatan Perwakilan tidak dapat dibaca dengan jelas → PERLU VERIFIKASI.

============================================================
PERBANDINGAN KECAMATAN
============================================================

Bandingkan secara langsung:

Kecamatan PBP
VS
Kecamatan Perwakilan.

Kategori:

- SAMA
- BERBEDA
- TIDAK DAPAT DIVERIFIKASI

Jika SAMA → memenuhi syarat.

Jika BERBEDA → TIDAK LOLOS.

Jika tidak dapat ditentukan → PERLU VERIFIKASI.

PENTING:

Jangan menganggap dua nama Kecamatan berbeda sebagai sama hanya karena secara administratif/geografis mungkin memiliki hubungan.

Contoh:

"VII KOTO"
dan
"VII KOTO SUNGAI SARIK"

HARUS diperlakukan sebagai BERBEDA jika PDF tidak memberikan bukti eksplisit bahwa keduanya adalah nama yang sama.

Jangan melakukan normalisasi nama Kecamatan.

============================================================
KETENTUAN DESA / NAGARI
============================================================

Desa/Nagari PBP dan Perwakilan BOLEH berbeda.

Perbedaan Desa/Nagari bukan alasan TIDAK LOLOS selama Kecamatan terbukti sama.

Sebaliknya:

Kabupaten yang sama TIDAK cukup untuk membuktikan Kecamatan sama.

============================================================
PEMERIKSAAN KK PERWAKILAN
============================================================

Jika terdapat KK dalam PDF:

WAJIB periksa secara visual.

Catat:

- Nomor KK Perwakilan.
- Nama Perwakilan.
- NIK Perwakilan jika terlihat.
- Alamat jika terlihat.
- Kecamatan jika terlihat.

Jika nomor KK terlihat jelas → tuliskan nomor KK.

Jika nomor KK tidak terbaca → TIDAK DAPAT DIVERIFIKASI.

Jika KK PBP tidak tersedia → jangan mengarang.

============================================================
DETAIL KK
============================================================

Gunakan:

- SAMA
- BERBEDA — DIPERBOLEHKAN
- TIDAK DAPAT DIVERIFIKASI

Jika hanya KK Perwakilan yang tersedia:

KK PBP = TIDAK TERSEDIA
KK Perwakilan = nomor KK yang terlihat.

Detail KK tidak boleh menyebabkan TIDAK LOLOS hanya karena nomor KK berbeda.

============================================================
KTP PBP
============================================================

KTP PBP TIDAK WAJIB untuk kategori PERWAKILAN BEDA KK.

KTP PBP:

- Tidak ada → bukan otomatis TIDAK LOLOS.
- Fotokopi → bukan otomatis TIDAK LOLOS.
- Ada → dapat digunakan sebagai bukti tambahan.

Jangan menjadikan KTP PBP sebagai syarat wajib.

============================================================
PEMERIKSAAN VISUAL PDF
============================================================

WAJIB memeriksa gambar/dokumen dalam PDF secara VISUAL.

Jangan hanya mengandalkan text layer.

Khusus:

- KTP Perwakilan;
- KK Perwakilan;
- dokumen yang memuat Kecamatan;
- dokumen identitas lainnya.

Baca informasi dari gambar secara langsung.

Jika informasi tidak jelas, jangan menebak.

============================================================
HASIL AKHIR
============================================================

Gunakan HANYA:

1. LOLOS
2. TIDAK LOLOS
3. PERLU VERIFIKASI

LOLOS jika:

1. Nama Perwakilan sesuai dengan KTP.
2. NIK Perwakilan sesuai dengan KTP.
3. NIK 16 digit.
4. KTP Perwakilan tersedia.
5. KTP Perwakilan secara visual merupakan KTP fisik asli.
6. Kecamatan PBP dapat diverifikasi.
7. Kecamatan Perwakilan dapat diverifikasi.
8. Kecamatan PBP = Kecamatan Perwakilan.
9. Tidak terdapat bukti lain yang bertentangan.

TIDAK LOLOS jika:

- Nama Perwakilan terbukti berbeda;
- NIK Perwakilan terbukti berbeda;
- NIK tidak memenuhi ketentuan;
- KTP Perwakilan fotokopi;
- KTP Perwakilan tidak ada;
- Kecamatan PBP dan Perwakilan terbukti berbeda.

PERLU VERIFIKASI jika:

- Kecamatan tidak dapat dibaca;
- NIK tidak dapat dibaca;
- nama tidak dapat dibaca;
- KTP tidak dapat ditentukan;
- atau bukti lainnya tidak cukup untuk menentukan hasil.

============================================================
FORMAT OUTPUT
============================================================

Buat tabel:

No | No PBP | Nama PBP | NIK PBP | Kecamatan PBP | Nama Perwakilan | Nama KTP Perwakilan | Detail Nama | NIK Perwakilan | NIK KTP Perwakilan | Detail NIK | KK PBP | KK Perwakilan | Detail KK | Kecamatan Perwakilan | Detail Kecamatan | KTP Perwakilan | HASIL | ALASAN

============================================================
DETAIL KECAMATAN
============================================================

Gunakan:

- SAMA
- BERBEDA
- TIDAK DAPAT DIVERIFIKASI

============================================================
DETAIL KK
============================================================

Gunakan:

- SAMA
- BERBEDA — DIPERBOLEHKAN
- TIDAK DAPAT DIVERIFIKASI

============================================================
RECHECK
============================================================

Sebelum memberikan hasil akhir, lakukan pemeriksaan ulang:

1. Nama Perwakilan sudah dibandingkan dengan KTP.
2. NIK sudah dibandingkan digit per digit.
3. NIK sudah dipastikan 16 digit.
4. KTP Perwakilan sudah diperiksa secara visual.
5. Kecamatan PBP sudah dibaca dari bukti yang tersedia.
6. Kecamatan Perwakilan sudah dibaca dari bukti yang tersedia.
7. Kecamatan dibandingkan secara langsung.
8. Jangan menyamakan nama Kecamatan yang berbeda tanpa bukti eksplisit.
9. Perbedaan KK TIDAK boleh dijadikan alasan TIDAK LOLOS.
10. Desa/Nagari yang berbeda tetapi Kecamatan sama tetap dapat LOLOS.
11. Kabupaten yang sama saja tidak cukup untuk menyatakan Kecamatan sama.
12. KK yang terlihat dibaca sebagai KK Perwakilan jika memang dokumen tersebut adalah KK Perwakilan.
13. Jangan mengarang KK PBP jika tidak tersedia.
14. Jangan mengarang atau menebak data apa pun.
15. Setiap PBP harus diverifikasi secara INDIVIDUAL.
16. Pastikan tidak ada PBP yang terlewat.
"""
}

class VerifikasiBanpangPage(ctk.CTkFrame):

    def __init__(self, master, status_bar=None):
        super().__init__(master, fg_color=Colors.WORKSPACE_BG)
        self.status_bar = status_bar
        self.banpang_driver = None

        self.collection_rows = []
        self.output_folder = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "Verifikasi Banpang"
        )
        os.makedirs(self.output_folder, exist_ok=True)
        self.pbp_photo_folder = os.path.join(
            self.output_folder,
            "Foto_PBP"
        )

        os.makedirs(
            self.pbp_photo_folder,
            exist_ok=True
        )
        self.output_pdf_path = os.path.join(
            self.output_folder,
            "Hasil_Banpang.pdf"
        )

        self.configure_layout()
        self.create_header()
        self.create_workflow()
        self.create_main_content()

    # ==========================================================
    # LAYOUT
    # ==========================================================
    def configure_layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 12)
        )
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        title_area = ctk.CTkFrame(header, fg_color="transparent")
        title_area.grid(row=0, column=0, sticky="w")

        icon_box = ctk.CTkFrame(
            title_area,
            width=80,
            height=80,
            corner_radius=24,
            fg_color=Colors.MERGE_BG
        )
        icon_box.pack(side="left", padx=(0, 15))
        icon_box.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_box,
            text="",
            image=Icons.BULOG_LOGO
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        text_area = ctk.CTkFrame(title_area, fg_color="transparent")
        text_area.pack(side="left")

        title = ctk.CTkLabel(
            text_area,
            text="Verifikasi Banpang",
            font=Fonts.PAGE_TITLE,
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            text_area,
            text="Otomatisasi pengambilan data dan pembuatan PDF dari website Banpang.",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(3, 0))

        info_card = ctk.CTkFrame(
            header,
            width=360,
            height=82,
            corner_radius=16,
            fg_color="#EFF6FF",
            border_width=1,
            border_color=Colors.BORDER
        )
        info_card.grid(row=0, column=1, sticky="e", padx=(20, 0))
        info_card.grid_propagate(False)

        info_title = ctk.CTkLabel(
            info_card,
            text="ⓘ  Petunjuk",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=Colors.PRIMARY
        )
        info_title.pack(anchor="w", padx=16, pady=(10, 2))

        info_text = ctk.CTkLabel(
            info_card,
            text="Filter dilakukan manual di website, lalu aplikasi mengambil data dan foto.",
            font=ctk.CTkFont(size=11),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=325,
            justify="left"
        )
        info_text.pack(anchor="w", padx=16)

    def create_workflow(self):
        workflow = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=18,
            border_width=1,
            border_color=Colors.BORDER
        )
        workflow.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15)
        )

        for column in range(5):
            workflow.grid_columnconfigure(column, weight=1)

        steps = [
            ("1", "Buka Website"),
            ("2", "Persiapan Filter Manual"),
            ("3", "Pengambilan Data & PDF"),
            ("4", "Prompt Verifikasi"),
            ("5", "Hasil")
        ]

        self.workflow_steps = {}

        for index, (number, title) in enumerate(steps):
            step = ctk.CTkFrame(workflow, fg_color="transparent")
            step.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=5,
                pady=8
            )

            circle = ctk.CTkFrame(
                step,
                width=38,
                height=38,
                corner_radius=19,
                fg_color=Colors.PRIMARY if index == 0 else "#E8EEF7"
            )
            circle.pack(pady=(2, 5))
            circle.pack_propagate(False)

            number_label = ctk.CTkLabel(
                circle,
                text=number,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#FFFFFF" if index == 0 else Colors.TEXT_SECONDARY
            )
            number_label.place(relx=0.5, rely=0.5, anchor="center")

            title_label = ctk.CTkLabel(
                step,
                text=title,
                font=ctk.CTkFont(
                    size=11,
                    weight="bold" if index == 0 else "normal"
                ),
                text_color=Colors.PRIMARY if index == 0 else Colors.TEXT_MUTED,
                wraplength=155,
                justify="center"
            )
            title_label.pack()

            self.workflow_steps[index] = {
                "frame": step,
                "circle": circle,
                "number": number_label,
                "title": title_label
            }

    # ==========================================================
    # MAIN CONTENT
    # ==========================================================
    def create_main_content(self):
        container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 5)
        )
        container.grid_columnconfigure(0, weight=1)

        self.create_website_card(container)
        self.create_manual_preparation_card(container)
        self.create_collection_card(container)
        self.create_prompt_verification_card(container)
        self.create_result_card(container)

    # ==========================================================
    # CARD 1 - WEBSITE
    # ==========================================================
    def create_website_card(self, parent):
        card = self.create_card(parent)
        card.pack(fill="x", padx=15, pady=(0, 12))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=22, pady=18)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)
        content.grid_columnconfigure(2, weight=0)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            left,
            text="①  Buka Website Banpang",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(anchor="w")

        website = ctk.CTkLabel(
            left,
            text="https://banpang.bulog.co.id",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=Colors.PRIMARY
        )
        website.pack(anchor="w", pady=(5, 2))

        description = ctk.CTkLabel(
            left,
            text="Browser akan dibuka untuk proses verifikasi Banpang.",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY
        )
        description.pack(anchor="w")

        self.browser_status = ctk.CTkLabel(
            content,
            text="● Browser belum dibuka",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#DC2626"
        )
        self.browser_status.grid(
            row=0,
            column=1,
            padx=(20, 20)
        )

        self.open_button = ctk.CTkButton(
            content,
            text="Buka Website",
            width=165,
            height=42,
            corner_radius=10,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.open_banpang_website
        )
        self.open_button.grid(row=0, column=2)

    # ==========================================================
    # CARD 2 - MANUAL FILTER
    # ==========================================================
    def create_manual_preparation_card(self, parent):
        card = self.create_card(parent)
        card.pack(fill="x", padx=15, pady=(0, 12))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=22, pady=18)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="ew")

        title_row = ctk.CTkFrame(left, fg_color="transparent")
        title_row.pack(fill="x")

        title = ctk.CTkLabel(
            title_row,
            text="②  Persiapan Filter Manual",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(side="left")

        badge = self.create_badge(title_row, "MANUAL", color="#F59E0B", bg="#FFF7E6")
        badge.pack(side="left", padx=(12, 0))

        instructions = [
            "Pilih Tahun, Bulan, Provinsi, Kabupaten, Kecamatan, dan Kelurahan di website.",
            "Pilih seluruh filter PBP sesuai kebutuhan.",
            "Pilih Baris per halaman = 500 agar seluruh data tampil sekaligus.",
            "Klik Filter dan pastikan tabel Daftar PBP tampil lengkap."
        ]

        instruction_frame = ctk.CTkFrame(
            left,
            fg_color="transparent"
        )
        instruction_frame.pack(fill="x", pady=(8, 0))

        for index, text in enumerate(instructions, start=1):
            row = ctk.CTkFrame(instruction_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            num = ctk.CTkLabel(
                row,
                text=str(index),
                width=24,
                height=24,
                corner_radius=12,
                fg_color="#EFF6FF",
                text_color=Colors.PRIMARY,
                font=ctk.CTkFont(size=10, weight="bold")
            )
            num.pack(side="left")

            label = ctk.CTkLabel(
                row,
                text=text,
                font=ctk.CTkFont(size=12),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w"
            )
            label.pack(side="left", padx=(8, 0))

        tips = ctk.CTkFrame(
            content,
            width=250,
            corner_radius=14,
            fg_color="#F8FAFC",
            border_width=1,
            border_color=Colors.BORDER
        )
        tips.grid(row=0, column=1, sticky="nse", padx=(18, 0))
        tips.grid_propagate(False)

        tips_title = ctk.CTkLabel(
            tips,
            text="💡  Tips",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Colors.PRIMARY
        )
        tips_title.pack(anchor="w", padx=14, pady=(10, 4))

        tips_text = ctk.CTkLabel(
            tips,
            text="Gunakan 500 baris per halaman agar data tampil sekaligus dan tidak perlu pagination.",
            font=ctk.CTkFont(size=11),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=220,
            justify="left"
        )
        tips_text.pack(anchor="w", padx=14, pady=(0, 12))

    # ==========================================================
    # CARD 3 - DATA & OUTPUT
    # ==========================================================
    def create_collection_card(self, parent):
        card = self.create_card(parent)
        card.pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )

        # ======================================================
        # HEADER
        # ======================================================

        header = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=22,
            pady=(16, 6)
        )

        title = ctk.CTkLabel(
            header,
            text="③  Pengambilan Data & Pembuatan Output",
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(side="left")

        badge = self.create_badge(
            header,
            "OTOMATIS"
        )
        badge.pack(
            side="left",
            padx=(12, 0)
        )

        self.collection_status = ctk.CTkLabel(
            header,
            text="● Menunggu data website siap",
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            ),
            text_color=Colors.TEXT_MUTED
        )
        self.collection_status.pack(
            side="right"
        )

        # ======================================================
        # DESCRIPTION
        # ======================================================

        description = ctk.CTkLabel(
            card,
            text=(
                "Aplikasi membaca data PBP dan mengambil Foto KTP "
                "serta Foto PBP. PDF hanya berisi data dan Foto KTP, "
                "sedangkan Foto PBP disimpan terpisah ke folder yang dipilih."
            ),
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            justify="left",
            wraplength=1050
        )
        description.pack(
            fill="x",
            padx=22,
            pady=(0, 10)
        )

        # ======================================================
        # KPI STATISTICS
        # ======================================================

        stats = ctk.CTkFrame(
            card,
            fg_color="#F8FAFC",
            corner_radius=14,
            border_width=1,
            border_color=Colors.BORDER
        )
        stats.pack(
            fill="x",
            padx=22,
            pady=(0, 12)
        )

        stat_items = [
            (
                "TOTAL PBP",
                "0",
                Colors.PRIMARY
            ),
            (
                "DATA TERBACA",
                "0 / 0",
                "#16A34A"
            ),
            (
                "FOTO KTP",
                "0 / 0",
                Colors.PRIMARY
            ),
            (
                "FOTO PBP",
                "0 / 0",
                "#7C3AED"
            ),
            (
                "PDF DIBUAT",
                "0 / 0",
                "#DC2626"
            )
        ]

        for index in range(len(stat_items)):
            stats.grid_columnconfigure(
                index,
                weight=1
            )

        for index, (
            label,
            value,
            value_color
        ) in enumerate(stat_items):

            item = ctk.CTkFrame(
                stats,
                fg_color="transparent"
            )

            item.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=3,
                pady=10
            )

            value_label = ctk.CTkLabel(
                item,
                text=value,
                font=ctk.CTkFont(
                    size=21,
                    weight="bold"
                ),
                text_color=value_color
            )

            value_label.pack(
                pady=(2, 1)
            )

            label_widget = ctk.CTkLabel(
                item,
                text=label,
                font=ctk.CTkFont(
                    size=9,
                    weight="bold"
                ),
                text_color=Colors.TEXT_SECONDARY
            )

            label_widget.pack()

            # Simpan reference label untuk update realtime
            if label == "TOTAL PBP":
                self.total_pbp_value = value_label

            elif label == "DATA TERBACA":
                self.data_read_value = value_label

            elif label == "FOTO KTP":
                self.ktp_value = value_label

            elif label == "FOTO PBP":
                self.pbp_photo_value = value_label

            elif label == "PDF DIBUAT":
                self.pdf_value = value_label

        # ======================================================
        # LOWER CONTENT
        # ======================================================

        lower = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        lower.pack(
            fill="x",
            padx=22,
            pady=(0, 10)
        )

        lower.grid_columnconfigure(
            0,
            weight=1
        )

        lower.grid_columnconfigure(
            1,
            weight=0
        )

        # ======================================================
        # LEFT - PROGRESS PANEL
        # ======================================================

        progress_panel = ctk.CTkFrame(
            lower,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color=Colors.BORDER
        )

        progress_panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 14)
        )

        progress_title = ctk.CTkLabel(
            progress_panel,
            text="Progress Pengambilan Data",
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color=Colors.TEXT_PRIMARY
        )

        progress_title.pack(
            anchor="w",
            padx=16,
            pady=(12, 6)
        )

        # Progress bar
        self.collection_progress = ctk.CTkProgressBar(
            progress_panel,
            height=10,
            corner_radius=5
        )

        self.collection_progress.pack(
            fill="x",
            padx=16,
            pady=(2, 5)
        )

        self.collection_progress.set(0)

        # Progress info
        progress_info = ctk.CTkFrame(
            progress_panel,
            fg_color="transparent"
        )

        progress_info.pack(
            fill="x",
            padx=16,
            pady=(0, 3)
        )

        self.collection_percentage = ctk.CTkLabel(
            progress_info,
            text="0%",
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color=Colors.TEXT_PRIMARY
        )

        self.collection_percentage.pack(
            side="left"
        )

        self.collection_page_info = ctk.CTkLabel(
            progress_info,
            text="Data: 0 / 0",
            font=ctk.CTkFont(
                size=10
            ),
            text_color=Colors.TEXT_SECONDARY
        )

        self.collection_page_info.pack(
            side="right"
        )

        # Status information
        self.data_info_label = ctk.CTkLabel(
            progress_panel,
            text="Belum ada data yang dibaca.",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            justify="left"
        )

        self.data_info_label.pack(
            fill="x",
            padx=16,
            pady=(2, 12)
        )

        # ======================================================
        # RIGHT - OUTPUT SETTINGS
        # ======================================================

        output = ctk.CTkFrame(
            lower,
            width=390,
            corner_radius=14,
            fg_color="#FFFFFF",
            border_width=1,
            border_color=Colors.BORDER
        )

        output.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        output.grid_propagate(False)

        output_title = ctk.CTkLabel(
            output,
            text="⚙  Pengaturan Output",
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color=Colors.TEXT_PRIMARY
        )

        output_title.pack(
            anchor="w",
            padx=14,
            pady=(10, 7)
        )

        # ======================================================
        # NAMA FILE PDF
        # ======================================================

        filename_label = ctk.CTkLabel(
            output,
            text="Nama File PDF",
            font=ctk.CTkFont(
                size=10
            ),
            text_color=Colors.TEXT_SECONDARY
        )

        filename_label.pack(
            anchor="w",
            padx=14
        )

        self.pdf_filename_entry = ctk.CTkEntry(
            output,
            height=34,
            corner_radius=8,
            placeholder_text="Hasil_Banpang.pdf"
        )

        self.pdf_filename_entry.pack(
            fill="x",
            padx=14,
            pady=(3, 7)
        )

        self.pdf_filename_entry.insert(
            0,
            "Hasil_Banpang.pdf"
        )

        # ======================================================
        # FOLDER PDF
        # ======================================================

        folder_label = ctk.CTkLabel(
            output,
            text="Lokasi Penyimpanan PDF",
            font=ctk.CTkFont(
                size=10
            ),
            text_color=Colors.TEXT_SECONDARY
        )

        folder_label.pack(
            anchor="w",
            padx=14
        )

        folder_row = ctk.CTkFrame(
            output,
            fg_color="transparent"
        )

        folder_row.pack(
            fill="x",
            padx=14,
            pady=(3, 5)
        )

        folder_row.grid_columnconfigure(
            0,
            weight=1
        )

        folder_row.grid_columnconfigure(
            1,
            weight=0
        )

        self.output_folder_entry = ctk.CTkEntry(
            folder_row,
            height=34,
            corner_radius=8
        )

        self.output_folder_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 7)
        )

        self.output_folder_entry.insert(
            0,
            self.output_folder
        )

        browse_button = ctk.CTkButton(
            folder_row,
            text="📁",
            width=42,
            height=34,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color="#F5F8FC",
            border_width=1,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            command=self.choose_output_folder
        )

        browse_button.grid(
            row=0,
            column=1
        )

        # ======================================================
        # FOLDER FOTO PBP
        # ======================================================

        pbp_folder_label = ctk.CTkLabel(
            output,
            text="Lokasi Foto PBP",
            font=ctk.CTkFont(
                size=10
            ),
            text_color=Colors.TEXT_SECONDARY
        )

        pbp_folder_label.pack(
            anchor="w",
            padx=14,
            pady=(3, 0)
        )

        pbp_folder_row = ctk.CTkFrame(
            output,
            fg_color="transparent"
        )

        pbp_folder_row.pack(
            fill="x",
            padx=14,
            pady=(3, 7)
        )

        pbp_folder_row.grid_columnconfigure(
            0,
            weight=1
        )

        pbp_folder_row.grid_columnconfigure(
            1,
            weight=0
        )

        self.pbp_photo_folder_entry = ctk.CTkEntry(
            pbp_folder_row,
            height=34,
            corner_radius=8
        )

        self.pbp_photo_folder_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 7)
        )

        self.pbp_photo_folder_entry.insert(
            0,
            self.pbp_photo_folder
        )

        pbp_browse_button = ctk.CTkButton(
            pbp_folder_row,
            text="📁",
            width=42,
            height=34,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color="#F5F8FC",
            border_width=1,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            command=self.choose_pbp_photo_folder
        )

        pbp_browse_button.grid(
            row=0,
            column=1
        )

        # ======================================================
        # CHECKBOX
        # ======================================================

        self.open_pdf_after_checkbox = ctk.CTkCheckBox(
            output,
            text="Buka PDF setelah selesai",
            font=ctk.CTkFont(
                size=10
            ),
            text_color=Colors.TEXT_SECONDARY
        )

        self.open_pdf_after_checkbox.pack(
            anchor="w",
            padx=14,
            pady=(2, 10)
        )

        self.open_pdf_after_checkbox.select()

        # ======================================================
        # BOTTOM ACTION
        # ======================================================

        bottom = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        bottom.pack(
            fill="x",
            padx=22,
            pady=(0, 16)
        )

        bottom.grid_columnconfigure(
            0,
            weight=1
        )

        bottom.grid_columnconfigure(
            1,
            weight=0
        )

        action_info = ctk.CTkFrame(
            bottom,
            fg_color="transparent"
        )

        action_info.grid(
            row=0,
            column=0,
            sticky="w"
        )

        action_title = ctk.CTkLabel(
            action_info,
            text="Output:",
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            ),
            text_color=Colors.TEXT_PRIMARY
        )

        action_title.pack(
            side="left"
        )

        action_description = ctk.CTkLabel(
            action_info,
            text="PDF + Foto KTP  •  Foto PBP tersimpan terpisah",
            font=ctk.CTkFont(
                size=10
            ),
            text_color=Colors.TEXT_SECONDARY
        )

        action_description.pack(
            side="left",
            padx=(6, 0)
        )

        self.start_collection_button = ctk.CTkButton(
            bottom,
            text="▶  Mulai Pengambilan Data",
            width=250,
            height=42,
            corner_radius=9,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            command=self.start_data_collection
        )

        self.start_collection_button.grid(
            row=0,
            column=1,
            sticky="e"
        )

    # ==========================================================
    # CARD 4 - PROMPT VERIFIKASI
    # ==========================================================
    def create_prompt_verification_card(self, parent):
        card = self.create_card(parent)
        card.pack(fill="x", padx=15, pady=(0, 12))

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=22, pady=(16, 8))

        title = ctk.CTkLabel(
            header,
            text="④  Prompt Verifikasi ChatGPT",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(side="left")

        badge = self.create_badge(header, "SIAP COPY", color="#16A34A", bg="#ECFDF3")
        badge.pack(side="left", padx=(12, 0))

        description = ctk.CTkLabel(
            card,
            text="Pilih kategori PBP, salin prompt, buka ChatGPT, lalu upload PDF hasil pengambilan data.",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )
        description.pack(fill="x", padx=22, pady=(0, 10))

        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.pack(fill="x", padx=22, pady=(0, 10))
        controls.grid_columnconfigure(1, weight=1)

        label = ctk.CTkLabel(
            controls,
            text="Kategori PBP",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.prompt_category = ctk.CTkComboBox(
            controls,
            values=list(PROMPT_VERIFIKASI.keys()),
            width=230,
            height=36,
            corner_radius=9,
            command=self._on_prompt_category_changed
        )
        self.prompt_category.grid(row=0, column=1, sticky="w")
        self.prompt_category.set("Normal")

        copy_button = ctk.CTkButton(
            controls,
            text="📋  Salin Prompt",
            width=145,
            height=36,
            corner_radius=9,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.copy_verification_prompt
        )
        copy_button.grid(row=0, column=2, padx=(10, 6))
        self.copy_prompt_button = copy_button

        open_button = ctk.CTkButton(
            controls,
            text="↗  Buka ChatGPT",
            width=135,
            height=36,
            corner_radius=9,
            fg_color="#FFFFFF",
            hover_color="#F5F8FC",
            border_width=1,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.open_chatgpt
        )
        open_button.grid(row=0, column=3)

        self.prompt_status = ctk.CTkLabel(
            card,
            text="Prompt Normal siap digunakan.",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )
        self.prompt_status.pack(fill="x", padx=22, pady=(0, 6))

        prompt_box = ctk.CTkTextbox(
            card,
            height=310,
            corner_radius=12,
            border_width=1,
            border_color=Colors.BORDER,
            fg_color="#F8FAFC",
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        prompt_box.pack(fill="x", padx=22, pady=(0, 16))
        self.prompt_textbox = prompt_box
        self._set_prompt_text("Normal")

    def _set_prompt_text(self, category):
        prompt = PROMPT_VERIFIKASI.get(category, "")
        self.prompt_textbox.configure(state="normal")
        self.prompt_textbox.delete("1.0", "end")
        self.prompt_textbox.insert("1.0", prompt)
        self.prompt_textbox.configure(state="disabled")
        self.prompt_status.configure(
            text=f"Prompt {category} siap digunakan."
        )

    def _on_prompt_category_changed(self, category):
        self._set_prompt_text(category)

    def copy_verification_prompt(self):
        category = self.prompt_category.get()
        prompt = PROMPT_VERIFIKASI.get(category, "")
        if not prompt:
            return

        try:
            self.clipboard_clear()
            self.clipboard_append(prompt)
            self.update()
            self.prompt_status.configure(
                text=f"✓ Prompt {category} berhasil disalin ke clipboard.",
                text_color="#16A34A"
            )
            print(f"Prompt {category} berhasil disalin.")
        except Exception as error:
            self.prompt_status.configure(
                text=f"Gagal menyalin prompt: {error}",
                text_color="#DC2626"
            )

    def open_chatgpt(self):
        try:
            webbrowser.open("https://chatgpt.com/")
            self.prompt_status.configure(
                text="ChatGPT dibuka. Upload PDF lalu paste prompt yang sudah disalin.",
                text_color=Colors.PRIMARY
            )
        except Exception as error:
            self.prompt_status.configure(
                text=f"Gagal membuka ChatGPT: {error}",
                text_color="#DC2626"
            )

    # ==========================================================
    # CARD 5 - RESULT
    # ==========================================================
    def create_result_card(self, parent):
        card = self.create_card(parent)
        card.pack(fill="x", padx=15, pady=(0, 20))

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=22, pady=(16, 8))

        title = ctk.CTkLabel(
            header,
            text="⑤  Hasil",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(side="left")

        self.result_badge = self.create_badge(
            header,
            "MENUNGGU",
            color=Colors.TEXT_MUTED,
            bg="#F1F5F9"
        )
        self.result_badge.pack(side="left", padx=(12, 0))

        subtitle = ctk.CTkLabel(
            header,
            text="Hasil pengambilan data dan file PDF akan ditampilkan di sini.",
            font=Fonts.PAGE_SUBTITLE,
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle.pack(side="left", padx=(15, 0))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=22, pady=(0, 16))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        empty = ctk.CTkFrame(
            body,
            height=145,
            corner_radius=12,
            fg_color="#FFFFFF",
            border_width=1,
            border_color=Colors.BORDER
        )
        empty.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        empty.grid_propagate(False)

        empty_icon = ctk.CTkLabel(
            empty,
            text="▧",
            font=ctk.CTkFont(size=36),
            text_color=Colors.TEXT_MUTED
        )
        empty_icon.pack(pady=(22, 2))

        self.result_empty_title = ctk.CTkLabel(
            empty,
            text="Belum ada hasil",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        self.result_empty_title.pack()

        self.result_empty_text = ctk.CTkLabel(
            empty,
            text="Jalankan proses pengambilan data terlebih dahulu.",
            font=ctk.CTkFont(size=10),
            text_color=Colors.TEXT_SECONDARY
        )
        self.result_empty_text.pack(pady=(2, 0))

        summary = ctk.CTkFrame(
            body,
            corner_radius=12,
            fg_color="#F8FAFC",
            border_width=1,
            border_color=Colors.BORDER
        )
        summary.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        summary_title = ctk.CTkLabel(
            summary,
            text="◉  Ringkasan Hasil",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        summary_title.pack(anchor="w", padx=14, pady=(10, 8))

        kpi_row = ctk.CTkFrame(summary, fg_color="transparent")
        kpi_row.pack(fill="x", padx=10)
        for index in range(3):
            kpi_row.grid_columnconfigure(index, weight=1)

        self.result_pbp_value = self.create_result_kpi(
            kpi_row, 0, "0", "PBP Berhasil"
        )
        self.result_pages_value = self.create_result_kpi(
            kpi_row, 1, "0", "Halaman Data"
        )
        self.result_total_pages_value = self.create_result_kpi(
            kpi_row, 2, "0", "Halaman Total"
        )

        file_row = ctk.CTkFrame(summary, fg_color="transparent")
        file_row.pack(fill="x", padx=12, pady=(10, 12))
        file_row.grid_columnconfigure(0, weight=1)
        file_row.grid_columnconfigure(1, weight=0)
        file_row.grid_columnconfigure(2, weight=0)

        self.result_file_label = ctk.CTkLabel(
            file_row,
            text="-  PDF searchable / OCR",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )
        self.result_file_label.grid(row=0, column=0, sticky="w", padx=(4, 8))

        self.open_folder_button = ctk.CTkButton(
            file_row,
            text="📁  Buka Folder",
            width=125,
            height=36,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color="#F5F8FC",
            border_width=1,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            command=self.open_output_folder,
            state="disabled"
        )
        self.open_folder_button.grid(row=0, column=1, padx=4)

        self.open_pdf_button = ctk.CTkButton(
            file_row,
            text="▧  Buka PDF",
            width=115,
            height=36,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color="#F5F8FC",
            border_width=1,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            command=self.open_output_pdf,
            state="disabled"
        )
        self.open_pdf_button.grid(row=0, column=2, padx=(4, 0))

    # ==========================================================
    # DATA COLLECTION - CURRENT STAGE
    # ==========================================================
    def start_data_collection(self):
        """Mengambil seluruh PBP yang tampil, foto KTP/PBP, lalu membuat PDF."""
        if self.banpang_driver is None:
            try:
                self.banpang_driver = BanpangBrowserService.connect_driver()
            except Exception as error:
                self.collection_status.configure(
                    text="● Browser belum terhubung",
                    text_color="#DC2626"
                )
                self.data_info_label.configure(text=f"Gagal terhubung ke browser: {error}")
                return

        if not self.banpang_driver:
            self.collection_status.configure(
                text="● Browser belum terhubung",
                text_color="#DC2626"
            )
            return

        self.start_collection_button.configure(state="disabled")
        self.collection_status.configure(
            text="● Menyiapkan pengambilan data...",
            text_color=Colors.TEXT_SECONDARY
        )
        self.collection_progress.set(0.02)
        self.collection_percentage.configure(text="2%")
        self.update_idletasks()

        threading.Thread(
            target=self._collection_worker,
            daemon=True
        ).start()

    @staticmethod
    def _extract_pbp_nik(row):
        """Mengambil NIK 16 digit dari data satu row PBP."""
        text = str(row.get("nama", "") or "")
        match = re.search(r"\b\d{16}\b", text)
        return match.group(0) if match else ""

    def _collection_worker(self):
        try:
            driver = self.banpang_driver

            print("\n" + "=" * 70)
            print("=== MULAI PENGAMBILAN DATA & PDF ===")
            print("=" * 70)

            # ==========================================================
            # 1. BACA TABEL PBP YANG SEDANG TAMPIL
            # ==========================================================
            rows = self.read_visible_pbp_table(driver)
            total_text = self.get_total_pbp_from_website(driver)

            try:
                total_number = (
                    int(re.sub(r"[^0-9]", "", total_text))
                    if total_text
                    else len(rows)
                )
            except Exception:
                total_number = len(rows)

            print(f"Jumlah row PBP ditemukan : {len(rows)}")
            print(f"Total PBP website        : {total_number}")

            # ==========================================================
            # 2. GUNAKAN HANYA DATA PBP YANG SEDANG TAMPIL
            # ==========================================================
            print(
                f"Mode pengambilan: hanya memproses {len(rows)} "
                f"PBP yang sedang tampil pada halaman website."
            )

            if not rows:
                raise Exception(
                    "Tidak ada data PBP yang sedang tampil pada tabel website."
                )

            self._ui_call(
                self._prepare_collection_ui,
                total_number,
                len(rows)
            )

            # ==========================================================
            # 3. SIAPKAN RECORD
            # ==========================================================
            records = []

            total = len(rows)

            ktp_success = 0
            pbp_success = 0

            # ==========================================================
            # 4. PROSES SETIAP PBP
            # ==========================================================
            for index, row in enumerate(rows, start=1):

                no_pbp = str(row.get("no pbp", "")).strip()
                expected_nik = self._extract_pbp_nik(row)

                print("\n" + "-" * 60)
                print(f"Urutan website : {index}")
                print(f"No PBP : {no_pbp}")
                print(f"NIK target : {expected_nik or '(tidak ditemukan)'}")
                print("-" * 60)
                print(f"PBP {index}/{total}")
                print(f"No PBP : {no_pbp}")
                print("-" * 60)

                record = dict(row)
                record["collection_order"] = index
                record["target_nik"] = expected_nik

                # Pastikan field foto selalu ada
                record["foto_ktp_bytes"] = None
                record["foto_pbp_bytes"] = None

                self._ui_call(
                    self._update_collection_progress,
                    index - 1,
                    total,
                    f"Mengambil data PBP {index}/{total}: {no_pbp}"
                )

                # ======================================================
                # 4A. AMBIL FOTO KTP
                # ======================================================
                try:
                    print("Mengambil Foto KTP...")

                    result_ktp = (
                        BanpangBrowserService.capture_photo_from_pbp_row(
                            driver,
                            no_pbp,
                            0,
                            expected_nik=expected_nik
                        )
                    )

                    print(
                        "DEBUG result KTP:",
                        type(result_ktp),
                        "tuple=",
                        isinstance(result_ktp, tuple)
                    )

                    # Method capture mengembalikan:
                    # (image_bytes, image_url)
                    if isinstance(result_ktp, tuple):
                        foto_ktp, url_ktp = result_ktp
                    else:
                        foto_ktp = result_ktp
                        url_ktp = ""

                    # Pastikan benar-benar bytes
                    if foto_ktp is not None:
                        if isinstance(foto_ktp, bytes):
                            record["foto_ktp_bytes"] = foto_ktp
                        elif isinstance(foto_ktp, bytearray):
                            record["foto_ktp_bytes"] = bytes(foto_ktp)
                        else:
                            raise TypeError(
                                f"Format Foto KTP tidak dikenali: "
                                f"{type(foto_ktp)}"
                            )

                    if record["foto_ktp_bytes"]:
                        ktp_success += 1

                        print(
                            f"✓ Foto KTP berhasil: "
                            f"{len(record['foto_ktp_bytes']):,} bytes"
                        )

                        if url_ktp:
                            print(f"URL KTP: {url_ktp[:120]}...")

                    else:
                        print("✗ Foto KTP kosong.")

                except Exception as error:
                    print(
                        f"✗ Foto KTP gagal untuk {no_pbp}: "
                        f"{error}"
                    )

                self._ui_call(
                    self._update_photo_counters,
                    ktp_success,
                    pbp_success,
                    index,
                    total
                )

                # ======================================================
                # 4B. AMBIL FOTO PBP
                # ======================================================
                try:
                    print("Mengambil Foto PBP...")

                    result_pbp = (
                        BanpangBrowserService.capture_photo_from_pbp_row(
                            driver,
                            no_pbp,
                            1,
                            expected_nik=expected_nik
                        )
                    )

                    print(
                        "DEBUG result PBP:",
                        type(result_pbp),
                        "tuple=",
                        isinstance(result_pbp, tuple)
                    )

                    # Method capture mengembalikan:
                    # (image_bytes, image_url)
                    if isinstance(result_pbp, tuple):
                        foto_pbp, url_pbp = result_pbp
                    else:
                        foto_pbp = result_pbp
                        url_pbp = ""

                    # Pastikan benar-benar bytes
                    if foto_pbp is not None:
                        if isinstance(foto_pbp, bytes):
                            record["foto_pbp_bytes"] = foto_pbp
                        elif isinstance(foto_pbp, bytearray):
                            record["foto_pbp_bytes"] = bytes(foto_pbp)
                        else:
                            raise TypeError(
                                f"Format Foto PBP tidak dikenali: "
                                f"{type(foto_pbp)}"
                            )

                    if record["foto_pbp_bytes"]:
                        pbp_success += 1

                        print(
                            f"✓ Foto PBP berhasil: "
                            f"{len(record['foto_pbp_bytes']):,} bytes"
                        )

                        # ======================================================
                        # SIMPAN FOTO PBP KE FOLDER YANG DIPILIH USER
                        # ======================================================
                        try:
                            pbp_photo_path = self.save_pbp_photo(
                                record["foto_pbp_bytes"],
                                index,
                                no_pbp
                            )

                            record["foto_pbp_path"] = pbp_photo_path

                            print(
                                f"✓ Path Foto PBP: {pbp_photo_path}"
                            )

                        except Exception as save_error:
                            record["foto_pbp_path"] = None

                            print(
                                f"✗ Gagal menyimpan Foto PBP "
                                f"{no_pbp}: {save_error}"
                            )

                        if url_pbp:
                            print(f"URL PBP: {url_pbp[:120]}...")

                    else:
                        print("✗ Foto PBP kosong.")

                except Exception as error:
                    print(
                        f"✗ Foto PBP gagal untuk {no_pbp}: "
                        f"{error}"
                    )

                # ======================================================
                # 4C. VALIDASI RECORD SEBELUM DISIMPAN
                # ======================================================
                print("\nVALIDASI FOTO:")

                if record["foto_ktp_bytes"]:
                    print(
                        f"  Foto KTP : "
                        f"OK ({len(record['foto_ktp_bytes']):,} bytes)"
                    )
                else:
                    print("  Foto KTP : KOSONG")

                if record["foto_pbp_bytes"]:
                    print(
                        f"  Foto PBP : "
                        f"OK ({len(record['foto_pbp_bytes']):,} bytes)"
                    )
                else:
                    print("  Foto PBP : KOSONG")

                # Simpan record SETELAH data + dua foto untuk PBP ini selesai.
                # Tidak ada foto dari PBP lain yang boleh masuk ke record ini.
                record["photo_pair_valid"] = bool(
                    record.get("foto_ktp_bytes")
                    and record.get("foto_pbp_bytes")
                )

                if record["photo_pair_valid"]:
                    print(f"✓ RECORD PBP {index} VALID dan siap disimpan.")
                else:
                    print(f"⚠ RECORD PBP {index} disimpan dengan status FOTO TIDAK LENGKAP.")

                records.append(record)

                self._ui_call(
                    self._update_photo_counters,
                    ktp_success,
                    pbp_success,
                    index,
                    total
                )

                self._ui_call(
                    self._update_collection_progress,
                    index,
                    total,
                    f"Data PBP {index}/{total} selesai"
                )

            # ==========================================================
            # 5. VALIDASI SEBELUM MEMBUAT PDF
            # ==========================================================
            print("\n" + "=" * 70)
            print("=== VALIDASI SEBELUM MEMBUAT PDF ===")
            print("=" * 70)

            print(f"Total record : {len(records)}")
            print(f"Foto KTP OK : {ktp_success}")
            print(f"Foto PBP OK : {pbp_success}")

            for index, record in enumerate(records, start=1):
                print(
                    f"PBP {index} "
                    f"{record.get('no pbp', '')} | "
                    f"KTP={len(record.get('foto_ktp_bytes') or b'')} bytes | "
                    f"PBP={len(record.get('foto_pbp_bytes') or b'')} bytes"
                )

            # ==========================================================
            # 6. TENTUKAN OUTPUT PDF
            # ==========================================================
            output_path = self.get_output_pdf_path()

            self._ui_call(
                self.collection_status.configure,
                text="● Menyusun PDF...",
                text_color=Colors.TEXT_SECONDARY
            )

            self._ui_call(
                self._update_collection_progress,
                total,
                total,
                "Membuat PDF..."
            )

            print("\n" + "=" * 70)
            print("=== MEMBUAT PDF ===")
            print("=" * 70)
            print(f"Output: {output_path}")

            # ==========================================================
            # 7. URUTKAN RECORD SESUAI URUTAN WEBSITE
            # ==========================================================
            records.sort(
                key=lambda item: item.get("collection_order", 0)
            )

            print("\nUrutan FINAL PDF:")
            for index, record in enumerate(records, start=1):
                print(
                    f"  {index}. "
                    f"No PBP={record.get('no pbp', '')} | "
                    f"NIK={record.get('target_nik', '')} | "
                    f"PairValid={record.get('photo_pair_valid', False)}"
                )

            # ==========================================================
            # 8. BUAT PDF
            # ==========================================================
            BanpangPDFService.create_pdf(
                records,
                output_path
            )

            print("✓ PDF berhasil dibuat.")

            # ==========================================================
            # 8. SIMPAN HASIL
            # ==========================================================
            self.collection_rows = records
            self.output_pdf_path = output_path

            self._ui_call(
                self._collection_finished,
                records,
                output_path,
                ktp_success,
                pbp_success
            )

            print("\n" + "=" * 70)
            print("=== PENGAMBILAN SELESAI ===")
            print("=" * 70)

        except Exception as error:

            print("\n" + "=" * 70)
            print("=== ERROR PENGAMBILAN DATA ===")
            print("=" * 70)
            print(error)

            import traceback
            traceback.print_exc()

            self._ui_call(
                self._collection_failed,
                str(error)
            )

    def _ui_call(self, callback, *args, **kwargs):
        try:
            self.after(0, lambda: callback(*args, **kwargs))
        except Exception:
            pass

    def _prepare_collection_ui(self, total_number, row_count):
        self.total_pbp_value.configure(text=str(total_number))
        self.data_read_value.configure(text=f"{row_count} / {total_number}")
        self.ktp_value.configure(text=f"0 / {total_number}")
        self.pbp_photo_value.configure(text=f"0 / {total_number}")
        self.pdf_value.configure(text=f"0 / {total_number}")
        self.result_pbp_value.configure(text=str(row_count))
        self.result_pages_value.configure(text=str(row_count))
        self.result_total_pages_value.configure(text="0")
        self.result_file_label.configure(text="Sedang mengambil foto...")
        self.result_badge.configure(
            text="PROSES",
            text_color=Colors.PRIMARY,
            fg_color="#EFF6FF"
        )

    def _update_collection_progress(self, done, total, message):
        fraction = done / total if total else 0
        progress = 0.10 + (fraction * 0.75)
        self.collection_progress.set(progress)
        self.collection_percentage.configure(text=f"{int(progress * 100)}%")
        self.collection_page_info.configure(text=f"Data: {done} / {total}")
        self.data_info_label.configure(text=message)
        self.collection_status.configure(
            text=f"● Mengambil data {done}/{total}",
            text_color=Colors.TEXT_SECONDARY
        )

    def _update_photo_counters(self, ktp_count, pbp_count, done, total):
        self.ktp_value.configure(text=f"{ktp_count} / {total}")
        self.pbp_photo_value.configure(text=f"{pbp_count} / {total}")
        self.data_read_value.configure(text=f"{done} / {total}")

    def _collection_finished(self, records, output_path, ktp_success, pbp_success):
        total = len(records)
        total_pages = total * 2

        self.collection_progress.set(1.0)
        self.collection_percentage.configure(text="100%")
        self.collection_page_info.configure(text=f"Data: {total} / {total}")
        self.data_info_label.configure(
            text=f"Selesai. {total} PBP diproses dan PDF berhasil dibuat."
        )
        self.collection_status.configure(
            text=f"● Selesai — {total} PBP",
            text_color="#16A34A"
        )
        self.ktp_value.configure(text=f"{ktp_success} / {total}")
        self.pbp_photo_value.configure(text=f"{pbp_success} / {total}")
        self.pdf_value.configure(text=f"{total} / {total}")

        self.result_pbp_value.configure(text=str(total))
        self.result_pages_value.configure(text=str(total))
        self.result_total_pages_value.configure(text=str(total_pages))
        self.result_file_label.configure(
            text=f"PDF searchable / OCR: {os.path.basename(output_path)}"
        )
        self.result_badge.configure(
            text="SELESAI",
            text_color="#16A34A",
            fg_color="#ECFDF5"
        )
        self.open_folder_button.configure(state="normal")
        self.open_pdf_button.configure(state="normal")
        self.update_workflow_step(3)

        if self.open_pdf_after_checkbox.get():
            self.open_output_pdf()

        print("\n" + "=" * 70)
        print("=== PENGAMBILAN DATA & PDF SELESAI ===")
        print("Jumlah PBP:", total)
        print("Foto KTP berhasil:", ktp_success)
        print("Foto PBP berhasil:", pbp_success)
        print("Total halaman PDF:", total_pages)
        print("Output:", output_path)
        print("=" * 70)

        self.start_collection_button.configure(state="normal")

    def _collection_failed(self, message):
        self.collection_status.configure(
            text="● Pengambilan data gagal",
            text_color="#DC2626"
        )
        self.data_info_label.configure(text=f"Error: {message}")
        self.result_badge.configure(
            text="GAGAL",
            text_color="#DC2626",
            fg_color="#FEF2F2"
        )
        self.start_collection_button.configure(state="normal")
        print("Start Data Collection Error:", message)

    def get_total_pbp_from_website(self, driver):
        try:
            body_text = driver.find_element(
                "tag name",
                "body"
            ).text
            match = re.search(
                r"Total\s+([0-9.,]+)\s+PBP",
                body_text,
                re.IGNORECASE
            )
            if match:
                return match.group(1)
        except Exception:
            pass
        return ""

    def read_visible_pbp_table(self, driver):
        """Mencari tabel Daftar PBP berdasarkan nama kolom."""
        tables = driver.find_elements("tag name", "table")
        required = [
            "no pbp",
            "nama",
            "status pbp",
            "status serah",
            "verifikasi"
        ]

        def normalize(value):
            return re.sub(
                r"\s+",
                " ",
                (value or "").strip().lower()
            )

        target = None
        headers = []

        for table in tables:
            try:
                cells = table.find_elements(
                    "xpath",
                    ".//thead//th"
                )
                if not cells:
                    cells = table.find_elements(
                        "xpath",
                        ".//tr[1]/*"
                    )

                candidate = [
                    normalize(cell.text)
                    for cell in cells
                    if normalize(cell.text)
                ]

                if all(
                    any(req in item for item in candidate)
                    for req in required
                ):
                    target = table
                    headers = candidate
                    break
            except Exception:
                continue

        if target is None:
            raise Exception(
                "Tabel Daftar PBP tidak ditemukan. "
                "Pastikan filter PBP sudah diterapkan dan tabel tampil."
            )

        body_rows = target.find_elements(
            "xpath",
            ".//tbody/tr"
        )

        if not body_rows:
            all_rows = target.find_elements("xpath", ".//tr")
            body_rows = all_rows[1:] if len(all_rows) > 1 else []

        results = []

        for row in body_rows:
            try:
                cells = row.find_elements(
                    "xpath",
                    "./th|./td"
                )
                values = [cell.text.strip() for cell in cells]

                if not any(values):
                    continue

                item = {}
                for index, header in enumerate(headers):
                    item[header] = (
                        values[index]
                        if index < len(values)
                        else ""
                    )
                results.append(item)
            except Exception:
                continue

        if not results:
            raise Exception(
                "Tabel Daftar PBP ditemukan, tetapi tidak ada baris data."
            )

        return results

    # ==========================================================
    # OUTPUT SETTINGS
    # ==========================================================
    def choose_output_folder(self):
        folder = filedialog.askdirectory(
            title="Pilih Folder Penyimpanan PDF",
            initialdir=self.output_folder
        )
        if not folder:
            return

        self.output_folder = folder
        self.output_folder_entry.delete(0, "end")
        self.output_folder_entry.insert(0, folder)

    def choose_pbp_photo_folder(self):
        folder = filedialog.askdirectory(
            title="Pilih Folder Penyimpanan Foto PBP",
            initialdir=self.pbp_photo_folder
        )

        if not folder:
            return

        self.pbp_photo_folder = folder

        self.pbp_photo_folder_entry.delete(
            0,
            "end"
        )

        self.pbp_photo_folder_entry.insert(
            0,
            folder
        )

    def save_pbp_photo(self, photo_bytes, index, no_pbp=""):
        """
        Menyimpan Foto PBP ke folder yang dipilih pengguna.
        """

        if not photo_bytes:
            return None

        folder = self.pbp_photo_folder_entry.get().strip()

        if not folder:
            folder = self.pbp_photo_folder

        os.makedirs(
            folder,
            exist_ok=True
        )

        # Bersihkan No PBP agar aman digunakan sebagai nama file
        safe_no_pbp = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            str(no_pbp).strip()
        )

        if not safe_no_pbp:
            safe_no_pbp = f"PBP_{index:03d}"

        filename = (
            f"{index:03d}_{safe_no_pbp}.jpg"
        )

        file_path = os.path.join(
            folder,
            filename
        )

        with open(
            file_path,
            "wb"
        ) as file:
            file.write(photo_bytes)

        print(
            f"✓ Foto PBP disimpan: {file_path}"
        )

        return file_path

    def get_output_pdf_path(self):
        filename = self.pdf_filename_entry.get().strip()
        if not filename:
            filename = "Hasil_Banpang.pdf"

        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        folder = self.output_folder_entry.get().strip()
        if not folder:
            folder = self.output_folder

        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, filename)

    def open_output_folder(self):
        folder = self.output_folder_entry.get().strip()
        if not folder or not os.path.exists(folder):
            return

        try:
            os.startfile(folder)
        except Exception as error:
            print("Gagal membuka folder output:", error)

    def open_output_pdf(self):
        path = self.get_output_pdf_path()
        if not os.path.exists(path):
            return

        try:
            os.startfile(path)
        except Exception as error:
            print("Gagal membuka PDF:", error)

    # ==========================================================
    # UI HELPERS
    # ==========================================================
    def update_workflow_step(self, active_index):
        if not hasattr(self, "workflow_steps"):
            return

        for index, widgets in self.workflow_steps.items():
            if index <= active_index:
                widgets["circle"].configure(
                    fg_color=Colors.PRIMARY
                )
                widgets["number"].configure(
                    text_color="#FFFFFF"
                )
                widgets["title"].configure(
                    text_color=Colors.PRIMARY,
                    font=ctk.CTkFont(size=11, weight="bold")
                )
            else:
                widgets["circle"].configure(
                    fg_color="#E8EEF7"
                )
                widgets["number"].configure(
                    text_color=Colors.TEXT_SECONDARY
                )
                widgets["title"].configure(
                    text_color=Colors.TEXT_MUTED,
                    font=ctk.CTkFont(size=11)
                )

    def create_result_kpi(self, parent, column, value, label):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="ew", padx=3)

        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=Colors.TEXT_PRIMARY
        )
        value_label.pack()

        text_label = ctk.CTkLabel(
            frame,
            text=label,
            font=ctk.CTkFont(size=9),
            text_color=Colors.TEXT_SECONDARY
        )
        text_label.pack(pady=(1, 0))

        return value_label

    def create_card(self, parent):
        return ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=18,
            border_width=1,
            border_color=Colors.BORDER
        )

    def create_badge(self, parent, text, color=None, bg=None):
        color = color or Colors.PRIMARY
        bg = bg or "#EFF6FF"
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=color,
            fg_color=bg,
            corner_radius=8,
            padx=8,
            pady=3
        )

    # ==========================================================
    # WEBSITE
    # ==========================================================
    def open_banpang_website(self):
        try:
            result = BanpangBrowserService.open_website()

            if result.get("success"):
                try:
                    import time
                    for _ in range(12):
                        try:
                            self.banpang_driver = BanpangBrowserService.connect_driver()
                            break
                        except Exception:
                            time.sleep(0.5)
                except Exception:
                    self.banpang_driver = None

                self.browser_status.configure(
                    text="● Browser sudah dibuka",
                    text_color="#16A34A"
                )
                self.open_button.configure(
                    text="Buka Kembali Website"
                )
                self.update_workflow_step(1)

                print("========================================")
                print("=== BANPANG BROWSER ===")
                print("Website:", BanpangBrowserService.WEBSITE_URL)
                print("Status:", result.get("message"))
                print("========================================")

        except FileNotFoundError as error:
            self.browser_status.configure(
                text="● Google Chrome tidak ditemukan",
                text_color="#DC2626"
            )
            print("Banpang Browser Error:", error)

        except Exception as error:
            self.browser_status.configure(
                text="● Gagal membuka browser",
                text_color="#DC2626"
            )
            print("Banpang Browser Error:", error)


