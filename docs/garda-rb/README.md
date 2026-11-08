# GARDA RB / Pus RB TNI — Dokumentasi Penawaran Tier 1 Basic

**Status:** INTERNAL WORKING DRAFT / brainstorming, belum menjadi KAK final, belum mendapat persetujuan Pus RB, belum diuji sebagai sistem operasional.  
**Pencatatan:** 2026-11-08. **Asal:** diskusi proposal GARDA RB dalam Garda Project (Oktober–November 2026).

## Arah produk
GARDA RB ditawarkan sebagai aplikasi manajemen pengetahuan dan dokumen berbasis AI bagi Pusat Reformasi Birokrasi TNI. Fokus Tier 1 khusus Pus RB:
1. Ask Garda Knowledge — tanya dokumen/peraturan, ringkas, cari dengan rujukan.
2. Garda Drive — simpan, atur, cari, unduh, kontrol berkas.
3. CCTV Lite — tayangan dari kamera existing; bukan command center CCTV.
4. Administration & Security — pengguna, otorisasi, audit, backup dan keamanan.

Nilai jual utama: jawaban berbasis sumber arsip/peraturan yang sudah diindeks, terverifikasi, masih sesuai izin akses, dan bisa ditelusuri kembali. Tidak boleh mengklaim bahwa AI otomatis memahami *semua* peraturan tanpa proses pengadaan, validasi, indexing, pembaruan, dan pemastian akses dokumen.

## Pembedaan penting dengan lini GARDA CCTV lama
- `docs/GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md` berisi **Tier 1 generik GARDA CCTV/PUSADA** (1 site, 1–49 kamera, deteksi person/face-presence dan ANPR Lite serta perekaman). **Jangan ubah atau ganti baseline itu**.
- Dokumen di folder ini berisi **offering vertikal Pus RB**, secara komersial disebut *GARDA RB Tier 1 Basic Knowledge & Document Intelligence*. CCTV Lite hanya fitur pelengkap, dengan batas spesifik yang berbeda.
- Fitur `Ask Garda Knowledge` dalam GARDA RB **bukan** fitur `Ask GARDA` untuk pencarian event CCTV/PUSADA. Sumber pengetahuan, izin, pengujian, dan infrastrukturnya berbeda.
- `docs/GARDA_DECISION_REGISTER_v0.3.md`, katalog tier dan KAK PUSADA berlaku untuk produk/kontrak konteks masing-masing, bukan otomatis menjadi KAK Pus RB.

## Keputusan, usulan, dan hal yang belum dipilih
**Arahan pengguna:** lebih menonjolkan AI dokumen, tanya peraturan, arsip, penyimpanan seperti Drive; CCTV hanya Lite; disusun 4 tier, dengan Pus RB mengawali Tier 1. Pengembangan fitur soal, koreksi soal, video meeting, notulensi, AI yang paham arsip diarahkan sebagai roadmap. Pengguna meminta checklist Ask Garda Knowledge untuk dipilih; **belum ada pilihan final dari pengguna**.

**Seluruh angka dan acceptance gate berikut adalah USULAN**, bukan kontrak final: 30 akun, 500 dokumen indeks, 100 GB, 4 CCTV, 2 AI request simultan, 12 minggu implementasi; contoh hardware dan anggaran. Ada usulan alternatif 250/500/1.000 dokumen dan 1/2/4 concurrent. Jangan menyalin angka ini sebagai komitmen tanpa kesepakatan.

**Ketentuan proyek PUSADA yang sudah diputuskan berbeda:** implementasi 8 minggu + 2 minggu testing/commissioning serta support 12 bulan. Itu konteks PUSADA, **bukan otomatis jadwal GARDA RB**. KAK PUSADA asli pernah memuat penulisan waktu yang tidak konsisten; perbedaan historis wajib diberi catatan, bukan diterapkan diam-diam.

## Berkas
- [01 — Draft scope of work, batasan, hasil kerja dan 20 UAT](KAK_SCOPE_T1_BASIC_DRAFT.md)
- [02 — Checklist interaktif konseptual Ask Garda Knowledge, 14 opsi](ASK_GARDA_KNOWLEDGE_CHECKLIST.md)
- [03 — Penawaran bundling hardware dan asumsi biaya](HARDWARE_OPTIONS.md)
- [04 — Nama sistem, nama kontrak, tier dan penempatan roadmap](NAMING_ROADMAP.md)
- [05 — Keputusan, risiko dan hal yang perlu disahkan](DECISION_LOG.md)

## Referensi internal terkait
- [GARDA Tier 1 CCTV PRD](../GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md)
- [Register keputusan GARDA CCTV](../GARDA_DECISION_REGISTER_v0.3.md)
- [KAK gap matrix PUSADA](../GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md)
- [Katalog fitur GARDA](../GARDA_MASTER_FEATURE_CATALOG_v0.3.md)

## Catatan arsip
Konten teks diskusi telah direkonstruksi dalam Markdown yang bisa di-versioning di GitHub. Dokumen DOCX/PDF proposal chat sebelumnya **tidak dinyatakan diunggah** ke repo ini. Semua kutipan harga hardware dan rekomendasi model adalah catatan brainstorming, bukan quotation atau HPS yang terverifikasi.
