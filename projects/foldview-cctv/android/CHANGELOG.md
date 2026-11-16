# GARDA CCTV FOLD & Standard editions · Changelog

## v0.12.2 · 12 November 2026 — high-sensitivity joystick + motor diagnostics
- **Raised touch responsiveness:** larger 226dp joystick, default ×2.4 movement sensitivity with live adjustable slider (×1.0 to ×3.5). Touch feedback explicitly shows whether Android detects the gesture.
- **Fixed fast-finger cancellation race:** the first non-zero drag vector stays queued even when the user lifts a finger before the background network thread starts. One bounded motor command then Stop is sent on each quick directional tap.
- **Added four diagnostic direction buttons** (◀ ▲ ▼ ▶) that bypass the joystick's drag gesture and send a single motor test: ONVIF RelativeMove where supported or GARDA's vendor directional pulse. A camera may support only ContinuousMove or only RelativeMove.
- **ONVIF PTZ readiness check:** resolves PTZ service and media PTZConfiguration asynchronously before interpreting a touch as a working camera. Shows sanitized failures, e.g. missing PTZConfiguration, unsupported PTZ service, auth rejection, SOAP Fault and network timeout.
- **Background motor control:** stays on a single worker; no per-touch thread. Short touches are held for ~350ms after initial command to reduce premature Stop; ONVIF ContinuousMove retains its PT1S fail-safe timeout.
- **Never claim successful physical movement** based on HTTP acknowledgement or SOAP success. A camera that has ONVIF video only, including the early experimental FH8852V201 daemon, needs a genuine PTZ motor driver and functional ONVIF PTZ service (or working vendor API) before software joystick movement is possible.
- No camera firmware flash, settings writes, disk formatting or external network access were performed. GitHub CI tests validate source/build only; real camera/motor still requires field validation.
- Both Fold and Standard APK variants share the changes; signing keys may differ from installed debug versions. Export camera list before uninstalling an old APK.

## v0.12.1 · 12 November 2026 — joystick PTZ reliability hotfix
- **Fixed no-movement gesture failure:** replaced Compose touch-slop based `detectDragGestures` with immediate `awaitFirstDown` and `awaitPointerEvent(PointerEventPass.Initial)`, consuming touches before the scrollable Live view can intercept them. The thumb responds on initial touch rather than waiting for scroll recognition.
- **Fixed silent ONVIF command failure:** detect SOAP Fault in successful HTTP 200 responses (and SOAP faults in HTTP error bodies). A camera that acknowledges a SOAP envelope but rejects PTZ now shows a clear error instead of appearing successful.
- **Real capability validation:** PTZ can only use a Media Profile with `PTZConfiguration`; stop treating ordinary video-only profiles as PTZ enabled. ONVIF `ContinuousMove` uses `PT1S` device-side timeout for broad XML duration compatibility, with explicit `Stop` after release.
- **New backend selector:** for cameras with confirmed GARDA native status, a two-mode selector appears: `ONVIF` vs `GARDA`. GARDA pulses invoke bounded vendor REST requests (`/api/ptz`) and Stop; standard cameras use ONVIF `ContinuousMove`.
- **Nonblocking commands:** one background worker coalesces repeated drag position changes; UI never waits for network response; errors/status shown inline. Physical motor movements are **not verified** by HTTP acknowledgements.
- **Extra tests:** joystick native-direction mapping, SOAP Fault parsing, healthy SOAP result, analog deadzone/diagonal normalization.
- **Important hardware limitation:** the experimental `projects/cctv-firmware/fh8852v201-onvif/src/foldview_onvifd.c` in this repo explicitly implements **no PTZ**, so ONVIF discovery and streaming do not imply control over a physical motor. The camera's running firmware must expose a genuine PTZ driver. The user-reported motor failure cannot be guaranteed fixed by an APK alone.
- Both FOLD and Standard built from the same bugfix source; app IDs unchanged; v0.12.1 debug APK signer may differ from installed v0.12.0. Back up camera details before any uninstall. OTA remains gated on matching signing identities.
- No camera firmware, files, recordings, LAN devices, or motor settings were changed during this patch.

## v0.12.0 · 12 November 2026
- **Two independent APK editions from one shared Kotlin codebase:** GARDA CCTV **FOLD edition** and GARDA CCTV **Standard edition**.
- FOLD keeps Android ID `org.foldview.cctv` (existing Keystore-encrypted camera profiles preserved if the signing certificate matches); Standard uses `org.garda.cctv.standard`, so both apps can coexist but do not share protected camera data.
- **Fold layout:** responsive left navigation rail only in the Fold flavor at >=680dp, compact bottom navigation on cover screen. **Standard layout:** single-pane bottom navigation even on wide/landscape phones; native RTSP/ONVIF engine unchanged.
- **Dark Mode typography audit:** brighter secondary text on charcoal surfaces, improved outlines, high-contrast red-filled buttons with dark ink, accessible light mode red-white button contrast. Unit tests assert key WCAG AA text contrast ratios >=4.5.
- Improved **small screen layout:** adaptive 2-metric dashboard instead of three cramped cards, no side-by-side action buttons in Device discovery, saved-camera cards put actions on a dedicated row, all native motion buttons minimum 48dp high.
- More **visual UI** using offline Compose Canvas CCTV illustrations, red camera lens artwork, saved-camera thumbnails, RTSP/ONVIF status chips and contextual pictograms. No image download trackers or WebView 3D, to avoid adding GPU work during RTSP playback.
- Retained `Modifier.safeDrawingPadding()` around the app content; status bar, navigation keys, gesture zones and cutouts are respected without extra hardcoded bottom offsets. Removed hardcoded blue dividers incompatible with light/dark modes.
- **About** and in-app labels display edition-specific names. Language switch, PTZ joystick, memory-card discovery, camera backup/export, encryption and OTA UI remain shared.
- Internal OTA Python helper can now emit manifests for either `org.foldview.cctv` or `org.garda.cctv.standard`. Each installed edition needs its own correctly signed APK and matching manifest/package.
- CI builds, unit-tests, verifies package IDs, app labels and signatures, and uploads both artifacts; **physical screenshot/accessibility tests on Fold7 and non-foldable Android phones remain pending**.
- **Signing:** each CI debug build uses a new signing certificate. Upgrading a previously installed build may require backup and manual migration. Do not uninstall with unexported camera profiles.

## v0.11.0 · 12 November 2026
- **Native ONVIF analog joystick** using Compose pointer gestures: drag for pan/tilt proportional velocity, release/cancel/dispose issues Stop, 450 ms camera-side ContinuousMove timeout, coalesced commands (~5 Hz) on a background thread. Reduced fixed 280 ms button-pulse latency. Actual motor response depends on LAN and firmware; no field latency measurements.
- Pure Kotlin joystick geometry tests for center, cardinal and diagonal vectors. Retains hardware fallback PTZ/zoom controls where available.
- **Camera history is encrypted** with existing Android Keystore AES-GCM CameraVault; adds user-triggered export/import of saved camera names and RTSP/ONVIF addresses via Android SAF, **excluding all passwords**. Restore asks for credentials again. Prevents duplicates where possible.
- **Bahasa Indonesia / English** toggle persisted across launches; translated main navigation, Live, Devices, recording UI, Settings, About and action labels. Technical camera diagnostics may remain vendor-English.
- **Collapsible native panels** for joystick, quick actions, SD recordings, resolution profiles, privacy, compatibility, theme and About, plus icons/emoji. Does not add WebView/Three.js, minimizing battery and video render overhead.
- **Read-only ONVIF resolution discovery**: GetProfiles and optional GetVideoEncoderConfigurationOptions. Reports actual number and supported sizes from camera after querying. Selecting an ONVIF StreamUri changes only app playback; it never calls SetVideoEncoderConfiguration on the physical camera.
- **Camera microSD access test** via existing ONVIF Profile G GetServices/GetRecordings/GetReplayUri. Actual SD directory/file access remains unsupported unless camera firmware provides Profile G or vendor API.
- **Privacy & compatibility lists** Kotlin, Compose, Material3, Media3 RTSP, AndroidX, Keystore, SAF, ONVIF; server-only tools OpenCV, Python, FastALPR/ONNX, FastAPI, SQLite. Network caveat and library licensing explained.
- **Constraints:** 0.11 is debug signed by ephemeral GitHub runner signing key; Android may reject in-place updating 0.10. Save existing camera configuration manually before uninstall. New export/restore works AFTER 0.11 is installed but cannot recover already wiped old Keystore secrets.
- Live FH8852V201 camera PTZ performance, ONVIF Media services, memory-card support and available camera resolutions **not independently validated**. CI compile, XML and joystick math tests are not field tests.

## v0.10.0 · 12 November 2026
- Added **About GARDA** with app versionName and build versionCode loaded from PackageManager, developer credit **Adithya Pratama**, and **For internal use only** notice.
- Added **Check for updates** button and configurable internal OTA manifest server URL under Settings; JSON fetched asynchronously via Dispatchers.IO, never on the UI thread.
- Added downloadable internal OTA APK with progress, strict version upgrade, maximum 200 MiB, SHA-256 integrity, matching packageName and **APK certificate matches the installed app** before Android's official installer is invoked.
- Added FileProvider for cache-only APK sharing and Android REQUEST_INSTALL_PACKAGES user permission; **no silent installation**.
- Added Google Drive releases shortcut (manual authenticated fallback). Private GitHub repo and private Drive URLs cannot be used as anonymous direct APK download endpoints.
- Added separate LAN OTA Python server and setup guide for GARDA Desktop; it serves only /manifest.json and /GARDA-update.apk from an administrator-selected local APK.
- **Important signing limitation:** GitHub CI generates a fresh temporary debug signing certificate every run. Android cannot update across different signing certificates. Current OTA deliberately stops on mismatch to avoid data loss. **Persistent private signing keystore is required to enable seamless future in-place upgrades.**
- Physical Android/Fold7 OTA installation and LAN-server deployment are not yet verified; CI validates native build and parser tests.
- Local server defaults to loopback, must be bound to the specific PC LAN IP deliberately, and should be restricted to an authorized CCTV VLAN.
  
## v0.9.0 · 12 November 2026
- Fixed ONVIF XML parser crash on Android: the platform does **not** support JAXP `XMLConstants.FEATURE_SECURE_PROCESSING` in `DocumentBuilderFactory`. A shared Android-compatible safe parser handles Device, Media, PTZ and Replay SOAP XML; rejects DTD/entity declarations, uses a deny-all external EntityResolver, and caps XML size.
- Device Registry **Connect** and auto **Scan + Connect** show a login modal when an ONVIF camera needs credentials; for camera `192.168.1.19` or any private LAN host.
- Added username, masked password, show/hide, Remember checkbox (checked by default), Cancel, and anonymous retry. Includes optional full RTSP URL override if a vendor exposes RTSP on a nonstandard path such as port 8554.
- ONVIF WS-Security UsernameToken PasswordDigest submitted via SOAP; Media3 RTSP Basic/Digest playback uses credentials in protected RTSP URI.
- Remembered logins are stored per-camera host with Android Keystore AES-256-GCM and never saved in plaintext preferences. Non-remembered login remains session-only and is stripped from persisted camera profiles.
- After login resolves ONVIF Media GetStreamUri, connect to Live view and preserve dual-lens behavior where available; auto scan attempts remembered camera credentials.
- Applied secure parser to ONVIF Profile G replay and PTZ as well as discovery connection; avoid exposing SOAP bodies or entered credentials in error messages.
- Debug-signed CI release: Android may reject in-place upgrade if signer differs; save/record existing camera profiles before any uninstall.
- **Not hardware validated:** built/tested via CI, on-device login and playback depend on ONVIF/RTSP firmware support. Credential use over HTTP/RTSP on a trusted LAN still lacks transport encryption; use camera VLAN/VPN and secure device passwords.

## v0.8.0 · 10 November 2026
**Android launcher name:** GARDA CCTV FOLD edition.  
**Package:** `org.foldview.cctv` (unchanged from FOLDVIEW v0.7.0 so camera vault and app ID remain compatible if the signing certificate matches).

### User interface
- Replaced the teal/blue legacy UI with white + red Light Mode and black + red Dark Mode.
- Fold closed: four evenly spaced, touch-friendly navigation controls stay above Android system Back/Home/Recents; Fold unfolded: compact left-side navigation rail.
- `WindowInsets.safeDrawing` via `Modifier.safeDrawingPadding()` reserves space for Android 3-button and gesture navigation without hardcoded offsets.
- Combined mockup 01 **Command Deck** (dashboard and actions) with 08 **Dual Vision** (two RTSP lens feeds).
- Primary video tiles appear before secondary PTZ/recording controls; tools are in scrollable native panels.
- Responsive Focus / Dual / 4-tile / 9-tile layouts; Fold-open shows dual camera streams side-by-side, cover display stacks them.
- Native button press-scale feedback (~125ms), animated navigation selection (~210ms), red badges and in-app shield icon.
- Immediate skeleton placeholders during explicit LAN discovery, reduced motion respected where system animation scale is zero.
- New app launcher vector mark and camera snapshots stored under Pictures/GARDA_CCTV.
- Theme switch in Settings persists between app launches via private app preferences.

### Networking and performance
- Preserves FOLDVIEW v0.7.0 RTSP/ONVIF, WS-Discovery, dual-lens streams 1234 / 1235, GARDA native /api/status, PTZ and lamp controls.
- Network scanning and ONVIF calls remain on worker threads; recording-library disk enumeration now uses coroutine `Dispatchers.IO`.
- Limits active decoders to four; avoids WebView / Three.js background render loops during CCTV playback.
- Refreshing discovery sets visible loading state before scanning begins; scan is user initiated and private LAN scoped.

### Compatibility and limitations
- `org.foldview.cctv` is unchanged; this release is a native Kotlin/Jetpack Compose implementation, not the HTML mockup.
- GitHub CI signs debug APKs with ephemeral debug credentials; an already installed APK **may fail in-place update with INSTALL_FAILED_UPDATE_INCOMPATIBLE**. Export/save camera configuration before uninstalling the old build, because uninstall can erase Keystore-encrypted saved camera profiles.
- Physical Galaxy Z Fold7 3-button + gesture modes, fold transition, live RTSP and GARDA motor/LED response must still be tested on the user's device. Build success alone does not prove those hardware checks passed.
- Deleting earlier **Drive APK release files** does not delete the existing app on the user's smartphone, and Git history retains full source and changelog for reproducibility.
- The native ONVIF daemon firmware and existing GARDA Desktop Windows application are not modified by this Android UI release.

## v0.7.0 · 10 November 2026
- Native GARDA FH8852V201 camera detection and LAN REST controls, RTSP 1234/1235 dual-lens, RTSP-over-TCP, fixed LAN RTSP OPTIONS line endings.

## v0.6.0 · 10 November 2026
- User-triggered bounded LAN camera discovery, ONVIF Media negotiation and quick connect.

## v0.5.0 and earlier
- Prototype Android RTSP live grid, ONVIF PTZ, experimental intercom, local recording and replay.
