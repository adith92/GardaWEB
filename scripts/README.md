# Isolated ClearCam source checkout

`fetch_clearcam.ps1` (Windows) and `fetch_clearcam.sh` (Linux) clone original ClearCam into `vendor/clearcam` at verified Git commit `553be39ba6f20ce055a7418ed54636b32059b4ad` (current during development 2026-11-14). This retains upstream copyright and GPL-3.0 license and intentionally does **not** copy/relicense files into GARDA. This checkout is for reference, license inspection and later separate-process execution on supported platforms only.

On Windows, **do not assume** the original ClearCam server works: upstream explicitly has an unresolved FFmpeg issue. The Windows-first usable part is GARDA's standalone FastAPI lab; ClearCam interoperability is through an authenticated notification relay.

Do not commit downloaded `vendor` content or model weights to the GARDA proprietary repository.
