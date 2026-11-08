# Checklist Pemilihan Fitur Ask Garda Knowledge — Tier 1 Basic Pus RB TNI

**Status:** Daftar opsi. **Delapan fitur inti ditandai sebagai REKOMENDASI AWAL, belum berarti owner menyetujui.** Tanda [ ] harus dipilih pemilik proyek dan difinalkan sebelum KAK/HPS.

## A. Fitur inti yang disarankan
- [x] **AK-01 Chat AI Tanya Jawab Dokumen:** Bahasa Indonesia, menjawab berdasarkan dokumen internal terindeks.
- [x] **AK-02 Tanya Peraturan dan Kebijakan:** peraturan, SOP, SK, pedoman yang memang sudah terdaftar/diindeks.
- [x] **AK-03 Upload dan Indeks Dokumen:** admin memasukkan PDF berbasis teks, DOCX, TXT.
- [x] **AK-04 Pencarian Dokumen Cerdas:** pencarian kata kunci dan kesesuaian semantik.
- [x] **AK-05 Referensi Sumber Jawaban:** judul sumber dan halaman/bagian bila tersedia, serta akses sesuai izin.
- [x] **AK-06 Ringkasan Dokumen Otomatis:** ringkasan, poin utama dan kesimpulan satu dokumen.
- [x] **AK-07 Jawaban Berdasarkan Bukti:** tidak memaksa jawaban yang tidak didukung sumber; nyatakan keterbatasan.
- [x] **AK-08 Pembatasan Akses Dokumen:** retrieval, kutipan, preview, unduh, chat history mengikuti hak akses.

## B. Tambahan Basic yang boleh dipilih
- [ ] **AK-09 Integrasi Garda Drive:** folder/berkas terpilih sebagai sumber indeks tanpa dua kali unggah. **Direkomendasikan untuk dipertimbangkan**, tetapi belum dipilih.
- [ ] **AK-10 Filter Peraturan dan Arsip:** tahun, jenis, kategori, unit kerja; bergantung metadata yang tersedia.
- [ ] **AK-11 Riwayat Percakapan AI:** pengguna melihat riwayatnya sendiri.
- [ ] **AK-12 Salin dan Unduh Jawaban:** copy atau ekspor teks sederhana.
- [ ] **AK-13 Feedback Jawaban AI:** pengguna menandai jawaban membantu/tidak tepat.
- [ ] **AK-14 Status Peraturan Manual:** label berlaku/diubah/dicabut yang diperiksa dan ditetapkan petugas, **bukan penilaian AI otomatis**.

## C. Pilihan kapasitas (semua belum disahkan)
### Jumlah dokumen awal
- [ ] 250 dokumen
- [ ] 500 dokumen — **rekomendasi**
- [ ] 1.000 dokumen

### Beban inference bersamaan
- [ ] 1 request
- [ ] 2 request — **rekomendasi**
- [ ] 4 request

### Format
- [ ] PDF berbasis teks + DOCX
- [ ] PDF berbasis teks + DOCX + TXT — **rekomendasi**

Kapasitas AI sangat bergantung pada jumlah halaman dan token per dokumen, model, VRAM, indexing, context length dan waktu respons. Jumlah dokumen saja **tidak cukup** untuk sizing hardware.

## D. Exclusions dan acceptance contoh
Tidak termasuk OCR massal dokumen scan, tulisan tangan, pembuat soal, koreksi soal, notulen otomatis video meeting, legal judgment otomatis, crawling seluruh internet atau training model dari nol.

**Uji contoh:** (i) 18/20 pertanyaan acuan dijawab tepat; (ii) rujukan dari 20 pertanyaan dapat diperiksa; (iii) 9/10 pertanyaan yang tidak punya sumber dijawab dengan abstain; (iv) 20 format berkas valid bisa diproses; (v) ringkasan 5 dokumen tidak menambah fakta material; (vi) tidak terjadi kebocoran pada 10 skenario akses. Target baru mengikat setelah protokol, dataset dan lingkungan disepakati. Detail UAT di [draft KAK](KAK_SCOPE_T1_BASIC_DRAFT.md).

## E. Form keputusan owner untuk dipakai saat finalisasi
- Fitur yang dicentang final: **BELUM DIPILIH**.
- Batas dokumen: **BELUM DIPILIH**.
- Concurrency: **BELUM DIPILIH**.
- Format: **BELUM DIPILIH**.
- OCR scanner: **BELUM DIPILIH**.
- Tanggal keputusan & penanggung jawab: **BELUM DITETAPKAN**.
