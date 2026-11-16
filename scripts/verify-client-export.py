"""Fail packaging if a client includes files outside its explicit source allowlist."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = {"main.cjs", "preload.cjs", "policy.cjs", "connect.html", "connect.js"}
DENIED = ("garda_ai", "ai-core", ".onnx", ".p12", ".pfx", ".keystore", ".jks", ".password", ".env", "identity.db", "face.key", "camera.key", ".map")

def verify_names(names):
    for name in names:
        normalized = name.replace("\\", "/").lower()
        if any(item in normalized for item in DENIED):
            raise SystemExit("Client export contains forbidden file: " + name)

if __name__ == "__main__":
    config = json.loads((ROOT / "desktop/package.json").read_text())
    assert set(config["build"]["files"]) == DESKTOP, "Desktop file allowlist changed: review required"
    names = [p.relative_to(ROOT / "dist").as_posix() for p in (ROOT / "dist").rglob("*") if p.is_file()]
    if not names:
        raise SystemExit("Web dist missing")
    verify_names(names)
    for name in names:
        if not (name.startswith("assets/") or name in {"index.html", "logo.png", "faces.png", "cameras.png", "site-map.png"}):
            raise SystemExit("Unexpected Web export file: " + name)
    print(f"PASS: {len(names)} Web files and explicit desktop source allowlist; no core/models/keys/source maps")
