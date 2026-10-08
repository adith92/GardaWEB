# GARDA — Tier Naming Brainstorm v0.1
Date: 2026-10-08
Status: **PROPOSED, NOT APPROVED**. Do not modify programmatic tier IDs, SKU names, contracts or shipped UI until owner approval.
Customer focus: Indonesian government/TNI. Product: PUSADA MONITORING CENTER | GARDA.

## Product strategy
Keep stable internal entitlement/implementation identifiers `T1`, `T2`, `T3`, `T4` independent of display names; changing a brand label must not break APIs, licenses, RBAC or migrations.
Capabilities remain cumulative from lower tiers. The full 592 candidate capabilities and approved vs open decisions remain in `docs/GARDA_MASTER_FEATURE_CATALOG_v0.2.md` and `docs/GARDA_DECISION_REGISTER_v0.2.md`.

## Leading naming proposal (preferred, not yet locked)
| Internal ID | Current working / English baseline | Proposed Indonesian brand | Position and example modules |
|---|---|---|---|
| T1 | BASIC / Core Monitoring | **GARDA SIAGA** | Site CCTV/VMS, recording, live monitoring, playback, incidents, RBAC, audit, basic evidence and infrastructure health |
| T2 | SMART / Video Analytics | **GARDA WASPADA** | Adds computer-vision analytics, intrusion/loitering, advanced alert/rules, object detection |
| T3 | INTELLIGENCE / Recognition & Investigation | **GARDA WASKITA** | Adds authorized face recognition/ANPR, candidate cross-camera re-ID, evidence-linked AI copilot, investigations and semantic search |
| T4 | SOVEREIGN COMMAND / Advanced Command Center | **GARDA KOMANDO** | Adds integrated top Command Center federating T1–T4 nodes, TNI-style configurable hierarchy, classification controls, approval-based cross-unit access, GIS/IoT/radio/dispatch/SIEM/other-software integrations |

### Rationale
- **SIAGA** evokes readiness and duty at a guarded site.
- **WASPADA** evokes active situational awareness and early warning.
- **WASKITA** evokes sharp insight and intelligence (unusual, distinctive Indonesian-language word); pronunciation and audience familiarity should be user-tested.
- **KOMANDO** clearly identifies the top-level command-and-control integration tier.
- The words are brand proposals only and do **not** claim endorsement, an official TNI program or trademark availability.

## Alternative directions for user selection
### Alternative A: accessible/modern
T1 **GARDA SIAGA** → T2 **GARDA CERDAS** → T3 **GARDA INTELIJEN** → T4 **GARDA KOMANDO**.
More immediately understood, but `Intelijen` can create organizational/mission expectations beyond software features.

### Alternative B: national reach
T1 **GARDA SIAGA** → T2 **GARDA WASPADA** → T3 **GARDA TANGGUH** → T4 **GARDA NUSANTARA**.
Patriotic and memorable; less precise about distinguishing recognition/investigation tier T3, while `Nusantara` may imply nationwide deployment even before federation is commissioned.

### Alternative C: operational/direct
T1 **GARDA PANTAU** → T2 **GARDA DETEKSI** → T3 **GARDA ANALITIK** → T4 **GARDA KOMANDO**.
Clear function descriptions, less distinctive as brand names.

## Review gates
1. Owner selects or revises the four names. Until then `T1/T2/T3/T4` are canonical technical IDs, and existing documents can keep their working English labels.
2. Verify trademark/domain/brand conflict and legal IP strategy before external use. No trademark clearance or patent protection is asserted.
3. Validate product naming with the actual customer/KAK. **Warning**: the supplied 2026 PUSADA TNI KAK currently requires face recognition, LPR, Ask Garda, zone audio, rule engine and 16-point video as mandatory contract capabilities. This does **not** align neatly with the proposed T1 Basic feature exclusion list. Resolve by scoping a KAK-specific configured/bundled offering, negotiated procurement requirements or revised tier matrix, rather than secretly pretending T1 is compliant.
4. Once owner locks names, update PRD, feature matrix legends, UI content, SKU/license entitlements, documentation and release notes in one traceable PR.
