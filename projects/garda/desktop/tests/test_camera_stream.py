"""Synthetic desktop RTSP safety checks without Qt GUI or physical camera."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

class FakeSignal:
    def emit(self, *args):
        pass

class FakeThread:
    def __init__(self, *args, **kwargs):
        pass
    def start(self, *args, **kwargs):
        pass
    def wait(self, milliseconds):
        return True

class FakeQImage:
    class Format:
        Format_RGB888 = 1

qt = types.ModuleType("PySide6")
core = types.ModuleType("PySide6.QtCore")
gui = types.ModuleType("PySide6.QtGui")
core.QThread = FakeThread
core.Signal = lambda *args: FakeSignal()
gui.QImage = FakeQImage
sys.modules.update({"PySide6": qt, "PySide6.QtCore": core, "PySide6.QtGui": gui})

module_path = Path(__file__).resolve().parents[1] / "camera_stream.py"
spec = importlib.util.spec_from_file_location("garda_camera_stream_tested", module_path)
stream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stream)


class DesktopCaptureTests(unittest.TestCase):
    def setUp(self):
        self.thread = stream.CameraStreamThread("rtsp://camerauser:secret@192.168.1.100:554/live")

    def test_timeout_parameters_are_open_only(self):
        with patch.object(stream.cv2, "VideoCapture") as factory:
            self.thread._open_capture()
        args = factory.call_args.args
        self.assertEqual(args[1], stream.cv2.CAP_FFMPEG)
        self.assertEqual(args[2], [
            stream.cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000,
            stream.cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000,
        ])

    def test_recording_rejects_absent_frame(self):
        self.thread.running = True
        with patch.object(stream.cv2, "VideoWriter") as writer:
            self.assertFalse(self.thread.start_recording("some.mp4"))
            writer.assert_not_called()

    def test_recording_checks_encoder_and_releases_failed_writer(self):
        self.thread.running = True
        self.thread._frame_size = (1280, 720)
        with patch.object(stream.cv2, "VideoWriter") as writer:
            writer.return_value.isOpened.return_value = False
            self.assertFalse(self.thread.start_recording("some.mp4"))
            writer.return_value.release.assert_called_once()
            self.assertFalse(self.thread._is_recording)

    def test_recording_uses_actual_dimensions_and_is_synchronized(self):
        self.thread.running = True
        self.thread._frame_size = (1280, 720)
        with patch.object(stream.cv2, "VideoWriter") as writer:
            writer.return_value.isOpened.return_value = True
            self.assertTrue(self.thread.start_recording("some.mp4"))
            self.assertEqual(writer.call_args.args[-1], (1280, 720))
            with patch.object(stream.os.path, "isfile", return_value=True):
                with patch.object(stream.os.path, "getsize", return_value=10):
                    self.assertEqual(self.thread.stop_recording(), "some.mp4")
            writer.return_value.release.assert_called_once()
            self.assertFalse(self.thread._is_recording)

    def test_shutdown_returns_wait_result(self):
        self.thread.running = True
        with patch.object(self.thread, "wait", return_value=False) as wait:
            self.assertFalse(self.thread.stop())
            wait.assert_called_once_with(7000)
        self.assertFalse(self.thread.running)


if __name__ == "__main__":
    unittest.main()
