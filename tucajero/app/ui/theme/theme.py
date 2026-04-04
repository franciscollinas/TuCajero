"""
Sistema de Diseño TuCajero POS
Tema claro estilo Login (por defecto)
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QLinearGradient, QColor, QBrush, QPalette

# ============================================================
# TEMA CLARO - Estilo Login (por defecto)
# ============================================================
L_BG_APP = "#F1F5F9"
L_BG_SIDEBAR = "#FFFFFF"
L_BG_CARD = "#FFFFFF"
L_BG_INPUT = "#FFFFFF"
L_BG_HOVER = "#F1F5F9"
L_BG_ELEVATED = "#F8FAFC"

L_PRIMARY = "#2563EB"
L_PRIMARY_DARK = "#1D4ED8"
L_PRIMARY_LIGHT = "#DBEAFE"

L_SECONDARY = "#64748B"
L_SUCCESS = "#10B981"
L_SUCCESS_LIGHT = "#D1FAE5"
L_WARNING = "#F59E0B"
L_WARNING_LIGHT = "#FEF3C7"
L_DANGER = "#EF4444"
L_DANGER_LIGHT = "#FEE2E2"
L_INFO = "#06B6D4"

L_TEXT_PRIMARY = "#0F172A"
L_TEXT_SECONDARY = "#475569"
L_TEXT_MUTED = "#94A3B8"

L_BORDER_SUBTLE = "#F1F5F9"
L_BORDER_DEFAULT = "#E2E8F0"
L_BORDER_STRONG = "#CBD5E1"
L_BORDER_FOCUS = "#2563EB"

_font_family = "Segoe UI"


def app_light_style():
    """Estilo global claro - estilo Login"""
    return f"""
        /* Base */
        QWidget {{
            font-family: '{_font_family}', sans-serif;
            color: {L_TEXT_PRIMARY};
            background-color: {L_BG_APP};
        }}
        QMainWindow {{
            background-color: {L_BG_APP};
        }}
        QDialog {{
            background-color: {L_BG_APP};
        }}

        /* Labels */
        QLabel {{
            color: {L_TEXT_PRIMARY};
            background-color: transparent;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {L_PRIMARY};
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {L_PRIMARY_DARK};
        }}
        QPushButton:pressed {{
            background-color: #1E40AF;
        }}
        QPushButton:disabled {{
            background-color: {L_BORDER_DEFAULT};
            color: {L_TEXT_MUTED};
        }}

        /* Inputs */
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {L_BG_INPUT};
            color: {L_TEXT_PRIMARY};
            border: 1.5px solid {L_BORDER_DEFAULT};
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 14px;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {L_BORDER_FOCUS};
        }}
        QLineEdit::placeholder {{
            color: {L_TEXT_MUTED};
        }}

        /* Tables */
        QTableWidget {{
            background-color: {L_BG_CARD};
            color: {L_TEXT_PRIMARY};
            border: 1px solid {L_BORDER_DEFAULT};
            border-radius: 12px;
            gridline-color: {L_BORDER_SUBTLE};
        }}
        QTableWidget::item {{
            padding: 10px;
            border-bottom: 1px solid {L_BORDER_SUBTLE};
        }}
        QTableWidget::item:selected {{
            background-color: {L_PRIMARY};
            color: #FFFFFF;
        }}
        QTableWidget::item:hover {{
            background-color: {L_BG_HOVER};
        }}
        QHeaderView::section {{
            background-color: {L_BG_ELEVATED};
            color: {L_TEXT_SECONDARY};
            padding: 12px;
            border: none;
            border-bottom: 2px solid {L_BORDER_DEFAULT};
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
        }}

        /* Scroll bars */
        QScrollBar:vertical {{
            background-color: {L_BG_CARD};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {L_BORDER_STRONG};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {L_PRIMARY};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background-color: {L_BG_CARD};
            height: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {L_BORDER_STRONG};
            border-radius: 4px;
            min-width: 30px;
        }}

        /* Radio & Checkbox */
        QRadioButton {{
            color: {L_TEXT_PRIMARY};
            spacing: 8px;
        }}
        QCheckBox {{
            color: {L_TEXT_PRIMARY};
            spacing: 8px;
        }}

        /* GroupBox */
        QGroupBox {{
            border: 1.5px solid {L_BORDER_DEFAULT};
            border-radius: 10px;
            margin-top: 12px;
            padding-top: 16px;
            font-weight: 600;
            color: {L_TEXT_PRIMARY};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 0 10px;
            color: {L_TEXT_SECONDARY};
            font-size: 12px;
            text-transform: uppercase;
        }}

        /* ComboBox dropdown */
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {L_TEXT_SECONDARY};
        }}
        QComboBox QAbstractItemView {{
            background-color: {L_BG_CARD};
            color: {L_TEXT_PRIMARY};
            border: 1px solid {L_BORDER_DEFAULT};
            border-radius: 8px;
            selection-background-color: {L_PRIMARY};
            selection-color: #FFFFFF;
        }}

        /* QMessageBox */
        QMessageBox {{
            background-color: {L_BG_CARD};
        }}
        QMessageBox QLabel {{
            color: {L_TEXT_PRIMARY};
            background-color: transparent;
        }}

        /* TabWidget */
        QTabWidget::pane {{
            border: 1px solid {L_BORDER_DEFAULT};
            border-radius: 8px;
            background-color: {L_BG_CARD};
        }}
        QTabBar::tab {{
            background-color: {L_BG_ELEVATED};
            color: {L_TEXT_SECONDARY};
            padding: 8px 16px;
            border-radius: 8px 8px 0 0;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background-color: {L_PRIMARY};
            color: #FFFFFF;
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {L_BG_HOVER};
        }}

        /* ToolButton */
        QToolButton {{
            background-color: transparent;
            color: {L_TEXT_SECONDARY};
            border: none;
            border-radius: 6px;
            padding: 6px;
        }}
        QToolButton:hover {{
            background-color: {L_BG_HOVER};
            color: {L_TEXT_PRIMARY};
        }}

        /* ProgressBar */
        QProgressBar {{
            background-color: {L_BG_ELEVATED};
            border: 1px solid {L_BORDER_DEFAULT};
            border-radius: 6px;
            text-align: center;
            color: {L_TEXT_PRIMARY};
        }}
        QProgressBar::chunk {{
            background-color: {L_PRIMARY};
            border-radius: 5px;
        }}

        /* Frame */
        QFrame[frameShape="4"] {{
            background-color: {L_BORDER_DEFAULT};
            max-height: 1px;
            border: none;
        }}
        QFrame[frameShape="5"] {{
            background-color: {L_BORDER_DEFAULT};
            max-width: 1px;
            border: none;
        }}
    """


def app_dark_style():
    """Estilo global oscuro - Legacy (Maxton)"""
    return f"""
        QWidget {{
            font-family: '{_font_family}', sans-serif;
            color: #FFFFFF;
        }}
        QMainWindow {{
            background-color: #0F172A;
        }}
        QDialog {{
            background-color: #0F172A;
        }}
        QLabel {{
            color: #FFFFFF;
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: #7C3AED;
            border-radius: 4px;
            min-height: 30px;
        }}
    """


# Alias para compatibilidad - ahora apunta al tema claro
app_style = app_light_style
