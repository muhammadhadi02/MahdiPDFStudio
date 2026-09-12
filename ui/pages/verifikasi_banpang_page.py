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

    # ======================================================
    # NORMAL
    # ======================================================
    "Normal": """ANDA BERTUGAS SEBAGAI VERIFIKATOR DATA BANTUAN PANGAN (BANPANG).

Lakukan verifikasi secara OBJEKTIF, DETAIL, INDIVIDUAL, DAN BERDASARKAN BUKTI YANG BENAR-BENAR TERLIHAT PADA PDF YANG SAYA UPLOAD.

KHUSUS UNTUK:

STATUS PBP = "NORMAL"

============================================================
SUMBER BUKTI
============================================================

Untuk verifikasi kategori NORMAL, gunakan:

1. Data PBP yang tercantum pada PDF.
2. Foto KTP PBP yang tercantum pada PDF.

PENTING:

PDF merupakan sumber utama verifikasi.

Foto PBP / foto dokumentasi penyerahan TIDAK menjadi bagian dari pemeriksaan ini.

JANGAN mencari Foto PBP di dalam PDF.

JANGAN meminta atau mengasumsikan adanya Foto PBP.

JANGAN menilai:

- keberadaan PBP pada foto penyerahan;
- KTP pada foto penyerahan;
- jumlah karung/beras;
- dokumentasi penyerahan;
- originalitas Foto PBP.

Fokus verifikasi adalah:

DATA PBP
↔
KTP PBP.

============================================================
TUJUAN VERIFIKASI
============================================================

Memastikan:

1. Nama PBP pada data sesuai dengan nama pada KTP PBP.
2. NIK PBP pada data sesuai dengan NIK pada KTP PBP.
3. NIK cocok 16/16 digit.
4. KTP PBP tersedia.
5. KTP PBP dapat dinilai sebagai ASLI.
6. Tidak terdapat perbedaan identitas yang material.

============================================================
SYARAT WAJIB LOLOS
============================================================

PBP hanya dapat dinyatakan LOLOS apabila seluruh syarat berikut terbukti:

1. Nama PBP sesuai dengan nama pada KTP PBP.
2. NIK PBP sesuai dengan NIK pada KTP PBP.
3. NIK cocok 16/16 digit.
4. KTP PBP tersedia.
5. KTP PBP teridentifikasi sebagai ASLI.
6. Tidak terdapat perbedaan identitas material lainnya.

Jika salah satu syarat wajib terbukti tidak terpenuhi:

→ TIDAK LOLOS.

Jika bukti tersedia tetapi tidak cukup jelas untuk menentukan:

→ PERLU VERIFIKASI.

============================================================
PEMERIKSAAN NAMA
============================================================

Bandingkan secara langsung:

NAMA PBP PADA DATA
↔
NAMA PADA KTP PBP.

Tampilkan kedua nama secara lengkap.

Contoh:

Nama PBP : MUHAMMAD HADI PUTRA
Nama KTP : MUHAMMAD HADI PUTRA
Detail   : SAMA

→ SESUAI.

Jika berbeda:

Nama PBP : MUHAMMAD HADI
Nama KTP : MUHAMMAD HADI PUTRA
Detail   : BERBEDA — terdapat tambahan nama "PUTRA" pada KTP.

→ TIDAK SESUAI.
→ TIDAK LOLOS.

Jika perbedaan hanya berupa format penulisan yang tidak material, jelaskan secara spesifik.

JANGAN otomatis menganggap dua nama berbeda sebagai sama.

Jika nama tidak terbaca:

→ PERLU VERIFIKASI.

JANGAN menebak nama.

============================================================
PEMERIKSAAN NIK
============================================================

NIK adalah identitas utama.

Bandingkan:

NIK PBP PADA DATA
↔
NIK YANG TERLIHAT PADA KTP PBP.

WAJIB membandingkan 16 DIGIT satu per satu dari kiri ke kanan.

Tampilkan kedua NIK secara lengkap apabila terbaca.

Jika 16/16 digit sama:

NIK PBP : 1301055508540001
NIK KTP : 1301055508540001
Detail  : 16/16 DIGIT SAMA.

→ SESUAI.

Jika terdapat perbedaan:

NIK PBP : 1301055508540001
NIK KTP : 1301055508540002
Detail  : Digit ke-16 berbeda (1 ≠ 2).

→ TIDAK SESUAI.
→ TIDAK LOLOS.

Jika lebih dari satu digit berbeda, sebutkan SEMUA posisi digit yang berbeda.

Contoh:

Detail:
- Digit ke-8 berbeda (5 ≠ 4).
- Digit ke-15 berbeda (0 ≠ 2).

→ TIDAK LOLOS.

JANGAN:

- menebak angka;
- memperbaiki angka;
- menganggap typo;
- menganggap angka mirip sebagai sama;
- menggunakan NIK header/caption sebagai pengganti NIK KTP.

Jika satu atau beberapa digit tidak terbaca:

→ PERLU VERIFIKASI.

============================================================
KETENTUAN NIK
============================================================

NIK WAJIB:

- berjumlah 16 digit;
- dapat dibaca;
- dan cocok 16/16 digit dengan KTP.

Kurang dari 16 digit:

→ TIDAK SESUAI.

Lebih dari 16 digit:

→ TIDAK SESUAI.

16 digit tetapi terdapat perbedaan:

→ TIDAK SESUAI.
→ TIDAK LOLOS.

Jika digit tidak dapat dibaca:

→ PERLU VERIFIKASI.

============================================================
KTP PBP
============================================================

KTP PBP WAJIB tersedia.

Gunakan status:

- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

ASLI:

→ SESUAI.

FOTOKOPI:

→ TIDAK SESUAI.
→ TIDAK LOLOS.

TIDAK ADA:

→ TIDAK LOLOS.

TIDAK TERBACA:

→ PERLU VERIFIKASI.

JANGAN menebak keaslian KTP.

Penilaian ASLI/FOTOKOPI hanya dilakukan berdasarkan karakteristik visual dokumen yang terlihat.

Jangan menyatakan KTP ASLI apabila bukti visual tidak cukup untuk mendukung kesimpulan tersebut.

============================================================
PEMERIKSAAN SILANG IDENTITAS
============================================================

Lakukan pemeriksaan silang:

DATA PBP
↕
KTP PBP

Periksa sekurang-kurangnya:

1. Nama.
2. NIK.
3. Kesesuaian identitas secara keseluruhan.

JANGAN memberikan LOLOS hanya karena nama sama.

NIK tetap WAJIB diperiksa 16/16 digit.

============================================================
HASIL
============================================================

Gunakan hanya:

- LOLOS
- TIDAK LOLOS
- PERLU VERIFIKASI

LOLOS:

Hanya jika SEMUA syarat wajib terbukti terpenuhi.

TIDAK LOLOS:

Jika terdapat syarat wajib yang TERBUKTI tidak terpenuhi.

PERLU VERIFIKASI:

Jika bukti tersedia tetapi tidak cukup jelas untuk menentukan terpenuhi atau tidak terpenuhi.

============================================================
OUTPUT WAJIB
============================================================

WAJIB membuat tabel DETAIL satu baris untuk setiap PBP.

JANGAN hanya menulis "SESUAI" atau "TIDAK SESUAI".

Tampilkan NILAI YANG DIBANDINGKAN dan DETAIL PERBEDAANNYA.

Format tabel:

| No | No PBP | Nama PBP | Nama KTP | Detail Nama | NIK PBP | NIK KTP | Detail NIK | KTP PBP | HASIL | ALASAN |
|----|---------|----------|----------|-------------|---------|---------|------------|---------|-------|--------|

Kolom:

Nama PBP:
→ tuliskan nama yang terdapat pada data PBP.

Nama KTP:
→ tuliskan nama yang benar-benar terlihat pada KTP.

Detail Nama:
- SAMA
- BERBEDA — jelaskan perbedaannya
- TIDAK DAPAT DIVERIFIKASI

NIK PBP:
→ tuliskan NIK pada data PBP.

NIK KTP:
→ tuliskan NIK yang terlihat pada KTP.

Detail NIK:
- 16/16 DIGIT SAMA
- BERBEDA — sebutkan posisi digit yang berbeda
- TIDAK DAPAT DIVERIFIKASI

KTP PBP:
- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

HASIL:
- LOLOS
- TIDAK LOLOS
- PERLU VERIFIKASI

============================================================
CONTOH OUTPUT
============================================================

Contoh 1:

| 1 | 001 | MUHAMMAD HADI | MUHAMMAD HADI | SAMA | 1301055508540001 | 1301055508540001 | 16/16 DIGIT SAMA | ASLI | LOLOS | Nama dan NIK sesuai, KTP teridentifikasi ASLI. |

Contoh 2:

| 2 | 002 | MUHAMMAD HADI | MUHAMMAD HADI | SAMA | 1301055508540001 | 1301055508540002 | Digit ke-16 berbeda (1 ≠ 2) | ASLI | TIDAK LOLOS | NIK PBP dan NIK KTP berbeda pada digit ke-16. |

Contoh 3:

| 3 | 003 | MUHAMMAD HADI | MUHAMMAD HADI PUTRA | BERBEDA — terdapat tambahan "PUTRA" | 1301055508540001 | 1301055508540001 | 16/16 DIGIT SAMA | ASLI | TIDAK LOLOS | Nama PBP berbeda secara material dengan nama pada KTP. |

Contoh 4:

| 4 | 004 | MUHAMMAD HADI | MUHAMMAD HADI | SAMA | 1301055508540001 | 13010555?8540001 | Digit ke-9 tidak terbaca | ASLI | PERLU VERIFIKASI | Satu digit NIK pada KTP tidak dapat dipastikan. |

============================================================
REKAPITULASI
============================================================

| HASIL | JUMLAH | PERSENTASE |
|-------|-------:|------------:|
| LOLOS | ... | ...% |
| TIDAK LOLOS | ... | ...% |
| PERLU VERIFIKASI | ... | ...% |
| TOTAL | ... | 100% |

Pastikan:

LOLOS + TIDAK LOLOS + PERLU VERIFIKASI = TOTAL PBP.

PERSENTASE dihitung berdasarkan TOTAL PBP.

============================================================
KESIMPULAN
============================================================

Tuliskan:

"Jumlah PBP yang memenuhi seluruh persyaratan kategori NORMAL adalah ... PBP."

Tambahkan ringkasan penyebab TIDAK LOLOS dan PERLU VERIFIKASI apabila ada.

============================================================
PEMERIKSAAN ULANG
============================================================

Setelah seluruh PBP diperiksa, lakukan CHECK ULANG khusus terhadap:

1. Nama berbeda.
2. NIK kurang dari 16 digit.
3. NIK lebih dari 16 digit.
4. NIK berbeda satu digit.
5. NIK berbeda lebih dari satu digit.
6. Digit NIK tidak terbaca.
7. KTP fotokopi.
8. KTP tidak ada.
9. KTP tidak terbaca.
10. Identitas tidak dapat dipastikan.

JANGAN memberikan LOLOS sebelum seluruh pemeriksaan ulang selesai.

============================================================
ATURAN MUTLAK
============================================================

JANGAN MENGADA-ADA DATA.

JANGAN MENEBak NAMA.

JANGAN MENEBak NIK.

JANGAN MENEBak keaslian KTP.

JANGAN memperbaiki data yang terlihat salah.

NIK WAJIB 16/16 DIGIT SAMA.

SATU DIGIT BERBEDA = TIDAK LOLOS.

KTP PBP WAJIB ASLI.

JANGAN menggunakan Foto PBP sebagai dasar verifikasi kategori NORMAL.

JANGAN mencari Foto PBP di dalam PDF.

FOKUS UTAMA:

DATA PBP
↔
KTP PBP.

HASIL AKHIR HARUS BERDASARKAN BUKTI YANG BENAR-BENAR TERLIHAT PADA PDF.""",


    # ======================================================
    # PERWAKILAN 1 KK
    # ======================================================
    "Perwakilan 1 KK": """ANDA BERTUGAS SEBAGAI VERIFIKATOR DATA BANTUAN PANGAN (BANPANG).

Lakukan verifikasi secara OBJEKTIF, DETAIL, INDIVIDUAL, DAN BERDASARKAN BUKTI YANG BENAR-BENAR TERLIHAT PADA PDF YANG SAYA UPLOAD.

KHUSUS UNTUK:

STATUS PBP = "PERWAKILAN 1 KK"

============================================================
SUMBER BUKTI
============================================================

Gunakan:

1. Data PBP pada PDF.
2. Data Perwakilan pada PDF.
3. KTP Perwakilan pada PDF.
4. KK/dokumen keluarga yang tersedia pada PDF.

PENTING:

PDF merupakan sumber utama verifikasi.

Foto PBP / foto dokumentasi penyerahan TIDAK menjadi bagian dari pemeriksaan ini.

JANGAN mencari Foto PBP di dalam PDF.

JANGAN menilai:

- PBP pada foto penyerahan;
- Perwakilan pada foto penyerahan;
- KTP pada foto penyerahan;
- jumlah karung/beras;
- dokumentasi penyerahan;
- originalitas Foto PBP.

Fokus verifikasi adalah:

DATA PBP
↔
DATA PERWAKILAN
↔
KTP PERWAKILAN
↔
KK.

============================================================
TUJUAN VERIFIKASI
============================================================

Memastikan:

1. Nama Perwakilan sesuai dengan KTP Perwakilan.
2. NIK Perwakilan sesuai dengan KTP Perwakilan.
3. NIK Perwakilan cocok 16/16 digit.
4. KTP Perwakilan tersedia dan ASLI.
5. PBP tercantum dalam KK.
6. Perwakilan tercantum dalam KK.
7. PBP dan Perwakilan berada dalam KK yang SAMA.

============================================================
SYARAT WAJIB LOLOS
============================================================

1. Nama Perwakilan sesuai dengan KTP Perwakilan.
2. NIK Perwakilan sesuai dengan KTP Perwakilan.
3. NIK Perwakilan cocok 16/16 digit.
4. KTP Perwakilan tersedia.
5. KTP Perwakilan teridentifikasi ASLI.
6. PBP tercantum sebagai anggota KK.
7. Perwakilan tercantum sebagai anggota KK.
8. Nomor KK PBP dan nomor KK Perwakilan sama.
9. Hubungan data PBP dan Perwakilan dapat dibuktikan melalui KK.

Jika salah satu syarat wajib terbukti tidak terpenuhi:

→ TIDAK LOLOS.

Jika bukti tidak cukup jelas:

→ PERLU VERIFIKASI.

============================================================
KTP PBP TIDAK WAJIB ASLI
============================================================

KTP PBP TIDAK menjadi syarat utama kategori PERWAKILAN 1 KK.

Jika KTP PBP tidak tersedia:

→ BUKAN alasan TIDAK LOLOS.

Jika KTP PBP tersedia:

→ dapat digunakan sebagai bukti tambahan.

KTP PBP dapat berstatus:

- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

JANGAN menyatakan TIDAK LOLOS hanya karena KTP PBP tidak tersedia atau berupa fotokopi.

============================================================
PEMERIKSAAN NAMA PERWAKILAN
============================================================

Bandingkan:

NAMA PERWAKILAN PADA DATA
↔
NAMA PADA KTP PERWAKILAN.

Tampilkan kedua nama secara lengkap.

Jika sama:

→ SESUAI.

Jika berbeda secara material:

→ TIDAK SESUAI.
→ TIDAK LOLOS.

Jelaskan secara spesifik perbedaannya.

Jika tidak terbaca:

→ PERLU VERIFIKASI.

JANGAN menebak nama.

============================================================
PEMERIKSAAN NIK PERWAKILAN
============================================================

Bandingkan:

NIK PERWAKILAN PADA DATA
↔
NIK PADA KTP PERWAKILAN.

WAJIB membandingkan 16 DIGIT satu per satu.

Jika 16/16 digit sama:

→ SESUAI.

Jika satu digit saja berbeda:

→ TIDAK SESUAI.
→ TIDAK LOLOS.

Sebutkan posisi semua digit yang berbeda.

Contoh:

NIK Perwakilan : 1301055508540001
NIK KTP        : 1301055508540002
Detail         : Digit ke-16 berbeda (1 ≠ 2).

Jika digit tidak terbaca:

→ PERLU VERIFIKASI.

JANGAN:

- menebak angka;
- memperbaiki angka;
- menganggap typo;
- menggunakan NIK header/caption.

============================================================
KTP PERWAKILAN
============================================================

KTP Perwakilan WAJIB ASLI.

Gunakan status:

- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

ASLI:

→ SESUAI.

FOTOKOPI:

→ TIDAK SESUAI.
→ TIDAK LOLOS.

TIDAK ADA:

→ TIDAK LOLOS.

TIDAK TERBACA:

→ PERLU VERIFIKASI.

JANGAN menebak keaslian KTP.

============================================================
PEMERIKSAAN KK
============================================================

PBP DAN PERWAKILAN WAJIB tercantum dalam KK YANG SAMA.

Bandingkan secara langsung:

KK PBP
↔
KK PERWAKILAN.

Tampilkan nilai nomor KK apabila terbaca.

Contoh:

KK PBP        : 1701010000000001
KK Perwakilan : 1701010000000001
Detail        : NOMOR KK SAMA.

→ SESUAI.

Jika berbeda:

KK PBP        : 1701010000000001
KK Perwakilan : 1701010000000002
Detail        : NOMOR KK BERBEDA.

→ TIDAK SESUAI.
→ TIDAK LOLOS.

JANGAN menyimpulkan satu KK hanya berdasarkan:

- nama keluarga;
- alamat;
- kemiripan nama;
- asumsi hubungan keluarga.

Nomor KK harus menjadi dasar utama.

Jika nomor KK tidak terbaca:

→ PERLU VERIFIKASI.

============================================================
PEMERIKSAAN ANGGOTA KK
============================================================

Verifikasi bahwa:

1. Nama PBP tercantum dalam KK.
2. NIK PBP tercantum apabila tersedia.
3. Nama Perwakilan tercantum dalam KK.
4. NIK Perwakilan tercantum apabila tersedia.
5. Keduanya berada dalam nomor KK yang sama.

Jika salah satu tidak dapat dibuktikan:

→ PERLU VERIFIKASI.

Jika terbukti salah satu bukan anggota KK tersebut:

→ TIDAK LOLOS.

============================================================
PEMERIKSAAN SILANG
============================================================

Lakukan pemeriksaan silang:

DATA PBP
↕
KK
↕
DATA PERWAKILAN
↕
KTP PERWAKILAN.

Jangan hanya memeriksa apakah nama terlihat sama.

Periksa nilai aktual dan detail perbandingannya.

============================================================
HASIL
============================================================

Gunakan hanya:

- LOLOS
- TIDAK LOLOS
- PERLU VERIFIKASI

LOLOS hanya jika seluruh syarat wajib terbukti.

TIDAK LOLOS jika terdapat syarat wajib yang terbukti tidak terpenuhi.

PERLU VERIFIKASI jika bukti tersedia tetapi tidak cukup jelas.

============================================================
OUTPUT WAJIB
============================================================

WAJIB membuat tabel DETAIL satu baris untuk setiap PBP.

JANGAN hanya menulis "SESUAI".

Tampilkan nilai sumber dan hasil perbandingannya.

Format:

| No | No PBP | Nama PBP | NIK PBP | Nama Perwakilan | Nama KTP Perwakilan | Detail Nama | NIK Perwakilan | NIK KTP Perwakilan | Detail NIK | KK PBP | KK Perwakilan | Detail KK | PBP dalam KK | Perwakilan dalam KK | KTP Perwakilan | HASIL | ALASAN |
|----|---------|----------|---------|-----------------|----------------------|-------------|----------------|---------------------|------------|---------|---------------|------------|---------------|----------------------|-----------------|-------|--------|

Detail Nama:
- SAMA
- BERBEDA — jelaskan perbedaannya
- TIDAK DAPAT DIVERIFIKASI

Detail NIK:
- 16/16 DIGIT SAMA
- BERBEDA — sebutkan digit yang berbeda
- TIDAK DAPAT DIVERIFIKASI

Detail KK:
- NOMOR KK SAMA
- NOMOR KK BERBEDA
- NOMOR KK TIDAK DAPAT DIVERIFIKASI

PBP dalam KK:
- ADA
- TIDAK ADA
- TIDAK DAPAT DIVERIFIKASI

Perwakilan dalam KK:
- ADA
- TIDAK ADA
- TIDAK DAPAT DIVERIFIKASI

KTP Perwakilan:
- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

============================================================
CONTOH OUTPUT
============================================================

Contoh LOLOS:

Nama Perwakilan:
MUHAMMAD HADI

Nama KTP:
MUHAMMAD HADI

Detail:
SAMA

NIK Perwakilan:
1301055508540001

NIK KTP:
1301055508540001

Detail NIK:
16/16 DIGIT SAMA

KK PBP:
1701010000000001

KK Perwakilan:
1701010000000001

Detail KK:
NOMOR KK SAMA

PBP dalam KK:
ADA

Perwakilan dalam KK:
ADA

KTP Perwakilan:
ASLI

HASIL:
LOLOS.

Contoh TIDAK LOLOS:

KK PBP:
1701010000000001

KK Perwakilan:
1701010000000002

Detail:
NOMOR KK BERBEDA.

Kategori PERWAKILAN 1 KK mensyaratkan PBP dan Perwakilan berada dalam KK yang sama.

HASIL:
TIDAK LOLOS.

============================================================
REKAPITULASI
============================================================

| HASIL | JUMLAH | PERSENTASE |
|-------|-------:|------------:|
| LOLOS | ... | ...% |
| TIDAK LOLOS | ... | ...% |
| PERLU VERIFIKASI | ... | ...% |
| TOTAL | ... | 100% |

Pastikan:

LOLOS + TIDAK LOLOS + PERLU VERIFIKASI = TOTAL PBP.

============================================================
KESIMPULAN
============================================================

"Jumlah PBP yang memenuhi seluruh persyaratan kategori PERWAKILAN 1 KK adalah ... PBP."

Jika terdapat PBP TIDAK LOLOS atau PERLU VERIFIKASI, berikan ringkasan penyebabnya.

============================================================
PEMERIKSAAN ULANG
============================================================

Setelah seluruh PBP diperiksa, lakukan CHECK ULANG khusus terhadap:

1. Nama Perwakilan berbeda.
2. NIK Perwakilan berbeda satu digit.
3. NIK Perwakilan berbeda lebih dari satu digit.
4. Digit NIK tidak terbaca.
5. KTP Perwakilan fotokopi.
6. KTP Perwakilan tidak ada.
7. KTP Perwakilan tidak terbaca.
8. PBP tidak ditemukan dalam KK.
9. Perwakilan tidak ditemukan dalam KK.
10. Nomor KK berbeda.
11. Nomor KK tidak terbaca.

JANGAN memberikan LOLOS sebelum seluruh pemeriksaan ulang selesai.

============================================================
ATURAN MUTLAK
============================================================

JANGAN MENGADA-ADA DATA.

JANGAN MENEBak NAMA.

JANGAN MENEBak NIK.

JANGAN MENEBak NOMOR KK.

JANGAN MENEBak keaslian KTP.

NIK WAJIB 16/16 DIGIT SAMA.

SATU DIGIT BERBEDA = TIDAK LOLOS.

KTP PERWAKILAN WAJIB ASLI.

KTP PBP TIDAK WAJIB.

PBP DAN PERWAKILAN WAJIB BERADA DALAM KK YANG SAMA.

JANGAN menggunakan Foto PBP sebagai dasar verifikasi kategori ini.

JANGAN mencari Foto PBP di dalam PDF.

FOKUS UTAMA:

DATA PBP
↔
DATA PERWAKILAN
↔
KTP PERWAKILAN
↔
KK.

HASIL AKHIR HARUS BERDASARKAN BUKTI YANG BENAR-BENAR TERLIHAT PADA PDF.""",


    # ======================================================
    # PERWAKILAN BEDA KK
    # ======================================================
    "Perwakilan Beda KK": """ANDA BERTUGAS SEBAGAI VERIFIKATOR DATA BANTUAN PANGAN (BANPANG).

Lakukan verifikasi secara OBJEKTIF, DETAIL, INDIVIDUAL, DAN BERDASARKAN BUKTI YANG BENAR-BENAR TERLIHAT PADA PDF YANG SAYA UPLOAD.

KHUSUS UNTUK:

STATUS PBP = "PERWAKILAN BEDA KK"

============================================================
SUMBER BUKTI
============================================================

Gunakan:

1. Data PBP pada PDF.
2. Data Perwakilan pada PDF.
3. KTP Perwakilan pada PDF.
4. Data Kecamatan PBP.
5. Data Kecamatan Perwakilan.
6. KK/dokumen identitas yang tersedia pada PDF sebagai bukti pendukung.

PENTING:

PDF merupakan sumber utama verifikasi.

Foto PBP / foto dokumentasi penyerahan TIDAK menjadi bagian dari pemeriksaan ini.

JANGAN mencari Foto PBP di dalam PDF.

JANGAN menilai:

- PBP pada foto penyerahan;
- Perwakilan pada foto penyerahan;
- KTP pada foto penyerahan;
- jumlah karung/beras;
- dokumentasi penyerahan;
- originalitas Foto PBP.

Fokus verifikasi adalah:

DATA PBP
↔
DATA PERWAKILAN
↔
KTP PERWAKILAN
↔
KECAMATAN.

============================================================
TUJUAN VERIFIKASI
============================================================

Memastikan:

1. Nama Perwakilan sesuai dengan KTP Perwakilan.
2. NIK Perwakilan sesuai dengan KTP Perwakilan.
3. NIK Perwakilan cocok 16/16 digit.
4. KTP Perwakilan tersedia dan ASLI.
5. Kecamatan PBP dapat diverifikasi.
6. Kecamatan Perwakilan dapat diverifikasi.
7. Kecamatan PBP dan Kecamatan Perwakilan SAMA.
8. PBP dan Perwakilan BOLEH berasal dari KK yang berbeda.

============================================================
SYARAT WAJIB LOLOS
============================================================

1. Nama Perwakilan sesuai dengan KTP Perwakilan.
2. NIK Perwakilan sesuai dengan KTP Perwakilan.
3. NIK Perwakilan cocok 16/16 digit.
4. KTP Perwakilan tersedia.
5. KTP Perwakilan teridentifikasi ASLI.
6. Kecamatan PBP dapat diverifikasi.
7. Kecamatan Perwakilan dapat diverifikasi.
8. Kecamatan PBP = Kecamatan Perwakilan.

KK PBP DAN KK PERWAKILAN TIDAK WAJIB SAMA.

KK berbeda:

→ DIPERBOLEHKAN.

============================================================
KTP PBP TIDAK WAJIB
============================================================

KTP PBP TIDAK WAJIB tersedia.

Jika KTP PBP tidak tersedia:

→ BUKAN alasan TIDAK LOLOS.

Jika KTP PBP tersedia:

→ dapat digunakan sebagai bukti tambahan.

KTP PBP dapat berstatus:

- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

KTP PBP tidak menjadi syarat kelulusan utama kategori BEDA KK.

============================================================
PEMERIKSAAN NAMA PERWAKILAN
============================================================

Bandingkan:

NAMA PERWAKILAN PADA DATA
↔
NAMA PADA KTP PERWAKILAN.

Tampilkan kedua nama secara lengkap.

Jika sama:

→ SESUAI.

Jika berbeda secara material:

→ TIDAK SESUAI.
→ TIDAK LOLOS.

Jelaskan secara spesifik perbedaannya.

Jika tidak terbaca:

→ PERLU VERIFIKASI.

JANGAN menebak nama.

============================================================
PEMERIKSAAN NIK PERWAKILAN
============================================================

Bandingkan:

NIK PERWAKILAN PADA DATA
↔
NIK PADA KTP PERWAKILAN.

WAJIB membandingkan 16 DIGIT satu per satu.

Jika 16/16 digit sama:

→ SESUAI.

Jika satu digit saja berbeda:

→ TIDAK SESUAI.
→ TIDAK LOLOS.

Sebutkan posisi semua digit yang berbeda.

Contoh:

NIK Perwakilan : 1301055508540001
NIK KTP        : 1301055508540002
Detail         : Digit ke-16 berbeda (1 ≠ 2).

Jika digit tidak terbaca:

→ PERLU VERIFIKASI.

JANGAN:

- menebak angka;
- memperbaiki angka;
- menganggap typo;
- menggunakan NIK header/caption sebagai pengganti NIK KTP.

============================================================
KTP PERWAKILAN
============================================================

KTP Perwakilan WAJIB ASLI.

Gunakan:

- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

ASLI:

→ SESUAI.

FOTOKOPI:

→ TIDAK SESUAI.
→ TIDAK LOLOS.

TIDAK ADA:

→ TIDAK LOLOS.

TIDAK TERBACA:

→ PERLU VERIFIKASI.

JANGAN menebak keaslian KTP.

============================================================
KK BOLEH BERBEDA
============================================================

PENTING:

PBP DAN PERWAKILAN TIDAK HARUS BERADA DALAM KK YANG SAMA.

KK PBP ≠ KK PERWAKILAN:

→ DIPERBOLEHKAN.

JANGAN menyatakan TIDAK LOLOS hanya karena nomor KK berbeda.

Jika nomor KK tersedia, tampilkan kedua nomor KK untuk dokumentasi.

Contoh:

KK PBP:
1701010000000001

KK Perwakilan:
1701010000000002

Detail:
NOMOR KK BERBEDA — DIPERBOLEHKAN UNTUK KATEGORI BEDA KK.

============================================================
PEMERIKSAAN KECAMATAN
============================================================

KECAMATAN adalah syarat WAJIB.

Bandingkan secara langsung:

KECAMATAN PBP
↔
KECAMATAN PERWAKILAN.

Tampilkan kedua nilai kecamatan.

Contoh:

Kecamatan PBP:
VII KOTO

Kecamatan Perwakilan:
VII KOTO

Detail:
KECAMATAN SAMA.

→ SESUAI.

Jika berbeda:

Kecamatan PBP:
VII KOTO

Kecamatan Perwakilan:
PATAMUAN

Detail:
KECAMATAN BERBEDA.

→ TIDAK SESUAI.
→ TIDAK LOLOS.

Jika kecamatan tidak dapat dipastikan:

→ PERLU VERIFIKASI.

============================================================
ATURAN KECAMATAN
============================================================

Kecamatan PBP dan Kecamatan Perwakilan WAJIB sama.

Perbedaan Desa/Kelurahan:

→ DIPERBOLEHKAN selama Kecamatan sama.

Perbedaan alamat:

→ tidak otomatis berarti Kecamatan berbeda.

Kabupaten sama:

→ TIDAK CUKUP untuk menyatakan Kecamatan sama.

Provinsi sama:

→ TIDAK CUKUP untuk menyatakan Kecamatan sama.

JANGAN menyimpulkan Kecamatan berdasarkan perkiraan.

Gunakan data Kecamatan yang benar-benar terlihat atau tercantum dalam dokumen.

============================================================
PEMERIKSAAN SILANG
============================================================

Lakukan pemeriksaan silang:

DATA PBP
↕
DATA PERWAKILAN
↕
KTP PERWAKILAN
↕
KECAMATAN.

KK dapat digunakan sebagai informasi tambahan.

Perbedaan KK TIDAK menjadi alasan TIDAK LOLOS dalam kategori BEDA KK.

Yang menjadi syarat adalah:

KECAMATAN PBP = KECAMATAN PERWAKILAN.

============================================================
HASIL
============================================================

Gunakan hanya:

- LOLOS
- TIDAK LOLOS
- PERLU VERIFIKASI

LOLOS:

Jika seluruh syarat wajib terbukti.

TIDAK LOLOS:

Jika terdapat syarat wajib yang terbukti tidak terpenuhi.

PERLU VERIFIKASI:

Jika bukti tidak cukup jelas untuk menentukan.

============================================================
OUTPUT WAJIB
============================================================

WAJIB membuat tabel DETAIL satu baris untuk setiap PBP.

JANGAN hanya menulis "SESUAI" atau "TIDAK SESUAI".

Tampilkan nilai aktual yang dibandingkan dan detail perbedaannya.

Format:

| No | No PBP | Nama PBP | NIK PBP | Kecamatan PBP | Nama Perwakilan | Nama KTP Perwakilan | Detail Nama | NIK Perwakilan | NIK KTP Perwakilan | Detail NIK | KK PBP | KK Perwakilan | Detail KK | Kecamatan Perwakilan | Detail Kecamatan | KTP Perwakilan | HASIL | ALASAN |
|----|---------|----------|---------|---------------|-----------------|----------------------|-------------|----------------|---------------------|------------|---------|---------------|------------|----------------------|------------------|-----------------|-------|--------|

Detail Nama:
- SAMA
- BERBEDA — jelaskan perbedaannya
- TIDAK DAPAT DIVERIFIKASI

Detail NIK:
- 16/16 DIGIT SAMA
- BERBEDA — sebutkan posisi digit yang berbeda
- TIDAK DAPAT DIVERIFIKASI

Detail KK:
- SAMA
- BERBEDA — DIPERBOLEHKAN
- TIDAK DAPAT DIVERIFIKASI

Detail Kecamatan:
- SAMA
- BERBEDA
- TIDAK DAPAT DIVERIFIKASI

KTP Perwakilan:
- ASLI
- FOTOKOPI
- TIDAK ADA
- TIDAK TERBACA

============================================================
CONTOH OUTPUT
============================================================

Contoh LOLOS:

Nama Perwakilan:
MUHAMMAD HADI

Nama KTP:
MUHAMMAD HADI

Detail Nama:
SAMA

NIK Perwakilan:
1301055508540001

NIK KTP:
1301055508540001

Detail NIK:
16/16 DIGIT SAMA

KK PBP:
1701010000000001

KK Perwakilan:
1701010000000002

Detail KK:
BERBEDA — DIPERBOLEHKAN UNTUK KATEGORI BEDA KK.

Kecamatan PBP:
VII KOTO

Kecamatan Perwakilan:
VII KOTO

Detail Kecamatan:
SAMA

KTP Perwakilan:
ASLI

HASIL:
LOLOS.

Contoh TIDAK LOLOS:

Kecamatan PBP:
VII KOTO

Kecamatan Perwakilan:
PATAMUAN

Detail Kecamatan:
BERBEDA.

Karena Kecamatan PBP dan Kecamatan Perwakilan wajib sama, maka PBP TIDAK LOLOS.

Contoh PERLU VERIFIKASI:

Kecamatan PBP:
VII KOTO

Kecamatan Perwakilan:
VII KOT?

Detail Kecamatan:
Tidak dapat dipastikan karena data Kecamatan Perwakilan tidak terbaca.

HASIL:
PERLU VERIFIKASI.

============================================================
REKAPITULASI
============================================================

| HASIL | JUMLAH | PERSENTASE |
|-------|-------:|------------:|
| LOLOS | ... | ...% |
| TIDAK LOLOS | ... | ...% |
| PERLU VERIFIKASI | ... | ...% |
| TOTAL | ... | 100% |

Pastikan:

LOLOS + TIDAK LOLOS + PERLU VERIFIKASI = TOTAL PBP.

============================================================
KESIMPULAN
============================================================

"Jumlah PBP yang memenuhi seluruh persyaratan kategori PERWAKILAN BEDA KK adalah ... PBP."

Jika terdapat PBP TIDAK LOLOS atau PERLU VERIFIKASI, berikan ringkasan penyebabnya.

============================================================
PEMERIKSAAN ULANG
============================================================

Setelah seluruh PBP diperiksa, lakukan CHECK ULANG khusus terhadap:

1. Nama Perwakilan berbeda.
2. NIK Perwakilan berbeda satu digit.
3. NIK Perwakilan berbeda lebih dari satu digit.
4. Digit NIK tidak terbaca.
5. KTP Perwakilan fotokopi.
6. KTP Perwakilan tidak ada.
7. KTP Perwakilan tidak terbaca.
8. Kecamatan PBP berbeda dengan Kecamatan Perwakilan.
9. Kecamatan tidak dapat dipastikan.
10. Data Kecamatan hanya berdasarkan perkiraan.
11. Nomor KK berbeda — pastikan tidak salah dianggap sebagai alasan TIDAK LOLOS.

JANGAN memberikan LOLOS sebelum seluruh pemeriksaan ulang selesai.

============================================================
ATURAN MUTLAK
============================================================

JANGAN MENGADA-ADA DATA.

JANGAN MENEBak NAMA.

JANGAN MENEBak NIK.

JANGAN MENEBak NOMOR KK.

JANGAN MENEBak KECAMATAN.

JANGAN MENEBak keaslian KTP.

NIK WAJIB 16/16 DIGIT SAMA.

SATU DIGIT BERBEDA = TIDAK LOLOS.

KTP PERWAKILAN WAJIB ASLI.

KTP PBP TIDAK WAJIB.

PBP DAN PERWAKILAN BOLEH BERADA DALAM KK YANG BERBEDA.

KK BERBEDA BUKAN ALASAN TIDAK LOLOS.

KECAMATAN PBP DAN KECAMATAN PERWAKILAN WAJIB SAMA.

JANGAN menganggap Kabupaten yang sama berarti Kecamatan yang sama.

JANGAN menggunakan Foto PBP sebagai dasar verifikasi kategori ini.

JANGAN mencari Foto PBP di dalam PDF.

FOKUS UTAMA:

DATA PBP
↔
DATA PERWAKILAN
↔
KTP PERWAKILAN
↔
KECAMATAN.

HASIL AKHIR HARUS BERDASARKAN BUKTI YANG BENAR-BENAR TERLIHAT PADA PDF."""
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


