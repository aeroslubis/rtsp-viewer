"""
stream_worker.py - Low-Latency RTSP Stream Worker
Supports explicit main_url (used in fullscreen) and sub_url (used in live grid).
"""

import subprocess
import time
from typing import Optional

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

from app.config import resolve_stream_url


class StreamWorker(QThread):
    """
    Worker thread that decodes an RTSP stream using FFmpeg.
    Uses sub_url during live grid mode, and main_url during fullscreen mode.
    """
    frame_ready = pyqtSignal(int, QImage, float)   # channel_id, QImage, fps
    status_changed = pyqtSignal(int, str, str)     # channel_id, status_code, message

    def __init__(self, channel_id: int, config: dict, is_fullscreen: bool = False, parent=None):
        super().__init__(parent)
        self.channel_id = channel_id
        self.config = config
        self.is_fullscreen = is_fullscreen
        self._running = False
        self._ffmpeg_proc: Optional[subprocess.Popen] = None
        self._last_frame: Optional[QImage] = None

    def update_config(self, new_config: dict):
        self.config = new_config

    def set_fullscreen(self, is_fullscreen: bool):
        self.is_fullscreen = is_fullscreen

    def run(self):
        self._running = True
        reconnect_interval = self.config.get("reconnect_interval_sec", 4)
        auto_reconnect = self.config.get("auto_reconnect", True)

        while self._running:
            main_url = (self.config.get("main_url", "") or self.config.get("url", "")).strip()
            sub_url = self.config.get("sub_url", "").strip()

            if not main_url and not sub_url:
                self.status_changed.emit(self.channel_id, "stopped", "Belum ada URL")
                break

            # In fullscreen mode: use main_url (HD)
            # In grid mode: use sub_url (SD), or auto-derived sub-stream if not filled
            if self.is_fullscreen:
                active_url = main_url or sub_url
                stream_type = "Main HD"
            else:
                if sub_url:
                    active_url = sub_url
                else:
                    active_url = resolve_stream_url(main_url, is_fullscreen=False)
                stream_type = "Sub SD"

            self.status_changed.emit(
                self.channel_id,
                "connecting",
                f"Menghubungkan ({stream_type})..."
            )

            try:
                cmd = self._build_ffmpeg_cmd(active_url)
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    bufsize=0
                )
                self._ffmpeg_proc = proc

                buf = bytearray()
                frame_count = 0
                t_last_fps = time.time()
                current_fps = 0.0
                first_frame_received = False

                while self._running:
                    chunk = proc.stdout.read(16384)
                    if not chunk:
                        break
                    buf.extend(chunk)

                    while self._running:
                        soi = buf.find(b"\xff\xd8")
                        if soi == -1:
                            buf = bytearray()
                            break
                        eoi = buf.find(b"\xff\xd9", soi + 2)
                        if eoi == -1:
                            if soi > 0:
                                buf = buf[soi:]
                            break

                        jpg_bytes = buf[soi:eoi+2]
                        buf = buf[eoi+2:]

                        qimg = QImage.fromData(jpg_bytes)
                        if not qimg or qimg.isNull():
                            continue

                        self._last_frame = qimg
                        frame_count += 1
                        t_now = time.time()
                        dt = t_now - t_last_fps
                        if dt >= 1.0:
                            current_fps = frame_count / dt
                            frame_count = 0
                            t_last_fps = t_now

                        if not first_frame_received:
                            first_frame_received = True
                            self.status_changed.emit(
                                self.channel_id,
                                "live",
                                f"Live {qimg.width()}x{qimg.height()} [{stream_type}]"
                            )

                        self.frame_ready.emit(self.channel_id, qimg, current_fps)

            except Exception as e:
                self.status_changed.emit(self.channel_id, "error", f"Error: {str(e)[:30]}")

            finally:
                self._cleanup_stream_proc()

            if not self._running:
                break

            if auto_reconnect:
                for remaining in range(reconnect_interval, 0, -1):
                    if not self._running:
                        break
                    self.status_changed.emit(
                        self.channel_id,
                        "reconnecting",
                        f"Mencoba ulang ({remaining}s)..."
                    )
                    for _ in range(10):
                        if not self._running:
                            break
                        time.sleep(0.1)
            else:
                self.status_changed.emit(self.channel_id, "error", "Terputus")
                break

        self.status_changed.emit(self.channel_id, "stopped", "Offline")

    def _build_ffmpeg_cmd(self, url: str) -> list:
        if url.startswith("testsrc") or url.startswith("smptebars") or url.startswith("mandelbrot"):
            return [
                "ffmpeg", "-hide_banner", "-loglevel", "error",
                "-re", "-f", "lavfi", "-i", url,
                "-f", "image2pipe", "-vcodec", "mjpeg", "-q:v", "3", "pipe:1"
            ]

        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error"
        ]

        if url.startswith("rtsp://"):
            cmd.extend([
                "-rtsp_transport", "tcp",
                "-timeout", "5000000"  # 5s socket timeout
            ])

        cmd.extend([
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-strict", "experimental",
            "-probesize", "65536",
            "-analyzeduration", "500000",
            "-i", url,
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-q:v", "3",
            "pipe:1"
        ])
        return cmd

    def _cleanup_stream_proc(self):
        """Immediately terminate child process and close handles without deadlock."""
        proc = self._ffmpeg_proc
        self._ffmpeg_proc = None
        if proc:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                proc.wait(timeout=0.1)
            except Exception:
                pass
            try:
                if proc.stdout:
                    proc.stdout.close()
            except Exception:
                pass

    def stop(self):
        """Stop worker and kill subprocess immediately."""
        self._running = False
        self._cleanup_stream_proc()
        self.wait(1000)
