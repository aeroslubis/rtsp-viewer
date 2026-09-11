"""
window.py - Minimalist Multi-Stream RTSP Window
Supports configurable 4 (2x2), 6 (2x3), and 12 (3x4) stream grids.
"""

from typing import List, Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QShortcut, QMenu, QActionGroup, QApplication
)

from app.config import load_config, save_config, MAX_CHANNELS
from app.stream_worker import StreamWorker
from app.widgets.video_widget import VideoWidget
from app.widgets.settings_dialog import SettingsDialog
from app.icons import get_icon, get_app_icon


class MainWindow(QMainWindow):
    """Clean, uncluttered window showing 4, 6, or 12 RTSP video stream boxes."""

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.stream_count = self.config.get("general", {}).get("stream_count", 4)
        if self.stream_count not in (4, 6, 12):
            self.stream_count = 4

        self.setWindowTitle(f"RTSP Multi-View ({self.stream_count} Stream)")
        self.setWindowIcon(get_app_icon())
        self.resize(1180, 720)
        self.setMinimumSize(680, 420)
        self.setStyleSheet("background-color: #030712;")

        self.workers: List[Optional[StreamWorker]] = [None] * MAX_CHANNELS
        self.video_widgets: List[VideoWidget] = []

        # Central widget with tight grid
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.grid = QGridLayout(self.central_widget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(2)  # Clean 2px separator between stream tiles

        # Initialize all 12 VideoWidgets
        for ch in range(MAX_CHANNELS):
            ch_cfg = self.config["channels"][ch]
            vw = VideoWidget(ch, ch_cfg, self.central_widget)
            vw.request_reconnect.connect(self.start_single_stream)
            vw.request_settings.connect(self.open_settings)
            self.video_widgets.append(vw)

        # Apply initial grid layout
        self.apply_grid(self.stream_count, auto_start=False)

        # Shortcuts
        QShortcut(QKeySequence("F2"), self, lambda: self.open_settings(0))
        QShortcut(QKeySequence("Ctrl+,"), self, lambda: self.open_settings(0))

        # Auto-connect streams on startup
        QTimer.singleShot(200, self.start_all_active_streams)

    def apply_grid(self, count: int, auto_start: bool = True):
        """Rearrange grid for 4 (2x2), 6 (2x3), or 12 (3x4) streams."""
        self.stream_count = count
        self.setWindowTitle(f"RTSP Multi-View ({self.stream_count} Stream)")

        # Clear existing layout items
        for i in reversed(range(self.grid.count())):
            item = self.grid.takeAt(i)
            widget = item.widget()
            if widget:
                widget.hide()

        # Reset stretches
        for r in range(4):
            self.grid.setRowStretch(r, 0)
        for c in range(5):
            self.grid.setColumnStretch(c, 0)

        # Calculate rows and columns
        if count == 6:
            rows, cols = 2, 3
        elif count == 12:
            rows, cols = 3, 4
        else: # default 4
            rows, cols = 2, 2

        for r in range(rows):
            self.grid.setRowStretch(r, 1)
        for c in range(cols):
            self.grid.setColumnStretch(c, 1)

        # Place active widgets in grid and stop inactive ones
        for i in range(MAX_CHANNELS):
            if i < count:
                r = i // cols
                c = i % cols
                self.grid.addWidget(self.video_widgets[i], r, c)
                self.video_widgets[i].show()
                if auto_start:
                    self.start_single_stream(i)
            else:
                self.video_widgets[i].hide()
                self.stop_single_stream(i)

    def set_stream_count(self, count: int):
        if count in (4, 6, 12) and count != self.stream_count:
            self.config["general"]["stream_count"] = count
            save_config(self.config)
            self.apply_grid(count, auto_start=True)

    def contextMenuEvent(self, event):
        """Global right click menu for quick access."""
        menu = QMenu(self)

        # Grid layout selection submenu
        menu_grid = menu.addMenu(get_icon("camera"), "Tata Letak Grid")
        grid_group = QActionGroup(self)

        act_4 = menu_grid.addAction("4 Stream (2x2 Grid)")
        act_4.setCheckable(True)
        act_4.setChecked(self.stream_count == 4)
        act_4.triggered.connect(lambda: self.set_stream_count(4))
        grid_group.addAction(act_4)

        act_6 = menu_grid.addAction("6 Stream (2x3 Grid)")
        act_6.setCheckable(True)
        act_6.setChecked(self.stream_count == 6)
        act_6.triggered.connect(lambda: self.set_stream_count(6))
        grid_group.addAction(act_6)

        act_12 = menu_grid.addAction("12 Stream (3x4 Grid)")
        act_12.setCheckable(True)
        act_12.setChecked(self.stream_count == 12)
        act_12.triggered.connect(lambda: self.set_stream_count(12))
        grid_group.addAction(act_12)

        menu.addSeparator()

        act_settings = menu.addAction(get_icon("settings"), "Pengaturan Kamera (F2)...")
        act_settings.triggered.connect(lambda: self.open_settings(0))
        menu.addSeparator()

        act_reload = menu.addAction(get_icon("refresh"), "Hubungkan Ulang Semua")
        act_reload.triggered.connect(self.start_all_active_streams)

        act_stop = menu.addAction(get_icon("stop"), "Hentikan Semua")
        act_stop.triggered.connect(self.stop_all_streams)
        menu.addSeparator()

        act_quit = menu.addAction(get_icon("exit"), "Keluar")
        act_quit.triggered.connect(self.close)

        menu.exec_(event.globalPos())

    def start_single_stream(self, ch: int):
        self.stop_single_stream(ch)

        ch_cfg = dict(self.config["channels"][ch])
        ch_cfg.update({
            "auto_reconnect": self.config.get("general", {}).get("auto_reconnect", True),
            "reconnect_interval_sec": self.config.get("general", {}).get("reconnect_interval_sec", 4),
        })

        if not ch_cfg.get("url", "").strip():
            return

        worker = StreamWorker(ch, ch_cfg, self)
        self.workers[ch] = worker
        self.video_widgets[ch].attach_worker(worker)
        worker.start()

    def stop_single_stream(self, ch: int):
        worker = self.workers[ch]
        if worker:
            worker.stop()
            self.workers[ch] = None

    def start_all_active_streams(self):
        for ch in range(self.stream_count):
            self.start_single_stream(ch)

    def stop_all_streams(self):
        for ch in range(MAX_CHANNELS):
            self.stop_single_stream(ch)

    def open_settings(self, active_tab: int = 0):
        dlg = SettingsDialog(self.config, active_tab, self)
        dlg.settings_saved.connect(self.on_settings_updated)
        dlg.exec_()

    def on_settings_updated(self, new_config: dict):
        self.config = new_config
        new_count = new_config.get("general", {}).get("stream_count", 4)

        for ch in range(MAX_CHANNELS):
            self.video_widgets[ch].set_config(new_config["channels"][ch])

        self.apply_grid(new_count, auto_start=True)

    def closeEvent(self, event):
        for ch in range(MAX_CHANNELS):
            self.stop_single_stream(ch)
        event.accept()
        app = QApplication.instance()
        if app:
            app.quit()
