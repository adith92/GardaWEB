"""Manual ONVIF optical zoom probe/control for authorized cameras.

No autofocus, no automatic face tracking, no vendor binary protocol guessing.
A returned SOAP success is only an ACK, never proof of physical lens movement.
"""
from __future__ import annotations

import ipaddress
import socket
import time


def validate_host(host: str) -> str:
    """Allow only private/loopback literal IPs in the first LAN development phase."""
    try:
        ip = ipaddress.ip_address(host)
    except ValueError as exc:
        raise ValueError("Use a private literal camera IPv4/IPv6 address") from exc
    if not (ip.is_private or ip.is_loopback):
        raise ValueError("Camera IP must be private or loopback")
    if ip.is_multicast or ip.is_unspecified or ip.is_link_local:
        raise ValueError("Unsupported camera host")
    return str(ip)


class ZoomController:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = validate_host(host)
        if not 1 <= port <= 65535:
            raise ValueError("Invalid port")
        try:
            from onvif import ONVIFCamera
        except ImportError as exc:
            raise RuntimeError("Install optional onvif-zeep: pip install -r requirements-ptz.txt") from exc
        # onvif-zeep SDK and the WSDL package are optional and kept independent
        # from the high-throughput RTSP/ANPR camera capture.
        camera = ONVIFCamera(self.host, port, username, password, no_cache=True)
        media = camera.create_media_service()
        profiles = list(media.GetProfiles())
        valid = [profile for profile in profiles
                 if getattr(profile, "PTZConfiguration", None) is not None]
        if not valid:
            raise RuntimeError("No ONVIF profile with PTZConfiguration")
        self.profile = valid[0]
        self.ptz = camera.create_ptz_service()

    def inspect(self) -> dict[str, object]:
        cfg = getattr(self.profile, "PTZConfiguration", None)
        token = getattr(cfg, "token", None)
        if not token:
            return {"profile": str(self.profile.token), "zoom_supported": False}
        options = self.ptz.GetConfigurationOptions({"ConfigurationToken": token})
        spaces = getattr(options, "Spaces", None)
        ranges = getattr(spaces, "ContinuousZoomVelocitySpace", []) if spaces else []
        supported = bool(ranges)
        return {
            "profile": str(self.profile.token),
            "zoom_supported": supported,
            "mode": "ONVIF ContinuousMove Zoom",
            "ack_is_not_physical_movement": True,
        }

    def pulse(self, direction: str, duration: float = 0.35, speed: float = 0.5) -> dict:
        if direction not in ("in", "out"):
            raise ValueError("direction must be in/out")
        if not 0.10 <= duration <= 1.5:
            raise ValueError("duration must be 0.10..1.5 seconds")
        if not 0.1 <= speed <= 1:
            raise ValueError("speed must be 0.1..1.0")
        if not self.inspect()["zoom_supported"]:
            raise RuntimeError("Camera does not advertise ONVIF continuous zoom")
        value = speed if direction == "in" else -speed
        try:
            request = self.ptz.create_type("ContinuousMove")
            request.ProfileToken = self.profile.token
            request.Velocity = {"Zoom": {"x": value}}
            request.Timeout = f"PT{max(1, int(duration + .99))}S"
            self.ptz.ContinuousMove(request)
            time.sleep(duration)
            return {"acknowledged": True, "physical_zoom_verified": False,
                    "direction": direction, "duration_seconds": duration}
        finally:
            # Fail-safe stop, including timeouts / SOAP errors / keyboard interrupts.
            stop = self.ptz.create_type("Stop")
            stop.ProfileToken = self.profile.token
            stop.Zoom = True
            stop.PanTilt = False
            self.ptz.Stop(stop)
