# GARDA Security and Reliability Review | 2026-11-10

This is a **static review** of supplied source files, not a penetration test or live device certification.

| Priority | Finding | Evidence in uploaded files | Required action |
|---|---|---|---|
| CRITICAL | Desktop offers arbitrary shell command execution over root Telnet TCP/23 without password, and uses it to control lights | `srihome_client.py: execute_shell_cmd`, `set_white_light`, `set_ir_light` | Remove shell fallback from normal GUI; segregate camera; implement authenticated safe daemon API and eliminate passwordless root |
| CRITICAL | Camera-specific control APIs appear unauthenticated and use cleartext HTTP / TCP | `GardaApiClient.kt`, `srihome_client.py` | Authenticate and authorize PTZ/LED; require secure LAN/VPN; allowlist origins/clients; test rejection of unauthenticated commands |
| HIGH | PTZ TCP client can return success when ACK is present but not the expected `0xBB` | `srihome_client.py:send_ptz_packet` | Return failure on wrong ACK; validate frame length and opcode; bounded motion/Stop |
| HIGH | Light toggles sometimes return success even when REST/Telnet requests fail | `srihome_client.py:set_white_light/set_ir_light` | Propagate actual results and reflect verified state |
| HIGH | User config is JSON on disk; default username is admin and password field exists | `config.py` | Keep credentials out of repositories; encrypted credential vault; permission-restricted config; no secrets in logs |
| HIGH | Android manifest opts into backups and global cleartext traffic | `mobile/android/app/src/main/AndroidManifest.xml` | Explicitly limit backup of camera secrets, restrict cleartext to justified local IPs with scoped network security config |
| MEDIUM | Android WS-Discovery trusts sender IP without verifying ONVIF XML/probe correlation | `OnvifDiscovery.kt` | Parse SOAP securely, correlate probes and validate local-range/endpoint; multicast lock on Wi-Fi |
| MEDIUM | Desktop RTSP URL is logged, potentially leaking credentials in URI | `camera_stream.py` logging | Mask username/password and URL query when logging |
| MEDIUM | Desktop VideoWriter uses default resolution and doesn't confirm `isOpened()` | `camera_stream.py` | Capture actual stream dimensions/FPS and verify file writer before reporting recording started |
| MEDIUM | Android media player calls success callback immediately on `prepare`, not decoder READY state | `RtspPlayerManager.kt` | Use Player.Listener for isPlaying/error states and timeout/retry |
| MEDIUM | Windows runner (`RUN.BAT`) not provided and Android wrapper JAR/scripts absent | Uploaded file inventory | Capture repeatable launch scripts and add CI build/test pipeline |
| MEDIUM | Dual-lens vendor daemon and ARM firmware not included in source handoff | Missing in uploads | Preserve separate firmware source/binary and verified MTD backups OFF GitHub in secure storage |

## Guardrails
- Never place raw flash dumps in GitHub, including a private repo, without a dedicated encrypted archive and access policy; backup image can include secrets and calibration data.
- A successful ONVIF REST status response is not evidence that all PTZ/LED/RTSP capabilities work.
- No blind firmware flashing; image-to-board match, two off-device MTD reads and physical recovery path are still mandatory.
- Lock down existing unauthenticated Telnet/FTP interfaces before giving access to broader LAN devices or remote VPN users.
- Do not publish static passwords, private camera UID, remote shell outputs or customer video in source repositories or public issue comments.
