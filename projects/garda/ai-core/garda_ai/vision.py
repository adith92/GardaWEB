"""OpenCV motion + detection-only faces; FastALPR optional for plates."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

LOGGER = logging.getLogger("garda.vision")


@dataclass(frozen=True)
class Detection:
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    text: str = ""
    face_row: tuple[float, ...] | None = None


def crop_box(frame: np.ndarray, rect: tuple[int, int, int, int], padding: float = 0.15) -> np.ndarray:
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = rect
    pad_x = int((x2 - x1) * padding)
    pad_y = int((y2 - y1) * padding)
    x1 = max(0, x1 - pad_x); y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x); y2 = min(h, y2 + pad_y)
    return frame[y1:y2, x1:x2]


class MotionDetector:
    def __init__(self, minimum_fraction: float = 0.016, warmup_frames: int = 18):
        self.background = cv2.createBackgroundSubtractorMOG2(history=250, varThreshold=35,
                                                             detectShadows=True)
        self.min_fraction = minimum_fraction
        self.warmup_frames = warmup_frames
        self.frames = 0

    def detect(self, frame: np.ndarray) -> tuple[bool, float]:
        # Work on a reduced frame to keep CPU load predictable.
        h, w = frame.shape[:2]
        small = cv2.resize(frame, (max(1, min(w, 640)), max(1, int(h * min(640 / w, 1.0)))))
        mask = self.background.apply(small)
        self.frames += 1
        if self.frames <= self.warmup_frames:
            return False, 0.0
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,
                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
        fraction = float(cv2.countNonZero(mask)) / float(mask.size)
        return fraction >= self.min_fraction, fraction


class FaceDetector:
    """YuNet DNN when configured, OpenCV bundled Haar otherwise (lower quality)."""
    def __init__(self, model_path: Path | None = None):
        self.yunet = None
        self.haar = None
        if model_path:
            if not model_path.is_file():
                raise FileNotFoundError(f"YuNet model not found: {model_path}")
            if not hasattr(cv2, "FaceDetectorYN"):
                raise RuntimeError("OpenCV build does not expose cv2.FaceDetectorYN")
            self.yunet = cv2.FaceDetectorYN.create(str(model_path), "", (320, 320),
                                                   score_threshold=0.72)
            LOGGER.info("YuNet face detector enabled")
        else:
            self.haar = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
            if self.haar.empty():
                raise RuntimeError("OpenCV Haar face cascade not installed")
            LOGGER.warning("Using basic Haar face detector: configure GARDA_FACE_YUNET_MODEL for more robust results")

    def detect(self, frame: np.ndarray) -> list[Detection]:
        h, w = frame.shape[:2]
        if self.yunet:
            self.yunet.setInputSize((w, h))
            _, detected = self.yunet.detect(frame)
            if detected is None:
                return []
            return [Detection((max(0, int(row[0])), max(0, int(row[1])),
                               min(w, int(row[0] + row[2])), min(h, int(row[1] + row[3]))),
                              float(row[-1]), face_row=tuple(float(v) for v in row))
                    for row in detected]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.haar.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5,
                                           minSize=(32, 32))
        return [Detection((int(x), int(y), int(x + width), int(y + height)), 0.5)
                for (x, y, width, height) in faces]


class PlateReader:
    """Real detector + OCR pipeline, lazy-loaded to keep unit tests lightweight."""
    def __init__(self, minimum_confidence: float = 0.7):
        import os
        cache = os.environ.get("GARDA_PLATE_CACHE")
        if cache:
            from open_image_models.detection.core import hub as detector_hub
            from fast_plate_ocr.inference import hub as ocr_hub
            detector_hub.MODEL_CACHE_DIR = Path(cache) / "detector"
            ocr_hub.MODEL_CACHE_DIR = Path(cache) / "ocr"
        try:
            from fast_alpr import ALPR
        except ImportError as exc:
            raise RuntimeError('Install "fast-alpr[onnx]==0.4.0" for LPR') from exc
        self.engine = ALPR(detector_model="yolo-v9-t-384-license-plate-end2end",
                           ocr_model="cct-xs-v2-global-model")
        self.minimum_confidence = minimum_confidence

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = []
        for result in self.engine.predict(frame):
            if result.ocr is None:
                continue
            raw = str(result.ocr.text).upper()
            value = re.sub(r"[^A-Z0-9]", "", raw)
            confidence = float(result.ocr.confidence or 0)
            # Do not treat unreadable noise as a registered plate.
            if not (4 <= len(value) <= 11 and confidence >= self.minimum_confidence):
                continue
            b = result.detection.bounding_box
            box = (int(b.x1), int(b.y1), int(b.x2), int(b.y2))
            if box[2] <= box[0] or box[3] <= box[1]:
                continue
            results.append(Detection(box, min(confidence, 1.0), value))
        return results
