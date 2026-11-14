"""ONVIF continuous zoom with automatic STOP on a bounded timeout.

Camera-specific capabilities/profiles must be tested before enabling movement.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import timedelta

from .core import Camera

_locks: dict[str, threading.Lock] = {}


def zoom(camera: Camera, speed: float, seconds: float) -> dict:
    if not camera.onvif_host or not camera.onvif_user_env or not camera.onvif_pass_env:
        raise ValueError("Camera PTZ not configured")
    if not -1 <= speed <= 1 or not 0.05 <= seconds <= 2:
        raise ValueError("Invalid zoom speed/duration")
    user, password = os.getenv(camera.onvif_user_env), os.getenv(camera.onvif_pass_env)
    if not user or not password:
        raise ValueError("ONVIF credentials missing")
    # Optional installed extra: pip install onvif-zeep. Vendor WSDL availability varies.
    from onvif import ONVIFCamera  # type: ignore

    lock = _locks.setdefault(camera.id, threading.Lock())
    if not lock.acquire(blocking=False):
        raise RuntimeError("Camera PTZ already in use")
    try:
        device = ONVIFCamera(camera.onvif_host, camera.onvif_port, user, password)
        media = device.create_media_service()
        ptz = device.create_ptz_service()
        profiles = media.GetProfiles()
        token = camera.ptz_profile_token or next((p.token for p in profiles if getattr(p, "PTZConfiguration", None)), None)
        if not token:
            raise RuntimeError("No PTZ-capable media profile")
        request = ptz.create_type("ContinuousMove")
        request.ProfileToken = token
        request.Velocity = {"Zoom": {"x": speed}}
        # ONVIF device-side timeout limits motion even if host loses connection.
        request.Timeout = timedelta(seconds=seconds)
        try:
            ptz.ContinuousMove(request)
            time.sleep(seconds)
        finally:
            # Attempt STOP even if network fails after the camera received move.
            # Operator must check physical response if Stop itself fails.
            ptz.Stop({"ProfileToken": token, "PanTilt": False, "Zoom": True})
        return {"camera_id": camera.id, "zoom_speed": speed, "seconds": seconds, "stopped": True}
    finally:
        lock.release()
