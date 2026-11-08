# GARDA RB — Draft KAK / Scope of Work Tier 1 Basic

**Status:** DRAFT KAK internal, belum mendapat persetujuan pejabat/pemilik kegiatan. **Pemakai tujuan:** Pusat Reformasi Birokrasi TNI (Pus RB TNI).  
**Judul usulan:** Pengadaan dan Implementasi Aplikasi GARDA RB: Sistem Manajemen Pengetahuan dan Dokumen Berbasis Kecerdasan Buatan pada Pusat Reformasi Birokrasi TNI (Tier 1 Basic).

## 1. Maksud dan tujuan
Menyediakan satu aplikasi berbasis web untuk pencarian pengetahuan dan regulasi melalui AI yang merujuk sumber, arsip digital yang berizin, CCTV existing pada kapasitas dasar, serta kontrol pengguna dan audit. Asisten hanya memberikan pencarian, penjelasan dan ringkasan, bukan putusan hukum atau persetujuan administratif otomatis.

## 2. Ruang lingkup pekerjaan dan keluaran
- **Persiapan dan desain:** identifikasi klasifikasi dokumen; daftar sumber sah; alur pengguna; inventaris kapasitas, kamera existing, jaringan dan storage; matriks otorisasi; desain logis dan rencana UAT.
- **Pengembangan dan konfigurasi:** empat modul di bawah; autentikasi, metadata, indeks semantik, workflow indexing; UI berbahasa Indonesia.
- **Integrasi dan migrasi terbatas:** impor data yang telah disetujui; integrasi dengan folder Garda Drive dan kamera existing yang diverifikasi kompatibilitasnya.
- **Keamanan:** pembatasan dokumen pada retrieval *dan* akses file mentah, enkripsi saat transit, penyimpanan kredensial aman, audit trail dan backup/restore.
- **Pengujian:** uji fungsi, akurasi jawaban berbasis sumber, ketidakberhasilan/abstain saat tidak ada bukti, penolakan akses, restore, uji kamera dan UAT.
- **Serah terima:** aplikasi/demo yang berjalan pada lingkungan disepakati, source package/hak penggunaan sesuai kontrak, konfigurasi, panduan operator & admin, daftar perangkat, hasil UAT, pelatihan dan berita acara.

### Modul A — Ask Garda Knowledge (Basic)
1. Chat Bahasa Indonesia dengan dokumen terindeks.
2. Tanya peraturan, SOP, pedoman, keputusan dalam corpus yang disetujui.
3. Admin upload dan memproses PDF digital/DOCX/TXT.
4. Keyword + semantic search atas dokumen berizin.
5. Jawaban menyertakan judul sumber dan halaman/bagian jika tersedia.
6. Ringkasan satu dokumen.
7. AI menolak mengarang jawaban jika sumber tidak cukup; label jawaban sebagai keluaran AI.
8. Kebijakan izin akses pada indexing, retrieval, kutipan, tautan berkas dan riwayat.

**TAMBAHAN OPSIONAL dalam lingkup Basic (perlu dipilih dahulu):** sinkronisasi dokumen terpilih Garda Drive, filter metadata, riwayat chat, copy/ekspor teks sederhana, feedback jawaban, status berlaku/diubah/dicabut yang hanya ditetapkan admin setelah verifikasi manual. Lihat checklist terpisah.

### Modul B — Garda Drive
- Folder dan subfolder; unggah/unduh, tampilan berkas kompatibel; metadata dasar dan pencarian; RBAC per folder/dokumen, log tindakan dan kebijakan penghapusan/pemulihan.
- Manajemen versi file dan recycle bin adalah **usulan** yang harus dinyatakan dengan jelas bila termasuk kontrak.
- Bukan pengganti legal Sistem Informasi Kearsipan Dinamis Terintegrasi (SRIKANDI); integrasi resmi/retensi dan tata naskah di luar Basic kecuali diatur tersendiri.
- Konten tidak otomatis menjadi sumber AI tanpa otorisasi, pemeriksaan format dan indexing.

### Modul C — CCTV Lite
- Dashboard live view hingga 4 kanal kamera existing yang kompatibel, layout 1/2/4, status online/offline dan screenshot berizin.
- Tayang ulang hanya jika DVR/NVR existing menyediakan akses dan secara eksplisit diperjanjikan; **bukan kewajiban Basic saat ini**.
- Tidak termasuk pengadaan NVR baru, face recognition, ANPR/LPR, tracking, penyimpanan video 90 hari, GIS, video analytics atau otomatisasi alarm.
- Definisi ini khusus **GARDA RB offering**, tidak mengubah PRD Tier 1 generik CCTV di repo.

### Modul D — Administration & Security
- Pembuatan/nonaktif user, login, reset password aman, matriks hak akses, minimal role *Administrator, Knowledge Manager, Operator, Auditor, Viewer* (nama role dan hak final wajib disetujui).
- Audit tindakan sensitif, pembatasan kueri AI berdasarkan izin, enkripsi transit, kebijakan sesi, backup serta percobaan restore.
- MFA disarankan untuk admin; bila harus menjadi mandatory, tetapkan metode, infrastruktur dan acceptance case spesifik.
- Tidak termasuk integrasi SSO khusus, SOC 24/7, active-active HA maupun disaster recovery site.

## 3. Batas teknis usulan, belum final
| Parameter | Baseline pembicaraan | Pilihan/ketentuan |
|---|---|---|
| Akun | 30 | Belum disahkan |
| Dokumen diindeks | 500 | 250 / 500 / 1.000 |
| Storage berkas | 100 GB | Di luar salinan backup dan footage |
| CCTV existing | 4 kanal | Perlu cek RTSP/ONVIF/izin akses |
| Permintaan Ask Garda simultan | 2 | 1 / 2 / 4, dibuktikan benchmark |
| Format Ask Garda | PDF berbasis teks, DOCX, TXT | OCR massal/scan belum termasuk |
| Implementasi | Contoh estimasi 12 minggu | **Belum menjadi jadwal kontrak** |
| Masa support GARDA RB | Belum ditentukan | Jangan otomatis mengimpor durasi PUSADA |

## 4. Batasan / exclusions
- Tidak mengklaim lengkapnya seluruh peraturan tanpa korpus resmi, status versi, pemilik sumber dan jadwal pembaruan.
- Tidak ada browsing otomatis internet publik atau mengambil peraturan dari situs luar tanpa mekanisme yang disetujui.
- Di luar scope: OCR scan massal, handwriting, generator soal, koreksi ujian, pengolahan spreadsheet kompleks, analisis audio/video meeting, konferensi video, agentic workflow yang bertindak mandiri, pelatihan LLM dari nol, pembacaan dokumen rahasia tak berizin, validasi hukum otomatis.
- AI bersifat asisten referensi; tidak membuat keputusan administrasi, status hukum, atau tindakan terhadap personel secara otomatis.
- Jangan menjanjikan keamanan/privasi hanya karena on-prem. Kontrak harus menetapkan klasifikasi, lokasi data, retensi, pemilik akses, operasi backup, incident response dan sistem audit.

## 5. Draft 20 skenario UAT / acceptance test
**Seluruh target adalah USULAN awal**. Jawaban acuan, jenis dokumen, threshold, hardware, LAN dan prosedur penilaian harus disetujui sebelum UAT.
| ID | Area | Skenario | Kriteria penerimaan usulan |
|---|---|---|---|
| UAT-01 | Ask Garda | Tanya fakta eksplisit dari sumber | Minimal 18/20 pertanyaan acuan dinilai tepat |
| UAT-02 | Ask Garda | Tanya regulasi dengan judul/nomor | Sumber yang benar dan dapat dibuka |
| UAT-03 | Ask Garda | Tanya parafrasa semantik | Temukan dokumen relevan pada sampel uji |
| UAT-04 | Ask Garda | Tanya tanpa sumber | Minimal 9/10 menyatakan tidak ada bukti memadai |
| UAT-05 | Ask Garda | Periksa rujukan 20 jawaban | Semua klaim faktual dalam set uji memiliki rujukan yang dapat diverifikasi |
| UAT-06 | Ask Garda | Upload 20 file format valid | 20/20 sukses atau gagal dengan alasan format yang dapat diuji |
| UAT-07 | Ask Garda | Ringkas 5 dokumen | Tidak menambah fakta material dan mencakup pokok sumber |
| UAT-08 | Ask Garda | Uji perubahan dokumen sumber | Indeks diperbarui sesuai mekanisme yang dijanjikan |
| UAT-09 | Ask Garda | Dokumen role terlarang | Nol kebocoran dalam skenario role dan API |
| UAT-10 | Garda Drive | Buat folder, unggah, pindah berkas | Operasi tersimpan sesuai hak akses |
| UAT-11 | Garda Drive | Unduh dan preview file | Berkas valid, isi tidak berubah |
| UAT-12 | Garda Drive | Cari berdasarkan judul/metadata | Temukan berkas uji yang tersedia |
| UAT-13 | Garda Drive | Akses file tanpa izin melalui URL/API | Permintaan ditolak dan diaudit |
| UAT-14 | CCTV Lite | Live view 4 kamera kompatibel | 4 stream tampil selama 15 menit uji |
| UAT-15 | CCTV Lite | Putus/sambung satu kamera | Status berubah dan koneksi pulih |
| UAT-16 | CCTV Lite | Screenshot berizin/tidak berizin | Hanya pengguna berhak dapat melakukan tindakan |
| UAT-17 | Security | Matriks hak role di setiap modul | Tidak terjadi eskalasi hak akses |
| UAT-18 | Security | Audit login, ekspor, perubahan izin | Aktor, timestamp dan tindakan dapat ditelusuri |
| UAT-19 | Security | Restore backup ke test instance | Data penting dan konfigurasi kembali, integritas dicek |
| UAT-20 | Operasional | Operator melakukan alur kerja end-to-end | Unggah → indeks → tanya → sitasi → buka sumber berjalan |

Catatan: target `>=85%` dari 100 pertanyaan dan `>=95%` ketepatan sitasi pernah disebut di proposal ringkas sebagai **ambang usulan alternatif**. Di sini terdapat contoh 20 pertanyaan utama dan 20 skenario UAT. **Jangan menggabungkan denominasi itu tanpa menetapkan protokol final.**

## 6. Deliverable dokumen untuk HPS/KAK lanjutan
Daftar perangkat dan lisensi; matriks requirement-to-test; konfigurasi izin dokumen; sumber peraturan dan status pembaruan; prosedur proses indeks; test dataset; daftar kompatibilitas CCTV; SOP operasi, backup/restore, eskalasi; perincian support; acceptance evidence; pernyataan hak data dan hak software.

## 7. Hal yang memerlukan keputusan Pus RB
Sumber arsip/peraturan yang sah, tingkat klasifikasi, izin AI dan lokasi inference, server dedicated/shared, concurrency, volume dokumen, retensi arsip, wajib-tidaknya OCR, kamera existing, network segment, lisensi, jadwal implementasi, SLA dan masa support.
