## Keputusan final owner 16 Oktober 2026

- **DECIDED:** Implementasi 8 minggu (minggu 1–8), testing/UAT/commissioning 2 minggu (minggu 9–10). Support/warranty **12 bulan sejak BAST/serah terima operasional**. Seluruh pernyataan jadwal/support terdahulu yang bertentangan digantikan keputusan ini; tidak perlu ditanyakan ulang.
- **DECIDED DEMO:** PMC V2 diarahkan menjadi demo final khusus kebutuhan KAK PUSADA, memakai data sintetis. Ini tidak mengubah entitlement paket Basic produksi atau berarti uji penerimaan sistem nyata sudah lulus.
- **IMPLEMENTED DEMO:** Animasi jaringan abstrak diganti kamera CCTV bergerak; pilihan logo GARDA berputar, jeda dan reduced motion tersedia.
- Rincian pembahasan tahap final: `docs/PMC_V2_FINAL_DEMO_2026-10-16.md`.

# GARDA — Decision Register Addendum v0.3
Date: **2026-10-08** | Authoritative owner answers: questions 1–20, after decisions 21–25.
**Status:** Product owner intent = **DECIDED**; technical/commercial acceptance, legal feasibility and KAK compliance = **PENDING**.

## Precedence
This addendum **supersedes the 'Still open from questions 1–20' section** in `docs/GARDA_DECISION_REGISTER_v0.2.md` and any conflicting tier assumptions in `docs/GARDA_MASTER_FEATURE_CATALOG_v0.2.md`, `docs/GARDA_TIER_IMPLEMENTATION_SPEC_v0.2.md`, and the original **DEMO** `PRD_PMC_GARDA.md`. Do not delete historical files; follow the latest owner record + `GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md` and `GARDA_MASTER_FEATURE_CATALOG_v0.3.md`.

## Owner-confirmed answers
| Q | Status | Owner answer (normalized with explicit caveat) | Practical implication |
|---|---|---|---|
| 1 | DECIDED | Tier1 Basic supports **fewer than 50 cameras**. | Use **1–49 active licensed camera channels** as the product target, not an inferred measured hardware capacity. KAK PUSADA specifically mentions 16 points. |
| 2 | DECIDED | Tier1 is **one location/site**, initial reference deployment PUSADA TNI. | No Basic multi-site coordination; model organization/site IDs for future federation. |
| 3 | DECIDED | Existing **NVR remains recording independently as backup**; GARDA is the principal **WebApp** for users. | NVR retained; GARDA manages live/playback/evidence and may maintain its own recordings if hardware/storage permits. Need select GARDA recorder mode vs NVR archive for each site. |
| 4 | DECIDED GOAL | Mixed camera brands; owner wants **maximum possible brand compatibility**. | **Not universal compatibility guarantee**. Standards-first ONVIF/RTSP, DVR/NVR bridge, vendor adapters and verified model/firmware capability matrix; unsupported/cloud-only products marked clearly. |
| 5 | DECIDED DEFAULT | Basic GARDA recording retention **7 days by default**, adjustable by HDD capacity. | Do not promise 7-day minimum where undersized; capacity estimate and alarms. **PUSADA KAK separately requests 90 days** for video and metadata. |
| 6 | DECIDED | Basic includes **simple person detection** and optionally generic vehicle detection, with no name tagging. | Return person/vehicle presence/class + camera/time/clip; not identity, re-ID or suspect determination. |
| 7 | DECIDED | Basic includes **simple ANPR**. | Plate-detection/OCR candidate, plate text, camera/time and evidence, confidence where available. Advanced watchlist, journey, vehicle DB and correlation reserved for later tiers unless KAK bundle separately buys them. |
| 8 | DECIDED | Basic only reports **a face exists**; **Face Recognition/identity starts Tier2**, with progressively better depth in subsequent tiers. | No names, identity enrollment, watchlists, embedding identity matching in off-the-shelf Basic. Governed Tier2 match review; Tier3 advanced cross-camera identity/semantic investigations. |
| 9 | DECIDED | **100% local/offline operations**; internet may be enabled for authorized data/software updates. | Local inference and licensing without internet, optional approved update pathway. No external API dependency for mission-critical flows. |
| 10 | OPEN / EXPLAINED | Owner asked meaning of **air-gapped**. | No user decision yet. Air-gapped = intentionally segregated system **without connectivity to outside networks**, with vetted offline file/update media. Offline-first with optional online updates is **not** air-gapped. |
| 11 | DECIDED | Tier1 **one concurrent operator**. | One concurrently active operator seat; privileged maintenance/admin access and emergency continuity semantics require detail. |
| 12 | DECIDED GOAL | Tier4 top Command Center should federate **unlimited** subordinate sites. | Treat unlimited as **no arbitrary software cap in product architecture**, not infinite concurrent stream hardware capacity. Need scale-out, quotas, bounded throughput and validated capacity. |
| 13 | DECIDED | Android/iOS starts **Tier3**, not Basic. | Basic local browser WebApp only; responsive browser access is distinct from a native mobile application. |
| 14 | DECIDED | Include **light GARDA Vault in Basic**. | Limited internal evidence folders/upload/download/permissions/quota, no enterprise sharing/versioning/advanced legal holds as default. |
| 15 | DECIDED GOAL | Exports compatible with many devices; owner accepts **MP4/JPG/PDF/JSON + checksum**. | MP4 video (standard codec/device-tested), JPEG image, PDF case report, JSON manifest, SHA-256 plus optional alternate supported formats. |
| 16 | TARGET / NOT GUARANTEED | Desired **99.99% uptime** if possible. | Availability design goal requiring HA, power, storage/network redundancy and rigorous measured SLA. **Not a Tier1 single-server guarantee.** |
| 17 | DECIDED | Tiering governed by **features AND camera/site counts**. | Backend-enforced feature entitlements plus per-site channel quotas; scope/licensing obeys offline operation. |
| 18 | DECIDED | License must operate **without internet**. | Signed offline entitlements, local verification, carefully designed renewal/grace procedures, no online kill switch while operating. |
| 19 | DECIDED | **Operator and above** should be eligible for video exports, watchlists and authorized biometric access. | Tier/licensing/policy must enable actual capability; least privilege and explicitly delegated named permission within eligible roles. A role label alone is insufficient. Sensitive watchlist mutations require audit and recommended review, classified restrictions always prevail. |
| 20 | DECIDED | **Bilingual Indonesian and English**. | All operator UI, alerts, timestamps, report templates, documentation/localization test suites. |

## Previously owner-confirmed TNI answers (21–25, retained)
- 21: Tier4 unified top HQ Command Center controls/co-ordinates subordinate GARDA nodes of all tiers with **configurable hierarchical organization** (e.g., Mabes > Kotama > Satker > Site).
- 22: Cross-unit view **denied by default**, privileged access via **authorized scoped short-lived special-code/grant**, not password backdoor.
- 23: Tier4 data classification displayed/enforced: `Biasa`, `Terbatas`, `Rahasia` examples (official policy taxonomy OPEN).
- 24: Future GIS, alarms, radio/dispatch, IoT, access control, SIEM and cross-software integration via governed SDK/adapters.
- 25: Core GARDA backend/AI source proprietary; client may receive only separately approved **viewer/basic-source** code/license. Any public procurement IP/contractual obligation requires legal review.

## Tier-specific adjustments to prior baseline
1. Basic includes limited AI: person detection, face **presence detection** with no identity, and basic plate OCR.
2. **Recognition of who a person is** moves from old Tier3 baseline to **Tier2**, conditional on lawful authority, governed enrollment, accuracy tests and manual review.
3. Tier3 remains advanced multi-camera forensic intelligence and native mobile.
4. Tier4 remains nationwide/large-scale federation by architecture (no implied infinite throughput).
5. Existing feature IDs stay stable; proposed earliest tier changes and subfeature splits are recorded in catalog v0.3, not silently overwritten.

## KAK conflict warning — no silent waiver
The uploaded KAK for PUSADA calls for **16 monitoring points, 90-day video/metadata retention, face enrollment/watchlists, LPR, Ask Garda, zone audio, rules and integrations, redundant NVR/storage, ECC enterprise GPU server, and tests**. The owner’s **generic Tier1 Basic commercial package** does NOT cover all KAK-mandated modules or infrastructure. Do **not** call plain Tier1 KAK-compliant. Prepare a distinct **PUSADA Contract Bundle: T1 Core + separately priced/contracted T2/T3/T4 selected modules and KAK infrastructure** (or agree written changes to KAK) and validate procurement/legal compliance. See `GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md`.
Duration/support resolved by owner on 2026-10-16: 8 weeks implementation + 2 weeks testing/UAT/commissioning; 12 months support from BAST.

## Items remaining OPEN (do not invent)
- Q10: need for **true air gap** vs offline with controlled update access.
- Camera exact firmware/stream/API support and multi-vendor compatibility acceptance list.
- What GARDA records itself vs which recordings it merely accesses from still-recording NVR, and which footage is forensic primary.
- GARDA effective retention when HDD undersized; required recording resolution/fps/bitrate and actual disk/RAID sizing.
- Formal definition of one operator + admin and emergency sessions.
- Specific MVP ANPR camera angle/lighting and recognition accuracy thresholds.
- Time and responsibility for optional updates, vendor signature verification/rollback and telemetry policy.
- Mobile tier source distribution, user permission policy details, offline license expiry/grace.
- Concrete SLA/SLO scope, planned redundancies and 99.99% affordability.
- Exact KAK-reconciled first contract scope, paid add-ons, whether face recognition and Ask Garda must be active from day one, legal and privacy authorizations.
- Four marketing tier names remain **PROPOSED**: SIAGA/WASPADA/WASKITA/KOMANDO, not owner-approved.

## Production questionnaire answers (owner, 2026-10-08)

The following answers are now the owner intent for the PUSADA planning baseline. They do not by themselves amend the signed KAK or prove technical acceptance.

| Q | Owner answer recorded | Decision effect / remaining control |
|---|---|---|
| Q01 | KAK functions remain expected, while practical GARDA hot retention remains **7 days**. | Keep the PUSADA Contract Bundle for KAK functions. Treat 90-day availability as a separate NVR/archive acceptance obligation; do not label a 7-day hot window as 90-day compliance. |
| Q02 | **16 principal channels/points**: 13 dual-camera points, 2 face-recognition cameras and 1 LPR/ANPR camera. | Use this inventory for the next design pass. Confirm whether “13 dual-camera” means 26 physical cameras and record each stream/channel ID before sizing. |
| Q03 | KAK schedule uses **weeks**, with weeks **1–10** as the planning baseline. | Superseded on 2026-10-16: 8 weeks implementation + 2 weeks testing/UAT/commissioning; 12 months support from BAST. |
| Q04 | **50 kVA final owner target** for the generator. | Use 50 kVA as the owner BOM target, subject to load/power survey and written resolution of the KAK 500 kVA conflict. |
| Q05 | **Combination storage**: NVR has 1 TB; GARDA CPU/storage has 16 TB; NVR is only a backup of GARDA. | GARDA is the primary recorder. Prove 7-day hot retention and backup restore. A 1 TB NVR cannot be assumed to provide 90 days; 90-day KAK availability remains an explicit capacity, archive and acceptance item. |
| Q06 | 13 dual-camera channels use ordinary camera specification; face and ANPR/LPR cameras use a somewhat higher specification. | Keep exact resolution, FPS, codec, bitrate, lighting and lens requirements open until camera quotation/survey and benchmark. |
| Q07 | Follow the questionnaire recommendation for full-storage/disk-failure behavior. | Use alarmed policy-controlled overwrite, preserve protected evidence, and audit the action. |
| Q08 | Use the camera list already recorded in GitHub as the first compatibility baseline. | Trace the exact repository list into a test matrix; firmware, ONVIF/RTSP behavior and reconnect evidence remain required. |
| Q09 | AI should remain **simple/basic** for this baseline. | Basic scope is person/face presence and simple ANPR/LPR as supported by the approved list. Face identity, advanced LPR and Ask GARDA remain separate contract/tier decisions despite the KAK wording. GPU stays TBA. |
| Q10 | The ordinary **User** role is view-only and cannot replay video. | Define higher roles and server-side permissions for live, playback, export, watchlist and biometric actions; do not infer privileges from the label “User”. |
| Q11 | Follow the questionnaire recommendation. | Define a server-side concurrent operator lease, heartbeat, takeover and separate maintenance path in the PRD. |
| Q12 | Online access is **optional**; operations should work offline. | Use offline-first operation with a controlled, signed update path. Do not call the design air-gapped until network/media policy is approved. |
| Q13 | Follow the questionnaire recommendation. | Acceptance must contain measurable live, reconnect, recording, AI, restore, RTO and RPO thresholds with evidence and sign-off. |
| Q14 | Final decisions belong to the **Pejabat Pembuat Komitmen (PPK)**. The implementer is not the decision maker; contract terms will be adjusted accordingly. | Assign scope, privacy, hardware, acceptance and variation approvals to PPK/customer authority in the RACI. Treat implementer recommendations as proposals until contract authority accepts them. |

These answers supersede the questionnaire's temporary OPEN labels for owner intent. The technical controls, capacity calculations, compatibility tests, acceptance evidence and formal PPK/KAK changes remain pending.

## Architecture decision notes
- Security: Basic role/permission and tenant/site checks apply server-side to streams, playback, exports, events, evidence, and vault, not just frontend UI.
- Offline: no vendor cloud required for monitoring/recording/AI/license. Optional internet update separated from camera segment via screened management channel.
- Recording: NVR continuous independent recording is distinct from GARDA recording. If parallel, independently size storage and retention on both; never assume GARDA's 7-day default satisfies the KAK's 90-day requirement.
- Data rights: encrypted biometric records only when matching is a contracted/licensed lawful capability; Basic face detection shouldn't persist face embeddings or identity labels.

## Owner naming update — 2026-10-14

- **DECIDED:** The face module's UI name is **Face Recognitions**; the Tier 1 label is **Face Recognitions Basic**. Do not display “Face Detection” as the customer-facing module name.
- This is a naming decision: T1-008 still covers face presence, camera and time only. Identity matching, enrollment and watchlists remain Tier 2 capabilities.
- **DEMO:** The existing synthetic identity preview remains explicitly fictional and does not demonstrate a real biometric integration.

## Links
- `docs/GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md`
- `docs/GARDA_MASTER_FEATURE_CATALOG_v0.3.md`
- `docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md`
- `AGENTS.md`

