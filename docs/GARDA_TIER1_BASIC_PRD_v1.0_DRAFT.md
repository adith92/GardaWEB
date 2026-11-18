# GARDA SIAGA / Tier 1 BASIC — Product Requirements Document v1.0 (DRAFT)
**Date:** 2026-10-08 | **Status:** Owner scope decisions confirmed; **NOT customer/KAK signed off, NOT implemented or accepted**.
**Product:** PUSADA MONITORING CENTER | GARDA
**Product labels:** `T1` is canonical; **GARDA SIAGA** is a *proposed* marketing name, NOT yet approved.
**Target buyer:** government, notably TNI. First planned site: PUSADA TNI.

## 0. Executive scope and important distinction
This PRD describes the **repeatable commercial Tier1 Basic base package**, not a claim to deliver the entire PUSADA KAK. Its intended benefits: one-site CCTV monitoring from mixed vendors, on-prem live and evidence, independent NVR backup, limited useful AI, and user isolation/audit. It is engineered to upgrade through T2/T3/T4 without vendor lock-in.
- Tier1 cameras: **1–49 active channels (strictly fewer than 50)** per contracted deployment.
- Sites: **one**.
- Operator seats: **one concurrently active operational operator**, details for maintenance/admin sessions open.
- Local-first, **internet-independent** operations, licensing and AI.
- Current reference: PUSADA TNI with **16 KAK points**, subject to final device/channel counting.
- **GARDA as primary WebApp**; existing dedicated **DVR/NVR independently records as backup**. GARDA records locally as applicable to configured topology. Do not confuse browser WebApp with single physical machine.
- Default **GARDA** retention **7 days** adjusted with disk capacity, independent of NVR retention; must surface warning if target cannot fit.
- Bilingual ID/EN, basic evidence vault, universal-format export strategy, tight RBAC.
- Basic includes face-presence, person presence, simple ANPR plate OCR **but never full facial identity recognition**.

### Outscope for standalone Tier1
Face *identification* / biometric matching/enrollment and watchlists; multi-camera re-ID, advanced vehicle watchlist or journey; semantic video search and Ask GARDA; native Android/iOS; hierarchical HQ federation; multisite; classification-level ABAC; deep integration hub; advanced IoT; digital twin; automatic physical actuation. These are separately tiered or optionally bundled for **KAK-specific contract**.

## 1. Roles, rights and controls
Roles: Operator, Supervisor, Administrator, Auditor, optional read-only Viewer. **Exactly one concurrent Operator seat** entitlement in T1. Site membership determines eligible camera and video resources.
- Operator and above are *eligible* for controlled export; actual action requires explicit permission `evidence.export`. Viewer/Auditor are read-only unless custom permission approved.
- Watchlist and identity/biometric access **do not exist in standard Basic**. In Tier2+ or a contracted KAK addon, Operator+ may be assigned `watchlist.manage`, `biometric.search`, `biometric.enroll` by authorized admin, with logging and recommended two-person approval for sensitive modifications. Never grant by generic role name alone.
- Deny other unit/site assets by default. Tier4 special code alone must not bypass privileges.
- Server-side authorization required for every video stream, frame, playback segment, export, snapshot, incident, file, event, websocket and API response.
- Log successful/denied access and all sensitive changes with actor, time, organization, camera and device/session.

## 2. Functional requirements & acceptance outcomes
All marked **PROPOSED DELIVERY / ACCEPTANCE GATE** until customer signs scope and the first real device tests pass.

| ID | Priority | Requirement | Evidence of acceptance |
|---|---|---|---|
| T1-001 | P0 | License and config prevent >49 cameras and >1 site; **1 concurrent operator seat** | Reject channel 50; reject second site; concurrent operator cannot silently displace first |
| T1-002 | P0 | Add IP camera through ONVIF or RTSP; mixed-brand capability detection; encrypted credential storage | Two agreed real camera makes/models tested for live, recording, reconnect and credentials |
| T1-003 | P0 | NVR/DVR backup recording remains autonomous even if GARDA restarts or WAN drops | Disconnect/stop GARDA; NVR test recording remains continuous and can be played back separately |
| T1-004 | P0 | GARDA live video wall and single stream; suggested 1/4/9/16 layouts, with 25/custom conditional to benchmark | Each authorized feed plays with measured latency and no cross-unit leakage |
| T1-005 | P0 | GARDA local recording where enabled, rolling retention default 7 days adjustable to HDD, protect event evidence from unintended deletion | Recording persisted, disk estimator, low-disk alert, prune behavior and corrupt segment recovery tested |
| T1-006 | P0 | Per-camera timeline, playback, timestamps, bookmark, secure MP4/JPG export | Find footage by date/time; export tested on agreed devices with hash and camera provenance |
| T1-007 | P0 | Simple person presence: bounding region/event without identity/name | Positive/negative test clips; false alarms visible; no identity/profile/tag created |
| T1-008 | P0 | Face presence only: detect a face in video frame; **no identity matching** | No face enrollment, face embeddings for identity lookup or known-person display in Basic |
| T1-009 | P0 | Simple ANPR: plate candidate detection+OCR, camera/time, optional confidence, snapshot/clip reference | Test agreed plate types, lighting, angles; label uncertain OCR, require verification before operational action |
| T1-010 | P0 | Camera loss, service status, storage capacity and basic health + alarm acknowledgment | Inject camera disconnect and storage warning; audit the event lifecycle |
| T1-011 | P0 | Incident create/assign/comment/close and incident-to-evidence references | Incident preserves correct operator, time, linked camera and clip |
| T1-012 | P0 | Auth, RBAC, encryption-in-transit, audit, operator concurrency, secure roles | Test unauthorized clip URL, query parameter and API access; all denied + logged |
| T1-013 | P0 | Full local operation including offline signed license checks; controlled Internet update as option | Disconnect WAN/cloud, reboot server; live/record/playback/AI/licensing continue |
| T1-014 | P0 | UI bilingual Indonesian/English, localized alerts and export report templates | Change language without losing permissions/settings; operator task flow tests |
| T1-015 | P0 | Limited GARDA Vault: evidence folders, upload/download, storage quota and audit; no external public links | Operator can store/retrieve authorized files; cross-user/site files access denied |
| T1-016 | P0 | Backup/restore of app config and metadata; clock sync plan | Restore from a test backup and verify user/incident/video index integrity |
| T1-017 | P1 | Camera PTZ/presets, two-way audio only when verified supported, synced playback, extra layouts, simple site floor plan | Capability-tested per exact firmware; no unsupported buttons or fake simulation |
| T1-018 | P1 | Export as MP4 H.264/AAC when applicable, JPEG, PDF incident report and JSON metadata/SHA256 manifest, optional H.265 source archive | Compatibility matrix for Windows/macOS/Linux/mobile playback; preserve unmodified source evidence |
| T1-019 | P1 | Lightweight reporting, storage/retention calculator, operator shift handover and maintenance log | Report and handover readable and access-controlled |

**P0** means product candidate priority, **not** legally binding until KAK requirements and funding are reconciled; if KAK is unchanged, additional mandatory modules must be included in the **PUSADA CONTRACT BUNDLE** below.

## 3. What Basic AI actually means
### Person detection (T1)
Detects *presence of a person* with an optional bounding box/time and source event; no person name, recognition watchlist, unique identity or inferred dangerous intent. Optional generic vehicle class detection.
### Face Recognitions Basic (T1)
Owner-approved UI name (2026-10-14), traced to T1-008. The name does not change the capability or tier entitlement.
Says *"wajah terdeteksi"* and links to camera/time. **Face detection != Face Recognition**. Store only operational event data necessary for authorized processing. No identity embedding/gallery, no facial profile database for matching.
### ANPR Lite (T1)
Plate detector -> crop -> OCR -> confidence/quality -> event with plate string, timestamp, camera, source evidence. No automatic gate unlocking, no unsupported 'suspect' classification; manually verify uncertain reads. Advanced registration/watchlists, journeys/cross-camera correlation and higher-volume optimizations are T2/T3 features unless separately bought.
### Advanced recognition (T2)
With legal authority and contracted capacity: controlled face enrollment, known/unknown candidates, authorized watchlists, confidence and human review; encryption, purpose and retention policies, false-match evaluation. Never assume a face ID is fact.
### Deep intelligence (T3)
Cross-camera journeys/re-ID, investigator workspaces, more advanced ANPR, Ask GARDA/semantic discovery, native Android/iOS.

## 4. Proposed high-level deployment
```text
CCTV IP cameras + optional legacy DVR/NVR
                |     [segregated wired VLAN, ONVIF/RTSP, tested vendor adapters]
       +--------+--------------------------+
       |                                   |
   Existing dedicated NVR            GARDA on-prem Linux
   independent backup                ONVIF/RTSP media gateway
   (records 24x7)                        |
                                +--------+--------+
                                |                 |
                       Local recorder*      AI Lite worker
                       [video segments]     [person/face/ANPR]
                                |                 |
                                +--------+--------+
                                         |
                                     API + RBAC
                                         |
                             WebApp + Events + Vault
```
*Select per-camera whether GARDA ALSO records, relays/accesses the existing NVR archive or both; exact independent recording and retention behavior must be agreed. All GARDA critical workflows remain local with Internet down.

### Camera compatibility promise
- Target all common standards-conformant, reachable vendor/firmware combinations, prioritized by real customer inventory; use ONVIF profiles/RTSP first; vendor DVR/NVR stream bridge if needed; extensible per-vendor adapters only by tested capability.
- **DO NOT claim "compatible with every brand/model"**. Some cameras are cloud-only, encrypt proprietary protocols, limit stream count, require license, hide PTZ/backchannel, or support ONVIF incompletely.
- Define per-firmware support matrix `DISCOVER / LIVE / RECORD / PLAYBACK / PTZ / AUDIO / METADATA / AI` and test actual hardware before procurement promises.

## 5. Nonfunctional targets and measured engineering constraints
- Uptime **goal**: `99.99%` at agreed scope, a **stretch target**, not SLA guarantee; dedicated NVR backup does not automatically make GARDA WebApp HA. Requires redundant network/power/storage, application failover, monitors, DR/maintenance exclusions and customer budget signoff. Single X399 workstation + one process cannot guarantee 99.99.
- User's hardware procurement shortlist Threadripper 1950X / X399 / 128GB UDIMM DDR4 / up to four GPUs is **planning/reference**. This is not an enterprise ECC Xeon/EPYC redundant PSU storage server promised in KAK; do not substitute it into PUSADA bill of materials without formal review/approval.
- Per-camera throughput, bitrate/FPS, codec and AI worker GPU sizing must be benchmarked at up-to-49 product limits and at actual 16-site KAK point count. Licensing capacity is not physical throughput.
- Offline-first: no SaaS API required for critical functions. Optional authorized online update path with signed packages, audit, rollback; true air gap not yet requested.
- License: cryptographically verifiable signed offline entitlement for tier, camera quota, one site, one operational seat and add-on modules; never base entitlement checks only on frontend visibility.
- Security: CCTV segmentation, no public exposure of camera control/stream, VPN for remote access, least-privilege default, encrypted stored secrets, auditable exports, backup integrity.
- Retention: default 7 days is a **setting**; calculate capacity from actual camera bitrate, available usable storage, redundancy overhead, writing safety margin and reserved evidence. Warn before failed retention. Separate NVR retention policy and evidence legal hold where applicable.
- Export: MP4/JPG/PDF/JSON + hash, optional original stream where suitable; universal cross-device compatibility can be improved but not guaranteed for every codec/device.
- Bilingual UI and documentation, no requirement for native mobile app until Tier3.

## 6. Four-tier build/upgrade policy
| Tier | Candidate localized label (not approved) | Intended per-tier difference |
|---|---|---|
| T1 BASIC | GARDA SIAGA | One site, 1–49 channels, one operator, 7d default local retention, limited AI person+face presence+ANPR Lite |
| T2 SMART | GARDA WASPADA | Advanced object analytics + **governed face recognition**, authorized watchlists, advanced alarms and rules; quota/site thresholds to be agreed |
| T3 INTELLIGENCE | GARDA WASKITA | Native Android/iOS, AI copilot, forensic entity search, cross-camera journeys, advanced ANPR and investigation |
| T4 COMMAND | GARDA KOMANDO | Cross-tier unified Command Center, hierarchy, policy-gated multi-unit access, classification + sovereign integration platform, architecturally unbounded logical federation subject to engineering scale |

**Do not** quietly change SKU names from the latest naming brainstorming until user selects the names. Tier feature bundles and numeric licensing for T2–T4 remain **OPEN**.

## 7. Gaps vs uploaded PUSADA TNI KAK — procurement blocking
The uploaded five-page KAK refers to **16 monitoring points**, face enrollment/watchlist, advanced LPR, rule engine, audio zone command, device diagnostics and root cause, GIS/trends/heatmaps, Ask Garda, RBAC/MFA, backup/DR. It also specifies redundant NVR, **90-day** video+metadata retention, enterprise RAID and server GPU minimums, plus security/acceptance tests. These are **not all included in standalone Basic** and cannot be ignored.

**Proposed solution:** offer a special **PUSADA TNI CONTRACT BUNDLE** containing T1 Basic foundation PLUS explicitly scoped KAK-mandated licensed modules from T2/T3/higher tiers plus KAK-compliant hardware/storage. This does **not** automatically upgrade to full T2/T3/T4 federation entitlements, and no technical/commercial workaround should bypass procurement rules. Alternatively secure written formally approved KAK/contract changes where lawful. Do not certify plain Basic as KAK-compliant.

See `docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md` for mapped contradictions, evidence and clarification needs.

## 8. Scope acceptance checklist for Codex
- [ ] No artificial demo-only objects reported as live production CCTV.
- [ ] One-site and 49-channel limits enforced in **API/license**; second operator blocked per agreed seat behavior.
- [ ] Existing NVR continues autonomous backup while GARDA is down.
- [ ] Can ingest >=2 customer-approved brands/camera models after tests, documenting firmware and unsupported capabilities.
- [ ] Face detected but **never named** in Basic; ANPR OCR events trace to original footage.
- [ ] GARDA recording and NVR recording independently tested and storage requirement reviewed.
- [ ] Default 7-day setting and storage-fit alarm implemented (KAK 90d handled separately).
- [ ] Offline cold boot, signed license, person/face/ANPR AI and playback continue.
- [ ] RBAC plus export logs and vault segmentation negative tested.
- [ ] Indonesian/English operator UI tested.
- [ ] Uptime measured against specified test interval; 99.99% is not asserted without enterprise design and accepted SLA.
- [ ] KAK module add-ons and hardware gap resolved **before** procurement acceptance.

## 9. Open questions and dependencies
1. **True air-gap?** Not decided: owner only confirmed fully offline + Internet for optional updates.
2. On-prem GARDA recording duration vs independent NVR backup retention, exact NVR brands and recording API/access capabilities.
3. Camera count per type/channel for 16 PUSADA KAK points; intended resolution/FPS/bitrate/codec/storage capacity.
4. KAK-mandated face matching, 90d storage, Ask Garda, zone audio, alarm/analytics, infrastructure to be contracted as add-on or formal KAK modification?
5. 99.99% uptime definition (GARDA web/UI, NVR, whole site), measurement window, HA design and planned cost.
6. Precise Operator/Admin concurrent access and sensitive watchlist approver selection.
7. Acceptance dataset and precision/recall/false-match thresholds for ANPR, object detection and face detection.
8. Signed license lifecycle/offline upgrade package handling and SLA for security updates.
9. KAK timeline/warranty ambiguities, legal source handover wording and intellectual property assessment.
10. User has **not approved** proposed marketing tier names.

## 10. Reference documents
- Decision register: `docs/GARDA_DECISION_REGISTER_v0.3.md`
- Catalog: `docs/GARDA_MASTER_FEATURE_CATALOG_v0.3.md`
- KAK Gap Matrix: `docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md`
- Previous architecture/spec (historical): `docs/GARDA_TIER_IMPLEMENTATION_SPEC_v0.2.md`
- Owner choices 21–25 (historical): `docs/GARDA_DECISION_REGISTER_v0.2.md`
- Existing demo PRD: `PRD_PMC_GARDA.md` (DEMO, not contract)
