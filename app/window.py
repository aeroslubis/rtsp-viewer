"""
window.py - Minimalist Multi-Stream RTSP Window
Supports configurable 4, 6, and 12 stream grids,
auto-switching to stream 102 (SD) in grid and stream 101 (HD) in fullscreen.
"""

from typing import List, Optional

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QKeyEvent
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

        self.maximized_channel: Optional[int] = None

        self.setWindowTitle(f"RTSP Multi-View ({self.stream_count} Stream)")
        self.setWindowIcon(get_app_icon())
        self.resize(1180, 720)
        self.setMinimumSize(680, 420)
        self.setStyleSheet("background-color: #030712;")

        self.workers: List[Optional[StreamWorker]] = [None] * MAX_CHANNELS
        self.video_widgets: List[VideoWidget] = []

        # Central container
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.grid = QGridLayout(self.central_widget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(2)

        # Initialize all 12 VideoWidgets
        for ch in range(MAX_CHANNELS):
            ch_cfg = self.config["channels"][ch]
            vw = VideoWidget(ch, ch_cfg, self.central_widget)
            vw.request_reconnect.connect(lambda c: self.start_single_stream(c, self.maximized_channel == c))
            vw.request_settings.connect(self.open_settings)
            vw.double_clicked.connect(self.toggle_fullscreen_channel)
            vw.request_toggle_fullscreen.connect(self.toggle_fullscreen_channel)
            self.video_widgets.append(vw)

        # Apply initial grid layout
        self.apply_grid(self.stream_count, auto_start=False)

        # Shortcuts
        QShortcut(QKeySequence("F2"), self, lambda: self.open_settings(0))
        QShortcut(QKeySequence("Ctrl+,"), self, lambda: self.open_settings(0))
        QShortcut(QKeySequence("Escape"), self, self._on_escape_pressed)

        # Auto-connect streams on startup
        self._startup_timer = QTimer(self)
        self._startup_timer.setSingleShot(True)
        self._startup_timer.timeout.connect(self.start_all_active_streams)
        self._startup_timer.start(200)

    def _on_escape_pressed(self):
        if self.maximized_channel is not None:
            self.restore_grid()

    def toggle_fullscreen_channel(self, ch: int):
        """Toggle single camera view between Fullscreen (101 HD) and Grid (102 SD)."""
        if self.maximized_channel == ch:
            self.restore_grid()
        else:
            self.maximize_channel(ch)

    def maximize_channel(self, ch: int):
        """Expand single camera to full view and switch to Stream 101 HD."""
        self.maximized_channel = ch
        cam_name = self.config["channels"][ch].get("name", f"Kamera {ch + 1}")
        self.setWindowTitle(f"RTSP Multi-View - {cam_name} [Fullscreen Stream 101 HD]")

        # Remove all widgets from grid
        for i in reversed(range(self.grid.count())):
            item = self.grid.takeAt(i)
            widget = item.widget()
            if widget:
                widget.hide()

        # Stop all other camera streams to save 100% CPU & bandwidth
        for i in range(MAX_CHANNELS):
            if i != ch:
                self.stop_single_stream(i)

        # Reset stretches
        for r in range(4):
            self.grid.setRowStretch(r, 0)
        for c in range(5):
            self.grid.setColumnStretch(c, 0)

        # Maximize chosen camera
        self.grid.addWidget(self.video_widgets[ch], 0, 0)
        self.grid.setRowStretch(0, 1)
        self.grid.setColumnStretch(0, 1)
        self.video_widgets[ch].show()

        # Start stream on 101 HD
        self.start_single_stream(ch, is_fullscreen=True)

    def restore_grid(self):
        """Return from single camera view to the active multi-camera grid."""
        self.maximized_channel = None
        for vw in self.video_widgets:
            vw.set_fullscreen_mode(False)

        self.apply_grid(self.stream_count, auto_start=True)

    def apply_grid(self, count: int, auto_start: bool = True):
        """Rearrange grid for 4 (2x2), 6 (2x3), or 12 (3x4) streams."""
        self.stream_count = count
        self.maximized_channel = None
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
                self.video_widgets[i].set_fullscreen_mode(False)
                self.video_widgets[i].show()
                if auto_start:
                    self.start_single_stream(i, is_fullscreen=False)
            else:
                self.video_widgets[i].hide()
                self.stop_single_stream(i)

    def set_stream_count(self, count: int):
        if count in (4, 6, 12):
            self.config["general"]["stream_count"] = count
            save_config(self.config)
            self.apply_grid(count, auto_start=True)

    def contextMenuEvent(self, event):
        """Global right click menu for quick access."""
        menu = QMenu(self)

        # Grid layout selection submenu
        menu_grid = menu.addMenu(get_icon("grid"), "Tata Letak Grid")
        grid_group = QActionGroup(self)

        act_4 = menu_grid.addAction("2 × 2 Grid  (4 Stream)")
        act_4.setCheckable(True)
        act_4.setChecked(self.stream_count == 4 and self.maximized_channel is None)
        act_4.triggered.connect(lambda: self.set_stream_count(4))
        grid_group.addAction(act_4)

        act_6 = menu_grid.addAction("2 × 3 Grid  (6 Stream)")
        act_6.setCheckable(True)
        act_6.setChecked(self.stream_count == 6 and self.maximized_channel is None)
        act_6.triggered.connect(lambda: self.set_stream_count(6))
        grid_group.addAction(act_6)

        act_12 = menu_grid.addAction("3 × 4 Grid  (12 Stream)")
        act_12.setCheckable(True)
        act_12.setChecked(self.stream_count == 12 and self.maximized_channel is None)
        act_12.triggered.connect(lambda: self.set_stream_count(12))
        grid_group.addAction(act_12)

        menu.addSeparator()

        if self.maximized_channel is not None:
            act_restore = menu.addAction(get_icon("grid"), "Kembali ke Grid (Stream 102 SD)")
            act_restore.triggered.connect(self.restore_grid)
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

    def start_single_stream(self, ch: int, is_fullscreen: bool = False):
        self.stop_single_stream(ch)

        ch_cfg = dict(self.config["channels"][ch])
        ch_cfg.update({
            "auto_reconnect": self.config.get("general", {}).get("auto_reconnect", True),
            "reconnect_interval_sec": self.config.get("general", {}).get("reconnect_interval_sec", 4),
        })

        main_url = ch_cfg.get("main_url", ch_cfg.get("url", "")).strip()
        sub_url = ch_cfg.get("sub_url", "").strip()
        if not main_url and not sub_url:
            return

        self.video_widgets[ch].set_fullscreen_mode(is_fullscreen)
        worker = StreamWorker(ch, ch_cfg, is_fullscreen=is_fullscreen)
        self.workers[ch] = worker
        self.video_widgets[ch].attach_worker(worker)
        worker.start()

    def stop_single_stream(self, ch: int):
        worker = self.workers[ch]
        if worker:
            self.workers[ch] = None
            worker.stop()
            worker.deleteLater()

    def start_all_active_streams(self):
        for ch in range(self.stream_count):
            self.start_single_stream(ch, is_fullscreen=False)

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
        if hasattr(self, "_startup_timer"):
            self._startup_timer.stop()
        for ch in range(MAX_CHANNELS):
            self.stop_single_stream(ch)
        event.accept()
        app = QApplication.instance()
        if app:
            app.quit()
