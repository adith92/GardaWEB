# GardaWEB — PMC GARDA interactive demo

React 19, TypeScript, Vite, Tailwind CSS, Lucide, and Recharts. Opens directly into COMMAND. Original planning files and the supplied PUSADA logo are retained.

The current demo theme is **GARDA TNI Merah Putih Futuristik**: graphite mission surfaces, red/white command accents, technical grid treatment, and readable operational density. The redesign is visual only; all camera, AI, incident, and storage interactions remain synthetic demo behavior.

## Run locally

```sh
npm ci
npm run dev -- --port 5173
```

Open http://127.0.0.1:5173. Production check: `npm run build`. Logic checks: `npm test` (four tests covering filters, incident state, seeded queries, evidence references, and report totals).

Tier 1 LAN toolchain preparation is documented in [`infra/tier1/README.md`](./infra/tier1/README.md), with an optional MediaMTX/ONVIF/stream bridge compose harness. The standalone feature traceability page is [`docs/GARDA_TIER1_KAK_FEATURES_2026-10-11.html`](./docs/GARDA_TIER1_KAK_FEATURES_2026-10-11.html).

## Routes and interactions

COMMAND, LIVE, PLAYBACK, EVENTS, FACES, PLATES, MAP, INCIDENTS, ASK GARDA, ANALYTICS, VAULT, DEVICES, SYSTEM, AUDIT, SETTINGS.

Camera selection, 1/4/9/16 layouts, camera search, auto-cycle, fullscreen, synthetic snapshot download, recording-session metadata, PTZ position preview, playback controls and bookmarks, event search/filter/review, deterministic event simulation, face/plate categories and watchlists, map camera layers/zoom and Digital Twin Preview, incident creation/acknowledgement/assignment/notes/evidence/resolve/reopen/export, five seeded Ask GARDA answers with clickable evidence, Vault folder creation/file-metadata upload/search/share/archive/restore/download, system diagnostics, device search, audit export, saved settings, and demo entry/exit.

Changes persist in browser localStorage under `pmc-garda-demo-v1`. Settings → Reset demo data restores the original fixture. The fixture date remains 1 October 2026 so screenshots and query answers are deterministic.

## Demo boundaries

All camera/map/portrait images are synthetic except the user-supplied application crest. CCTV views use static images with local simulated controls. Clip exports contain metadata, not video. Snapshot downloads contain the synthetic camera atlas. Ask GARDA uses deterministic answers, not an external AI model. Vault stores file metadata only; uploaded file contents are neither retained nor sent. Sharing, roles, retention, device health, storage metrics, and login are demonstrations, not production security or infrastructure.

## Vercel

Project: `gardaweb` in the `adith92` scope. Vite output: `dist`. `vercel.json` rewrites extensionless app routes to `index.html`, preserving static asset paths. Deployment: `vercel deploy --prod --yes --scope adith92`. No environment variables are required by the frontend.

Published: https://gardaweb.vercel.app. Deployment `dpl_ACU4Uf5ADEy6MrogJPUWBjELXH9D`, production state READY, 2 October 2026. Public HTTP checks returned 200 for `/` and `/live`. Browser verification on the deployed site confirmed COMMAND renders, LIVE survives reload, the 4-camera layout produces four tiles, and no console errors/warnings appeared.

## Verification record

TypeScript and Vite production build passed. Four logic tests passed. In-app browser tested route navigation for all 15 modules; camera selection/PTZ/manual recording state/playback/frame step/synchronized layout/bookmarks; camera and event filtering/review/simulated event arrival; incident acknowledge/assign/note/attach/resolve/reopen and persistence after reload; all five Ask GARDA queries/evidence links; Vault create folder/synthetic metadata upload/share options/archive/restore; and Digital Twin entities. Desktop 1920×1080, 1366×768, and 390×844 checked. No document horizontal overflow at 1366 or 390. Mobile menu opens. Production browser tested navigation and deep-link reload.

Visual comparison used `view_image` on the COMMAND concept and final deployed screenshot. Compared sidebar order and original crest, red/white/olive palette, compact heading/control typography, central map plus four-feed strip, three-case incident rail, event table, and storage/infrastructure strip. Concept imagery and sample copy differ intentionally as described below. The generated concept is 1672×941; implementation additionally verified the requested 1920×1080 and 1366×768 targets. The live browser screenshot reflects the implemented app, not a raster UI mockup.

## Visual assets

`design/command-concept.png`, `design/key-screens-concept.png`; generated using the built-in Image Gen tool. Brief: complete operational COMMAND and LIVE/INCIDENTS/ASK/Vault content surfaces, white and red, compact Lucide icons, original crest, restrained olive branding accent. Production assets: `public/site-map.png`, `public/cameras.png`, `public/faces.png`. Screenshot evidence is in `screenshots/`.

Intentional concept adaptations: original JSON names/times override fabricated text in the image concepts; KPI metrics use one compact strip; headings use supplied PRD labels plus Indonesian operational descriptions; simulated controls are labeled; desktop COMMAND is tightened to retain the event table and infrastructure strip.
