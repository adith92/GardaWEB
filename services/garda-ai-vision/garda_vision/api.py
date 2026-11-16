"""Local-only FastAPI API. This is a development prototype, not a hardened VMS."""

import hmac
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from .core import Camera, load_cameras
from .storage import Store
from .vision import Vision
from .worker import Workers
from .ptz import zoom
from .scanner import ScanManager, network_interfaces, scan_network

MAX_UPLOAD = 8 * 1024 * 1024
security = HTTPBearer(auto_error=False)


def build_app(cameras: dict[str, Camera] | None = None, store: Store | None = None, vision: Vision | None = None, scan_engine=None) -> FastAPI:
    cameras = cameras if cameras is not None else load_cameras(os.getenv("GARDA_CAMERAS_FILE", "cameras.example.json"))
    roles = {role: os.getenv(f"GARDA_{role.upper()}_TOKEN", "") for role in ("viewer", "operator", "admin")}
    if not all(len(token) >= 24 for token in roles.values()) or len(set(roles.values())) != 3:
        raise RuntimeError("Set three unique GARDA_*_TOKEN values (>=24 chars) before starting")
    owned_store = store is None
    if store is None:
        store = Store(os.getenv("GARDA_DB_PATH", "data/garda-vision.sqlite3"), os.getenv("GARDA_DATA_KEY", ""))
    vision = vision or Vision(os.getenv("GARDA_FACE_ONNX"), os.getenv("GARDA_FACE_ID_ENABLED") == "1")
    workers = Workers(cameras, vision, store)
    scanner = ScanManager(store, scanner=scan_engine or scan_network)
    enable_face = os.getenv("GARDA_FACE_ID_ENABLED") == "1" and os.getenv("GARDA_CONTRACT_BUNDLE") == "pusada"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        workers.close()
        scanner_stopped = scanner.close()
        if owned_store and scanner_stopped:
            store.close()

    app = FastAPI(title="GARDA AI Vision LAB", version="0.1.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"], allow_methods=["GET", "POST", "DELETE"], allow_headers=["Authorization", "Content-Type"])

    def actor(credential: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]) -> str:
        token = credential.credentials if credential and credential.scheme.lower() == "bearer" else ""
        for role, secret in roles.items():
            if hmac.compare_digest(token, secret):
                return role
        raise HTTPException(401, "Valid bearer token required")

    def require(*allowed: str):
        def dependency(role: str = Depends(actor)):
            if role not in allowed:
                raise HTTPException(403, "Role not authorized")
            return role
        return dependency

    class NetworkScanRequest(BaseModel):
        cidr: str = Field(min_length=9, max_length=21)
        mode: Literal["quick", "extended"] = "quick"
        target_ip: str | None = Field(default=None, max_length=15)
        confirm_authorized: bool = False

    @app.get("/api/v1/network/interfaces")
    def interfaces(role: Annotated[str, Depends(require("admin"))]):
        return network_interfaces()

    @app.get("/api/v1/network/scans")
    def scan_history(role: Annotated[str, Depends(require("admin"))]):
        store.audit(role, "network_scan_history", "last_10", "ok")
        return store.scans(10)

    @app.post("/api/v1/network/scans", status_code=202)
    def scan_start(command: NetworkScanRequest, role: Annotated[str, Depends(require("admin"))]):
        if os.getenv("GARDA_NETWORK_SCAN_ENABLED", "0") != "1":
            raise HTTPException(403, "Enable GARDA_NETWORK_SCAN_ENABLED=1 for authorized local scans")
        if not command.confirm_authorized:
            raise HTTPException(422, "Explicit confirmation of network authorization required")
        try:
            scan_id = scanner.start(command.cidr, command.mode, command.target_ip)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(409, str(exc)) from exc
        store.audit(role, "network_scan_start", scan_id, "ok")
        return {"scan_id": scan_id, "status": "queued"}

    @app.get("/api/v1/network/scans/{scan_id}")
    def scan_result(scan_id: str, role: Annotated[str, Depends(require("admin"))]):
        result = store.scan(scan_id)
        if not result:
            raise HTTPException(404, "Scan not found")
        store.audit(role, "network_scan_read", scan_id, "ok")
        return result

    def camera_or_404(cid: str) -> Camera:
        if cid not in cameras:
            raise HTTPException(404, "Unknown camera")
        return cameras[cid]

    @app.get("/api/v1/health")
    def health():
        return {"status": "development", "biometrics_enabled": enable_face, "camera_count": len(cameras)}

    @app.get("/api/v1/cameras")
    def camera_list(role: Annotated[str, Depends(require("viewer", "operator", "admin"))]):
        statuses = workers.status()
        return [{**camera.public(), **statuses[camera.id]} for camera in cameras.values()]

    @app.get("/api/v1/events")
    def event_list(role: Annotated[str, Depends(require("viewer", "operator", "admin"))], limit: int = 50, site_id: str | None = None):
        if limit < 1 or limit > 200:
            raise HTTPException(400, "limit must be 1..200")
        if site_id and not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", site_id):
            raise HTTPException(400, "Bad site ID")
        records = store.events(limit, site_id)
        if role == "viewer":
            for item in records:
                item["data"] = {"redacted": True, "review_required": True}
        store.audit(role, "events_list", site_id or "all", "ok")
        return records

    @app.get("/api/v1/audit")
    def audit_log(role: Annotated[str, Depends(require("admin"))], limit: int = 50):
        return store.audit_rows(min(max(limit, 1), 200))

    @app.post("/api/v1/cameras/{cid}/start")
    def start(cid: str, role: Annotated[str, Depends(require("operator", "admin"))]):
        camera_or_404(cid)
        try:
            workers.start(cid)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc
        store.audit(role, "start_inference", cid, "ok")
        return {"camera_id": cid, "started": True}

    @app.post("/api/v1/cameras/{cid}/stop")
    def stop(cid: str, role: Annotated[str, Depends(require("operator", "admin"))]):
        camera_or_404(cid)
        workers.stop(cid)
        store.audit(role, "stop_inference", cid, "ok")
        return {"camera_id": cid, "stopped": True}

    class ZoomCommand(BaseModel):
        speed: float = Field(ge=-1, le=1)
        seconds: float = Field(ge=0.05, le=2)

    @app.post("/api/v1/cameras/{cid}/zoom")
    def camera_zoom(cid: str, cmd: ZoomCommand, role: Annotated[str, Depends(require("operator", "admin"))]):
        camera = camera_or_404(cid)
        try:
            result = zoom(camera, cmd.speed, cmd.seconds)
        except (ValueError, RuntimeError, ImportError) as exc:
            store.audit(role, "zoom", cid, "error")
            raise HTTPException(422, str(exc)) from exc
        except Exception as exc:
            store.audit(role, "zoom", cid, "error")
            raise HTTPException(502, "ONVIF PTZ command failed") from exc
        store.audit(role, "zoom", cid, "ok")
        return result

    async def read_image(upload: UploadFile) -> bytes:
        if upload.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(415, "Only JPEG/PNG allowed")
        raw = await upload.read(MAX_UPLOAD + 1)
        if not raw or len(raw) > MAX_UPLOAD:
            raise HTTPException(413, "Image missing or too large")
        return raw

    @app.post("/api/v1/cameras/{cid}/analyze")
    async def analyze(cid: str, image: UploadFile = File(...), role: str = Depends(require("operator", "admin"))):
        camera = camera_or_404(cid)
        try:
            frame = vision.decode(await read_image(image))
            result = vision.analyze(frame, store.faces() if enable_face else None)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        eid = store.event(camera.site_id, camera.id, "manual_frame_candidate", result)
        store.audit(role, "analyze_frame", cid, "ok")
        return {"event_id": eid, **result}

    @app.post("/api/v1/faces/enroll")
    async def enroll(person_id: str = Form(...), consent_reference: str = Form(...), image: UploadFile = File(...), role: str = Depends(require("admin"))):
        if not enable_face:
            raise HTTPException(403, "Biometric matching not enabled for this contract")
        if not re.fullmatch(r"[A-Za-z0-9_-]{3,64}", person_id) or len(consent_reference.strip()) < 5:
            raise HTTPException(422, "Invalid ID or authorization reference")
        try:
            frame = vision.decode(await read_image(image))
            faces = vision.faces(frame)
            if len(faces) != 1:
                raise HTTPException(422, "Exactly one detectable face required")
            x, y, w, h = faces[0]
            vector = vision.embed(frame[y:y+h, x:x+w])
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        store.enroll(person_id, vector)
        # Do not persist consent record or raw photo here; external compliance register required.
        store.audit(role, "face_enroll", person_id, "authorized_reference_verified_by_operator")
        return {"person_id": person_id, "enrolled": True, "requires_compliance_register": True}

    @app.delete("/api/v1/faces/{person_id}")
    def delete_face(person_id: str, role: Annotated[str, Depends(require("admin"))]):
        if not enable_face:
            raise HTTPException(403, "Biometric matching disabled")
        done = store.delete_face(person_id)
        store.audit(role, "face_delete", person_id, "ok" if done else "not_found")
        return {"deleted": done}

    @app.post("/api/v1/clearcam/notification")
    async def clearcam_notification(request: Request, authorization: str | None = Header(default=None), text: str = Form(default=""), body_text: str = Form(default="")):
        # ClearCam sends multipart form notification fields. This endpoint only
        # stores text metadata and does not ingest arbitrary uploaded images.
        token = os.getenv("GARDA_CLEARCAM_TOKEN", "")
        if len(token) < 24 or not authorization or not authorization.startswith("Bearer ") or not hmac.compare_digest(authorization[7:], token):
            raise HTTPException(401, "Invalid ClearCam shared secret")
        cam = request.query_params.get("camera")
        camera = camera_or_404(cam or "")
        combined = (text + " " + body_text).strip()[:2000]
        eid = store.event(camera.site_id, camera.id, "clearcam_notification", {"text": combined, "source": "clearcam", "review_required": True})
        store.audit("clearcam", "notification", camera.id, "ok")
        return {"event_id": eid, "accepted": True}

    return app


# Use `uvicorn garda_vision.api:app` only after env is configured.
# `build_app` is also directly testable with in-memory SQLite and fake engines.
app = None  # Intentionally no unsafe import-time initialization


def run():
    import uvicorn
    uvicorn.run(build_app(), host="127.0.0.1", port=int(os.getenv("GARDA_PORT", "8765")))


if __name__ == "__main__":
    run()
