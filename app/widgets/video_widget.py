"""
video_widget.py - Minimalist RTSP Video Stream Tile
Displays pure video stream with subtle camera label and right-click context menu.
"""

from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QImage, QPaintEvent, QContextMenuEvent
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QSizePolicy

from app.stream_worker import StreamWorker


class VideoWidget(QWidget):
    """
    Minimalist video display tile for one RTSP stream channel.
    Renders video smoothly with aspect ratio preservation and black letterboxing.
    """
    request_reconnect = pyqtSignal(int)
    request_settings = pyqtSignal(int)

    def __init__(self, channel_id: int, config: dict, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self.config = config
        self.worker: Optional[StreamWorker] = None

        self._image: Optional[QImage] = None
        self._fps: float = 0.0
        self._status_code: str = "stopped"
        self._status_msg: str = "Offline"
        self._camera_name: str = self.config.get("name", f"Kamera {channel_id + 1}")

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 150)
        self.setStyleSheet("background-color: #080c14;")

    def set_config(self, config: dict):
        self.config = config
        self._camera_name = config.get("name", f"Kamera {self.channel_id + 1}")
        if self.worker:
            self.worker.update_config(config)
        self.update()

    def attach_worker(self, worker: StreamWorker):
        self.worker = worker
        self.worker.frame_ready.connect(self.on_frame_ready)
        self.worker.status_changed.connect(self.on_status_changed)

    def on_frame_ready(self, channel_id: int, image: QImage, fps: float):
        if channel_id == self.channel_id:
            self._image = image
            self._fps = fps
            self.update()

    def on_status_changed(self, channel_id: int, code: str, msg: str):
        if channel_id == self.channel_id:
            self._status_code = code
            self._status_msg = msg
            if code != "live":
                self._image = None
            self.update()

    def contextMenuEvent(self, event: QContextMenuEvent):
        """Right click context menu for quick controls & settings."""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1f2937;
                color: #f3f4f6;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 18px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #2563eb;
                color: #ffffff;
            }
        """)

        act_title = menu.addAction(f"📹 {self._camera_name}")
        act_title.setEnabled(False)
        menu.addSeparator()

        act_reconnect = menu.addAction("🔄 Hubungkan Ulang")
        act_reconnect.triggered.connect(lambda: self.request_reconnect.emit(self.channel_id))

        if self.worker and self.worker.isRunning():
            act_stop = menu.addAction("■ Hentikan Stream")
            act_stop.triggered.connect(self.worker.stop)

        menu.addSeparator()
        act_settings = menu.addAction("⚙ Pengaturan Kamera...")
        act_settings.triggered.connect(lambda: self.request_settings.emit(self.channel_id))

        menu.exec_(event.globalPos())

    def mousePressEvent(self, event):
        # If stream is offline, left clicking opens settings
        if event.button() == Qt.LeftButton and self._status_code in ("stopped", "error"):
            if not self.config.get("url", "").strip():
                self.request_settings.emit(self.channel_id)
        super().mousePressEvent(event)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        rect = self.rect()

        # Fill background
        painter.fillRect(rect, QColor("#080c14"))

        if self._image and not self._image.isNull():
            # Draw video scaled maintaining aspect ratio
            scaled = self._image.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawImage(x, y, scaled)

            # Subtle camera name in top-left
            self._draw_subtle_label(painter, x + 8, y + 8)
        else:
            # Placeholder when offline / connecting
            self._draw_placeholder(painter, rect)

        # Subtle border between boxes
        painter.setPen(QColor("#1f2937"))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))

    def _draw_subtle_label(self, painter: QPainter, x: int, y: int):
        """Minimal subtle label on live video."""
        if self._image and not self._image.isNull():
            text = f"{self._camera_name} ({self._image.width()}x{self._image.height()})"
        else:
            text = self._camera_name
        font = QFont("Ubuntu", 9, QFont.Bold)
        painter.setFont(font)
        fm = painter.fontMetrics()
        w = fm.horizontalAdvance(text) + 12
        h = fm.height() + 6

        painter.fillRect(x, y, w, h, QColor(0, 0, 0, 140))
        painter.setPen(QColor(255, 255, 255, 220))
        painter.drawText(x + 6, y + fm.ascent() + 3, text)

    def _draw_placeholder(self, painter: QPainter, rect: QRect):
        """Draw placeholder when stream is not active."""
        center_x = rect.center().x()
        center_y = rect.center().y()

        # Camera Name
        painter.setPen(QColor("#9ca3af"))
        font = QFont("Ubuntu", 11, QFont.Bold)
        painter.setFont(font)
        painter.drawText(
            QRect(rect.left(), center_y - 20, rect.width(), 25),
            Qt.AlignCenter,
            self._camera_name
        )

        # Status text
        sub_font = QFont("Ubuntu", 9)
        painter.setFont(sub_font)
        if self._status_code == "connecting":
            painter.setPen(QColor("#60a5fa"))
            status_display = "Menghubungkan..."
        elif self._status_code == "reconnecting":
            painter.setPen(QColor("#fbbf24"))
            status_display = self._status_msg
        elif self._status_code == "error":
            painter.setPen(QColor("#f87171"))
            status_display = self._status_msg
        else:
            painter.setPen(QColor("#6b7280"))
            status_display = "Klik untuk atur URL" if not self.config.get("url") else "Offline"

        painter.drawText(
            QRect(rect.left(), center_y + 8, rect.width(), 20),
            Qt.AlignCenter,
            status_display
        )
