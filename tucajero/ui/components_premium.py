"""Componentes UI premium reutilizables - NO MODIFICAR SIN AUTORIZACIÓN"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGridLayout
)
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QBrush, QPen, QPainterPath, Qt, QFont
from PySide6.QtCore import QSize

from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius


# ==============================================================================
# BOTÓN PREMIUM
# ==============================================================================

class ButtonPremium(QPushButton):
    """Botón con estilo premium y estados hover/click"""

    def __init__(self, text, style="primary", parent=None):
        super().__init__(text, parent)
        self._style = style
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_stylesheet()

    def _update_stylesheet(self):
        if self._style == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    color: white;
                    border: none;
                    border-radius: {BorderRadius.MD}px;
                    padding: 10px 24px;
                    font-size: {Typography.BODY}px;
                    font-weight: {Typography.BOLD};
                }}
                QPushButton:hover {{
                    background-color: #2563eb;
                }}
                QPushButton:pressed {{
                    background-color: #1e3a8a;
                }}
            """)
        elif self._style == "secondary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f3f4f6;
                    color: {Colors.TEXT_SECONDARY};
                    border: 1px solid {Colors.BORDER_DEFAULT};
                    border-radius: {BorderRadius.MD}px;
                    padding: 10px 24px;
                    font-size: {Typography.BODY}px;
                    font-weight: {Typography.SEMIBOLD};
                }}
                QPushButton:hover {{
                    background-color: #e5e7eb;
                }}
            """)
        elif self._style == "success":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: #10b981;
                    color: white;
                    border: none;
                    border-radius: {BorderRadius.MD}px;
                    padding: 10px 24px;
                    font-size: {Typography.BODY}px;
                    font-weight: {Typography.BOLD};
                }}
                QPushButton:hover {{
                    background-color: #059669;
                }}
            """)


# ==============================================================================
# METRIC CARD MAXTON (Estilo Falcon)
# ==============================================================================

class MetricCardMaxton(QFrame):
    """
    Metric card estilo Falcon: compacta, limpia, con tendencia visible
    """

    def __init__(self, title, value, change_percent=None, change_positive=True,
                 accent_color="#3b82f6", parent=None):
        super().__init__(parent)
        self.accent_color = accent_color

        # ===================== TAMAÑO =====================
        self.setMinimumHeight(100)
        self.setMaximumHeight(120)
        self.setMinimumWidth(200)

        # ===================== ESTILOS =====================
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                border-left: 4px solid {accent_color};
            }}
        """)

        # ===================== LAYOUT PRINCIPAL =====================
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(6)

        # ===================== FILA 1: TÍTULO + CAMBIO =====================
        top_layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            }
        """)
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        if change_percent is not None:
            change_color = "#10b981" if change_positive else "#ef4444"
            sign = "+" if change_positive else ""
            change_label = QLabel(f"{sign}{change_percent}%")
            change_label.setStyleSheet(f"""
                QLabel {{
                    color: {change_color};
                    font-size: 11px;
                    font-weight: 600;
                    background: transparent;
                }}
            """)
            top_layout.addWidget(change_label)

        main_layout.addLayout(top_layout)

        # ===================== FILA 2: VALOR GRANDE =====================
        value_label = QLabel(value)
        self._value_widget = value_label
        value_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a;
                font-size: 24px;
                font-weight: 700;
                background: transparent;
                letter-spacing: -0.5px;
            }
        """)
        main_layout.addWidget(value_label)

        # ===================== FILA 3: LINK "See all" =====================
        see_all_label = QLabel('<a href="#" style="color: #3b82f6; text-decoration: none; font-size: 11px;">See all &gt;</a>')
        see_all_label.setOpenExternalLinks(False)
        see_all_label.setStyleSheet("background: transparent;")
        main_layout.addWidget(see_all_label)

        main_layout.addStretch()

    def set_value(self, value):
        """Actualiza el valor mostrado"""
        if hasattr(self, '_value_widget'):
            self._value_widget.setText(value)

    def set_change(self, percent, positive=True):
        """Actualiza el indicador de cambio/tendencia"""
        # Buscar el widget de cambio existente y actualizarlo
        for child in self.findChildren(QLabel):
            style = child.styleSheet()
            if "font-size: 11px" in style and "font-weight: 600" in style:
                sign = "+" if positive else ""
                color = "#10b981" if positive else "#ef4444"
                child.setText(f"{sign}{percent}%")
                child.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        font-size: 11px;
                        font-weight: 600;
                        background: transparent;
                    }}
                """)
                break


# ==============================================================================
# CHART CARD MAXTON
# ==============================================================================

class ChartCardMaxton(QFrame):
    """Card premium con espacio para gráficos"""

    def __init__(self, title="Gráfico", subtitle="", parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.XL}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H4}px;
                font-weight: {Typography.BOLD};
                background: transparent;
            }}
        """)
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.TEXT_MUTED};
                    font-size: {Typography.CAPTION}px;
                    background: transparent;
                }}
            """)
            layout.addWidget(subtitle_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 12, 0, 0)
        layout.addLayout(self.content_layout)


# Alias para compatibilidad con código existente
CardPremium = ChartCardMaxton


# ==============================================================================
# ESTILO DE TABLA PREMIUM
# ==============================================================================

TABLE_STYLE_PREMIUM = f"""
    QTableWidget {{
        background-color: {Colors.BG_CARD};
        border: none;
        border-radius: {BorderRadius.LG}px;
        gridline-color: {Colors.BORDER_DEFAULT};
        color: {Colors.TEXT_PRIMARY};
        font-size: {Typography.BODY}px;
    }}
    QTableWidget::item {{
        padding: 8px 12px;
        border-bottom: 1px solid {Colors.BORDER_DEFAULT};
    }}
    QTableWidget::item:hover {{
        background-color: {Colors.BG_HOVER};
    }}
    QTableWidget::item:selected {{
        background-color: {Colors.PRIMARY}44;
    }}
    QTableWidget::item:nth-child(even) {{
        background-color: rgba(255,255,255,0.02);
    }}
    QHeaderView::section {{
        background-color: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_SECONDARY};
        font-weight: {Typography.BOLD};
        font-size: {Typography.CAPTION}px;
        padding: 10px 12px;
        border: none;
        border-bottom: 2px solid {Colors.BORDER_DEFAULT};
    }}
    QScrollBar:vertical {{
        background: {Colors.BG_APP};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {Colors.BORDER_DEFAULT};
        border-radius: 4px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Colors.BORDER_FOCUS};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: {Colors.BG_APP};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: {Colors.BORDER_DEFAULT};
        border-radius: 4px;
        min-width: 30px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
"""
