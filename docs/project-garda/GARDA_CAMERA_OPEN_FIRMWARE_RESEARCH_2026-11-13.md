# GARDA — Riset kamera PoE, ANPR/LPR dan firmware modifikasi (2026-11-13)

## Status dan keputusan teknis
- **ANPR/LPR bisa dikerjakan pada software AI di server Linux tanpa modifikasi firmware kamera.** Kamera hanya perlu menghasilkan video yang memadai (RTSP/ONVIF). Kamera yang secara fisik dioptimalkan untuk plat bergerak tetap menguntungkan: sensor, shutter cepat, lensa vari-focal/telefoto, WDR, IR/pencahayaan dan sudut pemasangan.
- **Face recognition** juga dijalankan pada server, kamera fixed boleh dipakai untuk jalur wajah dan plat. Persyaratan KAK PTZ untuk titik lain dan perubahan KAK masih pending revisi resmi oleh user.
- **OpenIPC** cocok untuk eksperimen firmware pada modul chipset/sensor yang diverifikasi; tidak semua model kamera cocok meski namanya sama. Majestic adalah komponen streamer non-open-source menurut OpenIPC Wiki. Flash hanya setelah backup firmware dan konfirmasi kompatibilitas board/SPI/flash/sensor; risiko brick.
- **Thingino** alternatif firmware untuk beberapa model berbasis Ingenic, daftar kompatibilitas per varian: https://thingino.com/cameras
- Tidak perlu menuntut “semua protokol”; interoperabilitas inti: RTSP/RTP (H.264/H.265), ONVIF Profile T, ONVIF discovery, HTTP/HTTPS/API dan 802.3af/at PoE; opsional S (fase pensiun 2027), G (edge recording), M (metadata AI), NTP, SNMP, syslog, MQTT/FTP/SFTP. Garansi, update security, VLAN dan akses lokal perlu diuji.

## Shortlist pembelian Indonesia, harga listing bukan quotation final
1. **Tiandy TC-C34UN I8/A/E/Y/2.8-12mm/V4.2**, 4MP, motorized varifocal 2.8–12mm, PoE 802.3af, RTSP, ONVIF Profile S/T/G, IR hingga 80m, 120dB WDR, shutter 1s–1/100000s. Cocok diuji sebagai kamera fixed khusus capture plat (motorized zoom bukan PTZ). **Rp1.899.000** (JakartaCCTV): https://www.jakartacctv.co.id/tiandy-tc-c34un-i8-a-e-y-2-8-12mm-v4-2 | Official Tiandy: https://tiandy.co.za/products/4mp-motorized-ir-bullet-camera-tc-c34un-spec-i8-a-e-y-2-8-12mm-v4-2
2. **Dahua IPC-HFW2449TL-S-PRO**, 4MP, 1/1.8in sensor, fixed lens, manual electronic shutter, 802.3af PoE, RTSP and ONVIF S/T/G; suitable for fixed face/general low light at close/medium distances, must test footage and exposure. **Rp1.320.000** listing Blibli: https://www.blibli.com/p/dahua-ipc-hfw2449tl-s-pro-4mp-kamera-cctv-ip-camera-poe-audio-bullet-full-color/ps--TOC-70003-02306 | Official Dahua: https://www.dahuasecurity.com/ceen/products/network-products/network-cameras/WizSense-2-Series/WizColor/IPC-HFW2449TL-S-PRO%3DS1
3. **HiLook IPC-D140HA-LUC**, 4MP, fixed dome, PoE, ONVIF listed, for general indoor close-up, **Rp1.213.000** listing: https://www.blibli.com/p/ip-camera-hilook-hikvision-4mp-ipc-d140ha-luc-kamera-cctv-poe-bersuara-berwarna/ps--TOC-70003-02379
4. **Hikvision DS-2CD1341G2-LIUF**, 4MP turret fixed, PoE, RTSP/ONVIF S/T/G listed, **Rp1.659.000** listing: https://www.blibli.com/p/hikvision-ds-2cd1341g2-liuf-4mp-kamera-cctv-ip-camera-poe-audio-turret-smart-light/ps--TOC-70003-02439

**Firmware OpenIPC untuk keempat model di atas TIDAK diverifikasi dan JANGAN dicoba tanpa verifikasi PCB/SoC/sensor/flash.**

## Shortlist Alibaba untuk eksperimen firmware, bukan kamera jadi
1. HSTD **5MP IMX335 + SigmaStar SSC30KQ** PCB/OpenIPC-style RTSP module, listing **US$38.50, MOQ 1**: https://www.alibaba.com/pla/5MP-IMX335-SSC30KQ-IP-Camera-Module_1601836959308.html?product_id=1601836959308
2. HSTD **SSC30KQ+IMX335 PoE-supported** PCB, listing **US$59.90, MOQ 1 set**: https://www.alibaba.com/pla/SSC30KQ-IMX335-IP-Camera-Module-5MP_1601794931858.html?product_id=1601794931858
3. Vanhua **Ingenic T40N+Sony IMX335 5MP**, seller claims OpenIPC support, listing **US$26–36, MOQ 2**, actual compatibility must be confirmed by OpenIPC: https://www.alibaba.com/pla/Ingenic-T40N-Chipset-SONY-IMX335-Sensor_1601316569569.html?product_id=1601316569569
4. CCDCAM **SSC30KQ+IMX335 5MP** module, 12V DC board, not proof of integrated PoE: https://www.alibaba.com/product-detail/Drone-5MP-H265-Ip-STARVIS-HD_1600478579484.html

Harga board belum termasuk lensa varifocal/tele, housing IP67, IR cut & lighting, PoE board/power, mount, pengiriman, garansi. Jangan bandingkan langsung dengan kamera jadi.

## Persyaratan sampel dan pertanyaan wajib seller
- Foto **kedua sisi PCB**, markings SoC, sensor, flash capacity, RAM; firmware build, board revision; OpenIPC image tested with this exact combination? recovery method, factory firmware backup and UART 3.3V.
- PoE IEEE 802.3af/at **native on shipped assembly** vs optional splitter/12V-only.
- RTSP URL + credentials, ONVIF Profiles **T/S/G/M** per firmware, H.264/H.265, access offline LAN, no subscription, WebUI, manual shutter/gain/WDR, snapshots; timestamp sync NTP.
- One full assembly quote (case IP67 + lens appropriate distance + IR illuminator + power + mounts) for **1 sample and 10 units**, domestic shipping to China forwarder, delivery time, warranty and ability to supply exact same hardware batch.
- Ask uncompressed or lightly compressed **raw moving-vehicle footage day/night** for own GARDA ANPR tests.
- Compare capture quality using same camera position and motion speed before bulk order.

## Standards references
OpenIPC hardware check https://openipc.org/supported-hardware/full-list
OpenIPC getting started https://openipc.org/get-started
OpenIPC wiki device support caveat https://github.com/OpenIPC/wiki/blob/master/en/guide-supported-devices.md
ONVIF profiles https://www.onvif.org/profiles/
ONVIF S sunset announcement https://www.onvif.org/pressrelease/onvif-to-end-support-for-profile-s/

Status: informational procurement research only, no purchasing or firmware changes completed.
