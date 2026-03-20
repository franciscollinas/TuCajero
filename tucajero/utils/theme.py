import winreg


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
            "bg_app": "#0f1117",
            "bg_sidebar": "#13151f",
            "bg_card": "#1a1d2e",
            "bg_card_hover": "#1e2235",
            "bg_input": "#252840",
            "bg_elevated": "#222640",
            "text_primary": "#f0f2ff",
            "text_secondary": "#8b92b8",
            "text_muted": "#4a5080",
            "text_inverse": "#0f1117",
            "border": "#2a2d45",
            "border_strong": "#3a3d58",
            "accent": "#6c63ff",
            "accent_hover": "#7c73ff",
            "accent_light": "#6c63ff22",
            "success": "#00c48c",
            "success_light": "#00c48c22",
            "warning": "#ffab2e",
            "warning_light": "#ffab2e22",
            "danger": "#ff5b5b",
            "danger_light": "#ff5b5b22",
            "info": "#00b8d9",
            "info_light": "#00b8d922",
            "purple": "#a855f7",
            "purple_light": "#a855f722",
            "shadow_sm": "0px 2px 8px rgba(0,0,0,0.4)",
            "shadow_md": "0px 4px 16px rgba(0,0,0,0.5)",
            "shadow_lg": "0px 8px 32px rgba(0,0,0,0.6)",
        }
    else:
        return {
            "bg_app": "#f4f6fb",
            "bg_sidebar": "#1a1d35",
            "bg_card": "#ffffff",
            "bg_card_hover": "#f8f9ff",
            "bg_input": "#eef0f8",
            "bg_elevated": "#ffffff",
            "text_primary": "#1a1d2e",
            "text_secondary": "#5a6080",
            "text_muted": "#9ba3c4",
            "text_inverse": "#ffffff",
            "border": "#e2e5f0",
            "border_strong": "#c5c9de",
            "accent": "#6c63ff",
            "accent_hover": "#5a52e0",
            "accent_light": "#6c63ff18",
            "success": "#00c48c",
            "success_light": "#00c48c18",
            "warning": "#ffab2e",
            "warning_light": "#ffab2e18",
            "danger": "#ff5b5b",
            "danger_light": "#ff5b5b18",
            "info": "#00b8d9",
            "info_light": "#00b8d918",
            "purple": "#a855f7",
            "purple_light": "#a855f718",
            "shadow_sm": "0px 2px 8px rgba(99,102,241,0.07)",
            "shadow_md": "0px 4px 16px rgba(99,102,241,0.10)",
            "shadow_lg": "0px 8px 32px rgba(99,102,241,0.15)",
        }


def get_stylesheet():
    c = get_colors()
    bg = c["bg_app"]
    return f"""
        QMainWindow, QDialog {{
            background-color: {bg};
        }}
        QWidget#centralWidget, QStackedWidget, QWidget {{
            background-color: transparent;
        }}
        QWidget {{
            background-color: {bg};
            color: {c["text_primary"]};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }}
        QLabel {{
            color: {c["text_primary"]};
            background: transparent;
        }}
        QLineEdit, QTextEdit {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1.5px solid {c["border"]};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
            selection-background-color: {c["accent"]};
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 1.5px solid {c["accent"]};
            background-color: {c["bg_elevated"]};
        }}
        QComboBox {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1.5px solid {c["border"]};
            border-radius: 8px;
            padding: 7px 12px;
            font-size: 13px;
        }}
        QComboBox:focus {{
            border: 1.5px solid {c["accent"]};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {c["bg_card"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
            border-radius: 8px;
            selection-background-color: {c["accent"]};
        }}
        QSpinBox, QDoubleSpinBox {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1.5px solid {c["border"]};
            border-radius: 8px;
            padding: 7px 12px;
            font-size: 13px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1.5px solid {c["accent"]};
        }}
        QPushButton {{
            background-color: {c["accent"]};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 9px 18px;
            font-size: 13px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {c["accent_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {c["accent"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
        QTableWidget {{
            background-color: {c["bg_card"]};
            color: {c["text_primary"]};
            gridline-color: {c["border"]};
            border: 1.5px solid {c["border"]};
            border-radius: 12px;
            font-size: 13px;
        }}
        QTableWidget::item {{
            padding: 10px 8px;
        }}
        QTableWidget::item:selected {{
            background-color: {c["accent_light"]};
            color: {c["accent"]};
            border-radius: 4px;
        }}
        QTableWidget::item:alternate {{
            background-color: {c["bg_input"]};
        }}
        QHeaderView::section {{
            background-color: {c["bg_input"]};
            color: {c["text_secondary"]};
            border: none;
            border-bottom: 1.5px solid {c["border"]};
            padding: 10px 8px;
            font-weight: bold;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        QTabWidget::pane {{
            border: 1.5px solid {c["border"]};
            border-radius: 10px;
            background: {c["bg_card"]};
            top: -1px;
        }}
        QTabBar::tab {{
            background: transparent;
            color: {c["text_secondary"]};
            padding: 9px 20px;
            border-radius: 8px 8px 0 0;
            font-size: 13px;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background: {c["accent"]};
            color: white;
            font-weight: bold;
        }}
        QTabBar::tab:hover:!selected {{
            background: {c["bg_input"]};
            color: {c["text_primary"]};
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {c["border_strong"]};
            border-radius: 3px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {c["accent"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: transparent;
            height: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: {c["border_strong"]};
            border-radius: 3px;
        }}
        QCheckBox {{
            color: {c["text_primary"]};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1.5px solid {c["border_strong"]};
            background: {c["bg_input"]};
        }}
        QCheckBox::indicator:checked {{
            background: {c["accent"]};
            border: 1.5px solid {c["accent"]};
        }}
        QRadioButton {{
            color: {c["text_primary"]};
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 1.5px solid {c["border_strong"]};
            background: {c["bg_input"]};
        }}
        QRadioButton::indicator:checked {{
            background: {c["accent"]};
            border: 1.5px solid {c["accent"]};
        }}
        QGroupBox {{
            border: 1.5px solid {c["border"]};
            border-radius: 10px;
            margin-top: 12px;
            padding: 12px;
            color: {c["text_secondary"]};
            font-size: 12px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 6px;
            color: {c["text_secondary"]};
        }}
        QMessageBox {{
            background-color: {c["bg_card"]};
        }}
        QMessageBox QLabel {{
            color: {c["text_primary"]};
            font-size: 13px;
        }}
        QToolTip {{
            background-color: {c["bg_elevated"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
        }}
    """


def card_style(elevated=False):
    c = get_colors()
    bg = c["bg_elevated"] if elevated else c["bg_card"]
    return f"""
        background-color: {bg};
        border-radius: 14px;
        border: 1.5px solid {c["border"]};
    """


def btn_style(color_key="accent", size="md"):
    c = get_colors()
    color = c.get(color_key, c["accent"])
    padding = {"sm": "6px 12px", "md": "9px 18px", "lg": "12px 24px"}.get(
        size, "9px 18px"
    )
    font = {"sm": "12px", "md": "13px", "lg": "14px"}.get(size, "13px")
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 8px;
            padding: {padding};
            font-size: {font};
            font-weight: bold;
        }}
        QPushButton:hover {{ background-color: {color}cc; }}
        QPushButton:pressed {{ background-color: {color}aa; }}
        QPushButton:disabled {{ background-color: {c["border"]}; color: {c["text_muted"]}; }}
    """


def label_style(size="md", weight="normal", color_key="text_primary"):
    c = get_colors()
    sizes = {
        "xs": "10px",
        "sm": "12px",
        "md": "13px",
        "lg": "16px",
        "xl": "20px",
        "xxl": "28px",
    }
    return f"color: {c[color_key]}; font-size: {sizes.get(size, '13px')}; font-weight: {weight}; background: transparent;"


def separator_style():
    c = get_colors()
    return f"background-color: {c['border']}; max-height: 1px; border: none;"
