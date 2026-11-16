**Repository migration — 16 November 2026:** This baseline now lives in private `adith92/GardaWEB` under `projects/garda`. Continue development from [projects/README.md](../README.md). Historical handoff manifest is retained as originally supplied; current source provenance is in [migration manifest](../../docs/GARDA_CCTV_MIGRATION_MANIFEST_2026-11-16.json).

# GARDA Project | Baseline 2026-11-10

## GARDA Unified Source, Windows 11 → Linux, FOLD + Standard (2026-11-14)

The complete audited handoff source is documented in [UNIFIED_HANDOFF_2026-11-14.md](ai-core/docs/UNIFIED_HANDOFF_2026-11-14.md).
Existing AI Core stage 1 remains; the next branch adds opt-in SFace recognition, encrypted biometric enrollment, Windows PowerShell install/start scripts, manual ONVIF optical zoom, a PySide6 AI event/evidence tab, and Kotlin Compose AI event/evidence panels shared by both FOLD and Standard Android flavors.

The ClearCam repository is an architectural reference only. No GPL-3.0 ClearCam code was copied.
This is source for audit/development, **not** proof of motor zoom, Indonesian LPR accuracy or a physically tested Android APK.

This repository directory is the **canonical handoff baseline** for development of GARDA Desktop and GARDA Mobile after user-provided files from Antigravity. It is NOT a verified production release or a complete embedded firmware distribution.

## Applications
- **GARDA Desktop**: PySide6 desktop UI (`desktop/app.py`), OpenCV/FFmpeg RTSP playback (`desktop/camera_stream.py`), ONVIF via `onvif_controller.py`, direct camera REST and PTZ via `srihome_client.py`. Local Windows `RUN.BAT` is **not included** in uploaded files, and Windows runtime has not been tested from this handoff.
- **GARDA Mobile**: Android native XML/ViewBinding + ViewModel + Media3 RTSP. Application ID `com.garda.camera`, version `1.0.0`, target SDK 34. Source was extracted from the uploaded ZIP, normalized to POSIX paths, with **two documented XML encoding fixes**.
- **Camera firmware**: A user-reported custom FH8852V201 ONVIF/REST daemon provides ONVIF 8899, RTSP 1234/1235, PTZ 7777. **The actual running ARM daemon, full 8 MB flash backup, and proof of reboot persistence were not included in these attachments.** Do not claim those binaries are part of this code baseline.
- **FOLDVIEW CCTV** remains a separate Android project at `projects/foldview-cctv/android/` and has NOT been overwritten by GARDA Mobile.

## Read next
- `docs/ARCHITECTURE_AND_HANDOFF.md` — hardware, protocol matrix, project structure, setup, requirements and next milestones.
- `docs/SECURITY_REVIEW.md` — mandatory findings and remediation priorities.
- `docs/FILE_MANIFEST_SHA256.txt` — integrity hashes for normalized source files.

## Reproducibility
Android ZIP imported from user upload; local.properties excluded (contains Windows SDK path). Android XML lines 406 and 472 corrected by converting unescaped `&` to `&amp;`. All other ZIP source bytes were decoded and retained unchanged. Python source files retained unchanged. Files are informational until a real Windows/Android build and hardware smoke test are performed.

## Build requirements (based on uploaded source)
- **Android:** Android Studio or Gradle 8.4, JDK 17, AGP 8.2.2, Kotlin 1.9.22, Android SDK 34; Media3 1.2.1. The provided ZIP contains `gradle-wrapper.properties` but **does not include `gradlew`, `gradlew.bat`, or `gradle-wrapper.jar`**. Recreate a wrapper with trusted Gradle or use a locally installed Gradle 8.4. Avoid blindly upgrading all dependencies until baseline compilation is verified.
- **Desktop:** Python 3 with `PySide6`, `opencv-python`, `numpy`; optional `onvif-zeep` for the standalone ONVIF controller. Reproduce actual `RUN.BAT` separately; it was not provided. Ensure FFmpeg-powered OpenCV VideoCapture is available.

Do not check in raw firmware dumps, credentials, camera_config.json, personal recordings, snapshots, or `.env` files.


## Fold edition UI design exploration (2026-11-10)
The requested next-stage Android design name is **GARDA CCTV FOLD edition**.
The 10 alternative concept boards (20 light/dark versions), a standalone interactive HTML mockup, dual-lens fold-open previews, and the native Kotlin Compose implementation blueprint are in [design/fold-edition-2026-11-10](design/fold-edition-2026-11-10/).
**Mockups only:** No APK name, package ID, camera firmware, or current FOLDVIEW source changed in this design-only commit. Select a concept before implementing the native Android shell.


## GARDA AI Core stage 1 (2026-11-10)
The new on-premises detector and event-storage MVP lives in [ai-core](ai-core/README.md). This is a **separate Python server module**; no change to camera firmware, GARDA Desktop or Android APK is implied. It implements motion events, per-scene face sightings with up to three photos, FastALPR license plate OCR with confirmation/dedup, SQLite WAL, local private JPEG evidence and key-protected loopback FastAPI events. Unit tests use mock detectors and synthetic frames; live camera accuracy has not been independently measured. See [AI changelog](ai-core/CHANGELOG.md) and [architecture/privacy notes](ai-core/docs/ARCHITECTURE.md).
