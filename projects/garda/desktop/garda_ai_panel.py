"""GARDA Desktop on-prem AI timeline panel for Windows/Linux (PySide6).

Never displays API token, never sends camera passwords. All HTTP work runs
off the Qt GUI thread. Access requires GARDA_AI_API_KEY environment variable.
"""
from __future__ import annotations

import json
import os
import urllib.request
from urllib.parse import urlsplit

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)


def checked_api_origin() -> str:
    url = os.environ.get("GARDA_AI_URL", "http://127.0.0.1:8808").rstrip("/")
    parsed = urlsplit(url)
    allowed = parsed.scheme == "https" or (
        parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost", "::1"))
    if not allowed or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Use HTTPS for GARDA AI network connections; loopback HTTP is allowed")
    if parsed.path not in ("", "/"):
        raise ValueError("GARDA_AI_URL should point to the service root")
    return url


def api_get(path: str, binary: bool = False):
    key = os.environ.get("GARDA_AI_API_KEY", "")
    if len(key) < 24:
        raise ValueError("GARDA_AI_API_KEY is not set (requires >=24 chars)")
    request = urllib.request.Request(
        checked_api_origin() + path,
        headers={"X-GARDA-KEY": key, "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        data = response.read(4_000_001)
        if len(data) > 4_000_000:
            raise ValueError("GARDA AI server response exceeded 4 MB")
        return data if binary else json.loads(data.decode("utf-8"))


class AiFetchWorker(QThread):
    completed = Signal(object, str)

    def __init__(self, event_id: str = ""):
        super().__init__()
        self.event_id = event_id

    def run(self):
        try:
            if self.event_id:
                if len(self.event_id) != 32 or not all(c in "0123456789abcdef" for c in self.event_id):
                    raise ValueError("Invalid event ID")
                items = api_get(f"/api/events/{self.event_id}/photos").get("photos", [])
                photo = items[0]["id"] if items else ""
                result = api_get(
                    f"/api/events/{self.event_id}/photos/{photo}", binary=True
                ) if photo else b""
            else:
                result = (api_get("/api/stats"), api_get("/api/events?limit=40"))
            self.completed.emit(result, "")
        except Exception as exc:
            # Never expose a request URL or credentials in network errors.
            message = str(exc)
            self.completed.emit(None, message[:140].replace("GARDA_AI_API_KEY", "key"))


class GardaAiDesktopPanel(QWidget):
    """Drop-in tab for the existing GARDA Desktop PTZ application."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.events = []
        self.layout = QVBoxLayout(self)
        self.label = QLabel("🧠 GARDA AI | Plat • Wajah • Gerakan")
        self.label.setStyleSheet("color: #f4f5f9; font-size: 15px; font-weight: 700;")
        self.status = QLabel("API local: 127.0.0.1:8808 | Belum terhubung")
        self.status.setWordWrap(True)
        self.status.setStyleSheet("color: #cbd5e1;")
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.status)

        bar = QHBoxLayout()
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        self.evidence_btn = QPushButton("📸 Lihat Bukti")
        self.evidence_btn.clicked.connect(self.load_selected_photo)
        bar.addWidget(self.refresh_btn)
        bar.addWidget(self.evidence_btn)
        self.layout.addLayout(bar)

        self.table = QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels(["Waktu (UTC)", "Kamera", "Event", "Plat / Wajah", "Conf."])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet(
            "QTableWidget { background: #121620; color: #f7f7fa; gridline-color: #394452; }"
            "QHeaderView::section { background: #262d39; color: #ffffff; padding: 5px; }"
        )
        self.layout.addWidget(self.table)
        self.preview = QLabel("📷 Pilih event dan tekan 'Lihat Bukti'")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(100)
        self.preview.setMaximumHeight(190)
        self.preview.setStyleSheet("color: #cbd5e1; background: #111520; border-radius: 7px;")
        self.layout.addWidget(self.preview)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(20_000)
        QTimer.singleShot(300, self.refresh)

    def refresh(self):
        if self.worker is not None and self.worker.isRunning():
            return
        self.refresh_btn.setEnabled(False)
        self.worker = AiFetchWorker()
        self.worker.completed.connect(self.on_events)
        self.worker.finished.connect(lambda: self.refresh_btn.setEnabled(True))
        self.worker.start()

    def on_events(self, payload, error: str):
        if error:
            self.status.setText("⚠ AI server unavailable: " + error)
            return
        counts, response = payload
        self.events = response.get("events", [])
        self.status.setText(
            f"🚗 Plat: {counts.get('plate', 0)}  |  👤 Wajah: {counts.get('face', 0)}"
            f"  |  🎞 Gerakan: {counts.get('motion', 0)}")
        self.table.setRowCount(len(self.events))
        for row, event in enumerate(self.events):
            values = [
                event.get("observed_at", ""), event.get("camera_id", ""),
                event.get("kind", ""), event.get("plate_text") or
                event.get("face_label") or "(unknown)",
                str(round(event.get("confidence") or 0, 3))
            ]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))

    def load_selected_photo(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.events):
            QMessageBox.information(self, "GARDA AI", "Pilih satu event terlebih dahulu")
            return
        if self.worker is not None and self.worker.isRunning():
            return
        self.preview.setText("Memuat JPEG dari server lokal...")
        self.worker = AiFetchWorker(self.events[row]["id"])
        self.worker.completed.connect(self.on_evidence)
        self.worker.start()

    def on_evidence(self, payload, error: str):
        if error:
            self.preview.setText("⚠ " + error)
            return
        pixmap = QPixmap()
        if not payload or not pixmap.loadFromData(payload, "JPEG"):
            self.preview.setText("Tidak ada bukti JPEG untuk event ini")
            return
        self.preview.setPixmap(
            pixmap.scaled(self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                          Qt.TransformationMode.SmoothTransformation))
