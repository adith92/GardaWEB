"""No secrets in the repository: RTSP URLs are read from environment variables."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CameraConfig:
    id: str
    url: str
    location: str
    sample_fps: float = 2.0


@dataclass(frozen=True)
class GardaConfig:
    cameras: tuple[CameraConfig, ...]
    data_dir: Path
    retention_days: int = 90
    motion_min_fraction: float = 0.016
    plate_min_confidence: float = 0.70
    face_model: Path | None = None
    enable_plates: bool = True
    recognition_model: Path | None = None
    recognition_threshold: float = 0.55


def load_config(path: str | Path) -> GardaConfig:
    source = Path(path).resolve()
    data = json.loads(source.read_text(encoding="utf-8"))
    cameras = []
    for item in data.get("cameras", []):
        camera_id = str(item["id"])
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", camera_id):
            raise ValueError("Camera ID must use letters, numbers, underscore or hyphen")
        env_key = str(item.get("rtsp_env", ""))
        if not re.fullmatch(r"[A-Z][A-Z0-9_]{2,80}", env_key):
            raise ValueError(f"{camera_id}: rtsp_env is missing/invalid")
        url = os.environ.get(env_key, "")
        if not url.startswith(("rtsp://", "rtsps://")):
            raise ValueError(f"{camera_id}: set {env_key} to a valid RTSP URL")
        fps = float(item.get("sample_fps", 2.0))
        if not 0.2 <= fps <= 5:
            raise ValueError("sample_fps must be between 0.2 and 5")
        cameras.append(CameraConfig(camera_id, url, str(item.get("location", camera_id)), fps))
    if not 1 <= len(cameras) <= 2:
        raise ValueError("Stage 1 supports only 1-2 camera streams. Multi-site pool comes later.")
    if len({c.id for c in cameras}) != len(cameras):
        raise ValueError("Duplicate camera ID")
    data_dir = Path(os.environ.get("GARDA_AI_DATA_DIR", data.get("data_dir", "./var"))).expanduser().resolve()
    if data_dir == Path("/"):
        raise ValueError("Do not use the filesystem root as the analytics data directory")
    days = int(data.get("retention_days", 90))
    if not 1 <= days <= 365:
        raise ValueError("retention_days must be 1..365")
    fraction = float(data.get("motion_min_fraction", 0.016))
    if not 0.001 <= fraction <= 0.3:
        raise ValueError("motion_min_fraction must be 0.001..0.3")
    confidence = float(data.get("plate_min_confidence", 0.70))
    if not 0.4 <= confidence <= 1:
        raise ValueError("plate_min_confidence must be 0.4..1")
    model = os.environ.get("GARDA_FACE_YUNET_MODEL", "")
    recognition = os.environ.get("GARDA_FACE_SFACE_MODEL", "")
    threshold = float(data.get("face_match_threshold", 0.55))
    if not .36 <= threshold <= .90:
        raise ValueError("face_match_threshold must be 0.36..0.90")
    if recognition and not model:
        raise ValueError("GARDA_FACE_YUNET_MODEL is required alongside GARDA_FACE_SFACE_MODEL")
    return GardaConfig(tuple(cameras), data_dir, days, fraction, confidence,
                       Path(model).expanduser().resolve() if model else None,
                       bool(data.get("enable_plates", True)),
                       Path(recognition).expanduser().resolve() if recognition else None,
                       threshold)
