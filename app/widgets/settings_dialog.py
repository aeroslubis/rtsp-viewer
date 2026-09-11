"""
settings_dialog.py - RTSP Stream Settings Dialog for 4, 6, or 12 Channels
Allows selecting layout stream count (4, 6, 12), configuring each channel, and testing stream URLs.
"""

import subprocess
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QGridLayout, QFrame, QComboBox
)

from app.config import save_config, MAX_CHANNELS, SUPPORTED_STREAM_COUNTS
from app.icons import get_icon, get_app_icon


class ProbeWorker(QThread):
    """Background worker to probe RTSP URL without freezing UI."""
    probe_finished = pyqtSignal(bool, str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url.strip()

    def run(self):
        if not self.url:
            self.probe_finished.emit(False, "URL RTSP masih kosong.")
            return

        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height,r_frame_rate",
            "-of", "default=noprint_wrappers=1",
            "-timeout", "5000000"
        ]
        if self.url.startswith("rtsp://"):
            cmd.extend(["-rtsp_transport", "tcp"])
        cmd.extend(["-i", self.url])

        try:
            proc = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=7
            )
            if proc.returncode == 0:
                raw_lines = [l.strip() for l in proc.stdout.strip().split("\n") if l.strip()]
                info = {}
                for line in raw_lines:
                    if "=" in line:
                        k, v = line.split("=", 1)
                        info[k.strip()] = v.strip()

                codec = info.get("codec_name", "video")
                w = info.get("width", "?")
                h = info.get("height", "?")
                fps_raw = info.get("r_frame_rate", "")
                fps_str = ""
                if fps_raw and "/" in fps_raw:
                    try:
                        num, den = fps_raw.split("/")
                        if float(den) > 0:
                            fps_val = float(num) / float(den)
                            fps_str = f", {fps_val:.0f} fps"
                    except Exception:
                        pass

                msg = f"✓ Terhubung! Resolusi: {w}x{h} ({codec}{fps_str})"
                self.probe_finished.emit(True, msg)
            else:
                err = proc.stderr.strip()
                if "Connection refused" in err:
                    err_msg = "Koneksi ditolak (Connection refused)."
                elif "timed out" in err.lower():
                    err_msg = "Waktu koneksi habis (Timeout)."
                elif "Server returned 401" in err or "Unauthorized" in err:
                    err_msg = "Username / password salah (401 Unauthorized)."
                elif "Server returned 404" in err or "Not Found" in err:
                    err_msg = "Path stream tidak ditemukan (404 Not Found)."
                else:
                    err_msg = err[:80] if err else "Tidak dapat tersambung ke stream."
                self.probe_finished.emit(False, f"✗ {err_msg}")
        except subprocess.TimeoutExpired:
            self.probe_finished.emit(False, "✗ Waktu koneksi habis (Timeout 7 detik).")
        except Exception as e:
            self.probe_finished.emit(False, f"✗ Error: {str(e)[:60]}")


class SettingsDialog(QDialog):
    """Configuration dialog supporting 4, 6, and 12 stream channels."""
    settings_saved = pyqtSignal(dict)

    def __init__(self, config: dict, active_tab_index: int = 0, parent=None):
        super().__init__(parent)
        self.config = dict(config)
        self.probe_workers = {}

        self.setWindowTitle("Pengaturan Kamera RTSP")
        self.setWindowIcon(get_app_icon())
        self.resize(650, 310)
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Top Control: Grid Stream Count Selection
        top_bar = QHBoxLayout()
        lbl_count = QLabel("Jumlah Stream Tampil:")
        lbl_count.setStyleSheet("font-weight: 600; color: #f1f5f9; font-size: 13px;")
        top_bar.addWidget(lbl_count)

        self.cmb_stream_count = QComboBox()
        self.cmb_stream_count.addItem("4 Stream (2x2 Grid)", 4)
        self.cmb_stream_count.addItem("6 Stream (2x3 Grid)", 6)
        self.cmb_stream_count.addItem("12 Stream (3x4 Grid)", 12)

        current_count = self.config.get("general", {}).get("stream_count", 4)
        if current_count == 6:
            self.cmb_stream_count.setCurrentIndex(1)
        elif current_count == 12:
            self.cmb_stream_count.setCurrentIndex(2)
        else:
            self.cmb_stream_count.setCurrentIndex(0)

        self.cmb_stream_count.currentIndexChanged.connect(self._on_stream_count_changed)
        top_bar.addWidget(self.cmb_stream_count)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)

        # Tab Widget for 12 Channels
        self.tabs = QTabWidget(self)
        self.tabs.setUsesScrollButtons(True)
        main_layout.addWidget(self.tabs, 1)

        cam_icon = get_icon("camera")
        self.channel_forms = []
        for i in range(MAX_CHANNELS):
            ch_cfg = self.config["channels"][i]
            ch_tab, form_refs = self._create_channel_tab(i, ch_cfg)
            self.channel_forms.append(form_refs)
            self.tabs.addTab(ch_tab, cam_icon, f"Kamera {i + 1}")

        # Update tab visibility according to stream count
        self._update_tab_visibility(current_count)

        if 0 <= active_tab_index < current_count:
            self.tabs.setCurrentIndex(active_tab_index)

        # Footer Buttons
        footer = QHBoxLayout()
        footer.setSpacing(10)
        footer.addStretch()

        btn_cancel = QPushButton("Batal")
        btn_cancel.setFixedWidth(90)
        btn_cancel.clicked.connect(self.reject)
        footer.addWidget(btn_cancel)

        btn_save = QPushButton("Simpan")
        btn_save.setIcon(get_icon("save"))
        btn_save.setProperty("class", "btn-primary")
        btn_save.setFixedWidth(110)
        btn_save.clicked.connect(self.save_and_apply)
        footer.addWidget(btn_save)

        main_layout.addLayout(footer)

    def _on_stream_count_changed(self):
        count = self.cmb_stream_count.currentData()
        self._update_tab_visibility(count)

    def _update_tab_visibility(self, count: int):
        for i in range(MAX_CHANNELS):
            self.tabs.setTabVisible(i, i < count)
        if self.tabs.currentIndex() >= count:
            self.tabs.setCurrentIndex(0)

    def _create_channel_tab(self, ch_index: int, ch_cfg: dict):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        card = QFrame(tab)
        card.setObjectName("settingsCard")
        card_layout = QGridLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        row = 0

        # 1. Camera Name
        card_layout.addWidget(QLabel("Nama Kamera:"), row, 0)
        txt_name = QLineEdit(ch_cfg.get("name", f"Kamera {ch_index + 1}"))
        txt_name.setPlaceholderText(f"Contoh: Kamera {ch_index + 1}")
        card_layout.addWidget(txt_name, row, 1)
        row += 1

        # 2. RTSP URL with inline Test button
        card_layout.addWidget(QLabel("URL RTSP:"), row, 0)

        url_row = QHBoxLayout()
        url_row.setSpacing(6)
        txt_url = QLineEdit(ch_cfg.get("url", ""))
        txt_url.setPlaceholderText("rtsp://username:password@ip:port/stream")
        url_row.addWidget(txt_url, 1)

        btn_test = QPushButton("Uji Stream")
        btn_test.setIcon(get_icon("search"))
        btn_test.setToolTip("Tes koneksi dan otomatis deteksi resolusi stream ini")
        btn_test.setObjectName("btnTestStream")
        url_row.addWidget(btn_test)

        card_layout.addLayout(url_row, row, 1)
        row += 1

        # 3. Test Result Label
        lbl_test_res = QLabel("")
        lbl_test_res.setWordWrap(True)
        lbl_test_res.setStyleSheet("font-size: 12px; color: #64748b; padding-left: 2px;")
        card_layout.addWidget(lbl_test_res, row, 1)
        row += 1

        layout.addWidget(card)
        layout.addStretch()

        def run_test():
            url = txt_url.text().strip()
            if not url:
                lbl_test_res.setText("✗ Masukkan URL RTSP terlebih dahulu.")
                lbl_test_res.setStyleSheet("font-size: 12px; color: #f87171;")
                return

            lbl_test_res.setText("Menghubungi stream...")
            lbl_test_res.setStyleSheet("font-size: 12px; color: #38bdf8;")
            btn_test.setEnabled(False)

            worker = ProbeWorker(url)
            self.probe_workers[ch_index] = worker

            def on_finished(success, msg):
                btn_test.setEnabled(True)
                lbl_test_res.setText(msg)
                lbl_test_res.setStyleSheet(
                    "font-size: 12px; color: #34d399; font-weight: 500;"
                    if success else
                    "font-size: 12px; color: #f87171; font-weight: 500;"
                )

            worker.probe_finished.connect(on_finished)
            worker.start()

        btn_test.clicked.connect(run_test)

        refs = {
            "name": txt_name,
            "url": txt_url,
        }
        return tab, refs

    def save_and_apply(self):
        new_cfg = dict(self.config)
        new_cfg["general"]["stream_count"] = self.cmb_stream_count.currentData()

        for i in range(MAX_CHANNELS):
            refs = self.channel_forms[i]
            new_cfg["channels"][i]["name"] = refs["name"].text().strip() or f"Kamera {i + 1}"
            new_cfg["channels"][i]["url"] = refs["url"].text().strip()

        save_config(new_cfg)
        self.settings_saved.emit(new_cfg)
        self.accept()
