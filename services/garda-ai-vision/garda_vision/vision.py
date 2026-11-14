"""CPU-first plate OCR and optional licensed ONNX embedding provider.

Models/weights are deliberately NOT bundled. Plate reads and face matches are
candidates, never automated enforcement decisions. Face identity is disabled
unless explicitly enabled for a lawful contracted deployment.
"""
from __future__ import annotations

import os
from typing import Any

import cv2
import numpy as np

from .core import plate_candidates


class Vision:
    def __init__(self, face_model_path: str | None = None, enable_face_id: bool = False):
        self.detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if self.detector.empty():
            raise RuntimeError("OpenCV face-presence cascade unavailable")
        self.enable_face_id = enable_face_id
        self.face_model = None
        if enable_face_id:
            if not face_model_path or not os.path.isfile(face_model_path):
                raise RuntimeError("Face ID enabled but GARDA_FACE_ONNX is missing")
            self.face_model = cv2.dnn.readNetFromONNX(face_model_path)
        self.reader = None

    def _ocr(self, frame: np.ndarray) -> list[tuple[str, float]]:
        # Optional dependency. Downloads weights at first use; pre-cache for offline.
        try:
            if self.reader is None:
                import easyocr
                self.reader = easyocr.Reader(["en"], gpu=False)
            return [(str(text), float(conf)) for _, text, conf in self.reader.readtext(frame, detail=1)]
        except ImportError:
            return []

    def faces(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return [tuple(map(int, result)) for result in self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48))]

    def embed(self, face_bgr: np.ndarray) -> list[float]:
        if self.face_model is None:
            raise RuntimeError("Face recognition disabled or ONNX model missing")
        # ArcFace-style ONNX input. Verify preprocessing/threshold against actual model.
        face = cv2.resize(face_bgr, (112, 112))
        rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        blob = cv2.dnn.blobFromImage(rgb, 1.0 / 127.5, (112, 112), (127.5, 127.5, 127.5), swapRB=False)
        self.face_model.setInput(blob)
        vec = self.face_model.forward().ravel().astype(np.float32)
        if not np.isfinite(vec).all() or np.linalg.norm(vec) < 1e-6:
            raise RuntimeError("Invalid embedding")
        return (vec / np.linalg.norm(vec)).tolist()

    def analyze(self, frame: np.ndarray, enrolled: dict[str, list[float]] | None = None, threshold: float = 0.60) -> dict[str, Any]:
        faces = self.faces(frame)
        results: dict[str, Any] = {"face_count": len(faces), "plates": [], "face_candidates": [], "ocr_available": True}
        reads = self._ocr(frame)
        if self.reader is None:
            results["ocr_available"] = False
        for text, conf in reads:
            if conf < 0.25:
                continue
            for plate in plate_candidates(text):
                results["plates"].append({"plate": plate, "confidence": round(conf, 3), "review_required": True})
        if self.face_model is not None and enrolled:
            for x, y, w, h in faces:
                if w < 64 or h < 64:
                    continue
                probe = np.asarray(self.embed(frame[y:y+h, x:x+w]))
                scores = [(name, float(np.dot(probe, np.asarray(vec)))) for name, vec in enrolled.items() if len(vec) == len(probe)]
                if scores:
                    match, similarity = max(scores, key=lambda s: s[1])
                    if similarity >= threshold:
                        results["face_candidates"].append({"person_id": match, "similarity": round(similarity, 4), "review_required": True})
        return results

    @staticmethod
    def decode(image_bytes: bytes) -> np.ndarray:
        frame = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None or frame.size == 0 or frame.shape[0] * frame.shape[1] > 16_000_000:
            raise ValueError("Invalid image or too many pixels")
        return frame
