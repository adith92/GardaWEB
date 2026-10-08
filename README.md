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
