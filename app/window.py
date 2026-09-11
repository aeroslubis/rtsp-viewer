"""
window.py - Minimalist 4-Stream RTSP Window
Pure 4-box 2x2 stream display with modern icons and context menus.
"""

from typing import List, Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QShortcut, QMenu
)

from app.config import load_config, save_config
from app.stream_worker import StreamWorker
from app.widgets.video_widget import VideoWidget
from app.widgets.settings_dialog import SettingsDialog
from app.icons import get_icon, get_app_icon


class MainWindow(QMainWindow):
    """Clean, uncluttered window showing 4 RTSP video stream boxes."""

    def __init__(self):
        super().__init__()
        self.config = load_config()

        self.setWindowTitle("RTSP Multi-View (4 Stream)")
        self.setWindowIcon(get_app_icon())
        self.resize(1100, 680)
        self.setMinimumSize(640, 400)
        self.setStyleSheet("background-color: #030712;")

        self.workers: List[Optional[StreamWorker]] = [None, None, None, None]
        self.video_widgets: List[VideoWidget] = []

        # Central widget with tight 2x2 grid
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.grid = QGridLayout(self.central_widget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(2)  # Clean 2px separator between stream tiles

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for ch in range(4):
            ch_cfg = self.config["channels"][ch]
            vw = VideoWidget(ch, ch_cfg, self.central_widget)
            vw.request_reconnect.connect(self.start_single_stream)
            vw.request_settings.connect(self.open_settings)
            r, c = positions[ch]
            self.grid.addWidget(vw, r, c)
            self.video_widgets.append(vw)

        self.grid.setRowStretch(0, 1)
        self.grid.setRowStretch(1, 1)
        self.grid.setColumnStretch(0, 1)
        self.grid.setColumnStretch(1, 1)

        # Shortcuts
        QShortcut(QKeySequence("F2"), self, lambda: self.open_settings(0))
        QShortcut(QKeySequence("Ctrl+,"), self, lambda: self.open_settings(0))

        # Auto-connect streams on startup
        QTimer.singleShot(200, self.start_all_streams)

    def contextMenuEvent(self, event):
        """Global right click menu for quick access."""
        menu = QMenu(self)

        act_settings = menu.addAction(get_icon("settings"), "Pengaturan RTSP (F2)...")
        act_settings.triggered.connect(lambda: self.open_settings(0))
        menu.addSeparator()

        act_reload = menu.addAction(get_icon("refresh"), "Hubungkan Ulang Semua")
        act_reload.triggered.connect(self.start_all_streams)

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

    def start_all_streams(self):
        for ch in range(4):
            self.start_single_stream(ch)

    def stop_all_streams(self):
        for ch in range(4):
            self.stop_single_stream(ch)

    def open_settings(self, active_tab: int = 0):
        dlg = SettingsDialog(self.config, active_tab, self)
        dlg.settings_saved.connect(self.on_settings_updated)
        dlg.exec_()

    def on_settings_updated(self, new_config: dict):
        self.config = new_config
        for ch in range(4):
            self.video_widgets[ch].set_config(new_config["channels"][ch])
        self.start_all_streams()

    def closeEvent(self, event):
        for ch in range(4):
            self.stop_single_stream(ch)
        event.accept()
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.quit()
