"""One HTTPS origin for client assets and API, without an external proxy dependency."""
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse


class ApiPrefix:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"].startswith("/garda-api/"):
            scope = dict(scope)
            scope["path"] = scope["path"][len("/garda-api"):]
            scope["raw_path"] = scope.get("raw_path", b"")[len(b"/garda-api"):]
        await self.app(scope, receive, send)


def install_web(app, directory):
    root = Path(directory).resolve()
    if not (root / "index.html").is_file():
        raise ValueError("Build/copy the approved Web bundle before serving it")
    app.add_middleware(ApiPrefix)

    @app.get("/{path:path}", include_in_schema=False)
    def web(path: str):
        if path.startswith(("api/", "garda-api/")):
            raise HTTPException(404, "Unknown API route")
        target = (root / path).resolve()
        if not target.is_relative_to(root):
            raise HTTPException(404, "Unknown asset")
        if target.is_file():
            return FileResponse(target)
        if path in ("", "workspace") or path.startswith("workspace/"):
            return FileResponse(root / "index.html")
        raise HTTPException(404, "Unknown route")
