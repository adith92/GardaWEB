# GARDA third-party notices (planned Tier 1 toolchain)

This file records the open-source components evaluated for the on-premise video stack. No external service source code is copied into the GARDA frontend by the GUI redesign.

| Component | Repository | License | Intended use |
|---|---|---|---|
| MediaMTX | https://github.com/bluenviron/mediamtx | MIT | RTSP/RTSPS, HLS, WebRTC and LAN relay |
| go2rtc | https://github.com/AlexxIT/go2rtc | MIT | Optional stream compatibility bridge |
| Frigate | https://github.com/blakeblackshear/frigate | MIT repository | Optional NVR/object detection benchmark |
| agsh/onvif | https://github.com/agsh/onvif | MIT | Backend ONVIF discovery/control adapter |
| CompreFace | https://github.com/exadel-inc/CompreFace | Apache-2.0 | T2/add-on face API evaluation |
| face_recognition | https://github.com/ageitgey/face_recognition | MIT | Prototype face worker evaluation |
| OpenALPR | https://github.com/openalpr/openalpr | AGPL-3.0 | ANPR candidate; distribution review required |

Before any production distribution, pin an exact commit/tag, preserve each upstream LICENSE and NOTICE file, inventory transitive dependencies and model/dataset licenses, and have the selected distribution model reviewed. T1 Basic must not enable face identity matching.
