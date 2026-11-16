"""Lazy, interchangeable local AI engines. No model/network work at import time."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import re
import threading
from pathlib import Path

import cv2
import numpy as np

from .recognition import FaceGallery, FaceMatcher
from .vision import Detection, FaceDetector, PlateReader, crop_box


def model_file(variable: str) -> Path:
    path = Path(os.environ.get(variable, "")).expanduser()
    digest = os.environ.get(variable + "_SHA256", "").lower()
    if not path.is_file() or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise RuntimeError(f"Configure {variable} and its _SHA256 fingerprint")
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f"Model fingerprint mismatch: {variable}")
    return path.resolve()


class Faces:
    def __init__(self, name: str, root: Path):
        self.name = name
        self.lock = threading.RLock()
        self.detector = FaceDetector(model_file("GARDA_FACE_YUNET_MODEL"))
        self.gallery = FaceGallery(root / "templates" / name, os.environ.get("GARDA_FACE_KEY", ""))
        self.matcher = None
        self.engine = None
        try:
            if name == "sface":
                self.matcher = FaceMatcher(model_file("GARDA_FACE_SFACE_MODEL"), self.gallery)
            elif name == "deepface":
                # DeepFace manages its own cache. Network-enabled initial provisioning is explicit.
                if os.environ.get("GARDA_DEEPFACE_ALLOW_MODEL_DOWNLOADS") != "1":
                    raise RuntimeError("DeepFace model provisioning requires explicit local opt-in")
                from deepface import DeepFace
                self.engine = DeepFace
            elif name == "insightface":
                if os.environ.get("GARDA_INSIGHTFACE_MODEL_LICENSED") != "1":
                    raise RuntimeError("Configure an independently licensed InsightFace recognition model")
                from insightface.model_zoo import get_model
                self.engine = get_model(str(model_file("GARDA_INSIGHTFACE_MODEL")),
                                        providers=["CPUExecutionProvider"])
                self.engine.prepare(ctx_id=-1)
            else:
                raise ValueError("Unknown face provider")
        except Exception:
            self.gallery.close()
            raise

    def detect(self, frame):
        with self.lock:
            return self.detector.detect(frame)

    def feature(self, frame, detection):
        with self.lock:
            if self.matcher:
                return self.matcher.feature(frame, detection)
            if self.name == "deepface":
                crop = crop_box(frame, detection.bbox, 0.05)
                results = self.engine.represent(img_path=crop, model_name="SFace",
                    detector_backend="skip", enforce_detection=False, align=False)
                return np.asarray(results[0]["embedding"], dtype=np.float32).reshape(1, -1)
            from insightface.utils.face_align import norm_crop
            landmarks = np.asarray(detection.face_row[4:14], dtype=np.float32).reshape(5, 2)
            aligned = norm_crop(frame, landmark=landmarks, image_size=112)
            return np.asarray(self.engine.get_feat(aligned), dtype=np.float32).reshape(1, -1)

    def match(self, frame, detection):
        feature = self.feature(frame, detection)
        if feature is None:
            return None, None
        vector = feature.reshape(-1)
        best, score = None, -1.0
        for label, enrolled in self.gallery.registered():
            target = enrolled.reshape(-1)
            if target.shape != vector.shape:
                continue
            value = float(np.dot(vector, target) / max(1e-9, np.linalg.norm(vector) * np.linalg.norm(target)))
            if value > score:
                best, score = label, value
        threshold = float(os.environ.get("GARDA_" + self.name.upper() + "_THRESHOLD", "0.55"))
        if not 0.0 < threshold <= 1.0:
            raise ValueError("Provider threshold must be in (0, 1]")
        return (best if score >= threshold else None, score if score >= -0.99 else None)

    def enroll(self, frame, label, reference):
        faces = self.detect(frame)
        if len(faces) != 1:
            raise ValueError("Enrollment requires exactly one clear face")
        feature = self.feature(frame, faces[0])
        if feature is None:
            raise ValueError("Face landmarks unavailable")
        return self.gallery.enroll(label, feature, reference)

    def close(self):
        self.gallery.close()


class Plates:
    def __init__(self, name: str):
        if os.environ.get("GARDA_FASTALPR_MODELS_APPROVED") != "1":
            raise RuntimeError("Provision and approve FastALPR detector/OCR model assets locally first")
        self.name = name
        self.base = PlateReader()
        self.ocr = None
        if name == "paddleocr":
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(lang="en", use_doc_orientation_classify=False,
                                 use_doc_unwarping=False, use_textline_orientation=False)

    def detect(self, frame):
        if self.name == "fastalpr":
            return self.base.detect(frame)
        # PaddleOCR reads only detector crops, never arbitrary full-frame signage.
        output = []
        for item in self.base.engine.predict(frame):
            box = item.detection.bounding_box
            rect = tuple(int(v) for v in (box.x1, box.y1, box.x2, box.y2))
            crop = crop_box(frame, rect, 0.05)
            if crop.size == 0:
                continue
            for result in self.ocr.predict(crop):
                data = result.json
                if callable(data):
                    data = data()
                if isinstance(data, str):
                    import json
                    data = json.loads(data)
                fields = data.get("res", data)
                pairs = zip(fields.get("rec_texts", []), fields.get("rec_scores", []))
                text, confidence = "", []
                for value, score in pairs:
                    text += re.sub(r"[^A-Z0-9]", "", value.upper())
                    confidence.append(float(score))
                if text and confidence and min(confidence) >= .7:
                    output.append(Detection(rect, sum(confidence) / len(confidence), text))
        return output


class Providers:
    PACKAGES = {"sface": "cv2", "deepface": "deepface", "insightface": "insightface",
                "fastalpr": "fast_alpr", "paddleocr": "paddleocr"}

    def __init__(self, root: Path):
        self.root = root
        self.instances = {}
        self.errors = set()
        self.lock = threading.RLock()

    def get(self, name):
        if name not in self.PACKAGES:
            raise ValueError("Unknown provider")
        with self.lock:
            if name not in self.instances:
                try:
                    self.instances[name] = Faces(name, self.root) if name in ("sface", "deepface", "insightface") else Plates(name)
                    self.errors.discard(name)
                except Exception:
                    self.errors.add(name)
                    raise
            return self.instances[name]

    def status(self):
        with self.lock:
            return [{"id": name, "task": "face" if name in ("sface", "deepface", "insightface") else "plate",
                     "installed": importlib.util.find_spec(package) is not None,
                     "state": "loaded" if name in self.instances else "configuration_required" if name in self.errors else "not_loaded",
                     "hardware_validated": False} for name, package in self.PACKAGES.items()]

    def close(self):
        for engine in self.instances.values():
            if hasattr(engine, "close"):
                engine.close()
