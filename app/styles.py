"""
styles.py - Minimal Dark Theme Stylesheet for RTSP Multi-View
"""

DARK_THEME_QSS = """
QMainWindow, QDialog, QWidget {
    background-color: #030712;
    color: #f3f4f6;
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
    font-size: 13px;
}

/* Push Buttons */
QPushButton {
    background-color: #1f2937;
    color: #f3f4f6;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #374151;
    border-color: #4b5563;
    color: #ffffff;
}

QPushButton.btn-primary {
    background-color: #2563eb;
    border-color: #1d4ed8;
    color: #ffffff;
}
QPushButton.btn-primary:hover {
    background-color: #3b82f6;
}

/* Inputs, ComboBox */
QLineEdit, QComboBox {
    background-color: #111827;
    color: #ffffff;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 6px 10px;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #1f2937;
    color: #ffffff;
    border: 1px solid #374151;
    selection-background-color: #2563eb;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #1f2937;
    background-color: #0b0f19;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #111827;
    color: #9ca3af;
    border: 1px solid #1f2937;
    border-bottom: none;
    padding: 7px 14px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #0b0f19;
    color: #3b82f6;
    font-weight: bold;
    border-color: #3b82f6;
    border-bottom: 2px solid #3b82f6;
}

/* Group Box */
QGroupBox {
    border: 1px solid #1f2937;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
    color: #9ca3af;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
"""
