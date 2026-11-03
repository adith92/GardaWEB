# GARDA Camera Open-Firmware Research — Indonesia & China

Date: 2026-11-03

## Goal

Find CCTV / IP-camera hardware that is practical for GARDA lab work and can be inspected, reflashed, or replaced with an open firmware such as OpenIPC from a PC.

## Key finding

The safer route is to buy hardware by **SoC + board model**, not by retail camera model name.

OpenIPC documentation explicitly warns that manufacturers may change boards/components inside the same retail model without notice. Before flashing, identify the SoC/board/flash size, back up stock firmware, and confirm support.

## OpenIPC-friendly SoC families to prioritize

Preferred / well-supported families found in current OpenIPC documentation include:

- Goke GK7205V200 / V210 / V300
- HiSilicon HI3516EV200 / HI3516EV300
- Ingenic T21 / T23N / T31 family / T40 family
- SigmaStar SSC30KD / SSC30KQ / SSC333 / SSC335 / SSC337 / SSC338Q / SSC377/378 variants
- Xiongmai XM510 / XM530 / XM550 are present but some remain at MVP/expert-install stage, so board-specific verification is mandatory.

## Indonesia availability

No strong evidence was found for a mature Indonesian retail category explicitly branded “OpenIPC camera”.

However, Indonesian Shopee listings do exist for development-friendly camera modules with identifiable SoCs:

### Example 1
4MP XM IP Camera Module Board
- SoC: Goke GK7205V210
- Sensor: MIS2009
- H.265
- ONVIF
- RTSP
- XMEye / iCSee
- observed price around Rp573k

This is a much better lab candidate than a random sealed V380/Yoosee camera because the SoC is explicit and GK7205V210 is on OpenIPC's recommended list.

### Example 2
XM550AI + SC5335P module
- RTSP
- Xiongmai XM550
- observed around Rp1.0–1.28m

OpenIPC recognizes XM550 but current status must be checked before flashing; Xiongmai support is not uniformly “done”.

### Generic Indonesian finished cameras
Cheap XIHANCAM, V380, Yoosee, iCSee and similar cameras are widely available, but retail model names are not sufficient proof of flashability. Their SoC/board must be identified first.

## China / Alibaba availability

China is the stronger sourcing route.

Current Alibaba searches show modules explicitly sold as OpenIPC / OpenIPC-compatible.

Examples seen:

### GK7205V300 + IMX335
- 5MP camera development board
- OpenIPC
- 16 MB flash
- RTSP
- H.265
- roughly CNY 183–199
- MOQ 2

This is one of the strongest lab choices because GK7205V300 is a recommended OpenIPC SoC and the listing explicitly states 16 MB flash.

### Hi3516EV300 + IMX335
- 5MP IP camera module
- audio
- board-level module
- roughly USD 26–35
- MOQ 1

Hi3516EV300 is a recommended OpenIPC SoC with a generated installation guide available from OpenIPC.

### SigmaStar SSC30KQ + IMX335
- OpenIPC RTSP module
- 5MP
- H.265
- offered in Alibaba OpenIPC searches

### SigmaStar SSC338Q + IMX415
- 8MP OpenIPC module
- low-light
- current Alibaba result around USD 41–45 for MOQ 1 on at least one seller

### Ingenic T40N + IMX415
- 8MP / 4K board
- listings explicitly advertising OpenIPC firmware support
- observed Alibaba Indonesia price range about Rp203k–702k depending configuration/MOQ

## Recommended buying strategy for GARDA lab

### Best first board
Goke GK7205V300 + IMX335 + 16 MB NOR

Why:
- recommended OpenIPC SoC
- 16 MB flash gives more room than 8 MB
- board/module listings explicitly exist
- RTSP/H.265
- clear hardware identity

### Second board
HiSilicon HI3516EV300 + IMX335

Why:
- mature OpenIPC path
- known Xiongmai module variants exist
- installation wizard available

### Higher-resolution experiment
SigmaStar SSC338Q + IMX415 8MP

Why:
- 8MP/4K capability
- modern SigmaStar family
- OpenIPC module listings exist

## Pre-purchase checklist

Ask the seller for:

1. exact SoC marking
2. exact board/module code
3. sensor model
4. NOR/NAND flash size, prefer 16 MB or larger when possible
5. Ethernet PHY / RJ45 presence
6. whether PoE is native IEEE 802.3af/at or requires a splitter
7. ONVIF
8. RTSP
9. H.264/H.265
10. audio input/output if required
11. UART/TFTP recovery access or pinout
12. stock firmware backup availability
13. board photos, front and back
14. whether firmware is already OpenIPC or just “compatible”

## Flashing rule

Never flash based only on the external product name.

Process:

Retail listing -> identify SoC -> identify board -> verify OpenIPC support -> verify flash size -> save stock firmware -> confirm recovery path -> flash.

## GARDA use

These open/flashable modules are intended for development, research, interoperability testing, and prototyping. Formal production procurement requirements remain separate from GARDA lab hardware decisions.

## Sources checked

- OpenIPC Supported Hardware
- OpenIPC camera board catalogue
- OpenIPC installation/get-started documentation
- Shopee Indonesia current listings
- Alibaba / Alibaba China current module listings
