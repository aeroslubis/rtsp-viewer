"""
video_widget.py - Premium Minimalist RTSP Video Stream Tile
Features glassmorphic OSD badge, animated pulsing live indicator,
top-right hover action toolbar, and double-click 101/102 stream zoom.
"""

from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal, QRect, QTimer
from PyQt5.QtGui import (
    QPainter, QColor, QFont, QImage, QPaintEvent, QContextMenuEvent,
    QMouseEvent, QEnterEvent, QPen, QBrush, QLinearGradient
)
from PyQt5.QtWidgets import (
    QWidget, QMenu, QSizePolicy, QFrame, QHBoxLayout, QToolButton
)

from app.stream_worker import StreamWorker
from app.icons import get_icon


class VideoWidget(QWidget):
    """
    High-performance, beautifully styled video display tile for one RTSP stream channel.
    Renders video with preserved aspect ratio, glassmorphism badge, and interactive hover controls.
    """
    request_reconnect = pyqtSignal(int)
    request_settings = pyqtSignal(int)
    request_toggle_fullscreen = pyqtSignal(int)
    double_clicked = pyqtSignal(int)

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
        self._is_fullscreen: bool = False
        self._is_hovered: bool = False

        # Live pulsing animation
        self._pulse_state = 0
        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(500)
        self._pulse_timer.timeout.connect(self._toggle_pulse)
        self._pulse_timer.start()

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(180, 120)
        self.setStyleSheet("background-color: #06080f;")

        # Floating Hover Toolbar (top-right)
        self._overlay_toolbar = QFrame(self)
        self._overlay_toolbar.setObjectName("hoverToolbar")
        self._overlay_toolbar.setStyleSheet("""
            QFrame#hoverToolbar {
                background-color: rgba(15, 23, 42, 0.88);
                border: 1px solid rgba(51, 65, 85, 0.7);
                border-radius: 6px;
            }
            QToolButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: rgba(56, 189, 248, 0.2);
            }
        """)
        tb_layout = QHBoxLayout(self._overlay_toolbar)
        tb_layout.setContentsMargins(4, 3, 4, 3)
        tb_layout.setSpacing(4)

        # 1. Fullscreen Button
        self.btn_fs = QToolButton(self._overlay_toolbar)
        self.btn_fs.setIcon(get_icon("maximize"))
        self.btn_fs.setToolTip("Perbesar Layar Penuh (Stream 101 HD) - Atau Klik Ganda")
        self.btn_fs.clicked.connect(lambda: self.request_toggle_fullscreen.emit(self.channel_id))
        tb_layout.addWidget(self.btn_fs)

        # 2. Reconnect Button
        self.btn_reload = QToolButton(self._overlay_toolbar)
        self.btn_reload.setIcon(get_icon("refresh"))
        self.btn_reload.setToolTip("Hubungkan Ulang Stream")
        self.btn_reload.clicked.connect(lambda: self.request_reconnect.emit(self.channel_id))
        tb_layout.addWidget(self.btn_reload)

        # 3. Settings Button
        self.btn_cfg = QToolButton(self._overlay_toolbar)
        self.btn_cfg.setIcon(get_icon("settings"))
        self.btn_cfg.setToolTip("Pengaturan Kamera Ini")
        self.btn_cfg.clicked.connect(lambda: self.request_settings.emit(self.channel_id))
        tb_layout.addWidget(self.btn_cfg)

        self._overlay_toolbar.hide()

    def _toggle_pulse(self):
        if self._status_code in ("live", "connecting"):
            self._pulse_state = 1 - self._pulse_state
            self.update()

    def set_config(self, config: dict):
        self.config = config
        self._camera_name = config.get("name", f"Kamera {self.channel_id + 1}")
        if self.worker:
            self.worker.update_config(config)
        self.update()

    def set_fullscreen_mode(self, is_fullscreen: bool):
        self._is_fullscreen = is_fullscreen
        if is_fullscreen:
            self.btn_fs.setIcon(get_icon("grid"))
            self.btn_fs.setToolTip("Kembali ke Grid (Stream 102 SD)")
        else:
            self.btn_fs.setIcon(get_icon("maximize"))
            self.btn_fs.setToolTip("Perbesar Layar Penuh (Stream 101 HD)")
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

    def enterEvent(self, event: QEnterEvent):
        self._is_hovered = True
        self._position_toolbar()
        self._overlay_toolbar.show()
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._is_hovered = False
        self._overlay_toolbar.hide()
        self.update()
        super().leaveEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_toolbar()

    def _position_toolbar(self):
        tw = self._overlay_toolbar.sizeHint().width()
        th = self._overlay_toolbar.sizeHint().height()
        x = max(10, self.width() - tw - 10)
        y = 10
        self._overlay_toolbar.setGeometry(x, y, tw, th)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.channel_id)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._status_code in ("stopped", "error"):
            has_url = bool(self.config.get("main_url", "").strip() or self.config.get("url", "").strip())
            if not has_url:
                self.request_settings.emit(self.channel_id)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = QMenu(self)

        act_title = menu.addAction(get_icon("camera"), self._camera_name)
        act_title.setEnabled(False)
        menu.addSeparator()

        if self._is_fullscreen:
            act_fs = menu.addAction(get_icon("grid"), "Kembali ke Grid (Stream 102 SD)")
        else:
            act_fs = menu.addAction(get_icon("maximize"), "Perbesar Kamera (Stream 101 HD)")
        act_fs.triggered.connect(lambda: self.request_toggle_fullscreen.emit(self.channel_id))

        menu.addSeparator()

        act_settings = menu.addAction(get_icon("settings"), "Pengaturan Kamera...")
        act_settings.triggered.connect(lambda: self.request_settings.emit(self.channel_id))

        act_reconnect = menu.addAction(get_icon("refresh"), "Hubungkan Ulang")
        act_reconnect.triggered.connect(lambda: self.request_reconnect.emit(self.channel_id))

        if self.worker and self.worker.isRunning():
            act_stop = menu.addAction(get_icon("stop"), "Hentikan Stream")
            act_stop.triggered.connect(self.worker.stop)

        menu.exec_(event.globalPos())

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # 1. Background
        painter.fillRect(rect, QColor("#06080f"))

        # 2. Draw Video or Placeholder
        if self._image and not self._image.isNull():
            scaled = self._image.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawImage(x, y, scaled)

            # Elegant Glassmorphic OSD Badge
            self._draw_glassmorphic_osd(painter, x + 10, y + 10)
        else:
            self._draw_modern_placeholder(painter, rect)

        # 3. Outer Border (Glows subtly on hover or when live)
        if self._is_hovered:
            pen = QPen(QColor("#0284c7"), 1.5)
        elif self._status_code == "live":
            pen = QPen(QColor("#1e293b"), 1.0)
        else:
            pen = QPen(QColor("#111827"), 1.0)

        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect.adjusted(0, 0, -1, -1))

    def _draw_glassmorphic_osd(self, painter: QPainter, x: int, y: int):
        """Draws a sleek floating glassmorphism pill badge with live status and metadata."""
        stream_tag = "101 HD" if self._is_fullscreen else "102 SD"
        res_text = f"{self._image.width()}x{self._image.height()}" if self._image else ""
        fps_text = f"{self._fps:.0f} FPS" if self._fps > 0 else ""

        title_font = QFont("Ubuntu", 9, QFont.Bold)
        meta_font = QFont("Ubuntu", 8, QFont.Medium)
        fm = painter.fontMetrics()

        title_w = fm.horizontalAdvance(self._camera_name)
        stream_w = fm.horizontalAdvance(stream_tag) + 12
        res_w = fm.horizontalAdvance(res_text) + 8 if res_text else 0
        fps_w = fm.horizontalAdvance(fps_text) + 6 if fps_text else 0

        # Total badge dimensions
        badge_w = 24 + title_w + stream_w + res_w + fps_w + 14
        badge_h = 26

        # Draw semi-transparent rounded pill container
        badge_rect = QRect(x, y, badge_w, badge_h)
        painter.setPen(QPen(QColor(51, 65, 85, 180), 1))
        painter.setBrush(QColor(15, 23, 42, 215))
        painter.drawRoundedRect(badge_rect, 6, 6)

        curr_x = x + 8
        cy = y + badge_h // 2

        # 1. Pulsing Emerald Live Indicator Dot
        dot_radius = 4
        if self._pulse_state == 1:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(16, 185, 129, 90))
            painter.drawEllipse(curr_x - 2, cy - 6, 12, 12)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(52, 211, 153))
        painter.drawEllipse(curr_x, cy - 4, 8, 8)
        curr_x += 16

        # 2. Camera Title
        painter.setFont(title_font)
        painter.setPen(QColor(248, 250, 252))
        painter.drawText(curr_x, cy + 4, self._camera_name)
        curr_x += title_w + 10

        # 3. Stream Tag Pill (101 HD or 102 SD)
        tag_pill_rect = QRect(curr_x, cy - 8, stream_w, 16)
        painter.setPen(Qt.NoPen)
        if self._is_fullscreen:
            painter.setBrush(QColor(2, 132, 199, 220))  # Accent Blue for HD
            tag_text_color = QColor(255, 255, 255)
        else:
            painter.setBrush(QColor(30, 41, 59, 230))   # Slate for SD
            tag_text_color = QColor(148, 163, 184)

        painter.drawRoundedRect(tag_pill_rect, 4, 4)
        painter.setFont(meta_font)
        painter.setPen(tag_text_color)
        painter.drawText(tag_pill_rect, Qt.AlignCenter, stream_tag)
        curr_x += stream_w + 6

        # 4. Resolution
        if res_text:
            painter.setFont(meta_font)
            painter.setPen(QColor(148, 163, 184))
            painter.drawText(curr_x, cy + 4, res_text)
            curr_x += res_w + 4

        # 5. FPS
        if fps_text:
            painter.setFont(meta_font)
            painter.setPen(QColor(52, 211, 153))
            painter.drawText(curr_x, cy + 4, fps_text)

    def _draw_modern_placeholder(self, painter: QPainter, rect: QRect):
        """Draws a clean, modern aesthetic placeholder when stream is offline."""
        cx = rect.center().x()
        cy = rect.center().y()

        # Background subtle gradient
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0.0, QColor("#090d16"))
        grad.setColorAt(1.0, QColor("#04060a"))
        painter.fillRect(rect, grad)

        # Soft center watermark circle
        painter.setPen(QPen(QColor(30, 41, 59, 90), 2))
        painter.setBrush(QColor(15, 23, 42, 100))
        painter.drawEllipse(cx - 36, cy - 44, 72, 72)

        # Center Camera Icon Silhouette
        painter.setPen(QPen(QColor(56, 189, 248, 160), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(cx - 16, cy - 36, 24, 16, 3, 3)
        # lens
        painter.drawEllipse(cx - 7, cy - 31, 6, 6)
        # right triangle
        poly = [
            (cx + 8, cy - 31),
            (cx + 15, cy - 35),
            (cx + 15, cy - 21),
            (cx + 8, cy - 25)
        ]
        from PyQt5.QtGui import QPolygon
        from PyQt5.QtCore import QPoint
        painter.drawPolygon(QPolygon([QPoint(px, py) for px, py in poly]))

        # Camera Name Title
        painter.setPen(QColor("#e2e8f0"))
        font = QFont("Ubuntu", 11, QFont.Bold)
        painter.setFont(font)
        painter.drawText(
            QRect(rect.left(), cy + 4, rect.width(), 24),
            Qt.AlignCenter,
            self._camera_name
        )

        # Status Pill
        sub_font = QFont("Ubuntu", 9)
        painter.setFont(sub_font)
        fm = painter.fontMetrics()

        if self._status_code == "connecting":
            status_text = "● Menghubungkan..."
            pill_bg = QColor(2, 132, 199, 40)
            pill_border = QColor(2, 132, 199, 140)
            text_color = QColor("#38bdf8")
        elif self._status_code == "reconnecting":
            status_text = f"🔄 {self._status_msg}"
            pill_bg = QColor(217, 119, 6, 40)
            pill_border = QColor(217, 119, 6, 140)
            text_color = QColor("#fbbf24")
        elif self._status_code == "error":
            status_text = f"⚠ {self._status_msg}"
            pill_bg = QColor(220, 38, 38, 40)
            pill_border = QColor(220, 38, 38, 140)
            text_color = QColor("#f87171")
        else:
            has_url = bool(self.config.get("main_url", "").strip() or self.config.get("url", "").strip())
            status_text = "Offline" if has_url else "+ Klik untuk Isi URL"
            pill_bg = QColor(30, 41, 59, 120)
            pill_border = QColor(51, 65, 85, 120)
            text_color = QColor("#94a3b8")

        pw = fm.horizontalAdvance(status_text) + 16
        ph = 20
        pill_rect = QRect(cx - pw // 2, cy + 32, pw, ph)
        painter.setPen(QPen(pill_border, 1))
        painter.setBrush(pill_bg)
        painter.drawRoundedRect(pill_rect, 10, 10)

        painter.setPen(text_color)
        painter.drawText(pill_rect, Qt.AlignCenter, status_text)
