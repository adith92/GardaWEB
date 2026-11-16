"""Private event catalog; bind to loopback or use a TLS-authenticated reverse proxy."""
from __future__ import annotations

from contextlib import asynccontextmanager

import os
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader

from .storage import EventStore


def create_app(data_dir: str | Path | None = None, key: str | None = None) -> FastAPI:
    configured_key = key or os.environ.get("GARDA_AI_API_KEY", "")
    if len(configured_key) < 24:
        raise RuntimeError("Set GARDA_AI_API_KEY to a random secret of at least 24 characters")
    root = Path(data_dir or os.environ.get("GARDA_AI_DATA_DIR", "./var"))
    store = EventStore(root)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            yield
        finally:
            store.close()

    app = FastAPI(title="GARDA AI Core", version="0.2.0",
                  docs_url=None, redoc_url=None, openapi_url=None,
                  lifespan=lifespan)
    api_key = APIKeyHeader(name="X-GARDA-KEY", auto_error=False)

    def require_key(header: str | None = Security(api_key)):
        if header is None or not secrets.compare_digest(header, configured_key):
            raise HTTPException(status_code=401, detail="Unauthorized",
                                headers={"WWW-Authenticate": "APIKey"})

    @app.get("/health")
    def health():
        return {"service": "garda-ai-core", "status": "up"}

    @app.get("/api/events", dependencies=[Depends(require_key)])
    def events(kind: str | None = None, camera: str | None = None,
               plate: str | None = None, limit: int = Query(50, ge=1, le=100)):
        try:
            result = store.list_events(kind, plate, camera, limit)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        store.audit("list_events")
        return {"events": result, "count": len(result)}

    @app.get("/api/events/{event_id}/photos", dependencies=[Depends(require_key)])
    def photos(event_id: str):
        store.audit("list_photos")
        return {"photos": store.event_photos(event_id)}

    @app.get("/api/events/{event_id}/photos/{photo_id}", dependencies=[Depends(require_key)])
    def photo(event_id: str, photo_id: str):
        target = store.photo_path(event_id, photo_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Evidence not found")
        store.audit("read_evidence")
        return FileResponse(target, media_type="image/jpeg",
                            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

    @app.get("/api/stats", dependencies=[Depends(require_key)])
    def stats():
        store.audit("stats")
        return store.stats()

    return app
