# Demo design routes — 2026-10-14

Owner decision: keep the previous design at `/` and publish the refreshed design at `/V2`.

- `/` and its module routes use the design from commit `058b06f`, before the Stage 2 workspace refresh. The legacy shell and stylesheet are retained in `src/legacy/`.
- The root design has a Dark/Light toggle. Its preference uses `garda-root-theme`, independent of the V2 `garda-theme` preference.
- `/V2` and `/V2/*` use the current Stage 2 shell, collapsible menu, camera thumbnails, dark/light preferences, and Three.js Mission Grid.
- A route segment boundary selects the design, and React Router uses `/V2` as its basename. Client navigation, queries and direct page reloads remain in the selected version.
- Shared modules, synthetic demo data and the Face Recognitions Basic naming remain current. This routing change does not alter tier entitlements.
- Vercel continues to serve the SPA through the existing fallback rewrite. No new project or domain is created.
- Verification: build and existing demo tests; browser navigation from each entry, direct reload of V2 Live with a camera query, and checks for independent styling.
