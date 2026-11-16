# GARDA Engineering Handoff | 2026-11-10

## 1. Evidence and scope
Based on user-supplied `GARDA_Android_Project.zip`, `GARDA_Android_SourceCode_For_ChatGPT.md`, and 5 desktop Python files. The user reports a deployed FH8852V201 daemon and live hardware; that claim is noted as **user/Antigravity-reported**, not independently tested by this review. This handoff statically inspected the uploaded code; no remote Windows computer, camera LAN, actual ARM executable, `RUN.BAT`, credentials, camera screenshots, or flash dumps were available here.

## 2. System topology
```
                Local camera LAN / VPN
                        |
      +-----------------+-----------------+
      |                                   |
GARDA Desktop (Windows Python)       GARDA Mobile (Android Kotlin)
PySide6 + OpenCV/FFmpeg              ViewBinding + ViewModel + Media3
ONVIF Zeep / REST / Native PTZ       ONVIF discovery + REST + Native PTZ
      |                                   |
      +---------------+-------------------+
                      |
        FH8852V201 camera (owner-reported)
         :8899 HTTP REST + ONVIF SOAP
         :3702 UDP WS-Discovery
         :7777 TCP binary PTZ commands
         :1234 RTSP main lens, H264/AAC
         :1235 RTSP secondary lens, H264
```

## 3. Source-of-truth protocol contracts
| Interface | Endpoint | Purpose | Evidence/limitations |
|---|---|---|---|
| Camera status | `http://<IP>:8899/api/status` | JSON health, uptime, RAM, VPU/dual_lens | Consumed in both apps; runtime not verified |
| PTZ REST | `POST http://<IP>:8899/api/ptz?dir=left|right|up|down|stop|center` | Motor motion | Device-specific, not standardized ONVIF PTZ |
| LED REST | `POST http://<IP>:8899/api/led?mode=white_on|white_off|ir_on|ir_off|ircut_day|ircut_night` | Spotlight/IR/IR-cut | Depends on custom daemon/GPIO behavior |
| RTSP | `rtsp://<IP>:1234/`, `rtsp://<IP>:1235/` | Two lenses, transport TCP preferred | Hardware decode/latency unverified in review |
| ONVIF | `http://<IP>:8899/onvif/device_service` | Device/Media/PTZ via SOAP | Profile/credential compatibility requires live verification |
| Discovery | UDP 3702 multicast `239.255.255.250` | WS-Discovery | Local-LAN multicast restrictions apply |
| Native PTZ | TCP `<IP>:7777` | 32-byte binary packet, header `0xAA`, opcodes `0x40..0x49` | Private protocol; require ACK check and motor safety |
| Telnet root | TCP `<IP>:23` | Desktop legacy hardware fallback | **Critical security exposure**; should be removed from control workflow |

Camera IP may change; examples use `192.168.18.249` (reported alias .250). Do not hardcode the IP as a universal factory address.

## 4. Desktop application
- Entry: `desktop/app.py` launches Qt `GardaMainWindow` with title **GARDA Desktop**. Dual camera widgets, telemetry polling every 3 seconds, PTZ buttons, IR/spotlight settings, tracking/cruise controls, snapshot and MP4 recording are coded.
- Video decode pipeline: `desktop/camera_stream.py` uses `cv2.VideoCapture` with FFmpeg RTSP TCP, converts BGR->RGB into Qt image. It writes MP4 using re-encoding (`mp4v`), not lossless RTSP packet remux. Audio is not recorded by this code.
- Network: `desktop/srihome_client.py` REST requests and proprietary PTZ TCP packets. `desktop/onvif_controller.py` is separate ONVIF-zeep client.
- Settings: `desktop/config.py` JSON config stored beside code. The actual `camera_config.json` and local `RUN.BAT` were not uploaded.

## 5. Android application
- App: `mobile/android/` (`com.garda.camera`, versionName 1.0.0, Kotlin/Android Views, target SDK 34, min SDK 24).
- `CameraViewModel` provides telemetry polling, discovery, PTZ, IR/LED, cruise/tracking state.
- `RtspPlayerManager` uses Media3 RTSP with `setForceUseRtpTcp(true)`; discovery is WS-Discovery, not full subnet scanning.
- The original ZIP had invalid XML at `activity_main.xml` lines 406 and 472 (unescaped `&` in two `android:text` values); **corrected only in this normalized baseline** to use `&amp;`. Original ZIP is retained separately on Drive for audit.
- Original ZIP lacked Gradle wrapper executable and wrapper JAR, so out-of-box CLI build cannot be assumed. No APK build or Fold7 smoke test was performed in this handoff.
- Android project should not silently replace `projects/foldview-cctv/android/`: it has a different application ID and architecture, so merging requires a separate migration plan.

## 6. Testing performed in this handoff
- ZIP central directory CRC: PASS.
- Desktop Python syntax: 5 of 5 PASS (static AST parsing, NOT runtime import test).
- All Android XML resources: original layout had 2 unescaped ampersands in one malformed XML file; normalized baseline after the minimal correction: all XML parse successfully.
- Java/Kotlin compilation, APK packaging, Windows `RUN.BAT`, live camera ONVIF/RTSP/PTZ, permanent flash/reboot: **NOT TESTED HERE**.

## 7. Proposed next iteration
**P0** Secure control path: authenticate/authorize REST/PTZ; disable passwordless Telnet management; restrict camera VLAN and per-device permissions. Fix false-positive success reporting. Use explicit connect timeouts and safe PTZ stop/watchdog. Disable secrets in logs.

**P1** Reproducible builds & tests: restore validated Gradle wrapper; compile Android in CI; add Python requirements/lockfile and startup script after inspecting real RUN.BAT; create health check + protocol mock test suite.

**P2** Camera management: multi-device registry, credential vault, confirm ONVIF capabilities and stream URI; scan candidates, auto-connect only after real RTSP handshake; consistent camera identity and persistence.

**P3** Video features: reliable RTSP reconnect; validated local recording resolution, correct frame sizing, audio requirements, long-running DVR/NAS integration and playback timeline.

**P4** Integrate GARDA Mobile and FOLDVIEW deliberately: maintain separate packages until UX/features are compared, then select an explicit migration rather than overwriting one app.

## 8. Canonical project location
- GitHub: private `adith92/GardaWEB`, path `projects/garda/` (migrated 2026-11-16; original history remains in docs).
- Google Drive: `ChatGPT/GARDA - Project Source & Documentation/`.
- Uploaded original Android ZIP is preserved in Drive, normalized source in GitHub; desktop files mirrored to both.
