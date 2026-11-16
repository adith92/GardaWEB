**v0.13.0 source candidate — packaging not yet approved:** Android 13+ (minSdk 33), versionCode 17. Named GARDA server login and shared eight-camera Workspace added. Both package IDs preserved. Existing APK signer is unavailable; export profiles before manual migration. See [unified server and migration instructions](../../garda/ai-core/README_UNIFIED.md). Historical release notes follow.

# GARDA CCTV FOLD + Standard editions v0.12.2 — native Android

2026-11-08. Native Kotlin/Compose Android viewer. Latest build uses **AGP 9.5.1, Gradle 9.6.0, Kotlin Compose plugin 2.4.21, Compose BOM 2026.09.00 and Media3 1.11.1**. CI downloads Android SDK 37.0 and verifies v2 APK signature.

## Implemented
- Ad-free RTSP live viewer (H.264/H.265 subject to device decoder) with 1, 4, 9 and 16 tile layouts; max 4 concurrent active streams.
- Secure local camera setup storage with Keystore AES-GCM; manual RTSP URL and ONVIF endpoint + credentials.
- ONVIF WS-Discovery, GetCapabilities, GetProfiles, PTZ SOAP UsernameToken Digest, short-step ContinuousMove and Stop. Requires ONVIF PTZ support, unverified on the user's V380 camera.
- **Experimental ONVIF intercom:** RTSP DESCRIBE with ONVIF backchannel Require extension, SDP `a=sendonly`, G.711 PCMU/8000 RTP over TCP, MIC through Android AudioRecord with user runtime RECORD_AUDIO permission, Setup/Play/Teardown, Basic or Digest RTSP authentication where recognized. This works **only if the camera supports the standardized audio backchannel**, requires same LAN/VPN, and has **not been hardware tested**. It will fail or report unsupported on many V380 proprietary-cloud devices. There is no V380 vendor P2P intercom API implementation.
- **Video recording to phone or external USB HDD/SSD**: Android MediaProjection screen capture (explicit user approval) and MediaRecorder H.264 MP4, foreground service and persistent stop notification. Phone target: `Movies/FOLDVIEW/`. External target: `FOLDVIEW/` in a user-chosen SAF document tree, writing MP4 directly to a provider with a writable **seekable** file descriptor. External storage must remain mounted until Stop. **Max 30 min per user-approved recording; no unattended recording or automatic resumption.** Not raw RTSP, not camera microSD recording, and no audio recording.
- Local playback from recordings tab for MP4 captured by the app on phone or user-selected USB document folder. Uses MediaStore + SAF DocumentFile + Media3 player.
- **Experimental camera SD/NVR ONVIF Profile G playback**: query GetServices + GetRecordings, enumerate recording tokens, request GetReplayUri, and open camera's RTSP replay URL in Media3 player. Available only for devices exposing ONVIF Recording/Replay services; some replay streams require extensions/time seeking unsupported by Media3; unverified on V380.
- ONVIF PTZ has directional short pulses plus *experimental* zoom in/out buttons. Supported only if camera advertises and authorizes these controls.
- Camera snapshot (PixelCopy), audio monitoring RTSP (ExoPlayer), dark compact and unfolded Fold7 layout.
- No ad SDK, cloud login or 3rd-party telemetry.

## Unsupported or unverified
- **Complete camera microSD replay is not implemented**: Profile G recording enumeration and GetReplayUri are experimental, with no recording time-range search, calendar timeline, exact seek, trick-play, RTSP Range negotiation, or vendor SD-file export. Non-Profile-G V380 firmware will not work. Cloud playback and vendor push alerts remain unavailable.
- Vendor V380 proprietary P2P/UID/login and its firmware-specific audio protocol; ONVIF audio backchannel above is **experimental**, not guaranteed on V380.
- Bidirectional PTZ presets, 16 active decoders, continuous raw RTSP remux recording, background unattended 24x7 capture.
- Real-device Galaxy Z Fold7 smoke test, interoperability test with the actual V380 model/firmware, latency and battery profiling.

## Install and configuration
1. Install a verified **debug-signed APK** to sideload. This is not a stable production signing key. Debug certificates can change between GitHub Actions runs; installing a new build on top of the old version may require uninstalling. Uninstall removes locally encrypted camera configurations.
2. Add RTSP URL. Optionally configure `http://<camera-ip>/onvif/device_service`, ONVIF username and password for PTZ.
3. For **Talk (ONVIF)**, tap the button, approve Android microphone permission, and use only on a local camera that advertises standardized G711 PCMU RTSP backchannel. Stop talk explicitly; errors are shown.
4. Under **Recordings**, choose **Phone memory** or **Choose USB / HDD folder**. Connect an Android-visible OTG drive before selecting a folder. The Android document picker grants limited persistent read/write permission only for that folder.
5. For local MP4, open Live > Record MP4, approve Android screen capture every time, keep video displayed (this captures screen UI, not the compressed RTSP stream), stop from the app/notification or after max 30 minutes, then visit Recordings > Refresh > Play. Do not unplug USB during recording. If the USB DocumentsProvider cannot provide seekable output, the capture fails rather than silently writing to phone memory.
6. If an ONVIF Profile G camera has Recording and Replay services, select it and use **Recordings > Camera SD > Discover > Replay** to attempt remote RTSP replay. This is an exploratory feature, not a guaranteed V380 microSD timeline. Many firmwares will reject the SOAP/RTSP actions.
7. Remote viewing should be via private VPN; do not expose RTSP/PTZ to the public Internet. SMB/NAS continuous recording and 24/7 background NVR remain separate features.

## Privacy/security
- App stores camera URLs and ONVIF credentials encrypted by Android Keystore. No analytics/advertisements.
- RTSP intercom transmits live microphone only after explicit button and Android permission. It stops on Android Activity onStop (backgrounding/switching apps) and camera change. Standard RTSP without TLS sends camera stream/audio unencrypted over the transport; use trusted LAN/VPN.
- Android MediaProjection explicitly captures visible display; might include app UI or other screen content. Output stored to local MediaStore Movies/FOLDVIEW collection.
- Do not upload camera passwords or private RTSP URLs to GitHub or Google Drive.
- Camera motor movements should only be controlled on authorized cameras. Device-specific support may vary.

## References
- [Android MediaProjection](https://developer.android.com/media/grow/media-projection)
- [Android AudioRecord](https://developer.android.com/reference/android/media/AudioRecord)
- [Android Media3](https://developer.android.com/media/media3/exoplayer/rtsp)
- [ONVIF Audio Backchannel Streaming Spec](https://www.onvif.org/specs/stream/ONVIF-Streaming-Spec-v1906.pdf)
- [ONVIF PTZ Specification](https://github.com/onvif/specs)
- [Android local-network permission](https://developer.android.com/privacy-and-security/local-network-permission)

Build outputs are stored under GitHub Actions `.github/workflows/foldview-build.yml` and copied into the user's Google Drive: `ChatGPT/FOLDVIEW CCTV - APK & Release`. Android signing verification is mandatory; the APK and checksum must exist before any release is claimed ready.


## 2026-11-09 engineering update
- Added scoped-storage Storage Access Framework destination picker for Android-visible external USB HDD/SSD folders (and any compatible seekable provider), persistent user-controlled read/write grant, no broad-storage permission.
- Direct MediaRecorder MP4 output to SAF file descriptor without copying video through internal phone storage first; failure is surfaced via local notification. If an external drive is removed mid-record, the file may be corrupt/incomplete.
- Local playback library merges phone MediaStore and selected external folder clips, sorted by time, openable through Android content URIs.
- PTZ zoom in/out added; requires compatible ONVIF device.
- Verified dependency baseline: androidx.documentfile 1.1.0 stable (official release notes, May 2025); AGP, Compose and Media3 pinned as above and must pass CI.
- **No cloud/P2P V380 feature parity, no camera SD replay, no direct RTSP packet remux, no SMB/NAS and no 24/7 recording.** Intercom is experimental. No physical camera/USB HDD/Fold7 tests so far.
- Always test real HDD/OTG storage, USB disconnect, storage permission revocation, video seekability and playback before calling this production-ready.


## 2026-11-09 experimental Profile G extension (v0.6.0)
- Added `OnvifReplay.kt` to negotiate ONVIF GetServices, Recording GetRecordings, and Replay GetReplayUri.
- Parsed SOAP with XXE/DOCTYPE disabled, no camera credentials or replay URLs logged. Reuses existing ONVIF UsernameToken SOAP authentication.
- Camera SD button queries the camera and presents recording tracks returned by Profile G. Selecting a track opens the ONVIF replay RTSP URI in Media3.
- **Do not interpret listing a track or receiving a URI as proof that full camera SD playback works.** Media3 RTSP may not honor ONVIF Range/Scale extensions and cameras may reject G service even when ONVIF live works.
- Real camera (V380/NVR) verification, remote replay time selection, codec selection and robust RTSP backchannel tests remain mandatory before any production release.


## 2026-11-10 — LAN scan and quick connect (v0.6.0)
- Added `LanCameraScanner.kt`: user-triggered ONVIF WS-Discovery plus bounded RTSP/TCP camera port scan on the **active private Wi-Fi/Ethernet IPv4 subnet only**; maximum /24, 20 concurrent workers, 220 ms probe timeout. No full 65,535-port vulnerability scan, SSH/Telnet/login attempts, root detection or firmware writes.
- Added `CameraQuickConnect.kt`: confirm device service `GetCapabilities`, negotiate Media `GetProfiles` and `GetStreamUri` without guessing RTSP path; only accept endpoint URIs matching the discovered camera IP. For known Fullhan port 1234/1235, allows direct bare-root RTSP fallback. Port-open alone is never treated as verified ONVIF.
- Camera page now offers **Scan LAN** (preview detected hosts) and **Scan + Connect** (adds verified, supported local streams only) plus per-camera **Connect**. Camera URLs remain encrypted by Android Keystore.
- Cameras requiring authorized credentials or vendor-specific RTSP paths must be configured manually in **Add RTSP**. A failed negotiation does **not** bypass authentication or mark a camera connected.
- The latest CI-generated APK is **debug signed**, and each CI run may use a different debug signing certificate. **Back up camera profiles before uninstalling an older debug APK**. Stable upgrade signing needs a user-owned Android release signing key securely stored in GitHub Actions secrets.
- Device-specific camera compatibility, original V380 P2P/cloud, camera microSD replay, ONVIF two-way-audio compatibility, USB/HDD live tests and physical Fold7 smoke testing remain unverified.
- Local subnet discovery will not automatically traverse routers or VLANs. Wi-Fi should be connected to the actual camera VLAN.

## 2026-11-10 native GARDA ONVIF and dual-lens integration (v0.7.0)
- Integrates with **user-reported native GARDA FH8852V201 ONVIF/REST daemon** on camera port 8899; read-only detection validates `GET /api/status` reports `status=online` and `vlcview_running=true`. User's daemon is not bundled in the Android APK.
- Adds GARDA native PTZ/lighting controls on Live ONLY after status detection: left/right/up/down/stop/center, white spotlight on/off, IR on/off, IR-cut day/night. Uses narrow, fixed paths `/api/ptz` and `/api/led` with POST, does not use root Telnet or binary PTZ 7777. PTZ movement follows with best-effort STOP after 220ms; the firmware must have its own hardware timeout. **HTTP 200 means request accepted, not confirmed mechanical movement.**
- Restores **correct RTSP OPTIONS CRLF framing** in LAN camera discovery; previously double-escaped line terminators could prevent RTSP identification. This fixes a known scanner defect.
- Supports saving two camera entries when **both** GARDA RTSP listeners (1234 PTZ and 1235 wide) are found. Scan + Connect and per-device Connect preserve existing saved camera profiles and add missing streams. Automatically choose 4-up grid when multiple camera streams are present.
- Forces Media3 RTSP RTP-over-TCP for video tiles with `RtspMediaSource.Factory().setForceUseRtpTcp(true)`.
- Preserves Android application ID `org.foldview.cctv` and Android Keystore encrypted camera vault; versionCode 9 / versionName 0.7.0.
- GARDA vendor REST control is not standardized ONVIF, may be **unauthenticated**, and uses plain HTTP. Isolate CCTV on a trusted LAN/VLAN; never port-forward 8899, 7777, 23, or 21.
- **Hardware not remotely retested**: user reports native ONVIF running, but this build must be tested on actual Fold7 / FH8852V201. ONVIF device services, PTZ support, light GPIO and static IP alias may differ after camera reboot. GARDA Mobile `com.garda.camera` remains a separate Android project.
- GitHub Actions APKs are CI debug-signed with potentially changing keys. Updating over v0.6.0 might trigger a signature mismatch. Uninstall deletes encrypted camera profiles. Back up configuration or establish a persistent release keystore before uninstalling.

## v0.8.0 · New GARDA CCTV FOLD edition interface
The Android launcher name is **GARDA CCTV FOLD edition**. The Android applicationId stays `org.foldview.cctv` to retain in-place upgrade compatibility when the signing certificate is unchanged.

- White/red and black/red material schemes; user-toggle theme persists via local preferences.
- Adaptive cover-display bottom navigation vs fold-open vertical rail. Wraps the root user-interface in `safeDrawingPadding()` so Android Back/Home/Recents and system gesture zones cannot cover interactive buttons.
- Concept 01 Command Deck + 08 Dual Vision. Feed-first Live screen with native responsive tile arrangement (Focus / Dual / 4 / 9). Two Fullhan RTSP streams display vertically on narrow screens and side-by-side on unfolded Fold screens.
- Animated button press scale, navigation-selected colors, skeleton loaders while discovery operates, branded shield icon and red-camera badges.
- Slow recording-library disk enumeration moved to `Dispatchers.IO`; existing LAN scanning, SOAP and REST calls remain on worker threads.
- Retains native GARDA REST/ONVIF, local-only RTSP, PTZ/LED, recordings, and encrypted saved profiles.
- **No Three.js in Android native playback:** native Compose animation avoids WebView render loops and extra GPU load. HTML mockups can use Three.js ornaments, but the shipped native APK does not.
- Release notes: [CHANGELOG.md](CHANGELOG.md). Official mockups: [projects/garda/design/fold-edition-2026-11-10](../../garda/design/fold-edition-2026-11-10).

**Limitations:** Camera hardware and Galaxy Z Fold7 physical UI were not tested in this build environment. The previous CI APK used an ephemeral debug signing certificate, so Android may reject an in-place update. Do not uninstall before exporting camera profiles where possible, because uninstall erases encrypted app storage.

## v0.9.0 · ONVIF Login and Remember
Tap Devices → Scan LAN (or Scan + Connect) → **Connect**. When a protected camera is discovered, enter its ONVIF username/password in the native popup and select **Remember login** to keep it across app restarts via Android Keystore AES-GCM. If ONVIF cannot supply a media stream URL, enter the full RTSP playback URL in the optional fallback field. Anonymous cameras can use **Tanpa login**. No password is uploaded to GitHub or Drive.
Android's DocumentBuilderFactory does not implement JAXP FEATURE_SECURE_PROCESSING; fixed shared SOAP parser remains DTD/entity rejecting. Real protected-camera authentication and device playback need physical verification.

## v0.10.0 · Internal OTA, version & About
- Settings → About GARDA displays live APK versionCode/versionName; developer **Adithya Pratama**, **For internal use only**.
- Settings → App updates has **Check for updates**, **Download update**, **Install verified APK** and manual **Google Drive releases** shortcut.
- Configure a private LAN OTA manifest URL in Settings, e.g. `http://<PC LAN IP>:8877/manifest.json`. Use the bundled Python helper `ota-server/garda_ota_server.py` from GARDA Desktop Windows with a locally downloaded APK.
- OTA verifies SHA-256 **and current app signing identity** before opening Android system installer. This is not silent OTA. On Android 8+, approval of install-from-this-source may be needed.
- Private Github repository is not an anonymously accessible update distribution channel. Private Drive downloads require Google authentication, so the Drive button opens the user's Drive releases folder as an authenticated manual fallback.
- **Signing warning:** Existing debug APKs use ephemeral CI signer. Different signer blocks OTA; do not uninstall until camera settings are documented or exported. Configure a stable release keystore held privately for production.
- LAN OTA service source is included but is **not automatically running on the Windows computer**; the user must start it with the actual PC LAN IP and allow firewall access on their trusted LAN.

## v0.11.0: Joystick PTZ, bilingual UI, camera history and ONVIF capabilities
- **Live → Joystick PTZ**: drag analog thumb; pan/tilt velocity follows distance; release stops. Requests run on a single worker, ~5/sec, camera stop timeout 450ms. Actual latency depends on firmware/LAN.
- **Devices → Backup daftar kamera → Ekspor/Pulihkan**: JSON backups include saved camera names, RTSP/ONVIF addresses, not credentials. Android SAF chooses the output/input file. Passwords need re-entry after reinstall.
- **Settings → Bahasa / Language**: Indonesian/English persists, collapsible sections reduce UI clutter.
- **Live → Resolusi & profil video**: read-only ONVIF Media queries; shows observed profile count/resolutions. Choosing a verified StreamUri switches app playback only. No encoder writes.
- **Live → Rekaman microSD kamera** (or Clips): ONVIF Profile G only, if camera exposes recording and replay APIs. No direct proprietary microSD filesystem access.
- **Settings → Privasi & kompatibilitas**: complete library/tool disclosure in bilingual expandable panel.
- All existing features, firmware, OTA updater, encrypted camera vault, and private LAN handling retained.
- Full notes: [CHANGELOG.md](CHANGELOG.md).

## v0.12.0 · Two separately installable editions

| Release | Android ID | Layout |
|---|---|---|
| **GARDA CCTV FOLD edition** | `org.foldview.cctv` (original app ID) | Cover display bottom navigation, unfolded >=680dp navigation rail and wider Dual Vision |
| **GARDA CCTV Standard edition** | `org.garda.cctv.standard` | Compact single-column phone shell with bottom navigation; camera grid stacks on narrow widths |

Both editions use **one shared camera engine** and identical security/ONVIF/RTSP/OTA feature set. The Standard edition is a separate app, so its encrypted profiles **cannot access Fold's Android Keystore vault**. From Fold: `Devices > Backup daftar kamera > Ekspor`; from Standard: `Devices > Pulihkan`. **Passwords are not exported** and must be entered again.

Dark/Light palette, all device cards, native CCTV Canvas illustrations, buttons (>=48dp touch height), bottom navigation and metrics adapted to small displays. Root safe-area padding protects against Android system three-button/gesture overlap without nested insets. CI tests prove code builds and chosen contrast ratios, **not real hardware screenshot alignment**.

### Build both APKs
```shell
gradle :app:testFoldDebugUnitTest :app:testStandardDebugUnitTest
gradle :app:assembleFoldDebug :app:assembleStandardDebug
```

The resulting debug APKs appear in `app/build/outputs/apk/fold/debug/` and `app/build/outputs/apk/standard/debug/`.

### Distribution / OTA
The update-server `--package-name` flag selects the edition, and must match the installed APK's package ID:
- Fold (default): `--package-name org.foldview.cctv`.
- Standard: `--package-name org.garda.cctv.standard`.
Deploy one update manifest per edition (separate server endpoints/ports if both run concurrently). The **debug signing certificate changes across GitHub Actions runs**; a stable privately owned signing certificate is required for seamless in-place OTA.

## v0.12.1 — PTZ joystick recovery hotfix

Previously, Live screen vertical scrolling could consume the drag gesture before the joystick started moving. This version handles pointer-down immediately at the initial event pass, avoids touch-slop interference and keeps PTZ network calls off the UI thread. A camera reporting an ONVIF SOAP Fault under HTTP 200 now displays the fault, not an implicit success.

For confirmed GARDA native firmware the joystick offers **ONVIF / GARDA** backend options. The GARDA backend uses bounded vendor REST directional pulses; the ONVIF backend uses ContinuousMove, PT1S timeout, and explicit Stop. Both require actual camera motor support. The repository's earlier experimental FH8852V201 ONVIF daemon explicitly has **no physical PTZ driver**, so firmware-side motor control may still need work. See [native daemon limitations](../../cctv-firmware/fh8852v201-onvif/README.md).

**Manual validation**: on a physically motorized authorized camera select Live > PTZ > ONVIF, touch and drag; try the GARDA option only if the native server status is detected. Read status/error under the joystick, test STOP, hold and release. If it reports `PTZConfiguration missing` or `ActionNotSupported`, the camera firmware/server does not currently expose a working ONVIF PTZ command path. No HTTP response alone proves physical movement.

CI build and synthetic SOAP/gesture tests do not constitute motor movement validation. The new APKs use ephemeral debug signing and may not overwrite installed APKs unless certificate matches. Back up profiles before uninstalling.

## v0.12.2: PTZ gesture/firmware diagnosis
The joystick now captures first-touch, scales small finger movement with a visible sensitivity slider, and preserves one queued command on a short tap before releasing STOP. The four directional buttons directly test one-shot physical control independently of drag gesture detection. They use ONVIF RelativeMove when on the ONVIF backend and bounded vendor pulses when the device advertises the experimental GARDA backend.

If the on-screen text says **"Sentuhan joystick terbaca"**, Android is receiving your finger input. If the camera still does not move, inspect the status/fault and test directional buttons. **"PTZConfiguration missing"** or **"PTZ service unavailable"** means the camera is currently not exposing standards-compliant motor control. A successful HTTP 200 or returned vendor JSON is not proof that a physical motor moved.

The early [FH8852V201 daemon source](../../cctv-firmware/fh8852v201-onvif/README.md) explicitly lacks motor PTZ support. In that case a new APK cannot implement missing camera motor drivers. An authorized live firmware-side PTZ implementation and camera-specific physical validation are needed.

Only camera-name/address backup is portable; passwords are never exported. All APK builds are archived to the GARDA Drive release folder. The Google Drive backup is private; do not distribute the app or credentials publicly.

## Repository migration — 16 November 2026
Development now lives in private `adith92/GardaWEB`, at this same path. See [development entrypoint](../../README.md) and [migration record](../../../docs/GARDA_CCTV_MIGRATION_2026-11-16.md). Historical debug artifacts remain in docs Actions/Drive; future builds use GardaWEB Actions.
