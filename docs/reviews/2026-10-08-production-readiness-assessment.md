# Kajian awal GARDA menuju produksi PUSADA TNI

Tanggal: 8 Oktober 2026. Baseline GitHub yang dibaca: `67c659a` pada `adith92/GardaWEB/main` (private).
Status: **REVIEW / PROPOSED**. Bukan desain yang disetujui, rencana implementasi, penawaran final, persetujuan KAK, atau hasil commissioning.

## 1. Pemahaman tujuan dan batas tahap ini

Owner meminta membaca KAK dan seluruh konteks produk terbaru, memberi saran sebelum membangun aplikasi production-ready, memakai proses brainstorming, serta menyinkronkan hasil ke GitHub.

Tujuan yang tercatat: GARDA menjadi WebApp keamanan utama yang berjalan lokal/offline, dengan perekaman NVR independen, bukti yang dapat ditelusuri, pembatasan akses, dan kemampuan bertumbuh melalui empat tier. PUSADA adalah referensi awal 16 titik. Basic komersial tetap satu site, 1–49 kanal, satu operator operasional bersamaan, retensi default 7 hari, AI presence/OCR terbatas, dan Vault ringan. Itu tidak dengan sendirinya memenuhi seluruh KAK PUSADA.

Asumsi untuk kajian ini: KAK yang diberikan merupakan kerangka persyaratan yang harus dipetakan, tetapi status persetujuan kontraktual dan perubahan resminya belum dibuktikan. Tidak ada asumsi bahwa 592 fitur, nama pemasaran, seluruh tier, server kandidat, atau SLA sudah disetujui untuk dibangun. Validasi tujuan dan keputusan arsitektur tetap diperlukan dari owner.

Jalur brainstorming: **architectural**, dipecah menjadi subsistem. Urutan berikutnya adalah keputusan kebutuhan → alternatif → review desain per bagian → spec tertulis → review owner → implementation plan tertulis dan pilihan eksekusi. Tidak ada kode produk, koneksi kamera pelanggan, dependensi produk, layanan cloud baru, atau deployment yang dibuat dalam kajian ini.

## 2. Sumber dan status bukti

- `AGENTS.md`: urutan dokumen, keselamatan, IP, scope, serta kewajiban PR.
- `docs/GARDA_DECISION_REGISTER_v0.3.md`: jawaban owner 1–20 dan keputusan 21–25; sumber utama intent owner.
- `docs/GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md`: Basic candidate scope dan acceptance; belum KAK/customer approved.
- `docs/GARDA_MASTER_FEATURE_CATALOG_v0.3.md`: 592 VID unik, seluruhnya DRAFT; bukan delivery backlog.
- `docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md`: pemetaan gap awal; dikonfirmasi ulang terhadap dokumen sumber saat ini.
- `docs/project-garda/GARDA_HARDWARE_PROCUREMENT_2026-10-07.md`: shortlist lab/procurement, bukan bukti installed capacity atau KAK enterprise compliance.
- `RUN_DEMO.md`, `package.json`, `src/store.tsx`, `src/ui.tsx`, `src/Operations.tsx`, `src/Administration.tsx`, `src/logic.mjs`: batas demo dan jejak implementation lokal.
- KAK DOCX yang diberikan owner, 5 halaman, dibaca seluruh paragraf/tabel dan kelima hasil render. SHA-256 sumber: `78e17fcca76dcdff8ceae50dc396434ff1906233fae3c2891acd1854dd79fdf9`. Dokumen asli tidak diubah atau diunggah dalam PR ini. Lokasi sumber: Downloads, judul “Kerangka Acuan Kerja Pengadaan Sistem Pemantauan Keamanan Berbasis Artificial Intelligence PUSADA TNI”.
- Tiga varian workbook HPS di `outputs/20261006-hps-*` dan `public/hps-comparison.html` dibaca sebagai catatan lokal **untracked**, bukan baseline kontrak. Pemeriksaan terbatas pada struktur, item utama, formula, dan cached values; tidak mengesahkan harga pasar, tarif, pajak, atau keseluruhan workbook.

Checkout awal masih `55c4014`; sesudah fetch ditemukan main terbaru `67c659a`. Checkout di-fast-forward tanpa mengubah file lokal HPS yang belum dilacak. Kajian dibuat pada branch tersendiri untuk review, tidak langsung mengubah main.

## 3. Kesimpulan

Fondasi product thinking sudah jelas, tetapi repository saat ini adalah **demo frontend + dokumentasi kebutuhan**, bukan sistem CCTV/AI produksi yang hampir selesai. Build dan empat tes logika demo lulus; itu tidak membuktikan streaming nyata, perekaman, inferensi, keamanan backend, failover, atau retensi.

Rekomendasi utama: pertahankan Basic komersial sebagai paket reusable, lalu buat **PUSADA Contract Bundle** yang memasukkan hanya modul tambahan wajib KAK dengan scope dan biaya eksplisit. Bangun inti perekaman/akses/bukti terlebih dahulu sebagai tahap engineering internal, bukan menghilangkan kewajiban final face recognition, Ask GARDA, audio, atau retensi 90 hari bila KAK tetap berlaku. Nama ini hanya deskripsi usulan, bukan SKU atau sertifikasi baru.

## 4. Hal yang sudah tepat dan perlu dipertahankan

1. Operasi kritis lokal/offline dan NVR backup independen: internet, AI, atau dashboard tidak boleh menentukan apakah video tersimpan.
2. Bukti lebih dulu: kamera, timestamp, rekaman asli dan audit wajib dapat ditelusuri dari event/hasil AI.
3. Basic face presence berbeda dari face identity; pengenalan orang harus memiliki kewenangan, enrollment, threshold, pengujian dan review manusia.
4. Pembatasan server-side untuk API, media, pencarian, export dan integrasi; sembunyikan tombol bukan kontrol keamanan.
5. Katalog VID stabil dan status DRAFT/DECIDED/PROPOSED/IMPLEMENTED/TESTED/ACCEPTED dibedakan.
6. Source core privat, hak penggunaan/source deliverable diatur kontrak dan ditinjau hukum; tidak menganggap frontend yang dikirim ke browser dapat dirahasiakan.

## 5. Gap atau pertentangan yang harus ditutup

| Temuan | Bukti | Dampak dan saran |
|---|---|---|
| Basic bukan seluruh paket KAK | Basic 7 hari/presence; KAK 90 hari, face enrollment/watchlist, Ask GARDA, audio/rules/analytics | Pertahankan dua baseline: produk komersial dan konfigurasi kontrak PUSADA. Jangan menyebut Basic otomatis patuh KAK. |
| Jadwal dan support berbeda dalam KAK | §2: implementasi 8 bulan + testing 2 bulan + support 12 bulan; §8: minggu 1–10 + support 12 minggu; §9 kembali menyebut support 12 bulan | Minta klarifikasi tertulis dari pemilik KAK sebelum estimasi/kontrak. Jangan memilih sepihak versi paling pendek. |
| Genset berbeda antara dokumen | KAK §4: 500 kVA; tiga HPS lokal item 11: 100 kVA | Survey beban kritis dan fasilitas; tetapkan kebutuhan dengan engineer daya/customer. Tidak mengubah KAK menjadi 100 kVA tanpa otorisasi. |
| Jumlah titik tidak konsisten | KAK: 16; HPS lokal item 14: “Dashboard monitoring 116 titik” | Konfirmasi kemungkinan typo vs scope baru, kemudian seragamkan KAK/BOM/HPS/SOW. Tidak menganggap 116 adalah keputusan. |
| Redundansi ambigu | KAK menyebut “1 unit redundant ... per unit”; HPS lokal NVR/storage/server masing-masing dua unit/set pada beberapa item | Nyatakan node count, active/standby, shared-storage dependencies, failover dan RPO/RTO. Dua box tidak otomatis memberi HA. |
| Shortlist custom bukan KAK enterprise | Threadripper/X399/UDIMM/four-GPU target vs Xeon/EPYC, ECC, rack, NVMe RAID1, redundant PSU, 10GbE dan warranty onsite 3 tahun | Pisahkan BOM lab dari BOM kontraktual. Kapasitas lab tetap harus dibuktikan; jangan substitusi diam-diam. |
| Harga HPS disesuaikan dengan faktor global | Varian hardware-protected row 5: volume 16 × harga dasar 1.765.000 × 0,35 → jumlah dasar 9.884.000; kolom harga dasar tidak ikut berubah | Effective unit price menjadi 617.750 sebelum OH/PPN, berbeda dari kolom harga satuan. Perlu quotation dan formula jelas, bukan asumsi semua komponen memperoleh diskon sama. |
| Person-month dan biaya paket belum otomatis terhubung | Workbook memuat Indeks Personel dan biaya paket yang di-scale; KAK memisahkan material/software dan melarang OH ganda personel | Rekonsiliasi tiap paket ke deliverable, reuse platform, effort, tarif dan quote. Pastikan subtotal, satuan, durasi dan sumber dapat diaudit. Tarif/pajak tidak divalidasi di kajian ini. |
| Uptime 99,99% masih aspirasi | Decision/PRD belum mendefinisikan objek ukur dan HA/SLA | 99,99% setara sekitar 52,56 menit downtime dalam 365 hari, bila diukur terus tanpa pengecualian. Tetapkan cakupan, interval, maintenance, RTO/RPO dan biaya sebelum menjanjikan. |
| Primary recorder belum dipilih | PRD memungkinkan GARDA record sendiri atau akses archive NVR | Putuskan sumber rekaman primer, retensi masing-masing, failover dan siapa pemilik index/clock. NVR backup independen tetap dipertahankan. |
| Tes belum produksi | Empat tes Node logika demo; `test:e2e` ada namun tidak ada suite/config Playwright tracked atau workflow CI tracked saat kajian | Jangan menganggap script sama dengan coverage. Sesudah scope approval, buat integration/E2E, negative auth, fault/restore, AI evaluation dan perangkat nyata. |

## 6. Perbaikan struktur requirement yang disarankan

Katalog 592 fitur berguna sebagai roadmap; **227 baris bertier T1 bukan 227 komitmen rilis pertama**. Gunakan acceptance slice dari PRD dan KAK untuk menentukan backlog. T1/T2/T3/T4 adalah batas komersial, bukan alasan menunda kontrol keselamatan yang wajib bagi fitur yang sudah aktif.

Ada ketidakselarasan yang perlu direview, belum diubah:

- Header packaging katalog masih menggambarkan identity recognition terutama di T3, sementara keputusan v0.3 dan VID-150–156 menempatkan baseline recognition di T2.
- VID-110 (watchlist match review) bertier T3, tetapi VID-155 (face watchlist) T2: bedakan fitur alert lanjutan dari minimum matching/review yang dibutuhkan modul T2 atau bundle KAK.
- VID-281/282 (purpose/authority records) bertier T3, sementara biometric identity sudah mulai T2: lawful purpose, authority, retention dan access log tidak boleh menunggu upgrade.
- AI Lite telah masuk T1, namun confidence/evaluation/model versioning dasar masih banyak ditempatkan T2/T3 (misalnya VID-521/523/576/578). Tetapkan minimum model version, provenance, uncertain-result handling dan evaluasi untuk AI T1; enterprise model registry tetap boleh roadmap.
- MFA-ready (VID-261) berbeda dari MFA aktif yang diwajibkan KAK. Hash manifest T1 juga tidak otomatis sama dengan seluruh chain-of-custody enterprise atau bukti keaslian sumber.
- README/handoff historical mempunyai instruksi lama dan literal `\n\n`; yang authoritative tetap blok current context/decision v0.3. Saran: satu entrypoint current + historical notices konsisten, tanpa menulis ulang sejarah.

Untuk setiap acceptance requirement, gunakan hubungan `KAK clause → VID(s) → module/add-on → permission → test → evidence → signoff`. Acceptance dan status implementasi belum boleh diisi sebagai lulus tanpa bukti. Feature IDs existing tidak diganti atau ditambah hanya untuk kajian ini.

## 7. Tiga pendekatan untuk dibahas

### A. Inti GARDA reusable dan bundle PUSADA eksplisit — rekomendasi

Pertahankan UI React/Vite yang berguna dan bangun aplikasi lokal dengan API/policy serta data transaksional, integrasikan mesin media/recording yang matang dan teruji, lalu worker AI terpisah. Gunakan batas modul yang jelas tetapi jangan membuat ratusan microservice atau federation Tier4 sekarang. Modul kontrak KAK dapat diberi entitlement khusus tanpa membuka seluruh tier premium.

Manfaat: produk tetap milik GARDA, scope kontrak jelas, recording tidak tergantung AI. Biaya/risiko: tetap perlu engineering backend, interoperabilitas NVR, pengujian perangkat, lisensi dependency/model dan operator SOP. Pemilihan komponen final belum dilakukan; shortlist historis bukan keputusan stack produksi.

### B. Platform VMS/AI komersial lokal dan GARDA sebagai lapisan operasi

Validasi platform yang sudah memiliki fungsi recording/failover/AI, lalu integrasikan GARDA untuk workflow, laporan, policy dan bukti. Dapat mengurangi pekerjaan pada video/AI bila perangkat/API sesuai, tetapi ada biaya lisensi per kanal/modul, ketergantungan API/vendor, offline-license dan hak distribusi yang harus diuji. Tidak ada vendor yang direkomendasikan atau diprovision pada tahap ini.

### C. Membangun recorder dan pipeline video/AI sepenuhnya sendiri

Kontrol lebih besar atas seluruh stack, tetapi scope codec/media/failover/retention/model jauh lebih berat. Tidak direkomendasikan untuk rilis kontrak pertama kecuali uji kebutuhan membuktikan komponen matang tidak memenuhi KAK. Ini bukan izin membangun sekarang.

## 8. Urutan decomposition dan acceptance yang disarankan

Ini urutan kajian/engineering, **bukan implementation plan yang sudah disetujui**:

1. **Baseline kontrak & survey:** daftar 16 titik/kanal, kamera/firmware/API, jadwal, daya, BOM enterprise, hukum pemrosesan, hak source/lisensi, dan penanggung jawab acceptance.
2. **Inti operasi aman:** auth/MFA/policy/audit + satu alur nyata camera → ingest → recording → playback → export, sebelum memperluas kamera. Recorder harus tetap berjalan saat AI berhenti dan WAN putus.
3. **Bukti, incident & recovery:** source/provenance, file payload nyata, export/manifest, timestamps, retention + protected incident evidence, backup terpisah, restore dan failure drills. RAID bukan backup; watermark/transcode export tidak menimpa source asli.
4. **AI KAK dan alarm/audio:** evaluasi person/face/LPR di kondisi target, authorized face enrollment, rules/notification, bounded zoned PA command dengan audit dan ack perangkat. AI/LLM tidak boleh langsung mengeksekusi tindakan fisik.
5. **Ask GARDA dan analytics:** index event terotorisasi, 7/30/90-day query, semua jawaban evidence-linked, unknown/partial coverage eksplisit, confidence model bukan otomatis probabilitas benar. Query dibatasi server-side sebelum data masuk konteks model; tidak mengeksekusi SQL/command bebas hasil LLM.
6. **Release acceptance:** measured 16-channel live + continuous recording + AI + playback/export, cold boot offline/license, denied URL/API/socket/export, disconnect/reconnect, disk-full/failure, backup restore, privacy/deletion, UAT operator dan berita acara. Tidak ada klaim production-ready sebelum gates kontrak ditutup.

PUSADA final tetap memerlukan seluruh fungsi wajib KAK kecuali perubahan resmi disetujui. Urutan tahap tidak mengubah scope serah terima. Federation, 3D twin, native mobile full app, dan fitur ekstrem roadmap tidak ditambahkan hanya karena tersedia dalam katalog. Mobile notification yang disetujui KAK berbeda dari pembangunan native mobile app.

## 9. Kapasitas dan operasional yang perlu dihitung

Contoh aritmetika, **bukan spesifikasi bitrate aktual**:

- 16 stream × 4 Mbps × 90 hari = **62.208 TB decimal** video sebelum filesystem/index, cadangan evidence, peak bitrate dan margin.
- 16 stream × 8 Mbps × 90 hari = **124,416 TB decimal** sebelum margin.
- RAID6 + hot spare mengurangi usable terhadap raw. Misalnya seluruh 14 bay terisi disk 16 TB dan satu disk hot spare: 13 disk aktif dikurangi dua parity memberi 176 TB nominal, sebelum overhead; KAK belum menetapkan jumlah disk terpasang final. Jangan menyimpulkan semua 14 bay harus terisi hanya dari ukuran chassis.
- Jika GARDA dan NVR masing-masing menyimpan copy independen, kapasitas dan target retensi masing-masing harus dihitung. Backup/evidence protected mempunyai anggaran kapasitas terpisah.

Empat GPU tidak otomatis berarti 49 kamera; ukur decode, inference FPS, model VRAM, recording I/O, koneksi browser dan konkurensi playback/export. PTZ saat patrol dapat meninggalkan ROI wajah/plat; lokasi mounting, focal length, shutter, lighting dan pola patrol harus diuji. Usulkan fixed capture view/camera khusus hanya bila survey membuktikan perlu dan perubahan scope diotorisasi.

Lisensi offline perlu prosedur expiry/grace, perubahan hardware, pemulihan clock, recovery dan support yang tidak secara tak terduga menghentikan fungsi kritis. Batas satu operator perlu definisi atomic seat/lease, browser/tab, heartbeat, takeover operator berikutnya, admin maintenance dan emergency recovery. Semua ini **OPEN**, bukan perilaku yang boleh dipilih diam-diam.

Vercel saat ini adalah tempat demo sintetis publik. Jangan mengunggah footage nyata, biometrik, credential atau konfigurasi jaringan pelanggan ke demo/GitHub. Production lokal/offline harus melayani UI dan dependensi kritis dari jaringan yang disetujui, tanpa mensyaratkan public Vercel atau model API eksternal. Klasifikasi actual pelanggan dan kebijakan jaringan wajib diperiksa walau SKU komersial classification advanced ada di T4.

## 10. Verifikasi kajian pada 8 Oktober 2026

- GitHub metadata: `adith92/GardaWEB` private, baseline main `67c659a` setelah fetch; perubahan kajian via branch/PR.
- KAK: 38 paragraf, empat tabel; semua konten teks dan kelima halaman render dibaca. Tidak ada edit sumber atau klaim legal compliance.
- Catalog check: **592 rows / 592 unique VID**, T1 227, T2 123, T3 91, T4 151; seluruh rows DRAFT.
- `npm test`: **4 passed / 0 failed** (filter, incident transition, seeded query/evidence reference, report totals).
- `npm run build`: TypeScript + Vite berhasil.
- Belum dilakukan pada kajian ini: runtime/browser retest, camera/model/hardware benchmark, security audit/pentest, backup/DR drill, validation quotation/tax/legal, acceptance pelanggan. Hasil demo sebelumnya tidak dijadikan bukti produksi.
- Perubahan produk/code/config: **tidak ada**. File HPS lokal, raw KAK, `.env*`, `.vercel`, `dist`, `node_modules` tidak ditambahkan ke PR.

## 11. Pertanyaan brainstorming pertama

Pertahankan keputusan NVR merekam mandiri sebagai backup. **Untuk PUSADA, rekaman primer yang diandalkan GARDA sebaiknya:**

1. GARDA merekam sendiri, NVR menyimpan copy independen (rekomendasi jika budget/storage/stream support lolos survey).
2. GARDA mengakses archive NVR sebagai sumber utama; harus lebih dulu membuktikan playback/export API, retensi, failover dan availability NVR.
3. Belum dipilih: lakukan survey inventory NVR/kamera dan kapasitas sebelum menetapkan topology.

Pilihan ini belum dijawab. Setelah jawaban, lanjut satu pertanyaan per giliran sesuai skill brainstorming. Persetujuan opsi ini tidak sama dengan persetujuan spec tertulis atau izin implementasi.
