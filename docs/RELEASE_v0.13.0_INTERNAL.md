# GARDA 0.13.0 — Internal five-platform MVP

Rilis awal untuk pengujian internal. Repository dan Release tetap privat.

- Windows x64: installer EXE dengan sertifikat Authenticode internal permanen.
- macOS Apple Silicon (M1 dan seterusnya): DMG arm64, ad hoc signed, belum Apple notarized.
- Ubuntu/Linux x64: DEB dan AppImage; verifikasi integritas melalui SHA256SUMS.
- Android 13+: APK release FOLD dan Standard, ditandatangani key internal permanen yang sama; application ID lama dipertahankan.
- Web: bundle statis pada origin yang sama dengan reverse proxy `/garda-api` menuju AI server.

Satu server AI lokal Windows/Linux dipakai bersama kelima client. Mode awal langsung Admin tanpa login. Server dijalankan terpisah; installer client tidak menyertakan backend AI, model, rekaman, atau kredensial.

Fitur: delapan slot kamera awal, preview CCTV, referensi wajah, adapter SFace/DeepFace/InsightFace, FastALPR/PaddleOCR, pencarian kejadian, snapshot, dan manifest OTA Android dari GitHub melalui server. Model dan dependency inference dipasang serta dikonfigurasi pada server. InsightFace memerlukan hak penggunaan model yang sesuai. Loaded tidak berarti akurasi lokasi sudah tervalidasi.

Scanner LAN/TCP tersedia di tab **Jaringan** seluruh client Workspace. Pemindaian berasal dari LAN server: maksimal /24, satu pekerjaan aktif, 64 koneksi paralel, deadline 5 menit, tombol berhenti, progres, hasil parsial. Full port 1–65535 untuk satu IP. Petunjuk servis berdasarkan nomor port belum membuktikan kemampuan ONVIF/PTZ/audio/video kamera.

## Menghubungkan client

1. Siapkan server mengikuti [README_UNIFIED](../projects/garda/ai-core/README_UNIFIED.md). Mode default tanpa login.
2. Sajikan bundle Web menggunakan HTTPS LAN dan reverse proxy `/garda-api/*` ke `127.0.0.1:8808/*`. Gunakan CA internal yang dipercaya perangkat. HTTP loopback tersedia untuk uji pada mesin server.
3. Masukkan origin server di desktop atau GARDA AI Android, lalu buka Workspace. Web membuka `/workspace` pada server yang sama. Kamera memerlukan URL stream dan kredensial lokal.
4. APK lama dengan signer berbeda tidak bisa diperbarui langsung. Backup profil sebelum migrasi sideload manual; password kamera perlu dimasukkan ulang. Jangan hapus instalasi lama sebelum backup.
5. Salin aset `updates.json` ke direktori data server dan konfigurasikan token GitHub Contents read pada server saja (`GARDA_GITHUB_READ_TOKEN`). Set `GARDA_PUBLIC_ORIGIN` ke HTTPS origin server. Client tidak menerima token GitHub.

## Verifikasi dua langkah

Tahap 1: tes source Python lintas OS, tes kebijakan desktop, unit Android, TypeScript, dan audit alur UI. Tahap 2: pemeriksaan signature APK/EXE/aplikasi macOS, metadata/arsitektur paket, hash SHA256, inventaris ekspor client, smoke startup Linux, dan unduhan ulang aset Release sebelum publikasi.

Belum membuktikan delapan stream nyata bersamaan, akurasi wajah/plat lokasi, kemampuan PTZ kamera, instalasi DMG di Mac M1 fisik, ataupun instalasi APK di Android fisik. Ini MVP internal, bukan penerimaan produksi atau sertifikasi KAK.

Library frontend diperbarui ke stable terbaru pada 16 November 2026: React 19.3.1, Vite 8.3.8, TypeScript 7.0.2, Tailwind 4.3.5. Desktop memakai Electron 45.3.3 dan electron-builder 26.18.0. Dokumentasi signing dan komponen diperiksa melalui Context7 dan sumber resmi.
