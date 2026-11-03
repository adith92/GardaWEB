# NEXTCAM NC-858 — OEM / Equivalent Research

Date: 2026-11-03

## Finding

Strong match: **SriHome SH048 Dual-Lens Outdoor PTZ**.

Confidence: **Likely, not yet proven at PCB/firmware level**.

## Why it appears to be the same platform

NEXTCAM NC-858 listing:
- Dual lens, one fixed + one PTZ
- 2MP + 2MP / Full HD dual view
- 4 mm lens
- H.264
- 3x digital zoom
- Pan/Tilt around 320–345° / 90°
- 2.4 GHz Wi‑Fi
- RJ45 LAN
- Two-way audio
- Human detection / human tracking
- Full-color night vision
- microSD up to 128 GB
- IP66
- DC 12V 1A
- SriHome mobile app

SriHome SH048 official/OEM material:
- Dual lens, fixed + PTZ
- 2MP + 2MP
- 2 x 4 mm lens
- H.264/H.265 variants
- 3x digital zoom
- Pan/Tilt 345–355° / 90°
- 2.4 GHz Wi‑Fi
- RJ45 LAN
- Two-way audio
- human detection / tracking
- full-color / IR night vision
- microSD up to 128 GB
- IP66
- DC 12V 1A
- SriHome app

The housing, LED layout, dual antennas, mounting bracket and app ecosystem also visually match.

## OEM source

Alibaba listing from **Shenzhen Sricctv Technology Co., Ltd.** for SriHome SH048 supports OEM / ODM and custom logo. This materially strengthens the hypothesis that NEXTCAM NC-858 is a private-label/rebrand of the SH048 platform.

## Important limitation

This is **not native PoE** based on the available specs. Power is DC 12V/1A and LAN is RJ45 for data.

ONVIF is explicitly claimed by NEXTCAM marketplace listings. For SriHome SH048, third-party integration sources report ONVIF/RTSP support, but exact firmware should be tested before standardizing it for GARDA.

## GARDA procurement note

For the PUSADA/GARDA KAK, the required camera baseline is PTZ 4MP, PoE, ONVIF. NC-858 / SH048 is useful for lab/testing but does not satisfy the native PoE requirement.

## Sources

- NEXTCAM NC-858 official marketplace listings (Shopee/Blibli)
- Nextcam catalog
- SriHome / Sricam official SH048 product pages
- SriHome Malaysia SH048 product page
- Alibaba SriHome SH048 OEM listing
- CCTV Database community integration entry for SH048
