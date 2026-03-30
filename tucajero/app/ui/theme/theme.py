"""
Sistema de Diseño Moderno SaaS - TuCajero POS
Estilo oscuro con neón, gradientes y glassmorphism
"""

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QLinearGradient, QColor, QBrush, QPalette

BG_GRADIENT_START = "#0F172A"
BG_GRADIENT_END = "#1E293B"

PRIMARY = "#7C3AED"
PRIMARY_HOVER = "#8B5CF6"
PRIMARY_LIGHT = "rgba(124, 58, 237, 0.15)"

SECONDARY = "#06B6D4"
ACCENT = "#EC4899"

SUCCESS = "#22C55E"
SUCCESS_LIGHT = "rgba(34, 197, 94, 0.15)"
SUCCESS_HOVER = "#16A34A"

WARNING = "#F59E0B"
WARNING_LIGHT = "rgba(245, 158, 11, 0.15)"
WARNING_HOVER = "#D97706"

DANGER = "#EF4444"
DANGER_LIGHT = "rgba(239, 68, 68, 0.15)"
DANGER_HOVER = "#DC2626"

INFO = "#06B6D4"
INFO_LIGHT = "rgba(6, 182, 212, 0.15)"

TEXT_PRIMARY = "#FFFFFF"
TEXT_SECONDARY = "#94A3B8"
TEXT_MUTED = "#64748B"

CARD_BG = "rgba(255,255,255,0.05)"
CARD_BORDER = "rgba(255,255,255,0.08)"

BG_APP = "#0F172A"
BG_SIDEBAR = "#1E293B"
BG_CARD = "#1E293B"
BG_INPUT = "rgba(255,255,255,0.05)"

GLASS_BG = "rgba(30, 41, 59, 0.85)"
GLASS_BORDER = "rgba(124, 58, 237, 0.3)"

_font_family = "Segoe UI"


def app_style():
    return f"""
        QWidget {{
            font-family: '{_font_family}', sans-serif;
            color: {TEXT_PRIMARY};
        }}
        QMainWindow {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {BG_GRADIENT_START}, stop:1 {BG_GRADIENT_END});
        }}
        QDialog {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {BG_GRADIENT_START}, stop:1 {BG_GRADIENT_END});
        }}
        QLabel {{
            color: {TEXT_PRIMARY};
            background: transparent;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {PRIMARY};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {ACCENT};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """


def card_style():
    return f"""
        QFrame, QWidget {{
            background: {CARD_BG};
            border: 1px solid {CARD_BORDER};
            border-radius: 16px;
            padding: 16px;
        }}
    """


def kpi_card_style():
    return f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY}, stop:1 {SECONDARY});
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 20px;
            padding: 20px;
        }}
        QLabel {{
            background: transparent;
            color: {TEXT_PRIMARY};
        }}
    """


def button_primary():
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {PRIMARY}, stop:1 {ACCENT});
            color: {TEXT_PRIMARY};
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #F472B6);
        }}
        QPushButton:pressed {{
            background: #6D28D9;
        }}
    """


def button_secondary():
    return f"""
        QPushButton {{
            background: transparent;
            color: {TEXT_PRIMARY};
            border: 1px solid {CARD_BORDER};
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 500;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
        }}
    """


def button_success():
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {SUCCESS}, stop:1 #10B981);
            color: {TEXT_PRIMARY};
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4ADE80, stop:1 #34D399);
        }}
    """


def button_danger():
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DANGER}, stop:1 #DC2626);
            color: {TEXT_PRIMARY};
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F87171, stop:1 #EF4444);
        }}
    """


def button_warning():
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {WARNING}, stop:1 #D97706);
            color: {TEXT_PRIMARY};
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FBBF24, stop:1 #F59E0B);
        }}
    """


def input_style():
    return f"""
        QLineEdit, QComboBox, QSpinBox {{
            background: rgba(255,255,255,0.05);
            color: {TEXT_PRIMARY};
            border: 1px solid {CARD_BORDER};
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 14px;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 1px solid {PRIMARY};
            background: rgba(255,255,255,0.08);
        }}
        QLineEdit::placeholder {{
            color: {TEXT_SECONDARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {TEXT_SECONDARY};
            margin-right: 10px;
        }}
        QComboBox QAbstractItemView {{
            background: rgba(15, 23, 42, 0.95);
            color: {TEXT_PRIMARY};
            border: 1px solid {PRIMARY};
            border-radius: 10px;
            padding: 5px;
            selection-background-color: {PRIMARY};
        }}
    """


def table_style():
    return f"""
        QTableWidget {{
            background: transparent;
            color: {TEXT_PRIMARY};
            border: none;
            gridline-color: {CARD_BORDER};
            border-radius: 12px;
        }}
        QTableWidget::item {{
            padding: 12px;
            border-bottom: 1px solid {CARD_BORDER};
        }}
        QTableWidget::item:selected {{
            background: {PRIMARY};
        }}
        QHeaderView::section {{
            background: rgba(255,255,255,0.05);
            color: {TEXT_SECONDARY};
            padding: 12px;
            border: none;
            border-bottom: 1px solid {CARD_BORDER};
            font-weight: 600;
        }}
    """


def sidebar_style():
    return f"""
        QWidget {{
            background: rgba(15, 23, 42, 0.95);
            border-right: 1px solid {CARD_BORDER};
        }}
    """


def header_style():
    return f"""
        QWidget {{
            background: rgba(30, 41, 59, 0.8);
            border-bottom: 1px solid {CARD_BORDER};
        }}
    """


def label_title():
    return f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            font-size: 24px;
            font-weight: bold;
            background: transparent;
        }}
    """


def label_subtitle():
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: 14px;
            background: transparent;
        }}
    """


def label_kpi_value():
    return f"""
        QLabel {{
            color: {TEXT_PRIMARY};
            font-size: 36px;
            font-weight: bold;
            background: transparent;
        }}
    """


def label_kpi_label():
    return f"""
        QLabel {{
            color: {TEXT_SECONDARY};
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            background: transparent;
        }}
    """


def dialog_style():
    return f"""
        QDialog {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {BG_GRADIENT_START}, stop:1 {BG_GRADIENT_END});
        }}
    """


def glass_style():
    return f"""
        QFrame, QDialog {{
            background: {GLASS_BG};
            border: 1px solid {GLASS_BORDER};
            border-radius: 16px;
        }}
    """


def btn_sidebar():
    return f"""
        QPushButton {{
            background: transparent;
            color: {TEXT_SECONDARY};
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            text-align: left;
        }}
        QPushButton:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: {TEXT_PRIMARY};
        }}
        QPushButton:checked {{
            background: {PRIMARY};
            color: {TEXT_PRIMARY};
        }}
    """


def btn_primary():
    return button_primary()


def btn_secondary():
    return button_secondary()


def btn_success():
    return button_success()


def btn_danger():
    return button_danger()


def btn_warning():
    return button_warning()


def get_colors():
    return {
        "bg_app": BG_APP,
        "bg_sidebar": BG_SIDEBAR,
        "bg_card": BG_CARD,
        "bg_input": BG_INPUT,
        "bg_elevated": BG_INPUT,
        "bg_gradient_start": BG_GRADIENT_START,
        "bg_gradient_end": BG_GRADIENT_END,
        "text_primary": TEXT_PRIMARY,
        "text_secondary": TEXT_SECONDARY,
        "text_muted": TEXT_MUTED,
        "border": CARD_BORDER,
        "primary": PRIMARY,
        "primary_hover": PRIMARY_HOVER,
        "primary_light": PRIMARY_LIGHT,
        "secondary": SECONDARY,
        "success": SUCCESS,
        "success_light": SUCCESS_LIGHT,
        "success_hover": SUCCESS_HOVER,
        "warning": WARNING,
        "warning_light": WARNING_LIGHT,
        "warning_hover": WARNING_HOVER,
        "danger": DANGER,
        "danger_light": DANGER_LIGHT,
        "danger_hover": DANGER_HOVER,
        "info": INFO,
        "info_light": INFO_LIGHT,
        "accent": ACCENT,
        "glass_bg": GLASS_BG,
        "glass_border": GLASS_BORDER,
    }
