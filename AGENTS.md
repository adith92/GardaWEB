# AGENTS.md — Instructions for Codex in GARDA/GardaWEB
Applies to **every** file and AI coding session in this repository. Product: PUSADA MONITORING CENTER | GARDA. Language for product-owner summaries: **Bahasa Indonesia**.

## Read-first documents and precedence (updated 2026-10-08)
1. `docs/GARDA_DECISION_REGISTER_v0.3.md` — authoritative owner decisions 1–25, current Basic parameters and OPENs.
2. `docs/GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md` — current T1 scope, acceptance and explicit omissions; only owner intent is accepted, **KAK approval is pending**.
3. `docs/GARDA_MASTER_FEATURE_CATALOG_v0.3.md` — 592 candidate features and latest tier assignments.
4. `docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md` — mandatory first-contract KAK requirements NOT satisfied by standalone Basic.
5. **CURRENT NAMING CHANGE:** `docs/GARDA_TIER_NAMING_REVIEW_2026-10-09.md`. Owner **REJECTED WASKITA** for Tier 3; **GARDA NALAR** is preferred but NOT APPROVED. Never publish/implement WASKITA as an active product name. Internal code tier ID remains `T3`; existing v0.1 tier naming proposal and PDF are historical.
6. `docs/GARDA_DECISION_REGISTER_v0.2.md`, `docs/GARDA_TIER_IMPLEMENTATION_SPEC_v0.2.md`, `docs/GARDA_MASTER_FEATURE_CATALOG_v0.2.md`, `docs/GARDA_CODEX_HANDOFF_v0.2.md` — **historical** initial research and planning, superseded where different.
7. `docs/project-garda/` — equipment and procurement history; candidate hardware is **not** the KAK enterprise server.
8. `PRD_PMC_GARDA.md`, `CODEX_MASTER_PROMPT_PMC_GARDA.md`, `MOCKUP_DEMO_SPEC.md`, `RUN_DEMO.md` — existing **synthetic demo**, not a production/KAK build order.

## Visual PRD entrypoint (2026-10-08)
- **START MOBILE/TABLET WORK HERE:** `docs/mobile/PRD_GARDA_MOBILE_VISUAL_v1.0_DRAFT.md` and its six original SVG images in `docs/mobile/assets/`. Quick picture gallery: `docs/mobile/README.md`.
- Illustrations show **intended UX only** and do not mean built, security-tested, legally approved, or included in PUSADA procurement.
- Never reinterpret illustrated Tier2 VIEW as an approved tier change: mobile native was previously planned starting Tier3; it remains a proposal pending product-owner approval.
- Acceptance checklist `MOB-001`–`MOB-012` must be tied to individual implementation issues after scope authorization; do not deploy live biometric/physical control data or source to user devices.

## Mobile application proposal under review (2026-10-08)
- Read `docs/GARDA_MOBILE_TABLET_BUNDLING_PROPOSAL_v0.1.md` before designing any viewer/mobile/tablet interface.
- **PROPOSED, NOT YET OWNER-APPROVED:** T2 viewer-only Android/iOS GARDA VIEW; T3 dedicated bundled GARDA FIELD tablet/app; T4 managed GARDA COMMAND tablet. Previous owner decision said native Android/iOS begins T3, so do **not** silently treat the proposed T2 exception as approved.
- App can potentially be copied, so GARDA backend must authorize **enrolled device certificate/attestation + named user + site + RBAC + license** for every stream. Kiosk/MDM is defense in depth, not DRM proof.
- GARDA remains on-prem/offline-first; cloud-dependent MDM/Google Play attestation may fail on true air-gapped networks. Do not make product critical functions depend on cloud or enable any future mobile feature before owner and KAK scope approval.

## Non-negotiable build guardrails
- All four tiers are documented; **implement only the explicitly authorized active contract scope**. Tier 1 Basic is the **generic** offering; the PUSADA KAK requires extra paid/authorized functions and 90-day retention: **do NOT certify plain Basic as compliant**. Codex must not invent contractual waivers or silently implement whole Tier2/3/4.
- Distinguish: `DECIDED`, `PROPOSED`, `OPEN`, `DEMO`, `IMPLEMENTED`, `TESTED`, `ACCEPTED`. Never mark a mock as functional camera/AI integration.
- Preserve legacy frontend demo behavior where useful, but clearly label all simulated events, faces, plates, AI answers and streams. Do not enable full face identification or Ask GARDA in customer Basic merely because the demo has those routes.
- Basic product entitlements: **ONE site, strictly fewer than 50 cameras (1–49), ONE concurrent operational operator**. Backend/API checks required. Basic AI: simple person presence, face presence only (NO identity), basic ANPR plate OCR. Lite evidence Vault. Native Android/iOS starts Tier 3. Tier 2 includes governed **face recognition** (old docs erroneously put all identity at Tier 3).
- GARDA is principal WebApp, while the existing DVR/NVR records **autonomously as backup**. GARDA 7-day recording retention default must be capacity-configurable; **PUSADA KAK calls for 90-day minimum** (distinct contractual requirement).
- Add real functionality via independently testable modules: ingest/restream, recorder or validated NVR recording access, playback, API, UI, limited AI, incidents, evidence, health, auth, audit, policies. Separate recording from AI.
- Enforce authorization **server-side**, for every route, media URL, websocket, event message, query, export, API and integration. Default-deny cross-unit access. A code alone MUST NOT bypass RBAC, classification or approval policy.
- Do not put secrets, real addresses of government networks, actual credentials, biometric samples, classified content or customer footage in Git.
- Keep GARDA proprietary backend/AI source private. Do not publish repository, invite customers into private core, or include server code in customer viewer packages. Third-party OSS licenses still apply.
- Any cross-tier HQ control/federation or classification machinery belongs to roadmap Tier 4 unless an explicit new decision changes scope.
- No automated physical access, alarm, dispatch, drone or other consequential actuation based purely on AI or LLM output.
- Only approved lawful biometric uses, with consent/authority and monitoring safeguards where required.
- Owner's **99.99% uptime is an aspiration**, not a one-server SLA. 'All brands compatible' and 'unlimited Tier4' are architectural goals, NOT warranties or literally infinite concurrent hardware capacity. Test actual brands/firmware. No direct Internet dependency for Basic operation/licenses; controlled updates optional. True air-gap policy remains OPEN.
- Treat product claims and SLAs as hypotheses until measured and agreed in KAK; do not fabricate camera performance or availability.

## Workflow for every change
1. Read the documents above.
2. Identify requested tier, specific feature IDs, existing code, external dependencies and `DECIDED/PROPOSED` status.
3. Produce small implementation plan + boundary to avoid accidentally enabling premium features.
4. Write tests for tenant separation, RBAC, negative permissions, storage/export integrity and network-loss resilience as applicable.
5. Make code change, run actual tests, state what passed/failed, and avoid false claims.
6. Update feature status + ADR/decision log and PRD traceability for changed scope; ensure README points to current plan.
7. Submit changes via reviewable PR unless owner explicitly authorizes a different workflow.
8. Before any client package, run allowlist export and verify **no core source, models, secrets, service URLs or sensitive demo data** are included.

## Architecture
- Prefer ONVIF / RTSP interoperability, Linux on-prem and modular adapters. Prefer actual capabilities of each camera over broad vendor assumptions.
- Treat Threadripper + 128GB UDIMM + up-to-four GPU expansion as **planned hardware**, not installed capacity. Derive limits from load testing.
- Optional Windows VM for RDP workloads must have resource isolation and no impact to continuous recording.
- Highest-tier federation obeys local policies even if hub is disconnected.
- Schema evolution, audit, data classification and integration envelopes must be designed for future tiers without shipping unapproved functionality.
