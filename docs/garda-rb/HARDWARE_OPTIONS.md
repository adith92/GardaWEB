# Bundling Hardware GARDA RB Tier 1 — Opsi Penawaran

**Status:** rekomendasi awal, **bukan spesifikasi pengadaan final, bukan harga pasar yang divalidasi/quotation, bukan HPS**. CCTV dan genset telah disebut pengguna sebagai hardware yang sudah ada.

## Prinsip
Nilai perangkat harus menunjang penggunaan utama AI dokumen, bukan sekadar menambah material. **Prioritas konseptual:** AI compute → penyimpanan berizin & backup → UPS + segmentasi jaringan → scanner arsip (jika OCR dipilih) → display/meeting opsional. Hindari membeli mesin baru bila kapasitas dan klasifikasi sistem internal mencukupi.

## 1. Daftar hardware yang dibahas
| Perangkat | Rancangan awal yang dibahas | Posisi & catatan |
|---|---|---|
| AI server lokal | CPU 12–16 core, RAM 64–128 GB, NVIDIA GPU VRAM 16–24 GB, NVMe 2 TB | Prioritas **bila** inference harus on-prem; VRAM, RAM, AI concurrency wajib di-benchmark |
| NAS | 4-bay; opsi awal 2×8 TB atau 4×8 TB; RAID bila sesuai | Simpan Garda Drive/arsip; RAID bukan backup; hitung usable volume, snapshot, offsite dan retensi |
| Online UPS | 2–3 kVA dan perangkat shutdown/monitoring | Tetap berguna dengan genset, menutup jeda switchover dan memberi waktu shutdown |
| Firewall + managed switch | VLAN, VPN, pembatasan ingress/egress, segmentasi CCTV, app, admin | Prioritas keamanan; optimalkan existing bila memenuhi |
| Document scanner | ADF 80 lembar, duplex, jaringan, 600dpi (spesifikasi usulan) | Opsional; scanner saja tidak menciptakan teks pencarian. **OCR** perlu ditambah dalam KAK bila scan kertas akan di-query AI |
| Interactive display | 55–65 inci | Opsi show/demo eksekutif, bukan komponen utama Basic |
| Meeting room kit | webcam konferensi, mikrofon, speaker | Lebih cocok roadmap meeting Tier 2/3 kecuali ada kebutuhan ruang rapat immediate |

Perangkat contoh yang muncul dalam diskusi: NAS **Synology DS925+** (4 bay), scanner **Brother ADS-4300N** (ADF 80 lembar; kapasitas/kecepatan konfirmasi quotation), GPU **RTX 5060 Ti 16GB**. Contoh **bukan** pemilihan merek yang wajib, bukan bukti kecukupan dua AI request simultan, dan penulisan merek harus diperiksa terhadap aturan pengadaan.

## 2. Contoh rentang angka yang pernah dibahas (historis, belum diverifikasi untuk HPS)
- NAS Synology DS925+ di percakapan: sekitar **Rp15,8 juta unit tanpa HDD**.
- Scanner Brother ADS-4300N: sekitar **Rp11–14,5 juta**.
- GPU RTX 5060 Ti 16GB: contoh listing sekitar **Rp11,5 juta** (GPU saja).
- **Paket B** hardware keseluruhan: *placeholder* sekitar **Rp70–120 juta**, belum quotation lengkap, pajak, instalasi, lisensi, shipping atau pengujian.
Jangan gunakan angka ini sebagai harga terkini atau kontrak. Butuh survei pasar dan quotation tanggal penawaran.

## 3. Paket penawaran
**Paket A — Minimal:** AI server (jika tidak reuse), UPS dan kebutuhan jaringan. Reuse storage resmi jika layak.

**Paket B — Recommended (usulan):** AI server + NAS + UPS + firewall/switch (bila belum ada) + scanner **dengan OCR terbatas yang diperjanjikan**. Paket seimbang untuk dokumen dan arsip.

**Paket C — Executive Showcase:** Paket B + interactive display 65 inci + perangkat konferensi. Ini **tidak** otomatis memasukkan fitur software Zoom/Garda Meeting; tetap procurement item yang berbeda.

## 4. Sketsa integrasi (konseptual)
```text
Pegawai Pus RB (web browser, jaringan diizinkan)
            |
      Firewall / IAM / RBAC
            |
     GARDA RB App + AI Server
       /          |           \
Drive file/NAS  Search index  CCTV existing
       |
Separate backup (bukan RAID saja)
UPS → app/NAS/network ; genset existing untuk daya cadangan
Scanner → OCR optional → pemeriksaan metadata → Garda Drive → indexing Ask Garda
```

## 5. Sebelum dikunci dalam KAK/HPS
- Status peralatan existing; kebutuhan power dan UPS runtime; kapasitas genset dan ATS; jaringan LAN; kriteria isolated/air-gapped/offline.
- Jumlah halaman, tipe scan vs PDF digital, klasifikasi dokumen, kebutuhan model AI lokal, kemampuan concurrency/latensi, RAG indexing dan kebijakan audit prompt.
- Kamera existing RTSP/ONVIF, jumlah riil, izin akses, apakah hanya live stream.
- Ukur backup restore & kapasitas bebas, disk failure domain, snapshot offsite.
- Pisahkan item hardware, lisensi AI pihak ketiga, instalasi, pengembangan software, training, support dan pajak dari HPS. Jangan melakukan double counting.
