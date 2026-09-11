#!/usr/bin/env python3
"""
main.py - Minimalist 4-Stream RTSP Linux GUI Viewer.
"""

import sys
import os
import signal

if "QT_QPA_PLATFORM" not in os.environ:
    os.environ["QT_QPA_PLATFORM"] = "xcb"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt5.QtWidgets import QApplication
from app.styles import DARK_THEME_QSS
from app.window import MainWindow
from app.icons import get_app_icon


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("RTSP Multi-View")
    app.setWindowIcon(get_app_icon())
    app.setStyleSheet(DARK_THEME_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
