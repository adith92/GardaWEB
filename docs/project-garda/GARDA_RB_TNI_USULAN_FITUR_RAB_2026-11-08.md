# GARDA RB TNI: Usulan Fitur, Lingkup RAB/HPS, dan Tahapan

> **Status:** DRAF KONSEP / belum merupakan KAK, RAB, HPS, atau spesifikasi resmi Pus RB TNI.  
> **Tanggal dokumentasi:** 8 November 2026  
> **Satker sasaran (usulan):** Pusat Reformasi Birokrasi (Pus RB) TNI  
> **Nama kerja:** GARDA RB TNI — Integrated Reformasi Birokrasi Management & AI Monitoring System  
> **Rujukan diskusi:** Percakapan proyek Garda tentang pengajuan baru ke Pus RB TNI, fitur untuk RAB, dan pengelompokan prioritas.  
> **Pemisahan proyek:** Berbeda dari *GARDA PMC / PUSADA TNI* yang menitikberatkan CCTV, keamanan fisik, face recognition, dan LPR. Dokumen KAK PUSADA yang pernah dilampirkan bukan KAK Pus RB TNI.

## 1. Tujuan usulan

Menyediakan sistem kerja internal untuk memonitor pelaksanaan reformasi birokrasi, mengelola indikator kinerja, evaluasi mandiri, dokumen bukti (evidence), tindak lanjut temuan, dan pengambilan keputusan pimpinan berbasis data. AI berfungsi sebagai alat bantu pencarian, peringkasan, dan deteksi celah dokumen; keputusan penilaian resmi tetap dilakukan pejabat/asesor berwenang.

**Prinsip desain:** jangan menduplikasi pelaporan nasional yang sudah ada; prioritaskan workflow internal, kualitas eviden, akuntabilitas, dan integrasi *hanya* jika tersedia izin dan API/pertukaran data resmi.

## 2. Katalog 16 modul yang diusulkan

Keterangan: **P1** = wajib diusulkan sebagai inti awal, **P2** = tahap perluasan, **P3** = opsional menurut anggaran dan kebutuhan.

| Kode | Modul | Fitur terpenting | Prioritas |
|---|---|---|---|
| RB-01 | Executive Command Center | Dashboard capaian per satuan, status indikator, grafik, drill-down, ringkasan pimpinan | P1 |
| RB-02 | Reformasi Birokrasi Monitoring | Program/target RB, rencana aksi, PIC, tenggat, progres dan eskalasi | P1 |
| RB-03 | SAKIP & KPI Management | Target-realisasi, cascading indikator, analisis deviasi, evaluasi kinerja | P1 |
| RB-04 | Zona Integritas (ZI) WBK/WBBM | Checklist, PMPZI/penilaian mandiri, verifikasi asesor, eviden dan perbaikan | P1 |
| RB-05 | AI Document Intelligence | OCR, ekstraksi, klasifikasi, ringkasan, pencarian dokumen dan peraturan | P1 |
| RB-06 | Ask GARDA RB (AI Assistant) | Pertanyaan bahasa Indonesia atas data berizin, jawaban menyebut dokumen sumber | P1 |
| RB-07 | Digital Evidence Management | Repositori eviden, metadata, versi, tagging, periode, riwayat akses, retensi | P1 |
| RB-08 | Workflow & E-Approval | Penugasan, disposisi, approval berjenjang, notifikasi, SLA, jejak persetujuan | P1 |
| RB-09 | Audit & Risk Management | Temuan, register risiko, mitigasi, PIC, tenggat dan verifikasi tindak lanjut | P2 |
| RB-10 | SOP & Business Process | Pemetaan proses kerja, versi SOP, analisis bottleneck dan siklus persetujuan | P2 |
| RB-11 | Survey & Complaint Management | Survei layanan, masukan/pengaduan administratif, status penanganan, SLA | P2 |
| RB-12 | Organizational Capability | Evaluasi proses/fungsi/struktur dan rekomendasi tata kelola kelembagaan | P2 |
| RB-13 | Predictive Analytics | Penanda risiko keterlambatan, proyeksi tren berbasis data, anomali capaian | P2 |
| RB-14 | Integrasi Sistem Nasional | Konektor data yang diotorisasi; pemetaan data, sinkronisasi, log transfer | P2 |
| RB-15 | E-Learning RB | Materi internal, tes, status pembelajaran, sertifikat internal | P3 |
| RB-16 | Mobile Monitoring | Dashboard responsif/mobile, notifikasi, approval sesuai hak akses | P3 |

### Fitur operasional yang disarankan sebagai penguat

1. **PMPZI / WBK-WBBM:** form asesmen digital, verifikasi berjenjang, pembuktian indikator, dashboard kesiapan dan daftar kekurangan bukti.
2. **PEKPPP / evaluasi pelayanan publik:** instrumen evaluasi, nilai/kriteria yang dikonfigurasi oleh administrator berwenang, hasil penilaian, rekomendasi serta tindak lanjut.
3. **AI Evidence Gap Detection:** bandingkan persyaratan yang diinput asesor dengan eviden tersedia; tampilkan indikator yang kosong/kurang lengkap dan rujukan sumbernya.
4. **AI Report Generator:** draf laporan periodik dengan sumber, periode data, status validasi, serta persetujuan manusia sebelum diterbitkan.

Catatan: definisi indikator, bobot, nomenklatur dan regulasi evaluasi untuk tahun anggaran pengadaan harus divalidasi dengan kebijakan resmi terbaru dan kebutuhan Pus RB TNI; **tidak ditetapkan secara sepihak oleh vendor**.

## 3. Paket tahap pengadaan (konsep)

| Paket | Cakupan | Keluaran utama |
|---|---|---|
| **Tahap 1 – Core RB** | RB-01, RB-02, RB-03, RB-04, RB-07, RB-08 + RBAC, audit, laporan | Dashboard pimpinan, rencana aksi, KPI/SAKIP, ZI, alur eviden dan approval |
| **Tahap 2 – AI & Evaluasi** | RB-05, RB-06, RB-09, RB-11, RB-13 terpilih + PEKPPP dan AI evidence gap | Pencarian dokumen, asistensi AI terukur, instrumen evaluasi, temuan dan risiko |
| **Tahap 3 – Integrasi** | RB-10, RB-12, RB-14, RB-15, RB-16 + peningkatan ketersediaan dan DR | Integrasi resmi, mobile, SOP, pembelajaran, hardening/DR lanjutan |

Paket ini adalah **opsi pembagian lingkup**, bukan klaim tahapan kontrak yang sudah disetujui. Seluruh pengembangan perlu dinilai menurut prioritas dan kemampuan implementasi. Untuk **GARDA PMC/PUSADA**, keputusan jadwal yang sudah difinalkan terpisah adalah **8 minggu implementasi + 2 minggu testing/commissioning + 12 bulan support**. Jadwal GARDA RB perlu ditetapkan sendiri berdasarkan jumlah satker/pengguna dan integrasi.

## 4. Susunan baris RAB/HPS yang disarankan

### A. Pengembangan software

- RB-01 sampai RB-16 dihitung sebagai paket/modul sesuai lingkup yang dibeli, dengan *deliverables* yang dapat diuji.
- Komponen lintas modul: autentikasi, MFA, role-based access control (RBAC) per satker, audit trail, administrasi, API, pelaporan, ekspor, monitoring performa.
- Pisahkan **pengembangan kustom** dari **lisensi pihak ketiga/subscription**. Hindari penghitungan ganda biaya personel yang sudah terkandung dalam paket modul.

### B. Hardware/infrastruktur (volume awal untuk survei, belum spesifikasi final)

| Item | Volume asumsi awal | Perlu dikunci melalui survei |
|---|---:|---|
| Server aplikasi/database | 1–2 unit | concurrency, HA, kapasitas DB, OS, support |
| Server GPU AI lokal | 1 unit **jika** AI diproses on-premises | model, jumlah user, throughput, VRAM, daya |
| NAS/backup storage | 1 set | volume dokumen, retensi, RPO/RTO, offsite |
| Firewall/VPN/switch | 1 set | jaringan, segmentasi, zero-trust, bandwidth |
| UPS/rack | 1 set | total beban, runtime, instalasi |
| Workstation admin/operator | sesuai survei | jumlah operator dan asesmen |
| Layar monitoring pimpinan | opsional | kebutuhan ruang, biaya dan justifikasi |

**Jangan langsung menetapkan GPU, merk, ukuran NAS atau jumlah layar tanpa kapasitas beban dan quotation.** Tidak ada kebutuhan CCTV/PTZ, LPR, atau biometrik yang otomatis masuk pengadaan Pus RB.

### C. Jasa implementasi dan layanan

- Discovery dan pemetaan proses RB; workshop kebutuhan; desain arsitektur.
- Instalasi, konfigurasi, pengembangan, quality assurance, UAT, migrasi data/eviden yang disetujui.
- Hardening, penetration test berbasis izin, pengujian pemulihan backup, log dan audit, pelatihan admin/asesor/operator.
- Dokumentasi, hak penggunaan/source code sesuai kontrak, as-built dan serah terima.
- Garansi/support, SLA waktu respons/resolusi, patch keamanan dan transfer knowledge; **durasi kontrak ditetapkan dalam KAK RB**.

### D. Kolom RAB yang perlu ada

Kode; nama item; spesifikasi dan ruang lingkup; satuan; volume; harga satuan; subtotal; dasar estimasi/quotation; lisensi/periode; deliverable; metode uji penerimaan; catatan asumsi; klasifikasi biaya (software/hardware/jasa/OPEX).

**Belum ada angka harga yang diverifikasi** dalam diskusi ini. RAB/HPS final wajib didukung survei dan bukti kewajaran harga, kebutuhan rinci, komponen pajak/overhead sesuai aturan yang berlaku, dan tidak boleh menggunakan markup ganda.

## 5. Persyaratan keamanan & tata kelola

1. Lokasi dan klasifikasi data ditetapkan oleh TNI; **dokumen rahasia/terbatas tidak dikirim ke layanan AI publik tanpa persetujuan dan dasar kewenangan**.
2. RBAC per unit kerja, MFA, SSO/identity integration jika diotorisasi, principle of least privilege, segregation of duties.
3. Enkripsi data saat transit/tersimpan; backup terenkripsi; audit log append-only/tamper-evident; retensi dan penghapusan terkontrol.
4. AI retrieval hanya mengakses dokumen yang berhak dilihat pengguna; setiap jawaban menampilkan sumber dan periode, batas ketidakpastian serta aturan larangan mengarang data.
5. Skor atau usulan AI tidak menjadi keputusan final otomatis, termasuk penilaian ZI/SAKIP/PEKPPP, status personel maupun tindakan administratif yang berdampak.
6. Integrasi luar harus disetujui pemilik sistem, memiliki API/protokol resmi, autentikasi, pembatasan akses dan audit transfer.
7. Gunakan data sintetis/anonymized untuk demo dan pengujian sebelum memperoleh kewenangan memproses data nyata.

## 6. Kriteria penerimaan yang dapat dijadikan dasar KAK

- **Dashboard:** rekonsiliasi target/realisasi dapat ditelusuri ke rekaman sumber; filter periode/satker/indikator berjalan.
- **ZI/PMPZI dan PEKPPP:** instrumen dapat dikonfigurasi, eviden diunggah, penguji memberi komentar, riwayat perubahan terekam.
- **Workflow:** tiap permintaan menunjukkan status, pembuat, approver, waktu, versi dan keputusan.
- **Dokumen/AI:** hasil pencarian mengikuti hak akses, OCR diuji pada sampel representatif, jawaban menyertakan sumber, penolakan saat tidak punya bukti.
- **Keamanan:** pengujian MFA, pemisahan antar-satker, audit, backup-restore, vulnerability management.
- **UAT:** skenario dan ambang kelulusan disepakati dalam kontrak, termasuk jumlah pengguna serentak, performa dan target pemulihan.

## 7. Data yang masih wajib diperoleh sebelum RAB resmi

- Jumlah satker, pengguna total/serentak, level organisasi dan peran pengguna.
- Instrumen evaluasi dan bobot terkini yang disahkan, jenis laporan, siklus pelaporan, contoh formulir/arsip.
- Kondisi aplikasi yang sudah berjalan serta izin integrasi nasional/TNI.
- Kebijakan klasifikasi data, lokasi hosting, persyaratan infrastruktur, sumber AI yang diizinkan, akses jaringan.
- Volume dokumen saat awal dan proyeksi tahunan; kebijakan retensi; SLA; kebutuhan HA/DR.
- Batas anggaran, mekanisme pengadaan, tahun anggaran, waktu implementasi yang diminta, quotation harga.

## 8. Risiko utama

| Risiko | Mitigasi |
|---|---|
| Duplikasi aplikasi pemerintah | Konfirmasi *system of record* dan posisi GARDA RB sebagai workflow internal |
| Penilaian AI keliru/halusinasi | Sitasi eviden, verifikasi manusia, audit hasil, metrik penerimaan |
| Bocor data internal | On-premises/hosting yang disetujui, RBAC/MFA, enkripsi, redaksi data |
| RAB sulit dipertanggungjawabkan | Pecah per modul dan deliverable, survei harga, hindari biaya personel ganda |
| Scope creep karena integrasi | Fase dan API contract jelas, perubahan lingkup mengikuti tata kelola kontrak |
| Modul terlalu banyak di awal | Dahulukan 8 modul P1 dan bukti manfaat konkret |

## 9. Rekomendasi kesimpulan

Fokus penawaran yang paling terkait dengan aktivitas reformasi birokrasi adalah **PMPZI/Zona Integritas, PEKPPP, SAKIP/KPI, pengelolaan eviden, workflow tindak lanjut dan AI Document Intelligence**. Nilai strategisnya bukan sekadar visualisasi *command center*, tetapi mempercepat siklus pengumpulan data, evaluasi, koreksi, dan pertanggungjawaban.

---

**Riwayat:** v0.1 (2026-11-08) — mengarsipkan usulan fitur dari percakapan; belum dilakukan validasi instrumen regulasi terkini, pemilik proses, satuan kerja, quotation atau HPS.
