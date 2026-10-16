# PMC GARDA V2 demo final PUSADA

Keputusan owner 16 Oktober 2026: PMC V2 menjadi demo final yang mengikuti fungsi KAK PUSADA dengan data sintetis. Final di sini adalah target kelengkapan demonstrasi; bukan sertifikasi produksi, SLA, atau hasil UAT perangkat nyata.

## Jadwal final

Implementasi 8 minggu (minggu 1–8), testing/UAT/commissioning 2 minggu (minggu 9–10), support/warranty 12 bulan sejak BAST/serah terima operasional. Keputusan ini menggantikan seluruh konflik jadwal terdahulu dan tidak perlu ditanyakan ulang.

## Perubahan langsung pada putaran ini

- Animasi abstrak Three.js di Command V2 diganti ilustrasi CCTV GARDA bergerak. Operator dapat memilih logo PUSADA dalam identitas GARDA berputar dan menjeda animasi. Preferensi reduced motion dihormati. Tidak membutuhkan WebGL.
- Identitas V2 menggunakan demo KAK PUSADA agar tidak menyatakan fungsi premium sebagai entitlement Basic.
- Brief tahap 2, decision register dan gap matrix memakai jadwal final.
- Desain awal pada `/` dan navigasi `/V2` dipertahankan.

## Pembahasan perubahan besar untuk mencapai demo final

| Kebutuhan KAK | Keadaan saat telaah kode | Target demo final dan bukti klik |
| --- | --- | --- |
| 16 titik, multi-layout, playback | 8 fixture kamera, layout sampai 16; kontrol simulasi tersedia | 16 fixture berbeda; 16 tile terisi; kamera → timeline → bookmark → export berlabel demo |
| Face recognition | Identitas dan watchlist sintetis tersedia; belum seluruh proses KAK | Enrollment contoh sintetis, confidence/threshold, tertutup/uncertain, review manual, akses dan audit |
| LPR | Log dan kategori kendaraan sintetis tersedia | Pencarian plat + periode, whitelist/blacklist, confidence dan snapshot terhubung ke kejadian |
| Alarm dan rule engine | Event simulation dan incident lifecycle tersedia | Intrusi, loitering, tamper, signal loss; rule → event → acknowledge → assign → resolve; kanal notifikasi simulasi |
| Audio zonasi | Belum ada modul PA zonasi khusus | Pilih zona, pesan, prioritas; review operator sebelum simulasi kirim; hasil dan audit. Tidak menyalakan speaker nyata |
| Device health dan diagnostics | Halaman Devices/System sintetis tersedia | Online/offline/service/rusak, suhu/storage/bandwidth/uptime, tiket dan penyebab yang merujuk telemetry sintetis |
| Tren dan GIS | Analytics dan peta demo tersedia | Filter 7/30/90 hari pada dataset 90 hari yang konsisten; heatmap/top lokasi; titik → event → footage |
| Ask Garda | Lima jawaban deterministik; belum dataset 90 hari | Contoh jam masuk, lokasi hari ini, lokasi tersering; rentang, sumber event, confidence, lokasi, tautan rekaman, peminta; jawaban tidak mengarang data kosong |
| Administrasi, RBAC/MFA, audit | Role dan pengaturan frontend merupakan simulasi | Persona admin/operator/auditor/viewer, MFA demo, penolakan aksi dan audit yang terlihat; tidak diklaim sebagai auth produksi |
| Retensi, backup dan recovery | Metrik contoh dan backup belum membuktikan 90 hari | Tampilkan target KAK 90 hari terpisah dari hot storage; skenario backup/restore/failover dan hasil simulasi; tidak memalsukan kapasitas disk |

## Urutan pengerjaan yang direkomendasikan

1. Satu dataset sintetis 90 hari untuk 16 titik, dengan event ID, lokasi, timestamp WIB dan evidence ID yang konsisten di semua halaman.
2. Lengkapi alur prioritas: Command → alarm → kamera/playback → insiden → bukti; wajah/plat → histori → rekaman.
3. Tambah Rule Engine dan Audio Zonasi, lalu Ask Garda serta analytics 7/30/90 hari dari dataset yang sama.
4. Simulasi persona/hak akses, MFA, audit, retensi/backup/restore dan kesehatan perangkat.
5. Verifikasi klik end-to-end, direct-link reload V2, desktop/mobile, terang/gelap, reduced motion dan reset data demo. Baru label rilis sebagai demo final lengkap setelah checklist ini lulus.

## Skenario presentasi

Operator melihat alarm intrusi gudang pada Command, membuka kamera dan rekaman, membuat insiden, memeriksa bukti, menyimulasikan pesan zona setelah review, menyelesaikan insiden, lalu Ask Garda merangkum kejadian dengan tautan bukti. Skenario kedua mencari plat dan histori kemunculan; skenario ketiga memeriksa kamera offline, tiket, dan status pemulihan.

Semua identitas, plat, kamera, data lokasi, video/ilustrasi dan status perangkat bersifat fiktif. Paket demo KAK tidak mengubah batas paket Basic produksi, kebutuhan pengujian perangkat atau keputusan otoritas kontrak.
