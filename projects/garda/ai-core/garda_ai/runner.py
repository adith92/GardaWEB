"""One decoupled capture thread + bounded latest-frame queue per RTSP stream."""
from __future__ import annotations

import logging
import queue
import signal
import threading
import time

import cv2

from .config import CameraConfig, GardaConfig
from .processor import FrameProcessor
from .storage import EventStore
from .vision import FaceDetector, PlateReader

LOG = logging.getLogger("garda.runner")


class StreamWorker:
    def __init__(self, config: CameraConfig, processor: FrameProcessor, stop: threading.Event,
                 on_preview=None, on_inference=None):
        self.config, self.processor, self.stop = config, processor, stop
        self.on_preview = on_preview
        self.on_inference = on_inference
        self.frames: queue.Queue = queue.Queue(maxsize=1)
        self.reader = threading.Thread(target=self._read, name="rtsp-" + config.id, daemon=True)
        self.processor_thread = threading.Thread(target=self._process,
                                                 name="ai-" + config.id, daemon=True)

    def start(self):
        self.reader.start()
        self.processor_thread.start()

    def join(self):
        self.reader.join(timeout=5)
        self.processor_thread.join(timeout=5)

    def _read(self):
        backoff = 1.0
        preview_at = 0.0
        while not self.stop.is_set():
            # Never log the RTSP URL, which may contain credentials.
            cap = cv2.VideoCapture(self.config.url, cv2.CAP_FFMPEG, [
                cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000, cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000])
            if not cap.isOpened():
                cap.release()
                LOG.warning("%s: stream unavailable (retrying)", self.config.id)
                self.stop.wait(backoff)
                backoff = min(15.0, backoff * 2)
                continue
            try:
                backoff = 1.0
                LOG.info("%s: RTSP connected", self.config.id)
                while not self.stop.is_set():
                    ok, frame = cap.read()
                    if not ok or frame is None:
                        break
                    now = time.monotonic()
                    if self.on_preview and now >= preview_at:
                        self.on_preview(frame)
                        preview_at = now + .5
                    try:
                        self.frames.put_nowait(frame)
                    except queue.Full:
                        try:
                            self.frames.get_nowait()  # Drop stale frames, never queue seconds of lag.
                        except queue.Empty:
                            pass
                        try:
                            self.frames.put_nowait(frame)
                        except queue.Full:
                            pass
            finally:
                cap.release()
            LOG.warning("%s: RTSP disconnected, reconnecting", self.config.id)
            self.stop.wait(backoff)
            backoff = min(15.0, backoff * 2)

    def _process(self):
        next_time = 0.0
        interval = 1.0 / self.config.sample_fps
        while not self.stop.is_set():
            try:
                frame = self.frames.get(timeout=1.0)
            except queue.Empty:
                continue
            now = time.monotonic()
            if now < next_time:
                continue
            next_time = now + interval
            try:
                counts = self.processor.process(frame, now)
                if self.on_inference:
                    self.on_inference(True)
                if any(counts.values()):
                    LOG.info("%s: new events: %s", self.config.id, counts)
            except Exception:
                if self.on_inference:
                    self.on_inference(False)
                LOG.exception("%s: detection frame failed, continuing", self.config.id)


def run(config: GardaConfig):
    LOG.info("Starting GARDA AI Core (%d configured cameras; throughput unverified)", len(config.cameras))
    store = EventStore(config.data_dir)
    store.purge(config.retention_days)
    stop = threading.Event()
    gallery = None
    matcher = None
    try:
        if config.recognition_model is not None:
            from .recognition import FaceGallery, FaceMatcher
            import os
            gallery = FaceGallery(config.data_dir, os.environ.get("GARDA_FACE_KEY", ""))
            matcher = FaceMatcher(config.recognition_model, gallery,
                                  config.recognition_threshold)
        def shutdown(_signal, _frame):
            stop.set()
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, shutdown)
            signal.signal(signal.SIGTERM, shutdown)
        # A single PlateReader and lock avoids duplicating ONNX model memory.
        plate_reader = PlateReader(config.plate_min_confidence) if config.enable_plates else None
        plate_lock = threading.Lock()
        workers = [StreamWorker(camera, FrameProcessor(camera, store,
                      face_detector=FaceDetector(config.face_model),
                      plate_reader=plate_reader, plate_lock=plate_lock,
                      motion_min_fraction=config.motion_min_fraction,
                      face_matcher=matcher), stop)
                   for camera in config.cameras]
        for worker in workers:
            worker.start()
        last_purge = time.monotonic()
        while not stop.wait(1.0):
            if time.monotonic() - last_purge >= 24 * 3600:
                store.purge(config.retention_days)
                last_purge = time.monotonic()
        for worker in workers:
            worker.join()
    finally:
        stop.set()
        if gallery is not None:
            gallery.close()
        store.close()
