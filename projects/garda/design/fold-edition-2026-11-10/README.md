# GARDA CCTV FOLD edition — 10 GUI design directions

This is a **visual mockup package** created before updating the Android APK. Do not mistake illustrated camera frames for active RTSP streams or the HTML prototype for native Android code.

## Open the preview

- **Fastest:** open `GARDA_CCTV_FOLD_edition_10_Concepts.html` in a desktop browser. Camera scene illustrations are embedded, so the preview does not require a server. The optional Three.js orb imports from CDN; offline users see a CSS 3D fallback.
- Alternative: unzip and open `index.html` alongside the `scenes` directory.
- Choose any of the **10 concept thumbnails**.
- Switch **White / Red Light Mode** or **Black / Red Dark Mode**.
- Switch **Fold closed** or **Fold open** to inspect responsive arrangement.
- Click bottom navigation and camera actions. These are simulations and do not connect to the actual camera.
- Choose **Simulate LAN load** to see an immediate skeleton state before a demo-only result.
- Keyboard: left/right arrows switch concepts; T toggles palette.

## Ten distinct screens

| # | Name | UX priority |
|---|---|---|
| 01 | Command Deck | Camera first, metrics and PTZ second |
| 02 | Crimson Grid | Four live views in compact grid |
| 03 | Focus Lens | Immersive single-camera view |
| 04 | Guardian Rail | Persistent left rail for Fold open |
| 05 | Alert Priority | Incident-first control center |
| 06 | Precision Cards | Minimal, readable camera monitoring |
| 07 | Sentinel Radar | Exploratory spatial grouping (not real floorplan) |
| 08 | Dual Vision | Native dual-lens FH8852V201 layout |
| 09 | Timeline Studio | Local playback / event review concept |
| 10 | Tactical HUD | Cinematic overlays and optional Three.js |

For the actual camera **FH8852V201** with two known RTSP endpoints (`1234` PTZ / `1235` wide), **08 Dual Vision** is the strongest domain-specific starting point. Combine its dual-lens view with **01 Command Deck** for general monitoring.

## Exported files

- `GARDA_10_Mockups_DARK.png`: ten black/red mockup cards
- `GARDA_10_Mockups_LIGHT.png`: ten white/red mockup cards
- `screens/`: 20 individual cover-screen variants (10 x 2 themes) and four Fold-open explorations
- `scenes/`: four original SVG illustration backgrounds
- `docs/ANDROID_IMPLEMENTATION_BLUEPRINT.md`: native Kotlin Compose direction, 3-button safe insets and asynchronous background tasks
- `index.html`: interactive source preview
- `GARDA_CCTV_FOLD_edition_10_Concepts.html`: standalone interactive preview with embedded scenes

No APK, firmware, camera credentials, recording, or actual surveillance media is included. All screenshot canvases were authored as illustrated concepts; browser preview interactions are demo-only.
