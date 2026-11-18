# RINGKASAN EKSEKUTIF

**GARDA Security** adalah inisiatif pengembangan platform perangkat lunak pemantauan keamanan berbasis kecerdasan buatan yang dirancang untuk menyatukan video CCTV, perekaman, kejadian, analitik, bukti digital, dan pengawasan operasional dalam satu ekosistem. Pengembangan menekankan arsitektur **local-first/on-premises**, interoperabilitas perangkat melalui standar terbuka yang didukung, serta jalur peningkatan dari sistem monitoring satu lokasi menuju command center multi-lokasi.

**Tujuan dokumen:** membuka penjajakan investasi strategis untuk membiayai pengembangan produk GARDA Security. Dokumen ini **tidak** menetapkan nilai investasi, valuasi, persentase saham, skema bagi hasil, proyeksi laba final, atau jaminan pengembalian investasi. Pembiayaan akan dikaji berdasarkan milestone, anggaran terverifikasi, dan kesepakatan para pihak.

**Prioritas pasar awal:** pemerintah dan instansi yang membutuhkan pemantauan kawasan, pengelolaan kejadian, kontrol akses data, dan integrasi dengan perangkat terpasang. Segmen industri, logistik, gedung, fasilitas komersial, dan infrastruktur menjadi peluang ekspansi berikutnya, bukan klaim pelanggan yang telah diperoleh.

**Kondisi pengembangan:** GARDA telah memiliki source Web PMC, Android Fold/Standard, komponen Desktop, AI Core, fondasi perekaman lokal, serta demonstrasi antarmuka yang dapat diuji. Sebagian modul sudah melalui pengujian kode atau build internal; konektivitas CCTV nyata dalam skala target, akurasi AI, hardening produksi, dan serah terima pelanggan belum diklaim selesai.

[IMAGE:01-cover.jpg|Ilustrasi presentasi GARDA Security: Web Monitoring Center dan konsep mobile, menggunakan data demonstrasi.]

## Pokok penawaran nilai

- **Satu pusat kendali:** operator mengakses tampilan kamera, alert, insiden, dan rekaman melalui alur kerja yang saling terkait.
- **Kedaulatan pengolahan data:** arsitektur yang memungkinkan video dan AI diproses pada server milik pengguna, dengan koneksi internet tidak menjadi ketergantungan dasar pada paket yang telah selesai dibangun.
- **Perangkat yang lebih fleksibel:** pendekatan ONVIF/RTSP untuk kamera dan NVR kompatibel, setelah pemeriksaan model, firmware, dan fitur.
- **AI modular:** deteksi manusia/wajah, ANPR Lite, dan perluasan analitik lanjutan dilakukan bertahap dengan pengujian akurasi dan pengawasan manusia.
- **Peluang pendapatan berulang:** lisensi, pembaruan, layanan dukungan, pemeliharaan, modul tambahan, dan ekspansi pelanggan.

## Ringkasan keputusan investasi yang masih terbuka

| Parameter | Posisi draf |
|---|---|
| Nama/identitas pengusul | GARDA Security sebagai brand; entitas hukum belum dicantumkan |
| Tujuan | Pendanaan pengembangan produk, bukan pembiayaan satu pengadaan tertentu |
| Calon investor | Umum; tidak ditujukan kepada pihak bernama |
| Skema kerja sama | Belum diputuskan; dapat dibahas equity, pembiayaan, atau pola lain |
| Target dana | Belum ditetapkan, bergantung ruang lingkup dan RAB |
| Posisi pasar | Penjajakan, belum ada kontrak pelanggan yang dinyatakan di dokumen |
| Strategi produk | Empat tier sebagai roadmap pengembangan bertahap |

# 01 | LATAR BELAKANG DAN MASALAH PASAR

## Tantangan sistem pemantauan konvensional

Sistem CCTV tradisional umumnya efektif sebagai sarana perekaman visual, tetapi operasi keamanan skala organisasi juga membutuhkan proses yang lebih luas: mengetahui kondisi perangkat, memahami kejadian yang memerlukan perhatian, menelusuri rekaman tertentu, mendokumentasikan tindak lanjut, dan menjaga agar bukti digital dapat diperiksa kembali. Tantangan meningkat ketika kamera berasal dari beberapa merek atau berada di beberapa zona operasional.

Di lingkungan dengan kebutuhan keamanan dan tata kelola tinggi, aplikasi monitoring tidak cukup hanya menghadirkan tampilan video. Sistem perlu membatasi kewenangan pengguna, menyajikan audit, mencegah akses silang yang tidak berwenang, dan tetap berguna ketika koneksi ke internet tidak tersedia.

GARDA Security mengarah pada penyelesaian masalah tersebut melalui satu platform modular. Pendekatan ini **tidak mengasumsikan** seluruh merek CCTV kompatibel atau semua keputusan keamanan boleh diotomatisasi. Dukungan perangkat, kapasitas, dan akurasi harus dibuktikan per implementasi.

## Sasaran pengguna dan pembeli

| Segmen | Kebutuhan tipikal | Arah solusi |
|---|---|---|
| Instansi dan fasilitas pemerintahan | Monitoring kawasan, audit, izin akses, pelacakan kejadian | Web PMC, local server, evidence, tata kelola |
| Fasilitas industri dan gudang | Pengawasan area, kesehatan kamera, gangguan operasional | Multi-camera, event, incident, device health |
| Perumahan, kawasan dan gedung | Monitoring akses, kendaraan, rekaman, respons operator | Video wall, ANPR Lite, alert |
| Operator multisite | Konsolidasi tampilan dan kebijakan lintas lokasi | Roadmap Tier 4, federasi dan command center |

Segmentasi di atas adalah **hipotesis pasar**. Ukuran pasar, anggaran pengadaan, siklus penjualan, kebutuhan sertifikasi, serta kompetisi akan dibuktikan melalui riset pasar, diskusi calon pelanggan, dan pilot.

# 02 | VISI, MISI, DAN DIFERENSIASI

## Visi

Menjadi platform teknologi keamanan terintegrasi yang mendukung pemantauan responsif, investigasi berbasis bukti, dan pengelolaan keamanan secara bertanggung jawab.

## Misi

- Mengembangkan sistem monitoring yang menggabungkan rekaman video, metadata, kejadian, dan alur respons operator.
- Mengutamakan pengolahan data lokal dengan opsi integrasi yang terukur.
- Memanfaatkan AI sebagai **alat bantu analisis**, bukan sebagai otoritas tunggal untuk penindakan.
- Mengembangkan produk yang dapat dinaikkan kapasitas serta fiturnya sesuai kebutuhan dan lisensi pelanggan.
- Menyiapkan dokumentasi, keamanan, pengujian, dan dukungan yang layak untuk sektor institusional.

## Keunggulan yang hendak dibuktikan

| Pilar | Nilai yang dituju | Pembuktian sebelum komersial |
|---|---|---|
| Local-first | Kendali dan lokasi data lebih jelas | Uji sistem tanpa WAN, reboot, backup/restore |
| Interoperabilitas | Dapat mengintegrasikan perangkat standar | Matriks model/firmware ONVIF, RTSP, recording dan PTZ |
| Efisiensi pemrosesan | Server GPU bersama memproses analitik pada beberapa saluran | Benchmark FPS, latency, konsumsi GPU, akurasi |
| Perangkat lintas platform | Akses melalui Web, Desktop dan Android | Pengujian instalasi dan interaksi pada perangkat sasaran |
| Workflow berbasis bukti | Penelusuran kejadian dan bukti terkait | Uji integritas ekspor, hash, referensi sumber |
| Ekspansi modular | Upgrade fitur/lokasi bertahap | Pengujian lisensi, entitlement, keamanan lintas tier |

# 03 | EKOSISTEM PRODUK GARDA SECURITY

GARDA dirancang sebagai satu ekosistem. Kamera dan NVR menyediakan sumber media; media gateway dan recorder mengelola aliran video; AI Core mengekstrak kandidat kejadian; penyimpanan lokal mengelola metadata; dan aplikasi klien menyediakan antarmuka operator. Kombinasi modul harus tetap berfungsi sesuai batas tanggung jawab masing-masing, termasuk saat worker AI terhenti atau koneksi luar lokasi terganggu.

[IMAGE:19-architecture.jpg|Skema arsitektur target on-premises GARDA Security. Skema bukan hasil sertifikasi atau uji beban.]

## Komponen utama

| Modul | Fungsi utama | Status yang dapat dinyatakan |
|---|---|---|
| GARDA Web Monitoring Center | Dashboard, live wall, playback, alert, incident, analytics, map | Demo interaktif dengan data sintetis; integrasi produksi belum lengkap |
| GARDA Desktop | Klien workstation operator dan panel aktivitas | Source dan baseline klien tersedia, pengujian lintas OS terbatas |
| GARDA CCTV FOLD/Standard | Android native, LAN discovery, RTSP/ONVIF viewer, PTZ jika didukung | Source dan build internal; uji perangkat fisik belum menyeluruh |
| GARDA AI Core | Motion, face presence, OCR plat, event, snapshot | Prototipe dan pengujian kode/simulasi; akurasi lapangan belum terukur |
| GARDA Local Backend | API kamera/kejadian, database, pengelolaan sumber RTSP | Fondasi kode dan pengujian unit/CI; bukan layanan produksi tersertifikasi |
| Media & Storage | Restream, rekaman lokal, playback dan retensi | Foundation MediaMTX/PostgreSQL; perekaman lapangan dan bukti hukum belum diuji tuntas |
| Advanced Intelligence | Face ID berizin, Ask GARDA, korelasi lintas kamera | Prototipe terbatas/roadmap tergantung tier dan izin |
| Federated Command | Konsolidasi multisite, GIS, integrasi perangkat/sistem | Roadmap enterprise |

# 04 | GARDA WEB MONITORING CENTER

## Dashboard Command Overview

Command Overview dirancang sebagai pintu masuk operasional yang menghubungkan indikator kamera, kondisi sistem, daftar insiden, peta kawasan, cuplikan kamera, dan event terbaru. Operator tidak perlu berpindah aplikasi untuk melihat gambaran awal situasi. Data pada antarmuka saat ini merupakan dataset demonstrasi.

[IMAGE:02-command.jpg|Dashboard GARDA Command Overview. Render antarmuka berdasarkan aplikasi demo yang dijalankan, bukan instalasi pelanggan.]

## Live Monitoring dan Video Wall

Video wall mendukung pola tampilan beberapa kamera, pencarian sumber, pemilihan kamera, dan alur menuju rekaman atau insiden. Pada instalasi komersial, jumlah stream aktif per pengguna akan bergantung pada lisensi, hardware decoding, konektivitas, dan pengujian aktual.

[IMAGE:03-live.jpg|Demo video wall GARDA. Gambar kamera adalah simulasi, bukan umpan CCTV langsung.]

## Playback, Timeline dan Pencarian Bukti

Target pengalaman playback meliputi navigasi berdasarkan kamera dan waktu, penandaan bookmark, pencarian event terkait, serta ekspor dalam format yang dapat diverifikasi. Rekaman di sistem produksi harus menyertakan integritas waktu, sumber kamera dan kontrol akses.

[IMAGE:04-playback.jpg|Contoh alur playback/timeline pada aplikasi demo.]

# 05 | ANALITIK AI: WAJAH, KENDARAAN, DAN KEJADIAN

## AI Lite sebagai fondasi

Fitur dasar yang direncanakan meliputi deteksi keberadaan manusia, deteksi keberadaan wajah tanpa mengidentifikasi individu, dan kandidat pembacaan pelat nomor berbasis OCR. Sistem mencatat waktu dan kamera sumber, serta menautkan snapshot atau cuplikan terkait ketika tersedia. Kualitas hasil bergantung pada kondisi kamera dan pengujian data lokal.

## Pengenalan wajah tingkat lanjut

Pencocokan identitas adalah kemampuan **berbeda** dari deteksi keberadaan wajah. Penggunaan untuk identifikasi seseorang, enrollment, daftar pengawasan, dan pencarian biometrik membutuhkan dasar pemrosesan sah, kewenangan, pembatasan akses, proteksi template, evaluasi false match, dan keputusan manusia. Fitur ini tidak disertakan otomatis dalam paket Basic.

[IMAGE:06-faces.jpg|Antarmuka demonstrasi fitur wajah; bukan hasil verifikasi identitas operasional.]

## Automatic Number Plate Recognition / LPR

Pipeline ANPR yang dikembangkan mencakup pencarian area pelat, pemotongan gambar, OCR, nilai confidence, pencegahan duplikasi, dan pencatatan peristiwa. Nomor dengan kualitas rendah harus memerlukan pemeriksaan manual. Pelat OCR yang terbaca **tidak** langsung menjadi dasar membuka akses fisik, menolak kendaraan, atau tindakan terhadap seseorang.

[IMAGE:07-plates.jpg|Antarmuka demonstrasi pencarian pelat nomor dan kandidat OCR.]

## Rule engine dan deteksi anomali

Kemampuan lanjutan yang direncanakan meliputi aturan berdasarkan zona, waktu, gangguan kamera, kehilangan konektivitas, pergerakan, dan peristiwa yang didefinisikan pelanggan. Alarm memerlukan konfigurasi prioritas, batas false alarm, mekanisme acknowledgement, dan histori penanganan.

# 06 | INVESTIGASI, INSIDEN, DAN BUKTI DIGITAL

## Incident Command

Alur incident management ditujukan untuk mengubah penemuan di layar menjadi proses kerja: pencatatan kasus, pemberian prioritas, penugasan operator, catatan pemeriksaan, hubungan ke kamera/rekaman, serta penutupan dengan audit. Ini menyediakan landasan operasional yang lebih luas dibanding sekadar video wall.

[IMAGE:09-incidents.jpg|Contoh Incident Command pada demo GARDA; kejadian yang ditampilkan bersifat fiktif.]

## GARDA Vault dan chain of custody

Vault dirancang sebagai ruang penyimpanan metadata, berkas terkait, dan referensi bukti dengan kontrol akses. Standar produksi perlu meliputi hash file, metadata kamera, identitas pelaku ekspor, cap waktu terverifikasi, kebijakan retensi, serta legal hold agar bukti penting tidak ikut terhapus oleh sistem pembersihan otomatis.

## Ask GARDA: pencarian dengan bahasa alami

Dalam roadmap Intelligence, Ask GARDA ditujukan untuk menerima pertanyaan operasional tentang kejadian, waktu, lokasi, dan bukti yang benar-benar tersedia, lalu menyajikan jawaban dengan referensi sumber dan tingkat keyakinan. Pada demo yang sekarang tersedia, respons yang diperlihatkan bersifat **deterministik menggunakan data simulasi**, bukan kemampuan LLM/VLM operasional yang sudah tervalidasi.

[IMAGE:10-ask-garda.jpg|Visual Ask GARDA berbasis demo deterministik. Hasil bukan investigasi atas data nyata.]

# 07 | DEVICE HEALTH, GIS, DAN ANALYTICS

## Status perangkat

Rancangan device health mencakup daftar kamera, keadaan daring/luring, informasi koneksi, status layanan, penyimpanan, dan jalur penelusuran kegagalan. Integrasi telemetry, SNMP, dan root-cause analysis penuh bergantung pada kemampuan perangkat dan tahap pengembangan.

## Peta situasional dan analitik

Peta lokasi dan panel tren dapat menghubungkan titik perangkat dengan insiden atau rekaman. Untuk pelanggan multisite, model hierarki wilayah dan hak akses menjadi bagian penting agar pusat tidak memperoleh akses lintas unit tanpa otorisasi.

[IMAGE:08-map.jpg|Peta demo dan penempatan kamera; tidak menggambarkan lokasi pelanggan nyata.]

[IMAGE:11-analytics.jpg|Panel analytics demo; angka dan tren merupakan data simulasi.]

# 08 | GARDA DESKTOP DAN ANDROID

## Klien Desktop

GARDA Desktop dikembangkan menuju pengalaman operator pada Windows, macOS Apple Silicon, dan Linux. Pendekatan saat ini melibatkan baseline PySide6 dan kandidat shared Electron client. Paket installer serta pengujian integrasi perangkat masih memerlukan tahapan QA dan distribusi yang disepakati.

## Aplikasi mobile Fold/Standard

Aplikasi Android diarahkan untuk pemantauan layar kecil dan perangkat foldable, dengan dukungan yang dikonfirmasi per perangkat untuk RTSP, pencarian ONVIF di LAN, PTZ, snapshot, audio monitoring dan penyimpanan rekaman terbatas. Kemampuan mobile tidak otomatis menyertakan fungsi premium pada paket Basic dan membutuhkan desain akses server yang ketat.

[IMAGE:17-mobile.jpg|Konsep visual GARDA Security mobile yang disetujui untuk materi investor; bukan screenshot APK produksi.]

## Pengamanan akses dari perangkat klien

Prinsip desain meliputi sesi pengguna bernama, pembatasan perangkat, koneksi HTTPS/VPN, dan otorisasi untuk setiap stream serta tindakan. Akses lokal Admin tanpa login yang tersedia pada laboratorium pengembangan **tidak boleh** digunakan sebagai pola deployment eksternal atau produksi.

# 09 | EMPAT TINGKAT SOLUSI KOMERSIAL

Empat tier adalah kerangka roadmap komersial. Nama pemasaran masing-masing tier belum seluruhnya disahkan; proposal ini memakai **nama generik** agar tidak mengesankan merek atau SKU yang telah terdaftar.

[IMAGE:18-roadmap.jpg|Peta jalan empat tier GARDA Security: Basic, Smart, Intelligence dan Command.]

| Paket | Fungsi yang dituju | Segmentasi awal | Status |
|---|---|---|---|
| Tier 1 - Basic | Satu lokasi, 1-49 channel berlisensi, satu operator bersamaan, live/recording, person/face presence, ANPR Lite, incident, vault dasar | Instalasi lokal terkendali | Product target; integrasi/UAT belum lengkap |
| Tier 2 - Smart | Rule engine, alert lanjutan, diagnostik, pengenalan identitas berizin, analytics | Organisasi yang memerlukan AI operasional | Roadmap/komponen prototipe |
| Tier 3 - Intelligence | Investigasi lintas kamera, Ask GARDA, korelasi historis, mobile khusus | Tim investigasi/operasi kompleks | Roadmap |
| Tier 4 - Command | Federasi multisite, GIS, kendali hierarkis, integrasi sistem keamanan | Organisasi besar, multi-unit | Roadmap arsitektural |

**Catatan retensi:** rancangan Basic menggunakan retensi default sekitar 7 hari yang disesuaikan kapasitas media. Retensi 30/90 hari, perangkat redundant dan persyaratan enterprise lainnya hanya dapat dijanjikan melalui paket tersendiri yang didukung perhitungan storage, hardware dan kontrak.

# 10 | ARSITEKTUR TEKNIS DAN TATA KELOLA DATA

## Desain on-premises

Sumber video berasal dari kamera IP, DVR/NVR, atau gateway yang kompatibel. Media server menerima stream, recorder menangani penyimpanan berkelanjutan, worker AI memproses frame yang relevan, dan backend menyimpan metadata, event, hak akses, serta audit. Klien menerima video dan data melalui antarmuka yang diotorisasi server.

| Lapisan | Komponen kandidat | Fokus keamanan dan operasi |
|---|---|---|
| Kamera dan jaringan | ONVIF, RTSP, switch/VLAN | Segmentasi jaringan, kredensial dan akses terkontrol |
| Media gateway | MediaMTX / FFmpeg | Rekoneksi, stream internal, pemisahan rekam dari AI |
| Data operasional | PostgreSQL lokal; SQLite pada prototipe tertentu | Backup, migrasi, enkripsi, audit, restore |
| Video evidence | File media/NVR/NAS khusus | Retensi, kapasitas, legal hold, integritas |
| AI inference | Model deteksi dan OCR CPU/GPU | Benchmark, model/license audit, human review |
| Klien | Web, Desktop, Android | HTTPS/VPN, sesi, RBAC dan pembatasan perangkat |
| Operasional | Monitoring, log, backup, update | Recovery, hardening, uji keamanan dan dokumentasi |

## Privasi dan keamanan

Data kamera, pelat nomor, wajah, dan rekaman video memerlukan kebijakan tujuan pemrosesan, retensi, kewenangan, prosedur insiden, serta pengendalian akses yang sesuai dengan peraturan dan kebijakan pengguna. GARDA akan menekankan prinsip minimisasi data, penolakan akses secara default, pencatatan aktivitas sensitif, serta pemeriksaan manusia untuk hasil AI yang tidak pasti.

## Hak kekayaan intelektual

GARDA Security direncanakan sebagai produk dengan core backend dan AI proprietary. Pemanfaatan kode pihak ketiga tetap tunduk pada lisensi masing-masing, termasuk audit atas penggunaan komponen open-source dan model. Lisensi penggunaan, integrasi, source delivery, serta skema hak investor ditentukan melalui dokumen perjanjian dan due diligence hukum.

# 11 | STATUS PENGEMBANGAN DAN VALIDASI

## Aset yang telah tersedia

- Repository privat dengan source Web PMC, komponen shared API, aplikasi Android Fold/Standard, source Desktop, AI Core dan dokumentasi arsitektur.
- Demo interaktif Web dan visual investor berbasis tangkapan layar antarmuka yang dijalankan dengan data sintetis.
- Pengujian kode serta build internal yang terdokumentasi untuk beberapa komponen, termasuk pengujian API, Android source, serta baseline CI.
- Fondasi PostgreSQL/MediaMTX untuk penataan data kamera dan rekaman lokal; belum dinyatakan siap operasi pelanggan.
- Rancangan roadmaps modul dan catalog fitur internal. **Daftar kandidat 592 fitur bukan daftar fitur produksi.**

## Bukti yang belum tersedia dan wajib disiapkan

| Bukti | Pengujian yang diperlukan |
|---|---|
| Kompatibilitas kamera | Uji model dan firmware sebenarnya, RTSP/ONVIF, reconnect, kontrol PTZ jika ada |
| Kualitas video | Latency, packet loss, performa 8/16+ sumber dan recovery |
| Analitik AI | Dataset resmi/berizin, precision, recall, false positive, kualitas OCR pelat Indonesia |
| Penyimpanan | Durasi retensi aktual, bitrate, RAID/NVR, pemulihan backup dan legal hold |
| Keamanan | TLS, autentikasi, MFA bila diwajibkan, RBAC end-to-end, pentest dan pemisahan jaringan |
| Distribusi aplikasi | Android signing stabil, installer Desktop, QA perangkat, update terkendali |
| Operasional | Dokumentasi instalasi, helpdesk, SLA sesuai rancangan berbiaya, UAT dan berita acara |

# 12 | STRATEGI MASUK PASAR DAN KOMERSIALISASI

## Pendekatan go-to-market

Tahap awal berfokus pada calon pengguna institusional yang dapat melakukan demonstrasi terkontrol dan memvalidasi kebutuhan secara resmi. Urutan yang disarankan adalah discovery kebutuhan, demo nonrahasia, penilaian infrastruktur eksisting, proof of concept terbatas, evaluasi hasil, penyusunan penawaran, lalu kontrak dengan acceptance criteria terukur.

Dibutuhkan kesiapan pengadaan: identitas badan hukum, klasifikasi kegiatan usaha, hak lisensi produk, perjanjian kerahasiaan, daftar komponen dan ketentuan open-source, dokumentasi teknis, personel, layanan support, serta ketentuan keamanan data. **Status penjajakan bukan kontrak, penunjukan, ataupun pengakuan pelanggan.**

## Sumber pendapatan potensial

| Sumber | Dasar penagihan yang dapat dievaluasi |
|---|---|
| Lisensi penggunaan | Site/channel/operator atau modul dan periode sesuai kontrak |
| Pengembangan dan implementasi | Setup, integrasi, konfigurasi, deployment, pelatihan |
| Pemeliharaan | Support tahunan, bug fix, security patch, evaluasi kesehatan |
| Ekspansi lokasi/kapasitas | Upgrade tier, penambahan titik kamera, server, atau tenant |
| Integrasi khusus | Adapter vendor, SIEM, GIS, sistem akses atau sistem lain |
| Paket enterprise | Kebutuhan advanced analytics, command center, federasi |

Harga dan margin memerlukan studi biaya, validasi willingness-to-pay, quotation hardware dan daftar lisensi pihak ketiga. Belum ada harga final dalam draf ini.

# 13 | ROADMAP PENGEMBANGAN DAN MILESTONE

## Logika milestone pendanaan

| Tahap | Deliverable prioritas | Indikator keputusan lanjut |
|---|---|---|
| M0 - Audit baseline | Inventaris source, dependency/license audit, backlog dan arsitektur | Reproduksi build, risiko kritis dipetakan |
| M1 - Basic operasional | Live/record/playback, registrasi kamera, event, RBAC minimum | Uji CCTV fisik, retensi, isolasi akses, QA |
| M2 - Validasi pilot | Pilot pelanggan berizin, laporan kualitas AI, SOP support | UAT, temuan kritis ditutup, biaya aktual terdokumentasi |
| M3 - Smart expansion | Rules, analitik, pengenalan berizin dan model governance | Akurasi, privasi, otorisasi, hardware capacity |
| M4 - Intelligence | Investigasi, Ask GARDA berbasis sumber, mobile enterprise | Tautan bukti, kontrol akses, evaluasi halusinasi |
| M5 - Command | Multisite, GIS, kebijakan federasi, integrasi enterprise | Isolasi tenant, failover, audit, skalabilitas |

## Jadwal implementasi awal yang telah diputuskan

Untuk **ruang lingkup implementasi awal yang disetujui kontrak**, GARDA menggunakan target kerja **8 minggu implementasi + 2 minggu testing/UAT/commissioning**, dengan **dukungan 12 bulan sejak BAST**. Jadwal ini bukan estimasi penyelesaian seluruh roadmap empat tier, bukan jaminan kelayakan tanpa survei, dan tidak otomatis berlaku bagi semua kontrak dengan spesifikasi enterprise berbeda.

| Periode | Kegiatan utama | Keluaran |
|---|---|---|
| Minggu 1 | Survei, penajaman scope, arsitektur, rencana keamanan | Baseline perangkat dan acceptance |
| Minggu 2-4 | Integrasi perangkat/network, backend/media, UI prioritas | Ingest dan operasi dasar |
| Minggu 5-8 | AI Lite, event, incident, security, monitoring | Fitur paket yang disetujui |
| Minggu 9-10 | Uji beban dan keamanan, UAT, commissioning | Laporan uji, perbaikan, dokumentasi |
| Setelah BAST | Support 12 bulan sesuai kontrak | Helpdesk, maintenance dan perbaikan |

# 14 | KEBUTUHAN PEMBIAYAAN DAN PENGGUNAAN MODAL

## Prinsip budgeting

Karena pengusul belum menetapkan target pendanaan, rencana investasi disusun **berbasis modul dan milestone**, bukan angka total yang direkayasa. Setiap pengeluaran wajib dikaitkan dengan deliverable, sumber quotation, durasi personel, risiko, dan bukti penyelesaian. RAB rinci akan disahkan melalui kajian teknis dan finansial terpisah.

| Kelompok | Kebutuhan yang dievaluasi | Metode estimasi |
|---|---|---|
| Pengembangan aplikasi | Backend, frontend, Android, desktop, integrasi | Person-month x tarif tervalidasi |
| Riset dan quality assurance AI | Dataset berizin, model, evaluasi, labeling | Pekerjaan dan milestone, biaya model/lisensi |
| Infrastruktur laboratorium | GPU workstation/server, storage, switch, UPS, CCTV uji | BOM x quotation, spesifikasi terukur |
| DevOps dan keamanan | CI/CD, monitoring, backup, hardening, pentest | Paket pekerjaan, vendor/SDM |
| Dokumentasi dan pelatihan | Manual, SOP, materi pengguna, UAT | Deliverable dan person-day |
| Legal dan komersial | Badan hukum, merek, IP, kontrak, konsultasi | Penawaran jasa |
| Bisnis dan go-to-market | Demo, PoC, perjalanan, pemasaran, proposal | Budget disahkan per tahap |
| Cadangan risiko | Risiko teknis, kurs, impor, perubahan scope | Kebijakan contingency yang disetujui |

## Kerangka perhitungan

- **CAPEX =** total harga peralatan dan fasilitas pengembangan berdasarkan quotation yang berlaku.
- **OPEX per fase =** jumlah personel x durasi x tarif terverifikasi + biaya rutin terikat proyek.
- **Kebutuhan dana milestone =** CAPEX fase + OPEX fase + biaya layanan dan cadangan yang disetujui.
- **Biaya produk per pelanggan =** biaya implementasi langsung + alokasi platform + biaya dukungan dan lisensi yang relevan.
- **Pendapatan berulang =** pelanggan aktif x nilai kontrak layanan periodik yang benar-benar terjual.

Tidak ada nilai rupiah, margin, laba, IRR, ROI, ataupun valuasi yang ditetapkan sebelum asumsi dan data input divalidasi.

# 15 | KERANGKA PROYEKSI FINANSIAL INVESTOR

## Variabel yang perlu dikunci

| Variabel | Status | Sumber yang disyaratkan |
|---|---|---|
| Dana investasi awal | Belum ditentukan | RAB berbasis milestone |
| Biaya engineering per bulan | Belum dihitung | Struktur tim dan tarif |
| Jumlah proyek potensial/tahun | Belum diproyeksikan | Pipeline dan probabilitas penjualan |
| Harga paket Basic/Smart/Enterprise | Belum ditentukan | Studi harga dan biaya produk |
| Margin implementasi | Belum dihitung | Costing proyek yang diuji |
| Tarif support dan perpanjangan | Belum ditentukan | Rancangan SLA dan biaya pemenuhan |
| Periode balik modal | Belum dapat dinilai | Proyeksi arus kas berbasis bukti |
| Valuasi dan porsi saham | Belum dinegosiasikan | Due diligence dan perjanjian |

## Tiga skenario

**Konservatif:** penjualan lebih lambat, kebutuhan validasi dan dukungan lebih tinggi, pengembangan prioritas Basic. **Moderat:** pilot berhasil dan ada penjualan berulang yang dibuktikan. **Optimistis:** beberapa pelanggan institusional dan kebutuhan ekspansi modul terkonversi. Ketiga skenario akan disusun numerik setelah tersedia data pipeline, harga, biaya, dan persentase penagihan.

Proyeksi awal tidak boleh menyatakan hasil pasti atau memakai status penjajakan sebagai pendapatan yang telah dikontrak.

# 16 | ALTERNATIF STRUKTUR KERJA SAMA INVESTASI

| Alternatif | Mekanisme yang dapat dibahas | Catatan |
|---|---|---|
| Penyertaan saham (equity) | Investasi pada entitas hukum pemegang IP GARDA | Memerlukan valuasi, due diligence, hak investor, dilusi dan tata kelola |
| Convertible funding | Pendanaan awal dengan opsi konversi berdasarkan syarat | Memerlukan penilaian hukum/pajak dan skenario konversi |
| Pinjaman usaha | Pengembalian pokok dan biaya pembiayaan sesuai kesepakatan | Perlu uji arus kas dan kemampuan pembayaran |
| Revenue sharing | Persentase pendapatan dari lini atau kontrak terdefinisi | Perlu rumus yang mencegah sengketa basis pendapatan/biaya |
| Strategic development partnership | Kontribusi pendanaan/keahlian/pasar terhadap milestone | Kepemilikan IP, eksklusivitas dan hak jual harus dibahas |

Pemilihan skema, nominal, jadwal pencairan, hak audit investor, batas penggunaan modal, hak kekayaan intelektual dan exit mechanism **belum diputuskan**. Seluruh opsi di atas bersifat bahan diskusi, bukan penawaran surat berharga yang mengikat.

# 17 | RISIKO, MITIGASI, DAN TATA KELOLA

| Risiko | Dampak potensial | Rencana mitigasi |
|---|---|---|
| Integrasi CCTV beragam | Perangkat tidak mendukung protokol/fitur | Uji model dan firmware, matriks interoperabilitas, adapter terbatas |
| Akurasi AI dan OCR | Kesalahan identifikasi dan investigasi | Evaluasi dataset berizin, ambang keyakinan, human review |
| Biometrics dan privasi | Risiko hukum, penyalahgunaan data | Dasar hukum pemrosesan, kontrol akses, retensi, audit |
| Kegagalan penyimpanan | Kehilangan rekaman/bukti | NVR independen, RAID sesuai kebutuhan, backup, restore, legal hold |
| Keamanan siber | Eksposur stream, kredensial dan data | Zero trust untuk API/media, TLS/VPN, RBAC, audit, pentest |
| Jadwal pengembangan | Scope melebihi kapasitas tim | Milestone terukur, scope freeze, UAT bertahap |
| Open-source/model licensing | Batas penggunaan atau distribusi | License inventory, legal review, pemisahan kode |
| Pengadaan institusional | Siklus panjang dan syarat administrasi | Kesiapan dokumen, kanal resmi, diversifikasi segmen |
| Arus kas | Kas habis sebelum produk tervalidasi | Pendanaan bertahap, burn-rate dan runway dashboard |
| Risiko operasional AI | Kesalahan otomatis berdampak nyata | AI tidak mengaktifkan kontrol fisik tanpa otorisasi manusia |

## Tata kelola dana yang diusulkan

Setiap pencairan terkait milestone dan acceptance. Laporan investor memuat realisasi anggaran, progres teknis, perubahan risiko, temuan UAT, forecast biaya, dan keputusan gate fase berikutnya. Kerja sama baru berlaku setelah penyusunan perjanjian formal.

# 18 | RENCANA DUE DILIGENCE DAN KEPUTUSAN TERBUKA

## Dokumen yang siap disiapkan untuk calon investor

- Demo GARDA dengan data sintetis, rekaman layar, dan penjelasan batas fungsi.
- Arsitektur teknis, backlog, paket tier, matriks fitur dan hasil CI.
- Bukti kepemilikan/perizinan kode dan legal review model/lisensi pihak ketiga.
- RAB pengembangan yang didukung quotation hardware dan tarif SDM.
- Rencana uji kamera, benchmark GPU, keamanan, backup, retensi dan UAT.
- Struktur badan hukum, hak atas merek, dan tata kelola investor ketika sudah ditetapkan.

## Keputusan yang wajib memperoleh persetujuan berikutnya

| No. | Butir keputusan | Status |
|---|---|---|
| 1 | Badan hukum yang menerbitkan perjanjian investasi | TERBUKA |
| 2 | Status pendaftaran dan penggunaan merek GARDA Security | TERBUKA |
| 3 | Nilai pendanaan tiap milestone dan jadwal pencairan | TERBUKA |
| 4 | Skema equity/loan/revenue share/partnership | TERBUKA |
| 5 | Peta kepemilikan IP, source dan lisensi produk | TERBUKA |
| 6 | Daftar calon pelanggan/pilot yang boleh diungkap | TERBUKA |
| 7 | Baseline keamanan dan acceptance produksi | TERBUKA |
| 8 | Harga paket komersial dan kebijakan support | TERBUKA |

# 19 | PENUTUP DAN UNDANGAN KERJA SAMA

GARDA Security mengundang calon mitra strategis untuk mengevaluasi pembiayaan pengembangan platform keamanan digital yang dirancang modular, berorientasi pengolahan data lokal, dan menggabungkan monitoring CCTV dengan analitik AI serta workflow operasional berbasis bukti.

Langkah pembahasan berikutnya mencakup presentasi produk dan demonstrasi terbatas, perjanjian kerahasiaan bila diperlukan, verifikasi kesiapan teknis dan hukum, penyusunan RAB per milestone, dan negosiasi struktur investasi yang adil serta terukur. Proposal ini merupakan **draf penjajakan non-binding** dan belum menjadi penawaran final mengenai kepemilikan saham atau tingkat imbal hasil.

**GARDA Security**  
Integrated AI Security, Monitoring & Intelligence Platform  
**Kontak resmi:** [Diisi setelah ditetapkan]  
**Entitas penerbit:** [Belum ditetapkan]  
**Tempat dan tanggal:** Jakarta, November 2026

# LAMPIRAN A | KATALOG VISUAL GARDA

Seluruh visual yang digunakan dibuat dari source demonstrasi GARDA dan disimpan dalam galeri visual investor internal. Gambar mencakup Command, Live, Playback, Events, Faces, Plates, Map, Incidents, Ask GARDA, Analytics, Vault, Devices, System, Audit, Settings, mobile concept, roadmap, dan arsitektur. Gambar **bukan** bukti integrasi CCTV pelanggan atau penggunaan pada instansi tertentu.

[IMAGE:12-vault.jpg|Antarmuka GARDA Vault versi demo.]

[IMAGE:13-devices.jpg|Antarmuka pengelolaan perangkat GARDA versi demo.]

[IMAGE:14-system.jpg|Panel kondisi sistem versi demo. Statistik tidak mewakili server produksi.]

# LAMPIRAN B | MATRIKS STATUS DAN SUMBER

| Bukti internal | Kegunaan | Status |
|---|---|---|
| AGENTS.md dan decision register | Kebijakan scope, keamanan dan tier | Dokumen internal |
| Tier 1 Basic PRD | Batas Basic, acceptance, pengecualian | Draf owner |
| Five-platform MVP status | Source dan validasi Web/Desktop/Android/AI | Source/build internal |
| Local foundation PR | PostgreSQL dan MediaMTX | Fondasi development |
| AI Vision lab PR | OCR, face/ONVIF lab module | Prototipe |
| Investor Visual Library | Render demo dan konsep mobile | Materi komunikasi |
| Master feature catalog (592 kandidat) | Semesta ide dan tier | Kandidat, bukan produksi |

**Catatan penting:** Dokumen persyaratan pengadaan pelanggan tertentu tidak menjadi pengakuan kontrak GARDA. Perbedaan ruang lingkup, retensi, hardware, pengamanan dan masa layanan wajib direkonsiliasi secara tertulis dalam setiap pengadaan resmi.

# LAMPIRAN C | KERANGKA KOREKSI DRAF

| Aspek untuk revisi | Masukan pengusul |
|---|---|
| Identitas perusahaan dan kontak | [KOREKSI] |
| Nilai dan skema investasi | [KOREKSI] |
| Pembagian kontribusi pendiri/investor | [KOREKSI] |
| RAB laboratorium dan tim engineering | [KOREKSI] |
| Harga lisensi dan model kontrak | [KOREKSI] |
| Pilot dan daftar pipeline yang boleh diumumkan | [KOREKSI] |
| Status pengujian CCTV dan AI | [KOREKSI] |
| Bahasa, branding, dan desain final | [KOREKSI] |
