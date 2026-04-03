"""Componentes UI premium reutilizables - NO MODIFICAR SIN AUTORIZACIÓN"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QBrush

from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius


class MetricCardPremium(QFrame):
    """
    Card de métrica premium con gradiente
    """

    def __init__(self, title, value, change=None, change_positive=True,
                 gradient_type="blue", icon=None, parent=None):
        super().__init__(parent)

        self.gradient_type = gradient_type
        self.setMinimumHeight(140)
        self.setMinimumWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.MD)

        # Header (icono + título)
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(Spacing.SM)

        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"color: rgba(255, 255, 255, 0.9); font-size: 24px; background: transparent;")
            header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: rgba(255, 255, 255, 0.85); font-size: {Typography.CAPTION}px; font-weight: {Typography.MEDIUM}; background: transparent; text-transform: uppercase; letter-spacing: 0.5px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addWidget(header)

        # Valor principal
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: rgb(255, 255, 255); font-size: {Typography.H1}px; font-weight: {Typography.BOLD}; background: transparent; margin-top: {Spacing.XS}px;")
        layout.addWidget(value_label)

        # Cambio/tendencia
        if change:
            change_label = QLabel(change)
            change_color = Colors.SUCCESS if change_positive else Colors.DANGER
            change_label.setStyleSheet(f"color: {change_color}; font-size: {Typography.BODY_SM}px; font-weight: {Typography.SEMIBOLD}; background: transparent;")
            layout.addWidget(change_label)

        layout.addStretch()

    def paintEvent(self, event):
        """Dibuja el gradiente de fondo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())

        if self.gradient_type == "blue":
            gradient.setColorAt(0, QColor(Colors.PRIMARY))
            gradient.setColorAt(1, QColor("#1e40af"))
        elif self.gradient_type == "green":
            gradient.setColorAt(0, QColor(Colors.SUCCESS))
            gradient.setColorAt(1, QColor("#00cc66"))
        elif self.gradient_type == "orange":
            gradient.setColorAt(0, QColor(Colors.WARNING))
            gradient.setColorAt(1, QColor("#b45309"))
        elif self.gradient_type == "cyan":
            gradient.setColorAt(0, QColor(Colors.INFO))
            gradient.setColorAt(1, QColor("#0e7490"))
        elif self.gradient_type == "purple":
            gradient.setColorAt(0, QColor(Colors.PURPLE))
            gradient.setColorAt(1, QColor("#6d28d9"))
        else:
            gradient.setColorAt(0, QColor(Colors.PRIMARY))
            gradient.setColorAt(1, QColor("#1e40af"))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), BorderRadius.XL, BorderRadius.XL)


class CardPremium(QFrame):
    """Card contenedor premium con sombra y borde sutil"""

    def __init__(self, padding=None, parent=None):
        super().__init__(parent)

        padding = padding or Spacing.XL

        self.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {BorderRadius.XL}px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(padding, padding, padding, padding)


class ButtonPremium(QPushButton):
    """Botón premium con animación"""

    STYLES = {
        "primary": f"""
            QPushButton {{
                background: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.MD}px {Spacing.XXL}px;
                font-size: {Typography.BODY}px;
                font-weight: {Typography.SEMIBOLD};
            }}
            QPushButton:hover {{
                background: #1e40af;
            }}
            QPushButton:pressed {{
                background: #60a5fa;
            }}
            QPushButton:disabled {{
                background: {Colors.BG_INPUT};
                color: {Colors.TEXT_MUTED};
            }}
        """,
        "secondary": f"""
            QPushButton {{
                background: {Colors.BG_ELEVATED};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.MD}px {Spacing.XXL}px;
                font-size: {Typography.BODY}px;
                font-weight: {Typography.MEDIUM};
            }}
            QPushButton:hover {{
                background: {Colors.BG_HOVER};
                border-color: {Colors.BORDER_STRONG};
            }}
            QPushButton:pressed {{
                background: {Colors.BG_ACTIVE};
            }}
        """,
        "danger": f"""
            QPushButton {{
                background: {Colors.DANGER};
                color: white;
                border: none;
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.MD}px {Spacing.XXL}px;
                font-size: {Typography.BODY}px;
                font-weight: {Typography.SEMIBOLD};
            }}
            QPushButton:hover {{
                background: #b91c1c;
            }}
            QPushButton:pressed {{
                background: #f87171;
            }}
        """,
        "success": f"""
            QPushButton {{
                background: {Colors.SUCCESS};
                color: white;
                border: none;
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.MD}px {Spacing.XXL}px;
                font-size: {Typography.BODY}px;
                font-weight: {Typography.SEMIBOLD};
            }}
            QPushButton:hover {{
                background: #00cc66;
            }}
            QPushButton:pressed {{
                background: #34d399;
            }}
        """,
    }

    def __init__(self, text, style="primary", icon=None, parent=None):
        super().__init__(text, parent)

        self.setStyleSheet(self.STYLES.get(style, self.STYLES["primary"]))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)


class SectionHeaderPremium(QWidget):
    """Encabezado de sección premium"""

    def __init__(self, title, action_text=None, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.H3}px; font-weight: {Typography.BOLD};")
        layout.addWidget(title_label)
        layout.addStretch()

        if action_text:
            action_label = QLabel(action_text)
            action_label.setStyleSheet(f"color: {Colors.PRIMARY}; font-size: {Typography.BODY_SM}px; font-weight: {Typography.SEMIBOLD};")
            action_label.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(action_label)


class MetricCardMaxton(QFrame):
    """
    Metric card estilo Maxton con gradiente y sombra glow

    USO EXACTO:
    card = MetricCardMaxton(
        value="$262,226",
        label="Ventas hoy",
        gradient_colors="cyan"  # cyan, green, pink, purple, blue, orange
    )
    """

    def __init__(self, value, label, gradient_colors="cyan", icon=None, change=None, parent=None):
        super().__init__(parent)

        self.gradient_type = gradient_colors
        self.setMinimumHeight(140)
        self.setMinimumWidth(280)

        # Aplicar sombra glow según gradiente
        if gradient_colors == "cyan":
            shadow = Colors.SHADOW_GLOW_CYAN
        elif gradient_colors == "green":
            shadow = Colors.SHADOW_GLOW_GREEN
        elif gradient_colors == "pink":
            shadow = Colors.SHADOW_GLOW_PINK
        else:
            shadow = Colors.SHADOW_MD

        self.setStyleSheet(f"""
            QFrame {{
                border-radius: {BorderRadius.XL}px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)

        # Label (arriba, pequeño)
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.7);
                font-size: {Typography.CAPTION}px;
                font-weight: {Typography.MEDIUM};
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        """)
        layout.addWidget(label_widget)

        # Valor (grande, bold)
        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"""
            QLabel {{
                color: rgb(255, 255, 255);
                font-size: {Typography.H1}px;
                font-weight: {Typography.EXTRABOLD};
                background: transparent;
                letter-spacing: -1px;
            }}
        """)
        layout.addWidget(value_widget)

        # Cambio/indicador (si existe)
        if change:
            change_widget = QLabel(change)
            change_widget.setStyleSheet(f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.6);
                    font-size: {Typography.CAPTION}px;
                    background: transparent;
                }}
            """)
            layout.addWidget(change_widget)

        layout.addStretch()

    def paintEvent(self, event):
        """Dibuja gradiente de fondo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Crear gradiente según tipo
        gradient = QLinearGradient(0, 0, self.width(), self.height())

        if self.gradient_type == "cyan":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_CYAN_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_CYAN_END))
        elif self.gradient_type == "green":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_GREEN_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_GREEN_END))
        elif self.gradient_type == "pink":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_PINK_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_PINK_END))
        elif self.gradient_type == "purple":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_PURPLE_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_PURPLE_END))
        elif self.gradient_type == "blue":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_BLUE_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_BLUE_END))
        elif self.gradient_type == "orange":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_ORANGE_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_ORANGE_END))
        else:
            # Gradiente por defecto
            gradient.setColorAt(0, QColor(Colors.PRIMARY))
            gradient.setColorAt(1, QColor("#1e40af"))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), BorderRadius.XL, BorderRadius.XL)

        super().paintEvent(event)

    def set_value(self, value):
        """Actualiza el valor mostrado en la card"""
        for child in self.findChildren(QLabel):
            # El QLabel del valor tiene color blanco y font-size H1
            if "color: rgb(255, 255, 255)" in child.styleSheet() and f"font-size: {Typography.H1}px" in child.styleSheet():
                child.setText(value)
                break


class ChartCardMaxton(QFrame):
    """
    Card con gráfico estilo Maxton

    USO:
    card = ChartCardMaxton(title="Ventas últimos 7 días")
    """

    def __init__(self, title, subtitle=None, parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {BorderRadius.XL}px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H4}px;
                font-weight: {Typography.SEMIBOLD};
            }}
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Botón options (3 puntos)
        btn_options = QPushButton("⋮")
        btn_options.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_TERTIARY};
                border: none;
                font-size: {Typography.H3}px;
                padding: 0;
                max-width: 24px;
            }}
            QPushButton:hover {{
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        header_layout.addWidget(btn_options)

        layout.addLayout(header_layout)

        # Subtitle (si existe)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.TEXT_TERTIARY};
                    font-size: {Typography.CAPTION}px;
                }}
            """)
            layout.addWidget(subtitle_label)

        # Espacio para contenido del gráfico
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)


class InputPremium(QWidget):
    """Input premium con label"""

    def __init__(self, label, placeholder="", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.XS)

        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.CAPTION}px; font-weight: {Typography.SEMIBOLD}; text-transform: uppercase; letter-spacing: 0.5px;")
        layout.addWidget(label_widget)

        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.MD}px {Spacing.LG}px;
                font-size: {Typography.BODY}px;
                min-height: 20px;
            }}
            QLineEdit:hover {{
                border-color: {Colors.BORDER_STRONG};
            }}
            QLineEdit:focus {{
                border-color: {Colors.BORDER_FOCUS};
                background: {Colors.BG_ELEVATED};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_MUTED};
            }}
        """)
        layout.addWidget(self.input)


# ESTILOS PARA TABLAS
TABLE_STYLE_PREMIUM = f"""
    QTableWidget {{
        background: {Colors.BG_CARD};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_SUBTLE};
        border-radius: {BorderRadius.LG}px;
        gridline-color: {Colors.BORDER_SUBTLE};
        font-size: {Typography.BODY_SM}px;
    }}
    QTableWidget::item {{
        padding: {Spacing.MD}px;
        border: none;
        border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    }}
    QTableWidget::item:selected {{
        background: {Colors.PRIMARY};
        color: white;
    }}
    QTableWidget::item:hover {{
        background: {Colors.BG_HOVER};
    }}
    QTableWidget::item:nth-child(even) {{
        background: rgba(255, 255, 255, 0.02);
    }}
    QHeaderView::section {{
        background: {Colors.BG_ELEVATED};
        color: {Colors.TEXT_SECONDARY};
        padding: {Spacing.MD}px;
        border: none;
        border-bottom: 2px solid {Colors.BORDER_DEFAULT};
        font-weight: {Typography.SEMIBOLD};
        font-size: {Typography.CAPTION}px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    QScrollBar:vertical {{
        background: {Colors.BG_CARD};
        width: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background: {Colors.BG_ELEVATED};
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Colors.BG_HOVER};
    }}
"""
