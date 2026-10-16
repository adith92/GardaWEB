# GARDA — PUSADA TNI KAK vs Commercial Tier 1 Basic Gap Matrix
Date: 2026-10-08 | **Preliminary analysis based on user-supplied 5-page KAK**.
**NOT contractual interpretation, customer approval, final HPS, site survey or tested compliance.**
Source title: "Kerangka Acuan Kerja — Sistem Pemantauan Keamanan Berbasis Artificial Intelligence PUSADA TNI".
The source is referenced by page/section here, not copied verbatim and not automatically changed by user brainstorming.

## Why this is important
The KAK describes a **more capable first procurement** than GARDA commercial T1 Basic. Do not assume the words "first contract = Tier Basic" make a simpler software package satisfy all written mandatory requirements. This document separates actual **KAK obligations** from standalone **GARDA Tier1 defaults** and flags a possible **contract-specific bundle of add-on modules**. Pricing and approval required.

### Status vocabulary
- `BASE`: product T1 intent covers category, pending full tests.
- `GAP`: product T1 missing or materially less than KAK.
- `VERIFY`: implementation/specification ambiguity, exact test and acceptance unknown.
- `CONFLICT`: direct difference in requirement/owner preference or inconsistent KAK sections.

## Requirements traceability
| KAK source | KAK requirement (paraphrased) | GARDA T1 Basic owner intent | Gap / compliance implication | Suggested closure |
|---|---|---|---|---|
| p1 preface / p2 §3 live | **16 titik** monitoring; multi-layout/live/playback/bookmark/watermark export/time/location search | T1 one site, 1–49 channels, WebApp layouts+timeline+export | **BASE / VERIFY**: 16 point != automatically exactly 16 active feeds, capability/performance must be tested | Survey 16 points, validate streams per camera; define channel inventory and concurrent viewers |
| p1–2 §2 hardware | Redundant NVR/VMS, GPU AI, 16 cameras, RAID, enterprise network/audio/power | Preserve independently recording NVR; cost-optimized on-prem Threadripper prototype | **GAP / VERIFY**: enterprise redundancy/hardware requirements exceed workstation proposal | Distinct KAK-compliant procurement BOM and onsite tests; budget sources separate |
| p2 §3 face recognition | Enrollment/watchlists, thresholds/confidence, covered-face detection, searchable matches, encrypted templates, access logs and measured false-match | T1 only **face presence** with no name/identity | **GAP**: actual biometric recognition is mandatory in KAK but T1 does not include it | Contract-specific T2 recognition module with governed permissions or formal approved KAK revision |
| p2 §3 LPR | Plate OCR, confidence, image/time/location, searchable plate periods, authorized whitelist/blacklist | T1 simple ANPR OCR/plate/time/camera/snapshot; no advanced lists | **GAP** for whitelist/blacklist, multi-period search/advanced checks | LPR advanced module as explicit add-on and test dataset |
| p2 §3 rule/event | Intrusion, loitering, tamper, device loss, danger; notification dashboard/mobile/email/approved | T1 basic camera/offline/stream health, limited person detection | **GAP**: loitering/rules/zone intrusion/mobile alert not standard | Add T2 rules/analytics/notifications required by KAK |
| p2 §3 audio zonasi | Authorized zone-based speaker messaging, priority and audit | T1 optional camera audio if model supports; no zoned PA control | **GAP** | Contract audio/PA integration and safe approvals + per-zone testing |
| p2 §3 device health | Device status, service/damage/temp/storage/bandwidth/uptime, ticket faults and root-cause diagnostics | T1 basic camera/server/HDD status | **GAP** for tickets/RCA depth | Add device diagnostics & service desk module for KAK |
| p2 §3 trend and map | Daily/week/month/3month trends, heatmaps, event site map, drill-down to footage | T1 incident dashboards/simple floor plan | **GAP** for rich trend analytics, heatmaps and drill-down | Contract Tier2 analytics and map extension |
| p2–3 §3 Ask Garda | Natural-language search over person activity, location and 7/30/90-day history; evidence/confidence/audit request | T1 no LLM/VLM copilot or face identification | **GAP**; requires data/index architecture and meaningful retention | Contract Tier3 Ask GARDA and evidence-linked query module; match KAK retention/data authorization |
| p3 §3 AI control | AI suggests/retrieves only; actions on persons require operator authorization/RBAC/audit | T1 no autonomous physical action; RBAC audited | **BASE** in principles, must test actual rule/AI actions of add-ons | Require human confirmation and proof of action audit |
| p3 §3 administration | RBAC/MFA/watchlist/retention/encryption/backup/recovery/logs/export and role separation | T1 RBAC/MFA-ready, no watchlist; local backup/restore | **GAP / VERIFY**: MFA-ready is not MFA enforced, watchlist feature missing, DR scope not settled | Mandatory MFA + watchlist admin via separately contracted module; acceptance tests |
| p3–4 §4 camera | 16 PTZ 4MP, PoE, ONVIF, IR/WDR etc | Mixed-brand support goal, compatibility not guaranteed | **VERIFY** | Procurement matrix tested for PTZ/PoE/codec/stream firmware/IR |
| p3 §4 NVR | NVR redundancy minimum 16 channels/unit, external storage, failover, event API | Existing NVR remains recording backup | **VERIFY/GAP**: retaining any NVR does not prove dual redundancy/event API/failover | Verify exact topology or procure compliant NVR cluster |
| p3 §4 storage | **90-day minimum** video+metadata retention; ≥14-bay chassis, ≥16TB HDD spec, RAID6 + hot spare | GARDA default 7 days, adjustable HDD; backup NVR independent | **CONFLICT / GAP**: 7 days cannot be represented as 90-day compliance | KAK-specific retention override (≥90 days) with bitrate sizing and RAID bill of materials; clarify minimum drive spec |
| p3–4 §4 AI server | Rack 2U/4U Xeon/EPYC, **128GB ECC**, enterprise NVIDIA CUDA GPU, OS NVMe RAID1, redundant PSU, 10GbE and 3y on-site warranty | Planned Threadripper 1950X/X399/128GB UDIMM/4GPU experimental server | **CONFLICT / GAP**: current hardware preference does not satisfy listed enterprise CPU/redundant requirements | Separate KAK-grade enterprise server; do not silently swap to Threadripper without written approval |
| p4 §4 network/power | Managed PoE, VLAN/SNMP/10Gb links where needed; online UPS and **silent 500kVA** genset ATS/AMF | General PoE/VLAN/UPS plan | **GAP / VERIFY** including unusually large genset specification | Confirm power survey, actual kVA/load spec with customer, procure quoted compliant material |
| p1 §2 implementation | Site survey, risk/network/storage design; ONVIF/API/SNMP, hardening, security test/training/UAT | Planned testable on-prem engineering | **VERIFY** | Produce designs, integration tests and handover evidence per contract |
| p4 §5 supplier | Running base demo, proven delivery, personnel, licenses, data security and documentation; "**source code or usage rights as required**" | Core proprietary; client source only viewer/basic allowed | **VERIFY** not automatic source transfer. KAK permits source code **or usage rights as required**; contract controls | Written license and source-deliverable schedule, legal/procurement review before award |
| p4 §6 acceptance | Test all cameras, NVR failover, storage/backup, face/LPR accuracy, zones, trends, Ask Garda periods, hardening and UAT | T1 acceptance narrowly scoped, some tests not yet developed | **GAP** | Map each KAK test to bundle module, funded engineering, test script and signoff |
| p4 §7 data protection | Wajah/plat require special controls, lawful access, retention, backup/deletion and responsibilities | T1 limited detection/OCR plus RBAC; recognized identity only T2 | **VERIFY** | Document processing basis, access policy, storage and deletion schedule even for basic plate images |
| §2 / §8 jadwal final 2026-10-16 | Implementasi **8 minggu** + testing/UAT/commissioning **2 minggu**; support **12 bulan sejak BAST** | Keputusan final owner 16 Oktober 2026 | **RESOLVED** | Gunakan minggu 1–8, minggu 9–10, support 12 bulan; jangan tanyakan ulang |
| p5 §8 change limits | New modules/locations/capacity require contractual variation and appropriations | Tier upgrade across contracts | **BASE** in business intent | Each add-on explicitly itemized, independently approved in contract/HPS |
| p5 §8 HPS pricing | Camera hardware and software AI cost separately; 10 software packages; licensing/support as separately justified | Four tier licensing + optional add-ons | **VERIFY** | Map HPS line items and pricing so no double charge or undocumented tier inclusion |

## Contract packaging recommendation (NOT approved)
**PUSADA 16-POINT SPECIAL BUNDLE**:
- Core T1 Basic: one site, up to 49 channels as capacity entitlements (actual site 16 points + exact channels), WebApp, VMS/NVR interoperability, simple AI, incident/security/audit.
- Explicit KAK extensions: Face ID/enrollment + guarded watchlist (normally T2); advanced plate searches and whitelist (T2/3); intrusion/loitering/rules, zoned PA, dashboards, device RCA; Ask GARDA and forensic evidence search (normally T3); 90-day video/metadata storage and enterprise redundancy; compulsory mobile notification delivery if required.
- **Bundle modules can be individually entitled** without granting full T3/T4 hierarchical/nationwide access. This is a contractual packaging strategy only.
- Do not call this plain "Basic" if it misleads about licensed features. Call it `GARDA PUSADA KAK COMPLIANT CONFIGURATION (PENDING TEST)` only after all KAK tests pass; before that use `Proposed PUSADA Procurement Bundle`.

## Questions to resolve with KAK owner and procurement
1. Is full original KAK an active obligatory baseline, or a draft still negotiable?
2. RESOLVED 2026-10-16: implementasi 8 minggu + testing/UAT/commissioning 2 minggu, support 12 bulan sejak BAST.
3. Are 16 points equivalent to 16 cameras/16 channels, and what exact PTZ camera models/firmware?
4. Verify enterprise GPU server versus current Threadripper wishlist, actual warranty and license rights.
5. Verify storage minimum phrase and 90-day policy: both NVR and GARDA? Which metadata/index?
6. Confirm lawful recognition purposes, watchlist ownership, false match thresholds and operator authority.
7. Clarify mobile notification wording versus native mobile app (native app is Tier3; push to approved external clients may be contracted).
8. Determine what source code vs executable/license documentation must legally be delivered.
9. Confirm audio zonation/hazard command safety procedures and exact 500kVA genset requirement.
10. Approve add-on license, 10 HPS software package mapping, module pricing and change-control pathway.

## Codex gate
**DO NOT** mark `T1 Basic` as `KAK_COMPLIANT`. Keep a matrix of source requirements, assigned module, owner status, implemented status and measured UAT evidence. Highlight mismatches in any RFP/contract proposal. No attempts to disguise missing AI functionality as "basic" compliance.

