"""
styles.py - Polished Modern Dark Theme Stylesheet for RTSP Multi-View
"""

DARK_THEME_QSS = """
/* Global Window & Dialog Background */
QMainWindow, QDialog, QWidget {
    background-color: #030712;
    color: #f3f4f6;
    font-family: 'Segoe UI', 'Ubuntu', 'Cantarell', sans-serif;
    font-size: 13px;
}

/* Dialog Frame & Card */
QDialog {
    background-color: #0b0f19;
}

QFrame#settingsCard {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
}

/* Context Menu */
QMenu {
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 7px 22px 7px 10px;
    border-radius: 5px;
    font-size: 13px;
}

QMenu::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}

QMenu::item:disabled {
    color: #64748b;
    font-weight: 600;
}

QMenu::separator {
    height: 1px;
    background-color: #1e293b;
    margin: 5px 6px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #1e293b;
    background-color: #0f172a;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #0b0f19;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-bottom: none;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 3px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #0f172a;
    color: #38bdf8;
    font-weight: 600;
    border-color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
}

QTabBar::tab:hover:!selected {
    background-color: #161f30;
    color: #e2e8f0;
}

/* Form Inputs */
QLineEdit {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 12px;
    selection-background-color: #2563eb;
}

QLineEdit:focus {
    border: 1px solid #38bdf8;
    background-color: #1e293b;
}

QLineEdit::placeholder {
    color: #64748b;
}

/* Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f3f4f6;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #334155;
    border-color: #475569;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton:disabled {
    background-color: #0f172a;
    color: #475569;
    border-color: #1e293b;
}

/* Primary Action Button (Simpan) */
QPushButton.btn-primary {
    background-color: #2563eb;
    border: 1px solid #1d4ed8;
    color: #ffffff;
    font-weight: 600;
}

QPushButton.btn-primary:hover {
    background-color: #3b82f6;
    border-color: #2563eb;
}

/* Inline Test Stream Button */
QPushButton#btnTestStream {
    background-color: rgba(56, 189, 248, 0.1);
    border: 1px solid #0284c7;
    color: #38bdf8;
    font-weight: 500;
    padding: 7px 14px;
}

QPushButton#btnTestStream:hover {
    background-color: #0284c7;
    color: #ffffff;
    border-color: #0284c7;
}

QPushButton#btnTestStream:disabled {
    background-color: #0f172a;
    color: #64748b;
    border-color: #1e293b;
}
"""
