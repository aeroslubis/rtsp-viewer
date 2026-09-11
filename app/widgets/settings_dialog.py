"""
settings_dialog.py - Clean, Modern RTSP Stream Settings Dialog
Features vector icons, inline connection testing, and automatic TCP transport.
"""

import subprocess
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QGridLayout, QFrame
)

from app.config import save_config
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
    """Clean and polished configuration dialog for the 4 RTSP channels."""
    settings_saved = pyqtSignal(dict)

    def __init__(self, config: dict, active_tab_index: int = 0, parent=None):
        super().__init__(parent)
        self.config = dict(config)
        self.probe_workers = {}

        self.setWindowTitle("Pengaturan Kamera RTSP")
        self.setWindowIcon(get_app_icon())
        self.resize(600, 260)
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Tab Widget
        self.tabs = QTabWidget(self)
        main_layout.addWidget(self.tabs, 1)

        cam_icon = get_icon("camera")
        self.channel_forms = []
        for i in range(4):
            ch_cfg = self.config["channels"][i]
            ch_tab, form_refs = self._create_channel_tab(i, ch_cfg)
            self.channel_forms.append(form_refs)
            self.tabs.addTab(ch_tab, cam_icon, f"Kamera {i + 1}")

        if 0 <= active_tab_index < self.tabs.count():
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

    def _create_channel_tab(self, ch_index: int, ch_cfg: dict):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(14, 14, 14, 14)
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

        # Connect Test Button
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
        for i in range(4):
            refs = self.channel_forms[i]
            new_cfg["channels"][i]["name"] = refs["name"].text().strip() or f"Kamera {i + 1}"
            new_cfg["channels"][i]["url"] = refs["url"].text().strip()

        save_config(new_cfg)
        self.settings_saved.emit(new_cfg)
        self.accept()
