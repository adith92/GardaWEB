"""
RTSP Video Stream Capture Thread using OpenCV and PySide6
Optimized for real-time low-latency H.264 RTSP streams.
"""
import os
import time
import logging
from typing import Optional

import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

# Force TCP transport for RTSP to prevent packet corruption and UDP dropouts
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

logger = logging.getLogger("CameraStream")


class CameraStreamThread(QThread):
    # Signals
    frame_ready = Signal(QImage)
    status_changed = Signal(bool, str)
    stats_updated = Signal(float, int, int)  # fps, width, height

    def __init__(self, rtsp_url: str):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.running = False
        self.is_connected = False

        # Snapshot & Recording
        self._snapshot_request: Optional[str] = None
        self._record_writer: Optional[cv2.VideoWriter] = None
        self._record_file: Optional[str] = None
        self._is_recording = False

    def run(self):
        self.running = True
        logger.info(f"Opening RTSP stream: {self.rtsp_url}")
        self.status_changed.emit(False, f"Menghubungkan ke RTSP: {self.rtsp_url}...")

        cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        # Minimize frame buffer to achieve real-time latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not cap.isOpened():
            self.status_changed.emit(False, f"Gagal membuka RTSP stream di {self.rtsp_url}")
            self.running = False
            return

        self.is_connected = True
        self.status_changed.emit(True, "RTSP Stream Terhubung (Live)")

        frame_count = 0
        fps_start_time = time.time()
        current_fps = 0.0

        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                # Connection dropped or EOF
                self.status_changed.emit(False, "RTSP frame stream terputus. Mencoba reconnect...")
                time.sleep(1.0)
                # Attempt quick reconnect
                cap.release()
                cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                if not cap.isOpened():
                    time.sleep(2.0)
                continue

            h, w, ch = frame.shape

            # Calculate FPS every 30 frames
            frame_count += 1
            if frame_count >= 15:
                now = time.time()
                elapsed = now - fps_start_time
                if elapsed > 0:
                    current_fps = round(frame_count / elapsed, 1)
                frame_count = 0
                fps_start_time = now
                self.stats_updated.emit(current_fps, w, h)

            # Handle Snapshot
            if self._snapshot_request:
                try:
                    cv2.imwrite(self._snapshot_request, frame)
                    logger.info(f"Snapshot saved to {self._snapshot_request}")
                except Exception as e:
                    logger.error(f"Failed to save snapshot: {e}")
                self._snapshot_request = None

            # Handle Recording
            if self._is_recording and self._record_writer is not None:
                try:
                    self._record_writer.write(frame)
                except Exception as e:
                    logger.error(f"Record write error: {e}")

            # Convert BGR (OpenCV) to RGB for Qt
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = ch * w
            q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()

            self.frame_ready.emit(q_img)

        # Cleanup
        if self._record_writer is not None:
            self._record_writer.release()
            self._record_writer = None

        cap.release()
        self.is_connected = False
        self.status_changed.emit(False, "Stream Dihentikan")

    def capture_snapshot(self, filepath: str):
        """Request saving the next incoming frame as an image file."""
        self._snapshot_request = filepath

    def start_recording(self, filepath: str, fps: float = 15.0, width: int = 1920, height: int = 1080) -> bool:
        """Start recording frames to MP4 file."""
        try:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self._record_writer = cv2.VideoWriter(filepath, fourcc, fps, (width, height))
            self._record_file = filepath
            self._is_recording = True
            logger.info(f"Started video recording: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self._is_recording = False
            return False

    def stop_recording(self) -> Optional[str]:
        """Stop current video recording."""
        saved_file = self._record_file
        self._is_recording = False
        if self._record_writer is not None:
            self._record_writer.release()
            self._record_writer = None
        self._record_file = None
        logger.info(f"Recording saved to {saved_file}")
        return saved_file

    def stop(self):
        """Stop thread and close stream."""
        self.running = False
        self.wait(2000)
