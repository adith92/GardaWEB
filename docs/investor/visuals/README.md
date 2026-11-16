# GARDA Security — Investor Visual Library (2026-11-16)

This folder contains presentation-ready images rendered **from the locally running React demo source in this private repository**, plus the approved conceptual mobile design. It does **not** contain production CCTV footage or measured AI outcomes.

## Assets
- `index.html`: 19 interactive landscape presentation frames (16:9; 1600×900 CSS pixels), with investor-neutral GARDA Security typography. Open locally in a browser, use the slide picker or arrow keys.
- `source-captures/`: 15 route screenshots taken from the running local Vite demo with investor-only removal of PUSADA/TNI labels. These are UI demo captures, **not CCTV/AI production evidence**.
- `renders/`: 19 rendered 16:9 JPEGs suitable for placement in the proposal Word/PDF/presentation.
- `../../../screenshots/command-mobile.jpg`: mobile **concept art**, approved by product owner, **not** a screenshot of a deployed Android app.
- `../../../screenshots/command-mobile-legacy.jpg`: prior mobile screenshot retained for traceability.

## Modules covered
1. Investor cover
2. Command Center
3. Live Monitoring
4. Playback
5. Events
6. Face Intelligence (demo only)
7. Plates / ANPR (demo only)
8. Site Map
9. Incident Command
10. Ask GARDA (deterministic demo)
11. Analytics
12. Vault
13. Device Management
14. System Health
15. Audit
16. Settings
17. Mobile concept
18. Four-tier roadmap
19. Local/on-prem architecture concept

## Reproduce
```bash
npm ci
npx playwright install --with-deps chromium
node scripts/render-investor-visuals.mjs
```
Requires Node.js 24, Playwright installed via the pinned project dependencies, and an environment able to launch Chromium. The script starts a **local** Vite server on `127.0.0.1:5181`, captures all fifteen routes in a browser, then renders this gallery. GitHub Actions runs the same script and commits results on main. It does not modify runtime app routes, the default Vercel deployment, camera credentials, or network camera devices.

## Important disclosure for investors
- GARDA is a product under development. Screens showcase design/UI flows and synthetic data.
- All statuses, video stills, faces, plates, storage metrics and alarm events shown by the demo are fictitious.
- UI demo face matching, Ask GARDA, RBAC, retention and NVR interfaces are **not** proof of production integrations or conformance with a government procurement contract.
- Investor visual adaptation replaces textual project names **only in browser DOM for capture**. It does not alter the app source or imply customer endorsement.
- Actual camera integration, ANPR accuracy, security UAT, storage sizing and device benchmarks require separate tests before commercial claims.

## Use in proposal
Use visuals as examples captioned *Tampilan demo aplikasi GARDA Security (data simulasi)*; for the phone, use *Konsep tampilan aplikasi mobile GARDA Security*. Avoid framing these as installed customer deployments. Do not distribute private repository links to outside investors without deliberate access approval.
