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
