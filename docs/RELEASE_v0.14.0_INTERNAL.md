# GARDA 0.14.0 — Recommended scan and independent NVR recorder

Rilis internal privat: Windows EXE, macOS M1/Apple Silicon DMG, Ubuntu DEB/Linux AppImage, Android 13+ FOLD/Standard APK, Web, serta dua paket server terpisah untuk Windows/Ubuntu. Android versionCode 18 memakai signer internal yang sama dengan v0.13.0(17).

## Scanner

Recommended Ports menjadi default di UI dan API. Advanced Settings menyediakan pilihan Recommended Ports dan Full Port. Full Port hanya berjalan setelah dipilih secara eksplisit dan untuk satu IP. Full scan tidak dijalankan otomatis. Recommended memeriksa 17 port umum kamera/vendor: 21,23,80,443,554,1111,1234,1235,6666,7777,8000,8080,8554,8888,8899,10055,10067.

## Recorder NVR

MediaMTX 1.21.4 dikompilasi dari upstream commit `e65f9411a56b19076a0dfde1fb4a59414bdf642c`. Mesin merekam stream RTSP langsung ke fMP4, terpisah dari AI dan client. Preview/AI berhenti tidak menghentikan rekaman. Supervisor menghidupkan ulang engine yang mati atau tidak merespons dan mengembalikan profil kamera dari penyimpanan terenkripsi. Engine menyambung kembali ke sumber yang terputus.

Retensi uji yang dipilih owner: satu hari pada `D:\GARDA-Recordings`. Bagian rekaman 1 detik dan segmen sekitar 1 menit; lama segmen juga mengikuti keyframe kamera. Ketika ruang kosong di bawah cadangan 10 GiB, rekaman dijeda secara terlihat dan dilanjutkan saat ruang kembali tersedia. Tidak ada penghapusan file pribadi; retensi hanya mengelola folder video GARDA. Kamera/disk/power terputus tetap dapat menyebabkan celah rekaman.

Tab **Rekaman** menampilkan sumber terhubung, bukti berkas yang masih diperbarui, ruang kosong, status disk, jumlah pemulihan, jeda/lanjut rekam per kamera, timeline, dan playback. Kontrol akses API tetap berlaku; mode awal Admin tanpa login dipertahankan.

## Setup server

Paket `GARDA-Server-*` berisi core server privat, Web bundle, engine hasil kompilasi, checksum engine, lisensi dan skrip setup. Core/model/key tidak dimasukkan ke installer client.

Windows: ekstrak paket, gunakan Python 3.11+, lalu jalankan `Setup-Server.ps1 -HostIP <IP-LAN-server>`. Setup memasang dependency, memprovisikan model YuNet/SFace/FastALPR dan fingerprint lokal, menyiapkan recorder, serta membuat CA dan sertifikat HTTPS persisten. Port default 8843. Instal CA situs pada perangkat client; validasi TLS tidak dimatikan. Model awal diunduh sekali saat provisioning, lalu operasi menggunakan aset lokal.

Ubuntu: ekstrak paket ke `/opt/garda-server`, jalankan `bash setup-server.sh <IP-LAN-server> <folder-rekaman> <folder-data>`, lalu pasang unit `garda-server.service` dengan user/group `garda` dan hak direktori sesuai lokasi data. Windows startup sebelum login menggunakan `Install-WindowsStartup.ps1` yang harus dijalankan sebagai Administrator; tidak ada batas waktu eksekusi dan task diatur restart saat gagal. Ini berbeda dari menyalakan server di terminal pengguna.

Masukkan URL/kredensial RTSP kamera melalui form lokal Perangkat. Server tidak menebak password kamera. Kamera yang disimpan otomatis disambungkan oleh recorder saat server berjalan/restart. Koneksi client tidak menentukan apakah recorder tetap berjalan.

## Validasi dan batas klaim

- Tes source Python mencakup profil scan default/eksplisit, CSRF, retensi/config engine, proteksi folder, disk pause/resume, integritas binary, gateway API, dan TLS CA persisten.
- Uji lokal menggunakan delapan sumber RTSP sintetis H264, 640×360, 10 FPS, target CBR 4 Mbps per sumber: sekitar 168 detik, 584,572,661 byte rekaman. Seluruh delapan recorder aktif, pulih setelah engine dimatikan paksa dan sumber terputus, pulih setelah simulasi disk rendah; playback berhasil didekode menjadi frame nyata.
- YuNet/SFace dan FastALPR menggunakan model asli dan berhasil inference pada frame kosong. Ini membuktikan model berjalan, bukan pengukuran akurasi wajah/plat lokasi.
- Belum merupakan uji 24 jam kamera fisik, benchmark delapan kamera 1080p, pengujian reboot mesin owner, atau SLA uptime. Akun agent Windows bukan Administrator sehingga pemasangan startup SYSTEM memerlukan eksekusi lokal owner sebagai Administrator.
- Delapan kamera pada 4 Mbps membutuhkan sekitar 346 GB/hari; kapasitas kosong disk uji saat konfigurasi sekitar 321 GB sebelum cadangan dan file uji, sehingga satu hari penuh pada bitrate tersebut memerlukan disk lebih besar atau bitrate rekam lebih rendah.

## Distribusi dan verifikasi

EXE/engine Windows memakai sertifikat internal; OS tidak otomatis mempercayainya. DMG arm64 menggunakan ad hoc codesign tanpa Apple notarization. APK memakai persistent internal signer; migrasi dari APK lama dengan signer berbeda memerlukan backup. SHA256SUMS.txt, detached signature RSA, public key dan manifest OTA updates.json disertakan. Token GitHub untuk OTA tetap di server, tidak dibagikan ke client. Repository dan Release tetap privat.
