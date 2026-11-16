# Migrasi development GARDA CCTV ke GardaWEB

Tanggal: 16 November 2026 (Asia/Jakarta).
Status: owner meminta pemindahan source dan kelanjutan development di GardaWEB.

## Asal dan cakupan

- Repository asal: private `adith92/docs`.
- Main asal saat diperiksa: `15e6cb59a22e1b2883ccd95deb45628e3c0e0afd`.
- Source aplikasi terbaru: branch `feature/garda-ai-unified-windows-android-20261114`,
  commit `e37d037458d6823178f75e1322d7e230bc8afaf1`.
- Base tujuan: GardaWEB main `9280add1be4ae759759f22571e6fdff584d95eaa`.
- Diimpor 124 file: `projects/foldview-cctv`, `projects/garda`,
  `projects/cctv-firmware` serta tiga workflow Android, AI dan native ONVIF.
- Perbandingan source main dengan branch terbaru tidak menemukan perubahan main
  tambahan pada cakupan yang diimpor. Update AI 14 November ikut dipertahankan.
- Riwayat penuh asal tetap di repo docs. Impor berupa snapshot dengan manifest
  blob Git; tidak membawa riwayat proyek lain di repo docs ke GardaWEB.

[Manifest](GARDA_CCTV_MIGRATION_MANIFEST_2026-11-16.json) mencatat commit asal,
path, mode dan SHA blob setiap file. File aplikasi dan gambar dipertahankan
identik. Penyesuaian migrasi terbatas pada README/petunjuk lokasi dan trigger PR
untuk workflow build Android/native; daftar pengecualian tercatat di manifest.

## Development dan distribusi

- [Entrypoint development](../projects/README.md).
- Android FOLD/Standard tetap v0.12.2, versionCode 16 dan package ID semula.
- Build debug asal terakhir berhasil pada
  [run 14 November](https://github.com/adith92/docs/actions/runs/43586731057).
  Ini bukti CI asal, bukan hasil tes perangkat fisik.
- Artifact/APK lama, arsip Drive dan riwayat Actions tetap di lokasi asal;
  pemindahan source tidak menyalin ulang atau menerbitkan APK lama.
- Build berikutnya berjalan melalui Actions GardaWEB. Tidak ada signing key,
  credential kamera, model atau video pengguna yang ditambahkan oleh migrasi.
- Frontend web demo tetap mengikuti jalur build semula. Folder `projects/`
  dikecualikan dari upload Vercel agar source aplikasi/server tidak ikut paket web.

## Batas implementasi

Kode yang dipindahkan adalah baseline/prototipe yang sudah ada, bukan aktivasi
fitur premium pada produk Basic atau bukti memenuhi KAK PUSADA. Native mobile,
biometrik, retensi dan model otorisasi tetap mengikuti dokumen produk otoritatif.
AI Core di folder ini terpisah dari `services/garda-ai-vision` pada PR #10;
keduanya belum memiliki kontrak API dan identitas pengguna terpadu.

Temuan keamanan baseline tetap berlaku. Tidak ada aplikasi/AI/firmware yang
dijalankan ke kamera atau motor selama migrasi ini. Pergerakan PTZ, kualitas OCR,
stream dan instalasi APK perlu verifikasi terpisah pada perangkat sebenarnya.

## Cutover repo asal

Hapus source aktif dan tiga workflow dari main docs hanya setelah snapshot
GardaWEB tersimpan serta diverifikasi di main tujuan. Sisakan README pengarah
pada ketiga folder asal dan perbarui indeks proyek. Branch sumber 14 November
dan riwayat commit lama dipertahankan sebagai arsip provenance; development
berikutnya dilakukan di GardaWEB.
