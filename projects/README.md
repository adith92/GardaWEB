# GARDA application development

Mulai development aplikasi GARDA di repository private **adith92/GardaWEB**.
Pemindahan ini diminta owner pada 16 November 2026.

| Modul | Lokasi | Status |
|---|---|---|
| GARDA CCTV FOLD + Standard | [foldview-cctv/android](foldview-cctv/android/README.md) | Source Android v0.12.2, versionCode 16; dua flavor, debug builds |
| GARDA Desktop | [garda/desktop](garda/desktop) | Baseline PySide6 dan panel AI; runtime perangkat masih perlu diuji |
| GARDA Mobile lama | [garda/mobile/android](garda/mobile/android) | Baseline terpisah, package com.garda.camera |
| GARDA AI Core | [garda/ai-core](garda/ai-core/README.md) | Prototipe Python Windows/Linux, integrasi Android/Desktop |
| Desain Fold | [garda/design](garda/design/fold-edition-2026-11-10/README.md) | Referensi desain dan blueprint |
| ONVIF native | [cctv-firmware](cctv-firmware/fh8852v201-onvif/README.md) | Prototipe host; bukan image firmware siap flash |

Source lengkap FOLD/Standard berada di sini. `mobile/android-starter` pada
branch AI Vision lain hanya contoh API client, bukan pengganti aplikasi ini.
Kedua modul AI yang berasal dari repo berbeda belum disatukan sebagai satu backend.

## Build Android

Ikuti toolchain yang dipin di [petunjuk Android](foldview-cctv/android/README.md).
Dari `projects/foldview-cctv/android`:

```shell
gradle :app:testFoldDebugUnitTest :app:testStandardDebugUnitTest
gradle :app:assembleFoldDebug :app:assembleStandardDebug
```

Workflow `.github/workflows/foldview-build.yml` menjalankan pemeriksaan dan
mengunggah kedua APK beserta checksum/signature reports ke GitHub Actions.
APK adalah artifact build, bukan file source yang disimpan di Git.
Package ID tetap `org.foldview.cctv` dan `org.garda.cctv.standard`.
Kunci debug CI bersifat sementara; migrasi repository tidak menjamin APK baru
bisa menimpa instalasi lama dengan sertifikat berbeda.

## Titik lanjut development

1. Verifikasi kedua flavor melalui CI di repository ini.
2. Lengkapi inventaris kemampuan kamera dengan akun ONVIF lokal; uji stream,
   profil, audio, SD/replay dan motor PTZ sesuai kemampuan firmware.
3. Jalankan smoke test Fold7/ponsel: live, reconnect, fold/unfold, STOP PTZ,
   rekaman dan pemulihan daftar kamera.
4. Selesaikan signing key persisten untuk jalur update internal.
5. Rencanakan konsolidasi API AI Core dan branch AI Vision sesudah membandingkan
   auth, event schema dan aturan produk; keduanya saat ini prototipe terpisah.

Baca [catatan migrasi](../docs/GARDA_CCTV_MIGRATION_2026-11-16.md),
[AGENTS.md](../AGENTS.md) dan [review baseline](garda/docs/SECURITY_REVIEW.md).
Pemindahan source tidak mengubah tier, kontrak, atau status penerimaan produk.
