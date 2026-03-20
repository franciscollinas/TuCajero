import winreg
from PySide6.QtGui import QColor


def get_theme():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except:
        return "dark"


def get_colors():
    if get_theme() == "dark":
        return {
            "bg_app": "#1a1d2e",
            "bg_sidebar": "#16192a",
            "bg_card": "#222640",
            "bg_input": "#2a2d45",
            "text_primary": "#ffffff",
            "text_secondary": "#8b92b8",
            "text_muted": "#5a6080",
            "border": "#2e3250",
            "accent": "#6c63ff",
            "accent_hover": "#5a52e0",
            "success": "#00c48c",
            "warning": "#ffab2e",
            "danger": "#ff5b5b",
            "info": "#00b8d9",
        }
    else:
        return {
            "bg_app": "#f4f6fb",
            "bg_sidebar": "#ffffff",
            "bg_card": "#ffffff",
            "bg_input": "#f0f2f8",
            "text_primary": "#1a1d2e",
            "text_secondary": "#5a6080",
            "text_muted": "#9ba3c4",
            "border": "#e0e4f0",
            "accent": "#6c63ff",
            "accent_hover": "#5a52e0",
            "success": "#00c48c",
            "warning": "#ffab2e",
            "danger": "#ff5b5b",
            "info": "#00b8d9",
        }


def get_stylesheet():
    c = get_colors()
    return f"""
        QMainWindow, QWidget {{
            background-color: {c["bg_app"]};
            color: {c["text_primary"]};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }}
        QLabel {{
            color: {c["text_primary"]};
            background: transparent;
        }}
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
            border-radius: 6px;
            padding: 7px 10px;
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1.5px solid {c["accent"]};
        }}
        QTableWidget {{
            background-color: {c["bg_card"]};
            color: {c["text_primary"]};
            gridline-color: {c["border"]};
            border: 1px solid {c["border"]};
            border-radius: 8px;
        }}
        QTableWidget::item:selected {{
            background-color: {c["accent"]};
            color: white;
        }}
        QHeaderView::section {{
            background-color: {c["bg_input"]};
            color: {c["text_secondary"]};
            border: none;
            padding: 8px;
            font-weight: bold;
            font-size: 12px;
        }}
        QTabWidget::pane {{
            border: 1px solid {c["border"]};
            border-radius: 8px;
            background: {c["bg_card"]};
        }}
        QTabBar::tab {{
            background: {c["bg_input"]};
            color: {c["text_secondary"]};
            padding: 8px 20px;
            border-radius: 6px 6px 0 0;
        }}
        QTabBar::tab:selected {{
            background: {c["accent"]};
            color: white;
        }}
        QScrollBar:vertical {{
            background: {c["bg_app"]};
            width: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {c["border"]};
            border-radius: 3px;
        }}
        QPushButton {{
            background-color: {c["accent"]};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {c["accent_hover"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
    """
