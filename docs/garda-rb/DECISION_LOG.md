# GARDA RB — Decision Register & Risks (DRAFT)

## Dinyatakan pengguna (arah produk, bukan parameter KAK akhir)
- Penawaran ditujukan kepada **Pus RB / Pusat Reformasi Birokrasi TNI**.
- Fokus AI untuk **pemrosesan dokumen, tanya dokumen/peraturan, arsip, storage**; kebutuhan jangka lanjut mencakup pembuatan soal, koreksi soal, dan meeting video sederhana dengan AI.
- CCTV cukup **Lite** sebagai pelengkap, mengingat hardware CCTV dan genset sudah ada.
- Target awal **Tier 1 Basic**, rencana empat tier dengan tiga tingkatan lebih tinggi.
- Pengguna meminta **pilihan dan checklist fitur**; pemilihan akhir belum diberikan.
- Pengguna meminta rekomendasi **bundling hardware** dan menyimpan dokumentasi ke GitHub.

## Usulan asisten, BELUM disetujui
- Empat modul: Ask Garda Knowledge, Garda Drive, CCTV Lite, Administration & Security.
- Delapan fitur inti AK-01 s.d. AK-08 otomatis dicentang dalam *default UI* sebagai rekomendasi, bukan persetujuan; enam tambahan AK-09 s.d. AK-14 belum dicentang.
- Contoh kuota: 30 user, 500 dokumen, 100 GB, 4 CCTV, 2 request AI simultan, 12 minggu; seluruhnya perlu finalisasi.
- Bundle hardware B AI server + NAS + UPS + network security + scanner; estimasi kasar Rp70–120 juta, bukan HPS.
- Nama GARDA NALAR RB dan judul kontrak panjang.
- UAT 20 kasus serta threshold awal; belum ada dataset dan benchmark produksi.

## Risiko kontrak/arsitektur
1. **Pencemaran scope:** Produk GARDA CCTV Tier 1 master menyertakan fitur yang berbeda (ANPR Lite/deteksi basic); untuk Pus RB jangan otomatis dimasukkan.
2. **Jawaban salah atau kehilangan konteks:** wajib jawaban ber-sitasi, no-source abstain, data terkurasi, human verification status peraturan.
3. **Dokumen sensitif:** klasifikasi, indexing, data residency, akses role, audit, enkripsi, lisensi model dan pengelolaan prompt harus ditetapkan.
4. **OCR scanner:** scanner fisik tidak otomatis menghasilkan dokumen searchable; jika dibutuhkan, ada biaya software OCR, QC hasil ekstraksi, alur koreksi.
5. **Storage keamanan:** RAID bukan backup; retensi, versi dan pemusnahan harus diatur, jangan klaim pengganti SRIKANDI.
6. **Meeting/soal:** belum ada dalam Basic; hindari menjual tanpa UAT, kapasitas server dan persetujuan scope.
7. **Hardware sizing:** kapasitas GPU tidak dapat diestimasi hanya dari jumlah user atau dokumen; test workload representatif.
8. **Penamaan:** singkatan tidak otomatis hak merek resmi; cek nomenklatur, instansi dan perizinan sebelum dokumen final.
9. **Harga & SLA:** estimasi diskusi dan contoh 12 minggu tidak boleh menjadi HPS/SLA final tanpa validasi.
10. **Timeline lintas proyek:** PUSADA 8+2 minggu dan 12 bulan support adalah instruksi spesifik PUSADA; jadwal GARDA RB belum ditentukan.

## Langkah akhir sebelum KAK siap pengadaan
- [ ] Pemilik proyek memilih AK-01 s.d. AK-14 serta kapasitas.
- [ ] Dapatkan daftar sumber dokumen/peraturan dan penanggung jawab keabsahannya.
- [ ] Tentukan batas klasifikasi dokumen dan kebijakan AI lokal vs layanan external.
- [ ] Cek 4 kamera existing atau jumlah lain, server/network existing, UPS dan kebutuhan NAS.
- [ ] Tentukan OCR: opsional atau termasuk.
- [ ] Setujui matriks role/permission serta retensi audit/backup.
- [ ] Finalisasi metode uji akurasi, sitasi, hallucination, concurrency, RPO/RTO dan keamanan.
- [ ] Tentukan judul resmi, jadwal, support, item kontrak serta HPS.
