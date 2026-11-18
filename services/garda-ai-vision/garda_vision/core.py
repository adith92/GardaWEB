"""Platform-neutral types, config and conservative Indonesian plate parsing."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Candidate only: must be manually verified, never a definitive identity.
PLATE_RE = re.compile(r"\b([A-Z]{1,2})\s*([0-9]{1,4})\s*([A-Z]{1,3})\b")


def plate_candidates(raw: str) -> list[str]:
    """Find plausible standard Indonesian plates in OCR text; does not validate registration."""
    normalized = re.sub(r"[^A-Z0-9]+", " ", raw.upper()).strip()
    results = []
    for text in (normalized, normalized.replace(" ", "")):
        for match in PLATE_RE.finditer(text):
            plate = " ".join(match.groups())
            if plate not in results:
                results.append(plate)
    return results


@dataclass(frozen=True)
class Camera:
    id: str
    site_id: str
    rtsp_env: str
    onvif_host: str | None = None
    onvif_port: int = 80
    onvif_user_env: str | None = None
    onvif_pass_env: str | None = None
    ptz_profile_token: str | None = None

    @property
    def rtsp_url(self) -> str | None:
        return os.getenv(self.rtsp_env)

    def public(self) -> dict[str, Any]:
        return {"id": self.id, "site_id": self.site_id,
                "rtsp_configured": bool(self.rtsp_url), "ptz_configured": bool(self.onvif_host)}


def load_cameras(path: str | Path) -> dict[str, Camera]:
    entries = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(entries, list) or len(entries) > 49:
        raise ValueError("Camera config must be a list of <=49 entries in development")
    cameras: dict[str, Camera] = {}
    for item in entries:
        camera = Camera(**item)
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", camera.id):
            raise ValueError("Invalid camera ID")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", camera.site_id):
            raise ValueError("Invalid site ID")
        if not camera.rtsp_env.startswith("GARDA_CAM"):
            raise ValueError("RTSP must be referenced by GARDA_CAM* environment variable")
        if not 1 <= camera.onvif_port <= 65535:
            raise ValueError("Invalid ONVIF port")
        if camera.id in cameras:
            raise ValueError("Duplicate camera ID")
        cameras[camera.id] = camera
    return cameras
