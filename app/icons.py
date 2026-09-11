"""
icons.py - Vector Icon Manager for RTSP Multi-View
Provides crisp SVG/PNG icons for windows, buttons, tabs, and menus.
"""

import os
from pathlib import Path
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

_ICON_CACHE = {}


def get_icon(name: str) -> QIcon:
    """Load an icon by name from assets/icons directory."""
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]

    svg_path = ICONS_DIR / f"{name}.svg"
    png_path = ICONS_DIR / f"{name}.png"
    root_png = ASSETS_DIR / f"{name}.png"

    if svg_path.exists():
        ico = QIcon(str(svg_path))
    elif png_path.exists():
        ico = QIcon(str(png_path))
    elif root_png.exists():
        ico = QIcon(str(root_png))
    else:
        ico = QIcon()

    _ICON_CACHE[name] = ico
    return ico


def get_app_icon() -> QIcon:
    """Returns the main application icon."""
    return get_icon("app_icon")
