# GARDA — Open Source Video/AI Stack Research

Tanggal: 2026-10-11  
Status: research dan rekomendasi integrasi, bukan persetujuan produksi.

## Rekomendasi utama

1. **MediaMTX** — https://github.com/bluenviron/mediamtx — MIT. Gateway RTSP/RTSPS, RTMP, HLS, WebRTC, SRT, relay/proxy, recording/playback.
2. **go2rtc** — https://github.com/AlexxIT/go2rtc — MIT. Restream multi-protokol, WebRTC/MSE/HLS, dan adapter kamera.
3. **Frigate** — https://github.com/blakeblackshear/frigate — MIT pada repository utama. NVR lokal dengan deteksi objek, recording event, review, MQTT, dan go2rtc.
4. **agsh/onvif** — https://github.com/agsh/onvif — MIT. Library Node.js untuk discovery, profile, PTZ, snapshot, dan operasi ONVIF.
5. **CompreFace** — https://github.com/exadel-inc/CompreFace — Apache-2.0. Service HTTP/Docker untuk face detection, recognition, verification, dan embeddings.
6. **face_recognition** — https://github.com/ageitgey/face_recognition — MIT. Python API berbasis dlib untuk prototipe.
7. **openalpr/openalpr** — https://github.com/openalpr/openalpr — AGPL-3.0. ANPR lokal; perlu review lisensi sebelum distribusi.
8. **ar00n/alpr-rust** — https://github.com/ar00n/alpr-rust — kandidat eksperimen; license dan model harus diverifikasi.
9. **YOLOV8_IND_ANPR forks** — kandidat model/dataset Indonesia; license bobot dan dataset wajib diverifikasi.

## Arsitektur disarankan

Kamera IP (ONVIF discovery + RTSP) -> GARDA Camera Adapter -> MediaMTX (LAN gateway RTSP ke WebRTC/HLS) -> GARDA WebApp, worker analytics, ANPR worker, dan evidence API.

T1 Basic GARDA tetap membatasi face ke **face presence**, bukan identitas. Face recognition/biometric matching dikunci sebagai capability tier berikutnya dengan policy, audit, dan persetujuan hukum.

## Matriks keputusan

| Komponen | Peran | Lisensi | Rekomendasi |
|---|---|---:|---|
| MediaMTX | Gateway LAN/WebRTC/HLS | MIT | Integrasikan sebagai service |
| go2rtc | Restream/adapter | MIT | Integrasikan bila diperlukan |
| Frigate | NVR + object detection | MIT repo | Service terisolasi; audit image/model |
| agsh/onvif | ONVIF control/discovery | MIT | Library adapter GARDA |
| CompreFace | Face API lokal | Apache-2.0 | Service opsional T2 |
| face_recognition | Prototype worker | MIT | Prototype/benchmark |
| OpenALPR | ANPR | AGPL-3.0 | Isolasi service dan review legal |
| alpr-rust | ANPR eksperimen | perlu verifikasi | Jangan masuk baseline dulu |

## Batasan copy

Jangan membuat exact copy dari UI, source code, logo, dokumentasi, atau aset proyek lain. Kode pihak ketiga hanya boleh digunakan sesuai license, dengan LICENSE, copyright notice, NOTICE, dan atribusi. Model AI dan dataset harus diperiksa terpisah. AGPL memerlukan keputusan lisensi/distribusi khusus.

## Rencana implementasi

1. Tambahkan camera adapter ONVIF dan RTSP URL normalization.
2. Jalankan MediaMTX pada Docker Compose untuk LAN.
3. Tambahkan health check, reconnect, credential separation, dan audit.
4. Buat synthetic camera pipeline.
5. Tambahkan integration test ONVIF/RTSP.
6. Benchmark person/face-presence dan ANPR terpisah dari UI.
7. Buat THIRD_PARTY_NOTICES.md dan license inventory sebelum merge service.

Repositori dan license diperiksa melalui GitHub pada 2026-10-11. Pin commit/tag dan ulangi pemeriksaan sebelum distribusi.
