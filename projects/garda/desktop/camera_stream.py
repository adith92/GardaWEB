"""Bounded RTSP capture and thread-safe snapshot/MP4 capture for GARDA Desktop.

The URL can contain camera credentials. Never include it in logs or Qt signals.
This remains an interactive desktop recorder, not a 24/7 NVR.
"""
from __future__ import annotations

import logging
import os
import threading
import time
from typing import Optional

# OpenCV reads this when its FFmpeg backend initializes.
os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp")

import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

logger = logging.getLogger("CameraStream")

OPEN_TIMEOUT_MS = 5000
READ_TIMEOUT_MS = 3000


class CameraStreamThread(QThread):
    frame_ready = Signal(QImage)
    status_changed = Signal(bool, str)
    stats_updated = Signal(float, int, int)

    def __init__(self, rtsp_url: str):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.running = False
        self.is_connected = False
        self._lock = threading.RLock()
        self._frame_size: Optional[tuple[int, int]] = None
        self._snapshot_request: Optional[str] = None
        self._record_writer: Optional[cv2.VideoWriter] = None
        self._record_file: Optional[str] = None
        self._is_recording = False

    def start(self, *args, **kwargs) -> None:
        # Set before QThread starts so stop() cannot race with run() initialization.
        self.running = True
        super().start(*args, **kwargs)

    def _open_capture(self) -> cv2.VideoCapture:
        # Open-only properties MUST be supplied to the constructor, not cap.set().
        return cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG, [
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, OPEN_TIMEOUT_MS,
            cv2.CAP_PROP_READ_TIMEOUT_MSEC, READ_TIMEOUT_MS,
        ])

    def _pause(self, seconds: float) -> None:
        end = time.monotonic() + seconds
        while self.running and time.monotonic() < end:
            time.sleep(min(0.1, end - time.monotonic()))

    def run(self) -> None:
        backoff = 1.0
        try:
            while self.running:
                cap = None
                try:
                    self.status_changed.emit(False, "Menghubungkan ke kamera RTSP...")
                    logger.info("Opening RTSP stream (camera URL redacted)")
                    cap = self._open_capture()
                    if not cap.isOpened():
                        self.status_changed.emit(False, "Kamera RTSP tidak merespons. Mencoba lagi...")
                    else:
                        backoff = 1.0
                        self.is_connected = True
                        self.status_changed.emit(True, "RTSP Stream Terhubung (Live)")
                        count, started = 0, time.monotonic()
                        while self.running:
                            ok, frame = cap.read()
                            if not ok or frame is None:
                                break
                            h, w, ch = frame.shape
                            with self._lock:
                                self._frame_size = (w, h)
                                snapshot = self._snapshot_request
                                self._snapshot_request = None
                                if self._is_recording and self._record_writer is not None:
                                    if self._record_writer.isOpened():
                                        if self._record_size != (w, h):
                                            self.status_changed.emit(False, "Resolusi kamera berubah; hentikan dan mulai rekaman baru.")
                                            self._finish_recording_locked()
                                        else:
                                            self._record_writer.write(frame)
                            if snapshot:
                                if not cv2.imwrite(snapshot, frame):
                                    logger.error("Snapshot could not be written")
                            count += 1
                            if count >= 15:
                                now = time.monotonic()
                                if now > started:
                                    self.stats_updated.emit(round(count / (now - started), 1), w, h)
                                count, started = 0, now
                            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            # Deep-copy before the NumPy buffer goes out of scope.
                            self.frame_ready.emit(QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy())
                except (cv2.error, OSError, RuntimeError) as exc:
                    # Do not log raw backend errors: FFmpeg can embed credentialed URLs.
                    logger.warning("RTSP capture failure (%s)", type(exc).__name__)
                    self.status_changed.emit(False, "Koneksi kamera bermasalah. Mencoba kembali...")
                finally:
                    if cap is not None:
                        cap.release()
                    self.is_connected = False
                    with self._lock:
                        self._frame_size = None
                if self.running:
                    self.status_changed.emit(False, "Stream terputus. Menyambungkan kembali...")
                    self._pause(backoff)
                    backoff = min(backoff * 2, 15.0)
        finally:
            with self._lock:
                self._finish_recording_locked()
                self._frame_size = None
            self.running = False
            self.is_connected = False
            self.status_changed.emit(False, "Stream Dihentikan")

    def capture_snapshot(self, filepath: str) -> None:
        with self._lock:
            self._snapshot_request = filepath

    def start_recording(self, filepath: str, fps: float = 15.0,
                        width: int = 1920, height: int = 1080) -> bool:
        """Create MP4 only after real frame dimensions and encoder readiness are known.

        width/height remain accepted for old callers but actual live dimensions win.
        """
        if not (0 < fps <= 120):
            return False
        with self._lock:
            if not self.running or self._frame_size is None or self._is_recording:
                return False
            w, h = self._frame_size
            writer = cv2.VideoWriter(filepath, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            if not writer.isOpened():
                writer.release()
                logger.error("MP4 writer could not be opened")
                return False
            self._record_writer = writer
            self._record_file = filepath
            self._record_size = (w, h)
            self._is_recording = True
            logger.info("MP4 encoder started")
            return True

    def _finish_recording_locked(self) -> Optional[str]:
        path = self._record_file
        self._is_recording = False
        if self._record_writer is not None:
            self._record_writer.release()
        self._record_writer = None
        self._record_file = None
        if path is not None and os.path.isfile(path) and os.path.getsize(path) > 0:
            return path
        return None

    def stop_recording(self) -> Optional[str]:
        with self._lock:
            return self._finish_recording_locked()

    def stop(self) -> bool:
        """Request cooperative shutdown; never destroy a live QThread on timeout."""
        self.running = False
        if self.isRunning():
            self.wait(7000)
        done = not self.isRunning()
        if not done:
            logger.error("Camera thread did not exit within the bounded timeout")
        return done
