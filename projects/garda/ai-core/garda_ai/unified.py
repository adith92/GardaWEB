"""Shared API for five client platforms. Local single-site MVP, no public enrollment."""
from __future__ import annotations

import hmac
import io
import os
import re
import secrets
from pathlib import Path
from urllib.parse import urlsplit

import cv2
import numpy as np
from fastapi import Depends, File, Form, HTTPException, Query, Request, Response, UploadFile
from pydantic import BaseModel, Field

from .auth import Identity
from .runtime import Runtime


class Login(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=256)


class CameraInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    rtsp_url: str = Field(min_length=1, max_length=2048)
    face_provider: str = "sface"
    plate_provider: str = "fastalpr"


def decode_image(raw):
    from PIL import Image
    if not raw or len(raw) > 4 * 1024 * 1024:
        raise ValueError("Image must be below 4 MiB")
    with Image.open(io.BytesIO(raw)) as image:
        if image.format not in ("JPEG", "PNG") or image.width * image.height > 12_000_000:
            raise ValueError("JPEG/PNG image must be below 12 megapixels")
        image.verify()
    frame = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Unreadable image")
    return frame


class Unified:
    def __init__(self, app, store, root, lab_no_login=False):
        self.identity, self.store = Identity(root), store
        self.lab_no_login = lab_no_login
        self.lab_actor = {"name": "Admin lokal", "role": "admin", "csrf": secrets.token_urlsafe(32),
                          "lab_no_login": True}
        self.runtime = Runtime(root, store)
        self.secure_cookie = os.environ.get("GARDA_COOKIE_SECURE", "1") != "0"
        self.allowed_origin = os.environ.get("GARDA_PUBLIC_ORIGIN", "").rstrip("/")
        self._routes(app)

    @staticmethod
    def token(request):
        value = request.headers.get("Authorization", "")
        return value[7:] if value.startswith("Bearer ") else request.cookies.get("garda_session", "")

    def same_origin(self, request):
        origin = request.headers.get("origin")
        expected = self.allowed_origin or str(request.base_url).rstrip("/")
        if origin and origin != expected:
            raise HTTPException(403, "Origin not allowed")

    def authorize(self, request: Request):
        actor = dict(self.lab_actor) if self.lab_no_login else self.identity.actor(self.token(request))
        if actor is None:
            raise HTTPException(401, "Session expired or unavailable")
        if request.method not in ("GET", "HEAD", "OPTIONS"):
            self.same_origin(request)
            if self.lab_no_login or not request.headers.get("Authorization", "").startswith("Bearer "):
                if not hmac.compare_digest(request.headers.get("X-GARDA-CSRF", ""), actor["csrf"]):
                    raise HTTPException(403, "CSRF token required")
        return actor

    def require(self, *roles):
        def guard(request: Request):
            actor = self.authorize(request)
            if actor["role"] not in roles:
                raise HTTPException(403, "Permission denied")
            self.store.audit(request.method + " " + request.url.path, actor["name"])
            return actor
        return guard

    def _routes(self, app):
        read = self.require("admin", "operator", "viewer")
        operate = self.require("admin", "operator")
        admin = self.require("admin")

        @app.middleware("http")
        async def headers(request, call_next):
            response = await call_next(request)
            response.headers["Cache-Control"] = "no-store"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "no-referrer"
            return response

        @app.post("/api/v1/auth/login")
        def login(command: Login, request: Request, response: Response):
            self.same_origin(request)
            try:
                token, actor = self.identity.login(command.username, command.password,
                                                  request.client.host if request.client else "local")
            except PermissionError:
                raise HTTPException(429, "Too many login attempts; retry in one minute")
            except ValueError:
                raise HTTPException(401, "Invalid username or password")
            response.set_cookie("garda_session", token, max_age=8*3600,
                                httponly=True, secure=self.secure_cookie, samesite="strict", path="/")
            self.store.audit("login", actor["name"])
            return {"access_token": token, "token_type": "bearer", **actor}

        @app.get("/api/v1/auth/me")
        def me(actor=Depends(read)):
            return actor

        @app.post("/api/v1/auth/logout")
        def logout(request: Request, response: Response, actor=Depends(read)):
            if self.lab_no_login:
                return {"logged_out": False, "lab_no_login": True}
            self.identity.logout(self.token(request))
            response.delete_cookie("garda_session", path="/")
            return {"logged_out": True}

        @app.get("/api/v1/cameras")
        def cameras(actor=Depends(read)):
            return {"cameras": self.runtime.cameras(), "minimum_target": 8,
                    "capacity_validated": False}

        @app.put("/api/v1/cameras/{camera_id}")
        def save(camera_id: str, command: CameraInput, actor=Depends(admin)):
            if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", camera_id):
                raise HTTPException(422, "Invalid camera ID")
            try:
                self.runtime.save(camera_id, command.name, command.rtsp_url,
                                  command.face_provider, command.plate_provider)
            except ValueError as exc:
                raise HTTPException(422, str(exc))
            return {"saved": True, "id": camera_id}

        @app.post("/api/v1/cameras/{camera_id}/start")
        def start(camera_id: str, actor=Depends(operate)):
            try:
                self.runtime.start(camera_id)
            except ValueError as exc:
                raise HTTPException(422, str(exc))
            except Exception:
                raise HTTPException(503, "Camera/model could not be started; inspect local configuration")
            return {"started": True, "online_verified": False}

        @app.post("/api/v1/cameras/{camera_id}/stop")
        def stop(camera_id: str, actor=Depends(operate)):
            try:
                self.runtime.stop(camera_id)
            except RuntimeError:
                raise HTTPException(409, "Worker still stopping; retry shortly")
            return {"stopped": True}

        @app.get("/api/v1/cameras/{camera_id}/preview.jpg")
        def preview(camera_id: str, actor=Depends(read)):
            image = self.runtime.preview(camera_id)
            if image is None:
                raise HTTPException(503, "No fresh frame available")
            return Response(image, media_type="image/jpeg")

        @app.get("/api/v1/providers")
        def providers(actor=Depends(read)):
            return {"providers": self.runtime.providers.status()}

        @app.get("/api/v1/events")
        def events(kind: str | None = None, camera: str | None = None,
                   q: str = Query("", max_length=100), limit: int = Query(50, ge=1, le=100),
                   actor=Depends(operate)):
            try:
                rows = self.store.list_events(kind, None, camera, limit, search=q)
            except ValueError as exc:
                raise HTTPException(422, str(exc))
            return {"events": rows, "count": len(rows)}

        @app.get("/api/v1/stats")
        def stats(actor=Depends(operate)):
            return self.store.stats()

        @app.get("/api/v1/events/{event_id}/photos")
        def photos(event_id: str, actor=Depends(operate)):
            return {"photos": self.store.event_photos(event_id)}

        @app.get("/api/v1/events/{event_id}/photos/{photo_id}")
        def photo(event_id: str, photo_id: str, actor=Depends(operate)):
            from fastapi.responses import FileResponse
            target = self.store.photo_path(event_id, photo_id)
            if target is None:
                raise HTTPException(404, "Evidence not found")
            return FileResponse(target, media_type="image/jpeg")

        @app.post("/api/v1/faces/enroll")
        async def enroll(image: UploadFile = File(...), label: str = Form(..., max_length=90),
                         reference: str = Form(..., min_length=1, max_length=140),
                         provider: str = Form("sface"), actor=Depends(admin)):
            from starlette.concurrency import run_in_threadpool
            if provider not in ("sface", "deepface", "insightface"):
                raise HTTPException(422, "Invalid face provider")
            raw = await image.read(4*1024*1024 + 1)
            def perform():
                return self.runtime.providers.get(provider).enroll(decode_image(raw), label, reference)
            try:
                record = await run_in_threadpool(perform)
            except ValueError:
                raise HTTPException(422, "Use one clear face in a valid JPEG/PNG and a reference")
            except Exception:
                raise HTTPException(503, "Face provider requires local model configuration")
            return {"id": record, "provider": provider, "status": "enrolled"}

        @app.delete("/api/v1/faces/{provider}/{face_id}")
        def revoke(provider: str, face_id: str, actor=Depends(admin)):
            if provider not in ("sface", "deepface", "insightface"):
                raise HTTPException(422, "Invalid face provider")
            try:
                deleted = self.runtime.providers.get(provider).gallery.revoke(face_id)
            except Exception:
                raise HTTPException(503, "Face provider unavailable")
            if not deleted:
                raise HTTPException(404, "Enrollment not found")
            return {"revoked": True}

        from .updates import install_updates
        install_updates(app, self, self.runtime.root)

    def close(self):
        self.runtime.close()
        self.identity.close()
