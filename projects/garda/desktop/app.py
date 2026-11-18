"""
GARDA Desktop - Tactical Dual-Lens IP Camera & ONVIF Command Center
Direktori: C:\\Users\\adith\\OneDrive\\Desktop\\CleanTV

Fitur Utama:
1. Terintegrasi penuh dengan Daemon ONVIF & REST API (Port 8899) + Native PTZ (Port 7777)
2. Dual-Lens Live Video Stream 1080p (Lensa 1: Port 1234, Lensa 2: Port 1235)
3. Live Telemetry Monitor (/api/status): Uptime, Free RAM, Status VPU, Model & Serial ONVIF
4. WS-Discovery Auto-Scanner (UDP 3702) untuk mendeteksi kamera otomatis di LAN
5. Kontrol Pencahayaan & Filter Optik: White Spotlight, IR Night LED, IR-Cut Day/Night
6. AI Human Auto-Tracking, 360° Cruise Patrol, Home Center (x=515, y=70) & Kalibrasi Motor
"""
import os
import sys
import subprocess
import threading
from datetime import datetime
from typing import Optional, Dict, Any

from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QImage, QPixmap, QFont, QKeySequence, QShortcut, QIntValidator
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSlider, QComboBox,
    QGroupBox, QGridLayout, QTextEdit, QMessageBox,
    QSizePolicy, QTabWidget, QBoxLayout, QFrame
)

from config import load_config, save_config
from camera_stream import CameraStreamThread
from srihome_client import SriHomeClient
from garda_ai_panel import GardaAiDesktopPanel


class TelemetrySignals(QObject):
    updated = Signal(bool, dict)
    device_info_ready = Signal(bool, dict)
    discovered_ips = Signal(list)
    log_msg = Signal(str)


class VideoWidget(QLabel):
    """Modern 1080p Video Canvas with aspect-ratio scaling and double-click fullscreen."""
    def __init__(self, title: str = "Kamera", accent_color: str = "#06b6d4", parent=None):
        super().__init__(parent)
        self.title = title
        self.accent_color = accent_color
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: #070a12;
                border: 1px solid #1e293b;
                border-top: 2px solid {self.accent_color};
                border-radius: 10px;
                color: #64748b;
            }}
        """)
        self.setText(f"🎥  {self.title}\nSiap Menerima Transmisi RTSP 1080p")
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(320, 180)
        self.current_pixmap: Optional[QPixmap] = None

    def update_frame(self, q_img: QImage):
        self.current_pixmap = QPixmap.fromImage(q_img)
        self._scale_and_set()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_pixmap:
            self._scale_and_set()

    def _scale_and_set(self):
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled = self.current_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
            self.setPixmap(scaled)

    def mouseDoubleClickEvent(self, event):
        window = self.window()
        if window.isFullScreen():
            window.showNormal()
        else:
            window.showFullScreen()


class GardaMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GARDA Desktop — Tactical Dual-Lens IP Camera & ONVIF Command Center")
        self.resize(1340, 860)
        self.setMinimumSize(1060, 680)

        # Config & Clients
        self.config = load_config()
        self.srihome: Optional[SriHomeClient] = None
        self.stream_thread_1: Optional[CameraStreamThread] = None
        self.stream_thread_2: Optional[CameraStreamThread] = None

        # Signals for thread-safe UI updates
        self.sig = TelemetrySignals()
        self.sig.updated.connect(self._on_telemetry_updated)
        self.sig.device_info_ready.connect(self._on_device_info_ready)
        self.sig.discovered_ips.connect(self._on_discovered_ips)
        self.sig.log_msg.connect(self.log)

        # State
        self.is_connected = False
        self.is_recording = False
        self.is_white_light_on = False
        self.is_ir_on = False
        self.is_tracking_on = False
        self.is_cruise_on = False

        self._telemetry_inflight = False
        self._fps_1 = 0.0
        self._fps_2 = 0.0
        self._res_1 = "-"
        self._res_2 = "-"

        # Apply GARDA Modern Cyber-Slate Theme
        self._apply_stylesheet()

        # Build UI
        self._init_ui()

        # Setup keyboard shortcuts
        self._setup_shortcuts()

        # Periodic Telemetry Timer (every 3 seconds)
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self._poll_telemetry)
        self.telemetry_timer.start(3000)

        # Auto-connect if configured or query telemetry immediately
        self._poll_telemetry()
        if self.config.get("auto_connect", False):
            self.on_connect_clicked()

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #090d16;
            }
            QWidget {
                color: #e2e8f0;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 13px;
            }
            QFrame#headerBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0f172a, stop:0.5 #131c31, stop:1 #0f172a);
                border: 1px solid #1e293b;
                border-bottom: 2px solid #06b6d4;
                border-radius: 10px;
            }
            QFrame#cardFrame {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 10px;
            }
            QGroupBox {
                font-weight: 600;
                border: 1px solid #1e293b;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 14px;
                background-color: #111827;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #38bdf8;
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QLineEdit, QComboBox {
                background-color: #090d16;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                color: #f8fafc;
                font-weight: 600;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #06b6d4;
                background-color: #0f172a;
            }
            QPushButton {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 7px;
                padding: 7px 12px;
                font-weight: 600;
                color: #f1f5f9;
            }
            QPushButton:hover {
                background-color: #283548;
                border-color: #38bdf8;
            }
            QPushButton:pressed {
                background-color: #0284c7;
            }
            QPushButton#btnConnect {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #06b6d4);
                border: none;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 14px;
            }
            QPushButton#btnConnect:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #0891b2);
            }
            QPushButton#btnDisconnect {
                background-color: #dc2626;
                border: none;
                color: white;
                font-weight: bold;
                padding: 8px 14px;
            }
            QPushButton#btnDisconnect:hover {
                background-color: #b91c1c;
            }
            QPushButton.ptzBtn {
                background-color: #0b1120;
                border: 1.5px solid #0ea5e9;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                min-width: 50px;
                min-height: 50px;
                color: #38bdf8;
            }
            QPushButton.ptzBtn:hover {
                background-color: #0284c7;
                color: #ffffff;
                border-color: #7dd3fc;
            }
            QPushButton.ptzBtn:pressed {
                background-color: #0369a1;
            }
            QPushButton#btnPtzCenter {
                background-color: #1e293b;
                border: 1.5px solid #10b981;
                border-radius: 10px;
                min-width: 50px;
                min-height: 50px;
                font-size: 16px;
                color: #10b981;
            }
            QPushButton#btnPtzCenter:hover {
                background-color: #10b981;
                color: #000000;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #1e293b;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #06b6d4;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #f8fafc;
                border: 2px solid #06b6d4;
                width: 14px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 8px;
            }
            QTextEdit {
                background-color: #060911;
                border: 1px solid #1e293b;
                border-radius: 8px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                color: #94a3b8;
            }
            QTabWidget::pane {
                border: 1px solid #1e293b;
                border-radius: 8px;
                background-color: #111827;
            }
            QTabBar::tab {
                background-color: #0b1120;
                border: 1px solid #1e293b;
                border-bottom: none;
                padding: 7px 14px;
                border-top-left-radius: 7px;
                border-top-right-radius: 7px;
                margin-right: 3px;
                color: #94a3b8;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #111827;
                border-color: #06b6d4;
                color: #38bdf8;
                font-weight: bold;
            }
        """)

    def _make_badge(self, text: str, bg: str = "#1e293b", fg: str = "#cbd5e1") -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            border-radius: 6px;
            padding: 4px 10px;
            font-family: 'Consolas', 'Segoe UI', monospace;
            font-size: 11px;
            font-weight: bold;
        """)
        return lbl

    def _init_ui(self):
        root_widget = QWidget()
        self.setCentralWidget(root_widget)
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(12, 10, 12, 10)
        root_layout.setSpacing(10)

        # =============================================================
        # TOP HEADER BAR: GARDA Brand + Live ONVIF Telemetry Pills
        # =============================================================
        header_frame = QFrame()
        header_frame.setObjectName("headerBar")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(16, 10, 16, 10)

        brand_title = QLabel("🛡️ GARDA DESKTOP")
        brand_title.setStyleSheet("font-size: 18px; font-weight: 900; color: #f8fafc; letter-spacing: 1px;")
        brand_sub = QLabel("TACTICAL DUAL-LENS ONVIF COMMAND CENTER")
        brand_sub.setStyleSheet("font-size: 10px; font-weight: bold; color: #06b6d4; letter-spacing: 1.5px;")

        brand_col = QVBoxLayout()
        brand_col.setSpacing(1)
        brand_col.addWidget(brand_title)
        brand_col.addWidget(brand_sub)
        header_layout.addLayout(brand_col)

        header_layout.addStretch()

        # Live Telemetry Badges
        self.badge_onvif = self._make_badge("ONVIF :8899 CHECKING...", "#1e293b", "#94a3b8")
        self.badge_vlc = self._make_badge("VPU: -", "#1e293b", "#94a3b8")
        self.badge_uptime = self._make_badge("UPTIME: -", "#0f172a", "#38bdf8")
        self.badge_ram = self._make_badge("RAM FREE: -", "#0f172a", "#a855f7")
        self.badge_stream = self._make_badge("⚪ STANDBY", "#1e293b", "#cbd5e1")

        header_layout.addWidget(self.badge_onvif)
        header_layout.addWidget(self.badge_vlc)
        header_layout.addWidget(self.badge_uptime)
        header_layout.addWidget(self.badge_ram)
        header_layout.addWidget(self.badge_stream)

        root_layout.addWidget(header_frame)

        # =============================================================
        # MAIN BODY: Left (Dual Video Wall) + Right (Tactical Dock)
        # =============================================================
        body_layout = QHBoxLayout()
        body_layout.setSpacing(12)

        # -------------------------------------------------------------
        # LEFT PANEL: Dual-Lens Video Wall + Action Bar
        # -------------------------------------------------------------
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # Action Bar above video
        video_toolbar = QHBoxLayout()
        self.lbl_stream_stats = QLabel("📊 Lensa 1: -  |  Lensa 2: -")
        self.lbl_stream_stats.setStyleSheet("color: #38bdf8; font-family: Consolas; font-weight: bold; font-size: 12px;")

        video_toolbar.addWidget(self.lbl_stream_stats)
        video_toolbar.addStretch()

        video_toolbar.addWidget(QLabel("Mode Layar:"))
        self.cmb_view_mode = QComboBox()
        self.cmb_view_mode.addItems([
            "Dual Lensa (Atas - Bawah)",
            "Dual Lensa (Kiri - Kanan)",
            "Fokus Lensa 1 (Port 1234)",
            "Fokus Lensa 2 (Port 1235)"
        ])
        self.cmb_view_mode.currentIndexChanged.connect(self.on_view_mode_changed)
        video_toolbar.addWidget(self.cmb_view_mode)

        self.btn_snapshot = QPushButton("📷 Snapshot")
        self.btn_snapshot.clicked.connect(self.on_snapshot_clicked)

        self.btn_record = QPushButton("⏺ Rekam MP4")
        self.btn_record.clicked.connect(self.on_record_clicked)

        self.btn_open_snaps = QPushButton("📁 Galeri")
        self.btn_open_snaps.clicked.connect(lambda: self._open_dir(self.config.get("snapshots_dir", "snapshots")))

        self.btn_fullscreen = QPushButton("⛶ Fullscreen")
        self.btn_fullscreen.clicked.connect(self._toggle_fullscreen)

        video_toolbar.addWidget(self.btn_snapshot)
        video_toolbar.addWidget(self.btn_record)
        video_toolbar.addWidget(self.btn_open_snaps)
        video_toolbar.addWidget(self.btn_fullscreen)

        left_layout.addLayout(video_toolbar)

        # Dual Video Container
        self.video_container = QWidget()
        self.video_box_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom, self.video_container)
        self.video_box_layout.setContentsMargins(0, 0, 0, 0)
        self.video_box_layout.setSpacing(8)

        # Lens 1 Widget (Port 1234)
        self.lens1_wrapper = QWidget()
        l1_layout = QVBoxLayout(self.lens1_wrapper)
        l1_layout.setContentsMargins(0, 0, 0, 0)
        l1_layout.setSpacing(3)
        l1_hdr = QHBoxLayout()
        self.lbl_lens1_title = QLabel("🟦 LENSA 1 (UTAMA / PTZ) — RTSP :1234 [Profile_1]")
        self.lbl_lens1_title.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px; letter-spacing: 0.5px;")
        l1_hdr.addWidget(self.lbl_lens1_title)
        l1_hdr.addStretch()
        self.video_widget_1 = VideoWidget("LENSA 1 (Port 1234)", "#06b6d4")
        l1_layout.addLayout(l1_hdr)
        l1_layout.addWidget(self.video_widget_1, stretch=1)

        # Lens 2 Widget (Port 1235)
        self.lens2_wrapper = QWidget()
        l2_layout = QVBoxLayout(self.lens2_wrapper)
        l2_layout.setContentsMargins(0, 0, 0, 0)
        l2_layout.setSpacing(3)
        l2_hdr = QHBoxLayout()
        self.lbl_lens2_title = QLabel("🟪 LENSA 2 (WIDE / FIXED) — RTSP :1235 [Profile_2]")
        self.lbl_lens2_title.setStyleSheet("color: #c084fc; font-weight: bold; font-size: 11px; letter-spacing: 0.5px;")
        l2_hdr.addWidget(self.lbl_lens2_title)
        l2_hdr.addStretch()
        self.video_widget_2 = VideoWidget("LENSA 2 (Port 1235)", "#a855f7")
        l2_layout.addLayout(l2_hdr)
        l2_layout.addWidget(self.video_widget_2, stretch=1)

        self.video_box_layout.addWidget(self.lens1_wrapper, stretch=1)
        self.video_box_layout.addWidget(self.lens2_wrapper, stretch=1)

        left_layout.addWidget(self.video_container, stretch=1)

        # Footer Shortcut Bar
        quick_cam_layout = QHBoxLayout()
        lbl_tip = QLabel("⌨️ Pintasan: [Panah / WASD] Gerak PTZ  •  [Spasi] Posisi Tengah  •  [L] Spotlight  •  [N] Night IR")
        lbl_tip.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")

        btn_cam_249 = QPushButton("Unit .249")
        btn_cam_249.clicked.connect(lambda: self._set_quick_ip("192.168.18.249"))

        btn_cam_250 = QPushButton("Unit .250")
        btn_cam_250.clicked.connect(lambda: self._set_quick_ip("192.168.18.250"))

        quick_cam_layout.addWidget(lbl_tip)
        quick_cam_layout.addStretch()
        quick_cam_layout.addWidget(btn_cam_249)
        quick_cam_layout.addWidget(btn_cam_250)
        left_layout.addLayout(quick_cam_layout)

        body_layout.addWidget(left_panel, stretch=7)

        # -------------------------------------------------------------
        # RIGHT PANEL: Tactical Control Dock
        # -------------------------------------------------------------
        right_panel = QWidget()
        right_panel.setFixedWidth(400)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # 1. Connection & ONVIF Discovery Card
        grp_conn = QGroupBox("KONEKSI & ONVIF DISCOVERY")
        conn_layout = QGridLayout(grp_conn)
        conn_layout.setSpacing(6)

        conn_layout.addWidget(QLabel("IP Kamera:"), 0, 0)
        self.txt_ip = QLineEdit(self.config.get("ip", "192.168.18.249"))
        conn_layout.addWidget(self.txt_ip, 0, 1, 1, 2)

        self.btn_scan_onvif = QPushButton("🔍 Scan LAN")
        self.btn_scan_onvif.setToolTip("Cari kamera ONVIF otomatis via WS-Discovery UDP 3702")
        self.btn_scan_onvif.clicked.connect(self.on_scan_onvif_clicked)
        conn_layout.addWidget(self.btn_scan_onvif, 0, 3)

        conn_layout.addWidget(QLabel("ONVIF Port:"), 1, 0)
        self.txt_onvif_port = QLineEdit(str(self.config.get("onvif_port", 8899)))
        conn_layout.addWidget(self.txt_onvif_port, 1, 1)

        conn_layout.addWidget(QLabel("PTZ Port:"), 1, 2)
        self.txt_ptz_port = QLineEdit(str(self.config.get("ptz_port", 7777)))
        conn_layout.addWidget(self.txt_ptz_port, 1, 3)

        conn_layout.addWidget(QLabel("RTSP L1:"), 2, 0)
        self.txt_rtsp_port = QLineEdit(str(self.config.get("rtsp_port", 1234)))
        conn_layout.addWidget(self.txt_rtsp_port, 2, 1)

        conn_layout.addWidget(QLabel("RTSP L2:"), 2, 2)
        self.txt_rtsp_port_2 = QLineEdit(str(self.config.get("rtsp_port_2", 1235)))
        conn_layout.addWidget(self.txt_rtsp_port_2, 2, 3)
        # Keep all port inputs within a valid TCP/UDP numeric range.
        for field in (self.txt_onvif_port, self.txt_ptz_port, self.txt_rtsp_port, self.txt_rtsp_port_2):
            field.setValidator(QIntValidator(1, 65535, self))

        btn_box = QHBoxLayout()
        self.btn_connect = QPushButton("⚡ HUBUNGKAN KAMERA")
        self.btn_connect.setObjectName("btnConnect")
        self.btn_connect.clicked.connect(self.on_connect_clicked)

        self.btn_disconnect = QPushButton("⏹ PUTUS")
        self.btn_disconnect.setObjectName("btnDisconnect")
        self.btn_disconnect.clicked.connect(self.on_disconnect_clicked)
        self.btn_disconnect.setEnabled(False)

        btn_box.addWidget(self.btn_connect, stretch=2)
        btn_box.addWidget(self.btn_disconnect, stretch=1)
        conn_layout.addLayout(btn_box, 3, 0, 1, 4)

        right_layout.addWidget(grp_conn)

        # 2. Tabs: Gimbal PTZ | Lampu & Optik | Info ONVIF
        tabs = QTabWidget()

        # --- TAB 1: GIMBAL PTZ ---
        tab_ptz = QWidget()
        ptz_layout = QVBoxLayout(tab_ptz)
        ptz_layout.setSpacing(10)

        dpad_grid = QGridLayout()
        dpad_grid.setSpacing(8)

        btn_up_left = self._create_ptz_btn("⬉", "up_left")
        btn_up = self._create_ptz_btn("▲", "up")
        btn_up_right = self._create_ptz_btn("⬈", "up_right")

        btn_left = self._create_ptz_btn("◀", "left")
        btn_center = QPushButton("🏠")
        btn_center.setObjectName("btnPtzCenter")
        btn_center.setToolTip("Posisi Tengah (x=515, y=70)")
        btn_center.clicked.connect(self.on_ptz_center)
        btn_right = self._create_ptz_btn("▶", "right")

        btn_down_left = self._create_ptz_btn("⬋", "down_left")
        btn_down = self._create_ptz_btn("▼", "down")
        btn_down_right = self._create_ptz_btn("⬊", "down_right")

        dpad_grid.addWidget(btn_up_left, 0, 0)
        dpad_grid.addWidget(btn_up, 0, 1)
        dpad_grid.addWidget(btn_up_right, 0, 2)

        dpad_grid.addWidget(btn_left, 1, 0)
        dpad_grid.addWidget(btn_center, 1, 1)
        dpad_grid.addWidget(btn_right, 1, 2)

        dpad_grid.addWidget(btn_down_left, 2, 0)
        dpad_grid.addWidget(btn_down, 2, 1)
        dpad_grid.addWidget(btn_down_right, 2, 2)

        ptz_layout.addLayout(dpad_grid)

        # Step Size Slider
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Kecepatan / Step:"))
        self.slider_step = QSlider(Qt.Orientation.Horizontal)
        self.slider_step.setRange(5, 100)
        self.slider_step.setValue(int(self.config.get("ptz_step", 30)))
        self.lbl_step_val = QLabel(f"{self.slider_step.value()}")
        self.lbl_step_val.setStyleSheet("font-family: Consolas; font-weight: bold; color: #06b6d4;")
        self.slider_step.valueChanged.connect(lambda v: self.lbl_step_val.setText(str(v)))
        step_layout.addWidget(self.slider_step)
        step_layout.addWidget(self.lbl_step_val)
        ptz_layout.addLayout(step_layout)

        ptz_Quick_row = QHBoxLayout()
        btn_home_pos = QPushButton("🏠 Posisi Tengah")
        btn_home_pos.clicked.connect(self.on_ptz_center)
        btn_reset_calib = QPushButton("⚙️ Kalibrasi Motor")
        btn_reset_calib.clicked.connect(self.on_ptz_reset)
        ptz_Quick_row.addWidget(btn_home_pos)
        ptz_Quick_row.addWidget(btn_reset_calib)
        ptz_layout.addLayout(ptz_Quick_row)

        tabs.addTab(tab_ptz, "🕹️ Gimbal PTZ")

        # --- TAB 2: LAMPU & OPTIK ---
        tab_features = QWidget()
        feat_layout = QVBoxLayout(tab_features)
        feat_layout.setSpacing(8)

        light_box = QGroupBox("PENCAHAYAAN & FILTER IR-CUT")
        l_layout = QVBoxLayout(light_box)

        self.btn_white_light = QPushButton("💡 White Spotlight LED: OFF")
        self.btn_white_light.clicked.connect(self.on_toggle_white_light)

        self.btn_ir_light = QPushButton("🌙 IR Night Vision (GPIO 44): OFF")
        self.btn_ir_light.clicked.connect(self.on_toggle_ir_light)

        ircut_row = QHBoxLayout()
        btn_day = QPushButton("☀️ Filter Siang (Day)")
        btn_day.clicked.connect(lambda: self.on_set_ircut(False))
        btn_night = QPushButton("🌑 Filter Malam (Night)")
        btn_night.clicked.connect(lambda: self.on_set_ircut(True))
        ircut_row.addWidget(btn_day)
        ircut_row.addWidget(btn_night)

        l_layout.addWidget(self.btn_white_light)
        l_layout.addWidget(self.btn_ir_light)
        l_layout.addLayout(ircut_row)
        feat_layout.addWidget(light_box)

        motion_box = QGroupBox("OTOMASI AI & PATROLI")
        m_layout = QVBoxLayout(motion_box)

        self.btn_tracking = QPushButton("🎯 AI Human Auto-Tracking: OFF")
        self.btn_tracking.clicked.connect(self.on_toggle_tracking)

        self.btn_cruise = QPushButton("🔄 360° Cruise Patrol: OFF")
        self.btn_cruise.clicked.connect(self.on_toggle_cruise)

        m_layout.addWidget(self.btn_tracking)
        m_layout.addWidget(self.btn_cruise)
        feat_layout.addWidget(motion_box)

        feat_layout.addStretch()
        tabs.addTab(tab_features, "💡 Lampu & AI")

        # --- TAB 3: INFO ONVIF & SISTEM ---
        tab_info = QWidget()
        info_layout = QVBoxLayout(tab_info)
        info_layout.setSpacing(8)

        self.lbl_onvif_details = QLabel(
            "Manufacturer : CleanTV\n"
            "Model        : FH8852V201_DualLens\n"
            "Firmware     : CleanTV_v1.0\n"
            "Serial Number: XQ2325415UBER\n"
            "ONVIF URL    : http://192.168.18.249:8899/onvif/device_service\n"
            "RTSP Lensa 1 : rtsp://192.168.18.249:1234/\n"
            "RTSP Lensa 2 : rtsp://192.168.18.249:1235/"
        )
        self.lbl_onvif_details.setStyleSheet("""
            background-color: #070a12;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 10px;
            font-family: Consolas, monospace;
            font-size: 11px;
            color: #38bdf8;
        """)
        self.lbl_onvif_details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addWidget(self.lbl_onvif_details)

        btn_refresh_info = QPushButton("🔄 Cek Ulang ONVIF & Telemetry")
        btn_refresh_info.clicked.connect(self._poll_telemetry)
        info_layout.addWidget(btn_refresh_info)

        btn_reboot = QPushButton("⚠️ Reboot Kamera (Warm Reset)")
        btn_reboot.setStyleSheet("border-color: #ef4444; color: #fca5a5;")
        btn_reboot.clicked.connect(self.on_reboot_camera)
        info_layout.addWidget(btn_reboot)

        info_layout.addStretch()
        tabs.addTab(tab_info, "📡 ONVIF")

        # GARDA AI server remains a separate Windows/Linux process; this native
        # Qt client reads authenticated metadata/evidence on worker threads.
        self.ai_events_panel = GardaAiDesktopPanel(self)
        tabs.addTab(self.ai_events_panel, "🧠 AI Events")

        right_layout.addWidget(tabs)

        # 3. Activity Log Console
        grp_log = QGroupBox("LOG KOMANDO & TELEMETRI")
        log_layout = QVBoxLayout(grp_log)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setFixedHeight(125)
        log_layout.addWidget(self.txt_log)

        btn_clear_log = QPushButton("Bersihkan Log")
        btn_clear_log.clicked.connect(self.txt_log.clear)
        log_layout.addWidget(btn_clear_log)

        right_layout.addWidget(grp_log)

        body_layout.addWidget(right_panel, stretch=3)
        root_layout.addLayout(body_layout, stretch=1)

        self.log("GARDA Desktop siap. Daemon ONVIF :8899 terdeteksi aktif.")

    def _create_ptz_btn(self, symbol: str, direction: str) -> QPushButton:
        btn = QPushButton(symbol)
        btn.setProperty("class", "ptzBtn")
        btn.clicked.connect(lambda: self.on_ptz_move(direction))
        return btn

    def _setup_shortcuts(self):
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, lambda: self.on_ptz_move("left"))
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, lambda: self.on_ptz_move("right"))
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, lambda: self.on_ptz_move("up"))
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, lambda: self.on_ptz_move("down"))

        QShortcut(QKeySequence(Qt.Key.Key_A), self, lambda: self.on_ptz_move("left"))
        QShortcut(QKeySequence(Qt.Key.Key_D), self, lambda: self.on_ptz_move("right"))
        QShortcut(QKeySequence(Qt.Key.Key_W), self, lambda: self.on_ptz_move("up"))
        QShortcut(QKeySequence(Qt.Key.Key_S), self, lambda: self.on_ptz_move("down"))

        QShortcut(QKeySequence(Qt.Key.Key_L), self, self.on_toggle_white_light)
        QShortcut(QKeySequence(Qt.Key.Key_N), self, self.on_toggle_ir_light)
        QShortcut(QKeySequence(Qt.Key.Key_T), self, self.on_toggle_tracking)
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.on_ptz_center)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def on_view_mode_changed(self, idx: int):
        if idx == 0:
            self.video_box_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self.lens1_wrapper.setVisible(True)
            self.lens2_wrapper.setVisible(True)
        elif idx == 1:
            self.video_box_layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.lens1_wrapper.setVisible(True)
            self.lens2_wrapper.setVisible(True)
        elif idx == 2:
            self.lens1_wrapper.setVisible(True)
            self.lens2_wrapper.setVisible(False)
        elif idx == 3:
            self.lens1_wrapper.setVisible(False)
            self.lens2_wrapper.setVisible(True)

    def _set_quick_ip(self, ip: str):
        self.txt_ip.setText(ip)
        self.log(f"Target IP diubah ke {ip}")
        self._poll_telemetry()

    def _open_dir(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(directory)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", directory])
        else:
            subprocess.Popen(["xdg-open", directory])

    def log(self, message: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.txt_log.append(f"[{ts}] {message}")

    @staticmethod
    def _parse_port(text: str, default: int) -> int:
        try:
            port = int(text.strip() or str(default))
        except ValueError as exc:
            raise ValueError("Port harus berupa angka 1 sampai 65535") from exc
        if not 1 <= port <= 65535:
            raise ValueError("Port harus antara 1 dan 65535")
        return port

    # -------------------------------------------------------------
    # Live ONVIF & REST Telemetry Polling
    # -------------------------------------------------------------
    def _poll_telemetry(self):
        ip = self.txt_ip.text().strip()
        if self._telemetry_inflight:
            return
        try:
            onvif_port = self._parse_port(self.txt_onvif_port.text(), 8899)
        except ValueError as exc:
            self.log(str(exc))
            return
        self._telemetry_inflight = True

        def worker():
            try:
                client = SriHomeClient(ip, onvif_port=onvif_port)
                ok, data = client.get_telemetry()
                self.sig.updated.emit(ok, data)
                if ok:
                    ok_i, info = client.get_onvif_device_info()
                    if ok_i:
                        self.sig.device_info_ready.emit(True, info)
            except Exception:
                self.sig.log_msg.emit("Telemetry kamera belum tersedia")
            finally:
                self._telemetry_inflight = False

        threading.Thread(target=worker, daemon=True).start()

    def _on_telemetry_updated(self, ok: bool, data: Dict[str, Any]):
        onvif_port = self.txt_onvif_port.text().strip() or "8899"
        if ok and data.get("status") == "online":
            self.badge_onvif.setText(f"🟢 ONVIF :{onvif_port} ONLINE")
            self.badge_onvif.setStyleSheet("background-color: #064e3b; color: #34d399; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")

            vlc_ok = data.get("vlcview_running", False)
            self.badge_vlc.setText("VPU: ACTIVE" if vlc_ok else "VPU: RESTARTING")
            self.badge_vlc.setStyleSheet(
                "background-color: #0c4a6e; color: #38bdf8; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;"
                if vlc_ok else
                "background-color: #7c2d12; color: #fdba74; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;"
            )

            up_sec = int(data.get("uptime_sec", 0))
            hrs, rem = divmod(up_sec, 3600)
            mins, secs = divmod(rem, 60)
            self.badge_uptime.setText(f"⏱️ UPTIME: {hrs}h {mins}m {secs}s")

            ram = data.get("free_ram_kb", "-")
            self.badge_ram.setText(f"🧠 FREE RAM: {ram} KB")
        else:
            self.badge_onvif.setText(f"🔴 ONVIF :{onvif_port} OFFLINE")
            self.badge_onvif.setStyleSheet("background-color: #450a0a; color: #f87171; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")

    def _on_device_info_ready(self, ok: bool, info: Dict[str, str]):
        if not ok:
            return
        ip = self.txt_ip.text().strip()
        p_onvif = self.txt_onvif_port.text().strip()
        p_l1 = self.txt_rtsp_port.text().strip()
        p_l2 = self.txt_rtsp_port_2.text().strip()
        text = (
            f"Manufacturer : {info.get('Manufacturer', 'CleanTV')}\n"
            f"Model        : {info.get('Model', 'FH8852V201_DualLens')}\n"
            f"Firmware     : {info.get('FirmwareVersion', 'CleanTV_v1.0')}\n"
            f"Serial Number: {info.get('SerialNumber', 'XQ2325415UBER')}\n"
            f"Hardware ID  : {info.get('HardwareId', 'FH8852V201-Dual')}\n"
            f"ONVIF Service: http://{ip}:{p_onvif}/onvif/device_service\n"
            f"RTSP Lensa 1 : rtsp://{ip}:{p_l1}/\n"
            f"RTSP Lensa 2 : rtsp://{ip}:{p_l2}/"
        )
        self.lbl_onvif_details.setText(text)

    def on_scan_onvif_clicked(self):
        self.btn_scan_onvif.setEnabled(False)
        self.btn_scan_onvif.setText("⏳ Scanning...")
        self.log("Memulai WS-Discovery broadcast (UDP 3702)...")

        def worker():
            ips = SriHomeClient.discover_onvif_lan(1.5)
            self.sig.discovered_ips.emit(ips)

        threading.Thread(target=worker, daemon=True).start()

    def _on_discovered_ips(self, ips: list):
        self.btn_scan_onvif.setEnabled(True)
        self.btn_scan_onvif.setText("🔍 Scan LAN")
        if ips:
            self.txt_ip.setText(ips[0])
            self.log(f"WS-Discovery menemukan kamera ONVIF: {', '.join(ips)}")
            self._poll_telemetry()
        else:
            self.log("WS-Discovery selesai. Menggunakan IP yang terkonfigurasi.")

    # -------------------------------------------------------------
    # Connection Lifecycle (Dual RTSP Streams + ONVIF)
    # -------------------------------------------------------------
    def on_connect_clicked(self):
        ip = self.txt_ip.text().strip()
        try:
            onvif_port = self._parse_port(self.txt_onvif_port.text(), 8899)
            rtsp_port_1 = self._parse_port(self.txt_rtsp_port.text(), 1234)
            rtsp_port_2 = self._parse_port(self.txt_rtsp_port_2.text(), 1235)
            ptz_port = self._parse_port(self.txt_ptz_port.text(), 7777)
        except ValueError as exc:
            QMessageBox.warning(self, "Port tidak valid", str(exc))
            return
        step = self.slider_step.value()

        # Save config
        self.config["ip"] = ip
        self.config["onvif_port"] = onvif_port
        self.config["rtsp_port"] = rtsp_port_1
        self.config["rtsp_port_2"] = rtsp_port_2
        self.config["ptz_port"] = ptz_port
        self.config["ptz_step"] = step
        save_config(self.config)

        self.log(f"Menghubungkan ke GARDA Dual-Lens Camera ({ip})...")
        self.btn_connect.setEnabled(False)

        # 1. Initialize Unified Client
        self.srihome = SriHomeClient(ip, onvif_port=onvif_port, ptz_port=ptz_port, telnet_port=23)
        # Do not block the Qt event loop on camera REST/ONVIF probing.
        def probe():
            try:
                ok, msg, tele = self.srihome.check_connection()
                self.sig.log_msg.emit(msg)
                if tele:
                    self.sig.updated.emit(ok, tele)
            except Exception:
                self.sig.log_msg.emit("Probe kamera belum berhasil; RTSP tetap dicoba")
        threading.Thread(target=probe, daemon=True).start()

        # Stop previous streams without abandoning any still-running QThread.
        if not self._stop_streams():
            self.log("Thread kamera belum berhenti; koneksi baru dibatalkan.")
            self.btn_disconnect.setEnabled(True)
            return

        # 2. Start Lens 1 Stream (Port 1234)
        rtsp_url_1 = f"rtsp://{ip}:{rtsp_port_1}/"
        self.log("Membuka Stream Lensa 1 (alamat RTSP disembunyikan)")
        self.stream_thread_1 = CameraStreamThread(rtsp_url_1)
        self.stream_thread_1.frame_ready.connect(self.video_widget_1.update_frame)
        self.stream_thread_1.status_changed.connect(lambda c, m: self._on_stream_status_changed(1, c, m))
        self.stream_thread_1.stats_updated.connect(lambda f, w, h: self._on_stream_stats_updated(1, f, w, h))
        self.stream_thread_1.recording_ended.connect(self._on_recording_finished)
        self.stream_thread_1.start()

        # 3. Start Lens 2 Stream (Port 1235)
        rtsp_url_2 = f"rtsp://{ip}:{rtsp_port_2}/"
        self.log("Membuka Stream Lensa 2 (alamat RTSP disembunyikan)")
        self.stream_thread_2 = CameraStreamThread(rtsp_url_2)
        self.stream_thread_2.frame_ready.connect(self.video_widget_2.update_frame)
        self.stream_thread_2.status_changed.connect(lambda c, m: self._on_stream_status_changed(2, c, m))
        self.stream_thread_2.stats_updated.connect(lambda f, w, h: self._on_stream_stats_updated(2, f, w, h))
        self.stream_thread_2.recording_ended.connect(self._on_recording_finished)
        self.stream_thread_2.start()

        self.btn_disconnect.setEnabled(True)

    def _stop_streams(self) -> bool:
        all_stopped = True
        for field in ("stream_thread_1", "stream_thread_2"):
            thread = getattr(self, field)
            if thread is not None:
                if thread.stop():
                    setattr(self, field, None)
                else:
                    all_stopped = False
        return all_stopped

    def on_disconnect_clicked(self):
        if not self._stop_streams():
            self.log("Masih menunggu thread kamera berhenti; coba putuskan kembali.")
            self.btn_disconnect.setEnabled(True)
            return
        self.is_recording = False
        self.btn_record.setText("⏺ Rekam MP4")
        self.btn_record.setStyleSheet("")
        self.is_connected = False
        self.badge_stream.setText("⚪ DISCONNECTED")
        self.badge_stream.setStyleSheet("background-color: #1e293b; color: #94a3b8; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        self.lbl_stream_stats.setText("📊 Lensa 1: -  |  Lensa 2: -")
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.log("Transmisi video kedua lensa dihentikan.")

    def _on_recording_finished(self, path: str):
        active = any(thread is not None and thread.is_recording_active
                     for thread in (self.stream_thread_1, self.stream_thread_2))
        if self.is_recording and not active:
            self.is_recording = False
            self.btn_record.setText("⏺ Rekam MP4")
            self.btn_record.setStyleSheet("")
            self.log("Perekaman dihentikan; periksa file MP4 hasil rekaman.")
        if not path:
            self.log("Ada rekaman yang tidak menghasilkan file MP4 valid.")

    def _on_stream_status_changed(self, lens_id: int, connected: bool, message: str):
        self.log(f"Lensa {lens_id}: {message}")
        c1 = self.stream_thread_1.is_connected if self.stream_thread_1 else False
        c2 = self.stream_thread_2.is_connected if self.stream_thread_2 else False
        if c1 and c2:
            self.badge_stream.setText("🟢 DUAL LIVE 1080P")
            self.badge_stream.setStyleSheet("background-color: #064e3b; color: #34d399; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        elif c1 or c2:
            self.badge_stream.setText(f"🟢 LIVE (Lensa {'1' if c1 else '2'})")
            self.badge_stream.setStyleSheet("background-color: #064e3b; color: #34d399; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        else:
            self.badge_stream.setText("🟡 CONNECTING...")
            self.badge_stream.setStyleSheet("background-color: #713f12; color: #fde047; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")

    def _on_stream_stats_updated(self, lens_id: int, fps: float, w: int, h: int):
        if lens_id == 1:
            self._fps_1 = fps
            self._res_1 = f"{w}x{h}"
        else:
            self._fps_2 = fps
            self._res_2 = f"{w}x{h}"
        self.lbl_stream_stats.setText(f"📊 Lensa 1: {self._fps_1} FPS ({self._res_1})   |   Lensa 2: {self._fps_2} FPS ({self._res_2})")

    # -------------------------------------------------------------
    # PTZ Gimbal Actions
    # -------------------------------------------------------------
    def _ensure_client(self) -> SriHomeClient:
        if not self.srihome:
            ip = self.txt_ip.text().strip()
            onvif_port = int(self.txt_onvif_port.text().strip() or "8899")
            ptz_port = int(self.txt_ptz_port.text().strip() or "7777")
            self.srihome = SriHomeClient(ip, onvif_port=onvif_port, ptz_port=ptz_port)
        return self.srihome

    def on_ptz_move(self, direction: str):
        client = self._ensure_client()
        step = self.slider_step.value()

        def do_move():
            if direction == "left":
                ok, msg = client.move_left(step)
            elif direction == "right":
                ok, msg = client.move_right(step)
            elif direction == "up":
                ok, msg = client.move_up(step)
            elif direction == "down":
                ok, msg = client.move_down(step)
            elif direction == "up_left":
                client.move_up(step)
                ok, msg = client.move_left(step)
            elif direction == "up_right":
                client.move_up(step)
                ok, msg = client.move_right(step)
            elif direction == "down_left":
                client.move_down(step)
                ok, msg = client.move_left(step)
            elif direction == "down_right":
                client.move_down(step)
                ok, msg = client.move_right(step)
            else:
                ok, msg = False, "Unknown"

            if not ok:
                self.sig.log_msg.emit(f"PTZ {direction} gagal: {msg}")

        threading.Thread(target=do_move, daemon=True).start()
        self.log(f"PTZ: {direction.upper()} (Step: {step})")

    def on_ptz_center(self):
        client = self._ensure_client()

        def do_center():
            ok, msg = client.center_position()
            self.sig.log_msg.emit(f"PTZ Home: {msg}")

        threading.Thread(target=do_center, daemon=True).start()

    def on_ptz_reset(self):
        client = self._ensure_client()

        def do_reset():
            ok, msg = client.reset_calibrate()
            self.sig.log_msg.emit(f"Kalibrasi Motor PTZ: {msg}")

        threading.Thread(target=do_reset, daemon=True).start()
        self.log("Mengirim komando Kalibrasi Motor PTZ...")

    # -------------------------------------------------------------
    # Lighting, IR-Cut & AI Toggles
    # -------------------------------------------------------------
    def on_toggle_white_light(self):
        client = self._ensure_client()
        self.is_white_light_on = not self.is_white_light_on
        state = self.is_white_light_on
        state_str = "ON" if state else "OFF"
        self.btn_white_light.setText(f"💡 White Spotlight LED: {state_str}")
        self.btn_white_light.setStyleSheet(
            "background-color: #f59e0b; color: #000000; font-weight: bold;" if state else ""
        )

        def do_toggle():
            ok, msg = client.set_white_light(state)
            self.sig.log_msg.emit(msg)

        threading.Thread(target=do_toggle, daemon=True).start()

    def on_toggle_ir_light(self):
        client = self._ensure_client()
        self.is_ir_on = not self.is_ir_on
        state = self.is_ir_on
        state_str = "ON" if state else "OFF"
        self.btn_ir_light.setText(f"🌙 IR Night Vision (GPIO 44): {state_str}")
        self.btn_ir_light.setStyleSheet(
            "background-color: #8b5cf6; color: #ffffff; font-weight: bold;" if state else ""
        )

        def do_toggle():
            ok, msg = client.set_ir_light(state)
            self.sig.log_msg.emit(msg)

        threading.Thread(target=do_toggle, daemon=True).start()

    def on_set_ircut(self, night_mode: bool):
        client = self._ensure_client()

        def do_ircut():
            ok, msg = client.set_ircut_filter(night_mode)
            self.sig.log_msg.emit(msg)

        threading.Thread(target=do_ircut, daemon=True).start()

    def on_toggle_tracking(self):
        client = self._ensure_client()
        self.is_tracking_on = not self.is_tracking_on
        state = self.is_tracking_on
        state_str = "ON" if state else "OFF"
        self.btn_tracking.setText(f"🎯 AI Human Auto-Tracking: {state_str}")
        self.btn_tracking.setStyleSheet(
            "background-color: #10b981; color: #000000; font-weight: bold;" if state else ""
        )

        def do_toggle():
            ok, msg = client.set_tracking(state)
            self.sig.log_msg.emit(f"AI Human Tracking: {'AKTIF' if state else 'NONAKTIF'} ({msg})")

        threading.Thread(target=do_toggle, daemon=True).start()

    def on_toggle_cruise(self):
        client = self._ensure_client()
        self.is_cruise_on = not self.is_cruise_on
        state = self.is_cruise_on
        state_str = "ON" if state else "OFF"
        self.btn_cruise.setText(f"🔄 360° Cruise Patrol: {state_str}")
        self.btn_cruise.setStyleSheet(
            "background-color: #06b6d4; color: #000000; font-weight: bold;" if state else ""
        )

        def do_toggle():
            ok, msg = client.set_cruise(state)
            self.sig.log_msg.emit(f"Patroli 360°: {'AKTIF' if state else 'BERHENTI'} ({msg})")

        threading.Thread(target=do_toggle, daemon=True).start()

    def on_reboot_camera(self):
        ans = QMessageBox.question(
            self,
            "Konfirmasi Reboot",
            "Apakah Anda yakin ingin me-reboot kamera ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if ans == QMessageBox.StandardButton.Yes:
            client = self._ensure_client()
            threading.Thread(target=lambda: client.execute_shell_cmd("reboot"), daemon=True).start()
            self.log("Perintah Warm Reboot dikirim ke kamera.")
            self.on_disconnect_clicked()

    # -------------------------------------------------------------
    # Snapshot & MP4 Recording (Dual Lens)
    # -------------------------------------------------------------
    def on_snapshot_clicked(self):
        c1 = self.stream_thread_1 and self.stream_thread_1.is_connected
        c2 = self.stream_thread_2 and self.stream_thread_2.is_connected
        if not c1 and not c2:
            QMessageBox.warning(self, "Peringatan", "Stream video belum terhubung!")
            return

        snapshots_dir = self.config.get("snapshots_dir", "snapshots")
        os.makedirs(snapshots_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved = []

        if c1:
            f1 = os.path.join(snapshots_dir, f"GARDA_Lensa1_{ts}.jpg")
            self.stream_thread_1.capture_snapshot(f1)
            saved.append(f1)
        if c2:
            f2 = os.path.join(snapshots_dir, f"GARDA_Lensa2_{ts}.jpg")
            self.stream_thread_2.capture_snapshot(f2)
            saved.append(f2)

        self.log(f"Permintaan snapshot dikirim ({len(saved)} file)")
        QMessageBox.information(self, "Snapshot Diminta",
                                "Snapshot akan disimpan setelah frame berikutnya diterima:\n" + "\n".join(saved))

    def on_record_clicked(self):
        c1 = self.stream_thread_1 and self.stream_thread_1.is_connected
        c2 = self.stream_thread_2 and self.stream_thread_2.is_connected
        if not self.is_recording and not c1 and not c2:
            QMessageBox.warning(self, "Peringatan", "Stream video belum terhubung!")
            return

        if not self.is_recording:
            recordings_dir = self.config.get("recordings_dir", "recordings")
            os.makedirs(recordings_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")

            ok1 = False
            ok2 = False
            if c1:
                f1 = os.path.join(recordings_dir, f"GARDA_Lensa1_{ts}.mp4")
                ok1 = self.stream_thread_1.start_recording(f1)
            if c2:
                f2 = os.path.join(recordings_dir, f"GARDA_Lensa2_{ts}.mp4")
                ok2 = self.stream_thread_2.start_recording(f2)

            if ok1 or ok2:
                self.is_recording = True
                self.btn_record.setText("⏹ Stop Rekam")
                self.btn_record.setStyleSheet("background-color: #dc2626; color: white; font-weight: bold;")
                self.log("Perekaman MP4 Dual-Lens dimulai...")
            else:
                QMessageBox.critical(self, "Error", "Gagal memulai perekaman video!")
        else:
            saved = []
            if self.stream_thread_1:
                s1 = self.stream_thread_1.stop_recording()
                if s1:
                    saved.append(s1)
            if self.stream_thread_2:
                s2 = self.stream_thread_2.stop_recording()
                if s2:
                    saved.append(s2)

            self.is_recording = False
            self.btn_record.setText("⏺ Rekam MP4")
            self.btn_record.setStyleSheet("")
            self.log("Perekaman MP4 Dual-Lens selesai.")
            QMessageBox.information(self, "Rekaman Selesai", "File MP4 tersimpan di:\n" + "\n".join(saved))

    def closeEvent(self, event):
        # QThread must finish before the containing QWidget can be destroyed.
        if not self._stop_streams():
            self.log("Tunda penutupan: kamera masih melepas koneksi RTSP.")
            event.ignore()
            QTimer.singleShot(250, self.close)
            return
        event.accept()


# Backward compatibility alias
CleanTVMainWindow = GardaMainWindow


def main():
    app = QApplication(sys.argv)
    window = GardaMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
