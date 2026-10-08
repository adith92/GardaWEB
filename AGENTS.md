# AGENTS.md — Instructions for Codex in GARDA/GardaWEB
Applies to **every** file and AI coding session in this repository. Product: PUSADA MONITORING CENTER | GARDA. Language for product-owner summaries: **Bahasa Indonesia**.

## Read-first documents and precedence
1. `docs/GARDA_DECISION_REGISTER_v0.2.md` — explicit decisions, uncertainties, IP/security policy.
2. `docs/GARDA_MASTER_FEATURE_CATALOG_v0.2.md` — complete *candidate* feature universe + suggested minimum tiers.
3. `docs/GARDA_TIER_IMPLEMENTATION_SPEC_v0.2.md` — delivery boundaries, architecture, RBAC, testable acceptance and roadmap.
4. `docs/GARDA_CODEX_HANDOFF_v0.2.md` — implementation workflow, ticket breakdown and definition of done.
5. `docs/GARDA_TIERED_PRODUCT_BRAINSTORM_v0.1.md` — historical first baseline.
6. `docs/project-garda/` — equipment, context and procurement history. Prefer *later dated* owner decisions over earlier proposed options.
7. `PRD_PMC_GARDA.md`, `CODEX_MASTER_PROMPT_PMC_GARDA.md`, `MOCKUP_DEMO_SPEC.md`, `RUN_DEMO.md` — existing **demo** guidance, not evidence that backend capabilities are production-ready.

## Non-negotiable build guardrails
- All four tiers are documented; **implement only the explicitly authorized active contract scope, initially Tier 1 Basic**. Do NOT automatically build or promise Tier 2–4; feature matrix is a roadmap, not a work order.
- Distinguish: `DECIDED`, `PROPOSED`, `OPEN`, `DEMO`, `IMPLEMENTED`, `TESTED`, `ACCEPTED`. Never mark a mock as functional camera/AI integration.
- Preserve legacy frontend demo behavior where useful, but clearly label all simulated events, faces, plates, AI answers and streams.
- Add real functionality via independently testable modules: ingest/restream, recorder, playback, API, UI, incident, evidence, storage health, auth, audit, policies. Separate recording from AI.
- Enforce authorization **server-side**, for every route, media URL, websocket, event message, query, export, API and integration. Default-deny cross-unit access. A code alone MUST NOT bypass RBAC, classification or approval policy.
- Do not put secrets, real addresses of government networks, actual credentials, biometric samples, classified content or customer footage in Git.
- Keep GARDA proprietary backend/AI source private. Do not publish repository, invite customers into private core, or include server code in customer viewer packages. Third-party OSS licenses still apply.
- Any cross-tier HQ control/federation or classification machinery belongs to roadmap Tier 4 unless an explicit new decision changes scope.
- No automated physical access, alarm, dispatch, drone or other consequential actuation based purely on AI or LLM output.
- Only approved lawful biometric uses, with consent/authority and monitoring safeguards where required.
- Treat product claims and SLAs as hypotheses until measured and agreed in KAK; do not fabricate camera limits or uptime metrics.

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
