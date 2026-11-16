**NEW DRAFT FOR CODEX — encrypted GARDA metadata backup:** [Offline backup / restore procedure](docs/GARDA_OFFLINE_BACKUP_RESTORE_2026-11-16.md). Snapshot-only (bounded 128 MiB) encrypted archive with SQLite-consistent DB copies, verification and restore into a new directory; DOES NOT back up NVR footage or certify disaster recovery.

**GARDA SECURITY INVESTOR VISUALS (2026-11-16):** [19 premium presentation renders](docs/investor/visuals/renders/) · [interactive investor gallery](docs/investor/visuals/index.html) · [source-capture and demo disclosures](docs/investor/visuals/README.md). Visuals use synthetic/demo data; the new mobile illustration is a design concept, not a production APK screen.

**FIVE-PLATFORM MVP SOURCE v0.13.0 (build pending confirmation):** [Source status / acceptance](docs/GARDA_FIVE_PLATFORM_MVP_STATUS_2026-11-16.md) · [Unified server](projects/garda/ai-core/README_UNIFIED.md) · [Windows/Mac/Ubuntu client](desktop/README.md). Web route: `/workspace`; Android 13+ retains FOLD/Standard package IDs.

**DEVELOPMENT GARDA CCTV — 16 November 2026:** Source lengkap Android **FOLD + Standard v0.12.2**, Desktop, AI Core dan prototipe ONVIF telah dikonsolidasikan dari repo `docs`. Mulai di [projects/README.md](projects/README.md). Lihat [provenance dan batas migrasi](docs/GARDA_CCTV_MIGRATION_2026-11-16.md).

**🗺️ CURRENT INTERACTIVE PRD / BUILD BLUEPRINT (2026-10-11):** [GARDA PRD Visual Build Blueprint](./docs/GARDA_PRD_VISUAL_BUILD_BLUEPRINT_2026-10-11.html) — light standalone interactive HTML mapping current T1 Basic vs proposed PUSADA KAK bundle, feature modules, architecture, repo demo status, implementation roadmap, acceptance and code handoff. For implementation decisions, canonical docs in AGENTS.md still take precedence; this visualization is explanatory and not customer acceptance.

**⚠️ GARDA NAMING UPDATE (2026-10-09):** Tier 3 name **WASKITA has been rejected** by product owner due to overlap concerns. **GARDA NALAR** is the preferred replacement, **not yet approved**. [Decision + alternatives + trademark cautions](./docs/GARDA_TIER_NAMING_REVIEW_2026-10-09.md). Previous executive PDF/infographics with WASKITA are **outdated** until regenerated. Preserve internal tier ID T3 and all feature allocations.

**🖼️ GARDA MOBILE VISUAL PRD (new):** [6 mockup screens + mobile/tablet PRD for Codex](./docs/mobile/README.md) · [Full annotated Visual PRD](./docs/mobile/PRD_GARDA_MOBILE_VISUAL_v1.0_DRAFT.md). Includes Tier2 GARDA VIEW (proposal), Tier3 FIELD KIT, Tier4 COMMAND KIT, device activation and admin registry. Illustrations only; no native app has been implemented by this docs change.

**🎖️ T1 GUI + KAK FEATURE MATRIX (2026-10-11):** The demo now uses the GARDA TNI red-white futuristic mission theme. See the [standalone Tier 1/KAK HTML matrix](./docs/GARDA_TIER1_KAK_FEATURES_2026-10-11.html) for the complete feature traceability and the [Tier 1 video toolchain](./infra/tier1/README.md) for MediaMTX, ONVIF, go2rtc, Frigate, face and ANPR integration boundaries.

# GARDA — ACTIVE PRODUCT CONTEXT (2026-10-08)

**Codex MUST begin with `AGENTS.md`.** Latest owner-confirmed Tier1 product intent (KAK approval pending):
- **1 site, 1–49 camera channels, 1 concurrent operator; GARDA is the principal on-prem WebApp; existing NVR continues independent backup recording.**
- GARDA default 7-day local recording retention (HDD-dependent), **offline** with optional controlled updates and signed **offline license**.
- **Limited AI in Basic:** person presence, face presence **without names/recognition**, simple ANPR OCR; light GARDA Vault; Indonesian/English UI; native mobile starts Tier3.
- **Tier2:** authorized face recognition. **Tier4:** governed hierarchical federation of subordinate T1–T4 nodes, no arbitrary software federation count cap but scalable capacity planning.
- **Conflict warning:** PUSADA TNI KAK requires `90 days` and face enrollment/recognition, Ask GARDA, audio zonation, advanced rules/analytics, enterprise redundant hardware, etc. These go **beyond standalone T1**, so special contract bundle and signed KAK mapping required. **99.99%** is a goal, not guaranteed SLA.

**NEW MOBILE/TABLET BRAINSTORM (NOT APPROVED):** [Mobile View Only Tier2 + Managed GARDA Field/Command Tablets Tier3/4](./docs/GARDA_MOBILE_TABLET_BUNDLING_PROPOSAL_v0.1.md). A T2 native viewer would be a **change** to the earlier T3-only native-mobile decision and must await owner approval. Device-locked backend access, enterprise kiosk/MDM and offline-first are required design goals, NOT DRM guarantees.

## CURRENT CANONICAL DOCUMENTS
1. [Current decision register v0.3](./docs/GARDA_DECISION_REGISTER_v0.3.md)
2. [Tier1 Basic PRD v1.0 DRAFT](./docs/GARDA_TIER1_BASIC_PRD_v1.0_DRAFT.md)
3. [Master 592-feature catalog v0.3](./docs/GARDA_MASTER_FEATURE_CATALOG_v0.3.md)
4. [PUSADA TNI KAK gap matrix](./docs/GARDA_PUSADA_KAK_GAP_MATRIX_2026-10-08.md)
5. [Indonesian tier-name proposals (unapproved)](./docs/GARDA_TIER_NAMING_PROPOSAL_v0.1.md)

---
# GARDA — Codex Documentation Entry Point (2026-10-08)

**Current project intent:** Four-tier PUSADA MONITORING CENTER / GARDA for Indonesian government/TNI, initial contracted deliverable **T1 BASIC only**, with a fully documented, separately contracted T2–T4 roadmap. Top T4 integrates all lower-tier GARDA deployments into a policy-governed command center. **All source/core AI is proprietary; client source deliverables, if any, are restricted to separately approved viewer/basic-client code.**

## START HERE — Codex read order
1. **[AGENTS.md](./AGENTS.md)** — repository-wide coding, security, IP and scope rules.
2. **[Decision Register v0.2](./docs/GARDA_DECISION_REGISTER_v0.2.md)** — explicit owner decisions, TNI hierarchy, cross-unit access special grant, classification, software integration and IP policy.
3. **[Master Feature Catalog v0.2](./docs/GARDA_MASTER_FEATURE_CATALOG_v0.2.md)** — **592 DRAFT capability ideas**, grouped into **34 domains**, each tagged with an indicative earliest T1/T2/T3/T4 tier and a stable `VID-nnn` feature ID.
4. **[Tier PRD & Implementation Spec v0.2](./docs/GARDA_TIER_IMPLEMENTATION_SPEC_v0.2.md)** — precise Basic contract candidate slice, Tier4 federation, architecture, acceptance gates, hardware caveats and KAK mapping.
5. **[Codex Handoff v0.2](./docs/GARDA_CODEX_HANDOFF_v0.2.md)** — implementation plan, tests and operational scope guards.
6. **[Initial 4-Tier Brainstorm v0.1](./docs/GARDA_TIERED_PRODUCT_BRAINSTORM_v0.1.md)** — earlier brainstorming preserved as history.
7. **[GARDA historical technical/hardware context](./docs/project-garda/)** — camera/ONVIF, procurement and earlier architectural choices.

**Naming brainstorm (NOT FINAL):** [Indonesian T1–T4 name proposals](./docs/GARDA_TIER_NAMING_PROPOSAL_v0.1.md): **SIAGA / WASPADA / WASKITA / KOMANDO** plus alternatives. Keep internal T1–T4 IDs and contract scope unchanged until owner selects names.\n\n**Scope alert**: The feature catalog is NOT an implementation order; the existing UI is a demo and is NOT evidence of a functional deployed CCTV/biometric product. Pending product questions and the actual customer **KAK** must be resolved before a binding SOW/acceptance baseline is set. Government/classified material and secrets must never enter Git.

---

# PUSADA MONITORING CENTER | GARDA

## Working demo — GardaWEB

The interactive application is implemented in this folder. Run `npm ci` then `npm run dev -- --port 5173`. See [RUN_DEMO.md](./RUN_DEMO.md) for routes, deployment, verification, and demo boundaries. The original planning package follows below.

This package contains the planning assets for a Codex-built interactive demo.

## Files
- `PRD_PMC_GARDA.md` — full product requirements document
- `MOCKUP_DEMO_SPEC.md` — screen-by-screen UX/UI mockup specification
- `CODEX_MASTER_PROMPT_PMC_GARDA.md` — prompt to continue the build in Codex
- `DEMO_DATA.json` — deterministic fictional demo data
- `DESIGN_TOKENS.json` — starter visual tokens

## Recommended build order in Codex
1. Generate complete visual concepts for COMMAND + key detail screens.
2. Approve the concept.
3. Implement app shell and COMMAND.
4. Implement LIVE, EVENTS, INCIDENTS.
5. Implement ASK GARDA and VAULT.
6. Add remaining routes.
7. Verify desktop layouts at 1920x1080 and 1366x768.

The demo should use synthetic data only and should not require live CCTV integrations during the first frontend phase.
