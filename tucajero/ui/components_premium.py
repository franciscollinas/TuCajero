"""Componentes UI premium reutilizables - NO MODIFICAR SIN AUTORIZACIÓN"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPen, QBrush, QFont

from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius, GRADIENTS, IconSize


class MetricCardPremium(QFrame):
    """
    Card de métrica premium con gradiente
    
    USO EXACTO:
    card = MetricCardPremium(
        title="Ventas Hoy",
        value="$280,175",
        change="+12.5%",
        change_positive=True,
        gradient_type="green"
    )
    """
    
    def __init__(self, title, value, change=None, change_positive=True, 
                 gradient_type="blue", icon=None, parent=None):
        super().__init__(parent)
        
        self.gradient_type = gradient_type
        self.setMinimumHeight(140)
        self.setMinimumWidth(200)
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL
        )
        layout.setSpacing(Spacing.MD)
        
        # Header (icono + título)
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(Spacing.SM)
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.9);
                    font-size: {IconSize.LG}px;
                    background: transparent;
                }}
            """)
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.85);
                font-size: {Typography.CAPTION}px;
                font-weight: {Typography.MEDIUM};
                text-transform: uppercase;
                letter-spacing: 0.5px;
                background: transparent;
            }}
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Valor principal
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: rgb(255, 255, 255);
                font-size: {Typography.H1}px;
                font-weight: {Typography.BOLD};
                background: transparent;
                margin-top: {Spacing.XS}px;
            }}
        """)
        layout.addWidget(value_label)
        
        # Cambio/tendencia
        if change:
            change_label = QLabel(change)
            change_color = Colors.SUCCESS_LIGHT if change_positive else Colors.DANGER_LIGHT
            change_label.setStyleSheet(f"""
                QLabel {{
                    color: {change_color};
                    font-size: {Typography.BODY_SM}px;
                    font-weight: {Typography.SEMIBOLD};
                    background: transparent;
                }}
            """)
            layout.addWidget(change_label)
        
        layout.addStretch()
    
    def paintEvent(self, event):
        """Dibuja el gradiente de fondo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Crear gradiente
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        
        if self.gradient_type == "blue":
            gradient.setColorAt(0, QColor(Colors.PRIMARY))
            gradient.setColorAt(1, QColor(Colors.PRIMARY_DARK))
        elif self.gradient_type == "green":
            gradient.setColorAt(0, QColor(Colors.SUCCESS))
            gradient.setColorAt(1, QColor(Colors.SUCCESS_DARK))
        elif self.gradient_type == "orange":
            gradient.setColorAt(0, QColor(Colors.WARNING))
            gradient.setColorAt(1, QColor(Colors.WARNING_DARK))
        elif self.gradient_type == "cyan":
            gradient.setColorAt(0, QColor(Colors.INFO))
            gradient.setColorAt(1, QColor(Colors.INFO_DARK))
        elif self.gradient_type == "purple":
            gradient.setColorAt(0, QColor(Colors.PURPLE))
            gradient.setColorAt(1, QColor(Colors.PURPLE_DARK))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), BorderRadius.XL, BorderRadius.XL)


class CardPremium(QFrame):
    """
    Card contenedor premium con sombra y borde sutil
    
    USO EXACTO:
    card = CardPremium(padding=Spacing.XL)
    """
    
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
        
        # Agregar padding
        layout = QVBoxLayout(self)
        layout.setContentsMargins(padding, padding, padding, padding)


class ButtonPremium(QPushButton):
    """
    Botón premium con animación
    
    USO EXACTO:
    btn = ButtonPremium("Confirmar", style="primary")
    btn = ButtonPremium("Cancelar", style="secondary")
    btn = ButtonPremium("Eliminar", style="danger")
    """
    
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
                background: {Colors.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background: {Colors.PRIMARY_LIGHT};
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
                background: {Colors.DANGER_DARK};
            }}
            QPushButton:pressed {{
                background: {Colors.DANGER_LIGHT};
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
                background: {Colors.SUCCESS_DARK};
            }}
            QPushButton:pressed {{
                background: {Colors.SUCCESS_LIGHT};
            }}
        """,
    }
    
    def __init__(self, text, style="primary", icon=None, parent=None):
        super().__init__(text, parent)
        
        self.setStyleSheet(self.STYLES.get(style, self.STYLES["primary"]))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)


class SectionHeaderPremium(QWidget):
    """
    Encabezado de sección premium
    
    USO EXACTO:
    header = SectionHeaderPremium("Ventas Recientes", "Ver todas →")
    """
    
    def __init__(self, title, action_text=None, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H3}px;
                font-weight: {Typography.BOLD};
            }}
        """)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Acción (link)
        if action_text:
            action_label = QLabel(action_text)
            action_label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.PRIMARY};
                    font-size: {Typography.BODY_SM}px;
                    font-weight: {Typography.SEMIBOLD};
                }}
            """)
            action_label.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(action_label)


class InputPremium(QWidget):
    """
    Input premium con label
    
    USO EXACTO:
    input = InputPremium("Nombre del producto", placeholder="Ej: Laptop HP")
    """
    
    def __init__(self, label, placeholder="", parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.XS)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.CAPTION}px;
                font-weight: {Typography.SEMIBOLD};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        layout.addWidget(label_widget)
        
        # Input
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


# ESTILOS PARA FORMULARIOS
def estilo_combobox_premium():
    """Retorna estilo para QComboBox"""
    return f"""
        QComboBox {{
            background: {Colors.BG_INPUT};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MD}px {Spacing.LG}px;
            font-size: {Typography.BODY}px;
            min-height: 25px;
        }}
        QComboBox:hover {{
            border-color: {Colors.BORDER_STRONG};
        }}
        QComboBox:focus {{
            border-color: {Colors.PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {Colors.TEXT_SECONDARY};
        }}
        QComboBox QAbstractItemView {{
            background: {Colors.BG_CARD};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {BorderRadius.MD}px;
            selection-background-color: {Colors.PRIMARY};
            selection-color: white;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: {Spacing.MD}px;
            border: none;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background: {Colors.BG_HOVER};
        }}
    """


def estilo_spinbox_premium():
    """Retorna estilo para QSpinBox / QDoubleSpinBox"""
    return f"""
        QSpinBox, QDoubleSpinBox {{
            background: {Colors.BG_INPUT};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MD}px {Spacing.LG}px;
            font-size: {Typography.BODY}px;
            min-height: 25px;
        }}
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {Colors.BORDER_STRONG};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {Colors.PRIMARY};
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            background: {Colors.BG_ELEVATED};
            border-left: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: 0 {BorderRadius.MD}px 0 0;
        }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
            background: {Colors.BG_HOVER};
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background: {Colors.BG_ELEVATED};
            border-left: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: 0 0 {BorderRadius.MD}px 0;
        }}
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background: {Colors.BG_HOVER};
        }}
    """


def mostrar_alerta_premium(parent, tipo, titulo, mensaje):
    """
    Muestra alerta con diseño premium
    tipo: 'success', 'warning', 'error', 'info'
    """
    from PySide6.QtWidgets import QMessageBox
    
    iconos = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    }
    
    colores = {
        'success': Colors.SUCCESS,
        'warning': Colors.WARNING,
        'error': Colors.DANGER,
        'info': Colors.INFO
    }
    
    msg = QMessageBox(parent)
    msg.setWindowTitle(titulo)
    msg.setText(f"{iconos.get(tipo, 'ℹ️')} {mensaje}")
    
    msg.setStyleSheet(f"""
        QMessageBox {{
            background: {Colors.BG_CARD};
        }}
        QMessageBox QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.BODY}px;
            padding: {Spacing.LG}px;
        }}
        QPushButton {{
            background: {colores.get(tipo, Colors.PRIMARY)};
            color: white;
            border: none;
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MD}px {Spacing.XXL}px;
            font-weight: {Typography.SEMIBOLD};
            min-width: 100px;
        }}
        QPushButton:hover {{
            background: {Colors.PRIMARY_DARK if tipo == 'info' else colores.get(tipo, Colors.PRIMARY)};
            opacity: 0.9;
        }}
    """)
    
    return msg.exec()


class DialogPremium(QDialog):
    """Diálogo base premium"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.XL}px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL
        )
        layout.setSpacing(Spacing.XL)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H3}px;
                font-weight: {Typography.BOLD};
            }}
        """)
        layout.addWidget(title_label)
        
        # Contenido (override en subclases)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.MD)
        
        btn_cancelar = ButtonPremium("Cancelar", style="secondary")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        btn_aceptar = ButtonPremium("Aceptar", style="primary")
        btn_aceptar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_aceptar)
        
        layout.addLayout(btn_layout)
