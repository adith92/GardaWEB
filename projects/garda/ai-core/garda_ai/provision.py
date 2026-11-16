"""Provision the licensed OpenCV default models with verified Git LFS digests."""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from pathlib import Path

MODELS = (
    {"env": "GARDA_FACE_YUNET_MODEL", "directory": "face_detection_yunet",
     "file": "face_detection_yunet_2023mar.onnx", "size": 232589,
     "sha256": "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4", "license": "MIT"},
    {"env": "GARDA_FACE_SFACE_MODEL", "directory": "face_recognition_sface",
     "file": "face_recognition_sface_2021dec.onnx", "size": 38696353,
     "sha256": "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79", "license": "Apache-2.0"},
)


def provision_opencv(root: Path):
    from cryptography.fernet import Fernet
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    model_root = root / "models"
    model_root.mkdir(exist_ok=True, mode=0o700)
    config = {}
    for model in MODELS:
        target = model_root / model["file"]
        valid = target.is_file() and target.stat().st_size == model["size"] and hashlib.sha256(target.read_bytes()).hexdigest() == model["sha256"]
        if not valid:
            url = f"https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/{model['directory']}/{model['file']}"
            part = target.with_suffix(".part")
            try:
                with urllib.request.urlopen(url, timeout=60) as source, part.open("wb") as output:
                    digest, count = hashlib.sha256(), 0
                    while chunk := source.read(65536):
                        count += len(chunk)
                        if count > model["size"]:
                            raise ValueError("Model exceeds pinned size")
                        digest.update(chunk)
                        output.write(chunk)
                if count != model["size"] or digest.hexdigest() != model["sha256"]:
                    raise ValueError("Official model size or fingerprint mismatch")
                os.replace(part, target)
            finally:
                part.unlink(missing_ok=True)
        config[model["env"]] = str(target.resolve())
        config[model["env"] + "_SHA256"] = model["sha256"]
        # Preserve upstream notices beside the actual local weights.
        notice = model_root / (model["directory"] + "-LICENSE.txt")
        if not notice.exists():
            url = f"https://raw.githubusercontent.com/opencv/opencv_zoo/main/models/{model['directory']}/LICENSE"
            with urllib.request.urlopen(url, timeout=30) as response:
                notice.write_bytes(response.read(100000))
    key = root / "face.key"
    if not key.exists():
        fd = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as output:
            output.write(Fernet.generate_key())
    config["face_key_file"] = str(key.resolve())
    (root / "model-provisioning.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    return {"provider": "sface", "files_verified": len(MODELS), "weights_downloaded": True,
            "accuracy_validated": False}


def local_models(root):
    manifest = root / "model-provisioning.json"
    if not manifest.is_file():
        return
    data = json.loads(manifest.read_text())
    for model in MODELS:
        for suffix in ("", "_SHA256"):
            key = model["env"] + suffix
            if key in data:
                os.environ.setdefault(key, str(data[key]))
    key_file = Path(data["face_key_file"])
    os.environ.setdefault("GARDA_FACE_KEY", key_file.read_text().strip())
