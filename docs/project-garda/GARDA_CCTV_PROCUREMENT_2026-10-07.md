# GARDA CCTV Procurement Progress — 2026-10-07

## Current Decision

### ANPR / LPR
Primary prototype candidate:
- **Anpaier 5MP Full HD PoE LPR/ANPR**
- Alibaba: https://www.alibaba.com/product-detail/5MP-Full-HD-POE-LPR-ANPR_1601613043705.html
- Price: **US$58–69**
- IDR reference at **US$1 = Rp17,889**: **Rp1,037,562–Rp1,234,341**
- Status: **BUY 1 TEST**
- Must verify before scaling: ONVIF, RTSP main/substream, IEEE 802.3af/at, focal length/varifocal, manual shutter, WDR/HLC, night plate sample.

Fallback / higher-confidence optics:
- **Dakang 4MP ANPR PoE 5–50mm**
- Alibaba: https://www.alibaba.com/product-detail/Dakang-4MP-ANPR-License-Plate-Camera_1601719557671.html
- Price: **US$122–126**
- IDR reference: **Rp2,182,458–Rp2,254,014**
- Status: **SHORTLIST**
- Key advantage: **5–50mm varifocal optics**, much easier to frame a license plate tightly at a gate.
- Decision rule: use Dakang if Anpaier fails night-plate sharpness, shutter control, or focal-length requirements.

### Price / Performance Conclusion
- **Anpaier is the current price/performance pick for a prototype** if integration and image controls pass testing.
- **Dakang is the safer production candidate** when longer focal length and controlled plate framing matter.
- Megapixel count alone is not the deciding factor. Plate sharpness, shutter, WDR/HLC, lens coverage, RTSP, and ONVIF matter more.

## PTZ / General Camera

### Local budget candidate
- **Nextcam NC858 Dual Lens PTZ**
- Approx. local price: **Rp556,000**
- Status: **BUY 1 TEST**
- Known target setup:
  - RJ45 LAN
  - PTZ
  - Dual lens
  - 12V power
  - Can be powered from PoE switch using **active IEEE 802.3af/at 48V → 12V PoE splitter** that outputs RJ45 data + DC power
- Must verify on real unit:
  - ONVIF discovery
  - RTSP stream
  - PTZ through ONVIF
  - DC barrel size
  - stable LAN operation without cloud dependence

### Other local PTZ shortlist
- **IMOU PS70F Cruiser Dual PoE 6MP/10MP** — native LAN + PoE + dual lens + PTZ + ONVIF
- **XMEYE 6MP Dual Lens PTZ PoE ONVIF** — good feature/price, test firmware stability
- **IMOU Ranger Mini PoE 5MP** — good indoor wired PTZ option
- **PROVIEW SM-PR5260-PT** — HOLD until physical RJ45/native PoE is confirmed
- **XIHANCAM 5MP PTZ Port LAN** — LAB TEST only until ONVIF/RTSP is proven

## Face Recognition Camera Candidates

Current Alibaba shortlist:
1. High Quality 4K AI PoE 5/8MP Bullet
2. HTW Warm Light Dual Light 8MP 4K
3. Quarkview Outdoor 8MP PoE Human Detect
4. HTW 4MP PoE TF Card ONVIF
5. ENSTER H.265 5MP PoE ONVIF Bullet

Important GARDA rule:
- Camera-side "face recognition" is optional.
- GARDA can perform face detection/recognition server-side.
- Priority is sharp local video via PoE/LAN with ONVIF/RTSP, good WDR, good low-light performance, and suitable focal length.

## GARDA Camera Integration Requirements

Minimum preferred:
- Wired LAN / RJ45
- PoE native when possible
- ONVIF
- RTSP main stream + substream
- Local operation without mandatory cloud
- PC/NVR compatibility
- H.265/H.264
- Good WDR / low-light performance

For ANPR:
- Manual/configurable shutter
- WDR/HLC/BLC
- Varifocal or suitable tele lens
- Reliable night plate capture
- Indonesian plates should be tested if using camera-side ANPR

## Shared Procurement Spreadsheet

Google Sheets:
https://docs.google.com/spreadsheets/d/1Xfl4xU2JY4I9O01GhaXXIu7XEX1EHRK4ceStVMH275Y/edit

Workbook contains:
- MASTER shortlist
- ANPR_COMPARE
- PTZ_LOCAL
- Names
- Features
- Prices
- IDR conversions
- Links
- Integration checklists
- GARDA score/status

## Next Test Order Suggested
1. **1× Anpaier 5MP LPR/ANPR**
2. **1× Nextcam NC858**
3. **1–2× face-camera finalists after ONVIF/RTSP/WDR confirmation**

Then test everything against GARDA on the same LAN before any bulk order.
