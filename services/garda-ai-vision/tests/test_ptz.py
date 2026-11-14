import sys
from types import SimpleNamespace
import pytest
from garda_vision.core import Camera
from garda_vision.ptz import zoom


def test_ptz_zoom_requires_credentials(monkeypatch):
    camera = Camera("c", "LAB", "GARDA_CAM01_RTSP", "192.0.2.1", 80, "PTZ_USER", "PTZ_PASS")
    with pytest.raises(ValueError):
        zoom(camera, 0.5, 0.4)


def test_ptz_always_stops_on_move_failure(monkeypatch):
    seen = []
    class FakePTZ:
        def create_type(self, name):
            return SimpleNamespace(ProfileToken=None, Velocity=None)
        def ContinuousMove(self, request):
            seen.append("move")
            raise RuntimeError("Link lost after moving")
        def Stop(self, data):
            seen.append("stop")
    class FakeCamera:
        def __init__(self, *args):
            pass
        def create_media_service(self):
            return SimpleNamespace(GetProfiles=lambda: [SimpleNamespace(token="profile1", PTZConfiguration=True)])
        def create_ptz_service(self):
            return FakePTZ()
    monkeypatch.setenv("PTZ_USER", "demo")
    monkeypatch.setenv("PTZ_PASS", "demo")
    monkeypatch.setitem(sys.modules, "onvif", SimpleNamespace(ONVIFCamera=FakeCamera))
    camera = Camera("c", "LAB", "GARDA_CAM01_RTSP", "192.0.2.1", 80, "PTZ_USER", "PTZ_PASS")
    with pytest.raises(RuntimeError):
        zoom(camera, 0.5, 0.05)
    assert seen == ["move", "stop"]
