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
            "bg_app": "#0f172a",
            "bg_sidebar": "#1e293b",
            "bg_card": "#1e293b",
            "bg_card_hover": "#263548",
            "bg_input": "#263548",
            "bg_elevated": "#263548",
            "text_primary": "#f1f5f9",
            "text_secondary": "#94a3b8",
            "text_muted": "#475569",
            "text_inverse": "#0f172a",
            "border": "#334155",
            "border_strong": "#475569",
            "accent": "#3b82f6",
            "accent_hover": "#2563eb",
            "accent_light": "#3b82f620",
            "success": "#10b981",
            "success_light": "#10b98120",
            "warning": "#f59e0b",
            "warning_light": "#f59e0b20",
            "danger": "#ef4444",
            "danger_light": "#ef444420",
            "info": "#06b6d4",
            "info_light": "#06b6d420",
            "purple": "#8b5cf6",
            "purple_light": "#8b5cf620",
            "shadow_sm": "0px 1px 3px rgba(0,0,0,0.3)",
            "shadow_md": "0px 4px 6px rgba(0,0,0,0.4)",
            "shadow_lg": "0px 10px 15px rgba(0,0,0,0.5)",
        }
    else:
        return {
            # Fondos
            "bg_app": "#f1f5f9",
            "bg_sidebar": "#1e293b",
            "bg_card": "#ffffff",
            "bg_card_hover": "#f8fafc",
            "bg_input": "#f1f5f9",
            "bg_elevated": "#ffffff",
            # Texto
            "text_primary": "#0f172a",
            "text_secondary": "#475569",
            "text_muted": "#94a3b8",
            "text_inverse": "#ffffff",
            # Bordes
            "border": "#e2e8f0",
            "border_strong": "#cbd5e1",
            # Colores semánticos
            "accent": "#3b82f6",
            "accent_hover": "#2563eb",
            "accent_light": "#3b82f618",
            "success": "#10b981",
            "success_light": "#10b98118",
            "warning": "#f59e0b",
            "warning_light": "#f59e0b18",
            "danger": "#ef4444",
            "danger_light": "#ef444418",
            "info": "#06b6d4",
            "info_light": "#06b6d418",
            "purple": "#8b5cf6",
            "purple_light": "#8b5cf618",
            # Sombras pronunciadas estilo Sovereign
            "shadow_sm": "0px 1px 3px rgba(0,0,0,0.08), 0px 1px 2px rgba(0,0,0,0.06)",
            "shadow_md": "0px 4px 6px rgba(0,0,0,0.07), 0px 2px 4px rgba(0,0,0,0.06)",
            "shadow_lg": "0px 10px 15px rgba(0,0,0,0.08), 0px 4px 6px rgba(0,0,0,0.05)",
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


def btn_primary():
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["accent"]};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: bold;
            min-height: 32px;
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
    """


def btn_secondary():
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1.5px solid {c["border"]};
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 13px;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {c["bg_card_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {c["border"]};
        }}
        QPushButton:disabled {{
            background-color: {c["bg_input"]};
            color: {c["text_muted"]};
        }}
    """


def btn_danger():
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["danger"]};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: bold;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: #dc2626;
        }}
        QPushButton:pressed {{
            background-color: {c["danger"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
    """


def btn_success():
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["success"]};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: bold;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: #059669;
        }}
        QPushButton:pressed {{
            background-color: {c["success"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
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
