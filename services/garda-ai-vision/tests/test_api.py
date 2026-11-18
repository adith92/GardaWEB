import os
from tempfile import TemporaryDirectory
from pathlib import Path
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from garda_vision.core import Camera
from garda_vision.storage import Store
from garda_vision.api import build_app


class FakeVision:
    enable_face_id = False
    def decode(self, raw):
        return raw
    def analyze(self, frame, enrolled=None):
        return {"face_count": 0, "plates": [{"plate": "B 1234 XYZ", "confidence": 0.5, "review_required": True}], "face_candidates": []}


def test_rbac_plate_redaction_and_notifications(monkeypatch):
    for role in ("VIEWER", "OPERATOR", "ADMIN"):
        monkeypatch.setenv(f"GARDA_{role}_TOKEN", role.lower() * 12)
    monkeypatch.setenv("GARDA_CLEARCAM_TOKEN", "clearcam" * 6)
    with TemporaryDirectory() as d:
        store = Store(str(Path(d) / "test.sqlite"), Fernet.generate_key().decode())
        app = build_app({"LAB-CAM-01": Camera("LAB-CAM-01", "LAB", "GARDA_CAM01_RTSP")}, store, FakeVision())
        with TestClient(app) as client:
            assert client.get("/api/v1/cameras").status_code == 401
            viewer = {"Authorization": "Bearer " + os.environ["GARDA_VIEWER_TOKEN"]}
            operator = {"Authorization": "Bearer " + os.environ["GARDA_OPERATOR_TOKEN"]}
            admin = {"Authorization": "Bearer " + os.environ["GARDA_ADMIN_TOKEN"]}
            assert client.post("/api/v1/cameras/LAB-CAM-01/start", headers=viewer).status_code == 403
            assert client.post("/api/v1/cameras/LAB-CAM-01/zoom", json={"speed": 1, "seconds": 1}, headers=viewer).status_code == 403
            assert client.post("/api/v1/faces/enroll", headers=admin, data={"person_id": "test_subject", "consent_reference": "AUTH-LAB-123"}, files={"image": ("test.jpg", b"test", "image/jpeg")}).status_code == 403
            result = client.post("/api/v1/cameras/LAB-CAM-01/analyze", headers=operator, files={"image": ("test.jpg", b"fake-jpeg", "image/jpeg")})
            assert result.status_code == 200
            assert result.json()["plates"][0]["review_required"] is True
            ev = client.get("/api/v1/events", headers=viewer).json()
            assert ev[0]["data"] == {"redacted": True, "review_required": True}
            ev_admin = client.get("/api/v1/events", headers=admin).json()
            assert ev_admin[0]["data"]["plates"][0]["plate"] == "B 1234 XYZ"
            cc = {"Authorization": "Bearer " + os.environ["GARDA_CLEARCAM_TOKEN"]}
            assert client.post("/api/v1/clearcam/notification?camera=LAB-CAM-01", headers=cc, data={"text": "Detected motion"}).status_code == 200
            assert client.post("/api/v1/clearcam/notification?camera=LAB-CAM-01", data={"text": "Detected motion"}).status_code == 401
        store.close()
