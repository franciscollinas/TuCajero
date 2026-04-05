"""Componentes UI premium reutilizables - NO MODIFICAR SIN AUTORIZACIÓN"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGridLayout
)
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QBrush, QPen, QPainterPath, QFont
from PySide6.QtCore import QSize, QPointF, Qt

from tucajero.ui.design_tokens import Colors, DarkColors, Typography, Spacing, BorderRadius


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
        elif self._style == "dark":
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {DarkColors.BG_ELEVATED};
                    color: {DarkColors.TEXT_SECONDARY};
                    border: 1px solid {DarkColors.BORDER_DEFAULT};
                    border-radius: {BorderRadius.MD}px;
                    padding: 10px 24px;
                    font-size: {Typography.BODY}px;
                    font-weight: {Typography.SEMIBOLD};
                }}
                QPushButton:hover {{
                    background-color: {DarkColors.BG_HOVER};
                    border-color: {DarkColors.BORDER_STRONG};
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

# ==============================================================================
# FALCON HERO CARD (Azul con gráfico de línea)
# ==============================================================================

# ==============================================================================
# HERO CHART WIDGET (Gráfico de línea personalizado)
# ==============================================================================

class HeroChartWidget(QWidget):
    """Widget que dibuja el gráfico de línea estilo Falcon"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        if w <= 0 or h <= 0:
            return
        
        # Márgenes
        margin_left = 5
        margin_right = 5
        margin_top = 20
        margin_bottom = 10
        
        # Puntos distribuidos horizontalmente con variación vertical suave
        import math
        num_points = 12
        points = []
        
        for i in range(num_points):
            x = margin_left + (w - margin_left - margin_right) * i / (num_points - 1)
            # Variación sinusoidal para curva natural
            y = margin_top + (h - margin_top - margin_bottom) * (0.4 + 0.35 * math.sin(i * 0.7 + 1.2))
            points.append((x, y))
        
        if len(points) < 2:
            return
        
        # Dibujar área rellena con gradiente
        area_path = QPainterPath()
        area_path.moveTo(points[0][0], points[0][1])
        for i in range(1, len(points)):
            area_path.lineTo(points[i][0], points[i][1])
        area_path.lineTo(points[-1][0], h - margin_bottom)
        area_path.lineTo(points[0][0], h - margin_bottom)
        area_path.closeSubpath()
        
        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0, QColor(255, 255, 255, 35))
        gradient.setColorAt(1, QColor(255, 255, 255, 3))
        painter.fillPath(area_path, QBrush(gradient))
        
        # Dibujar línea blanca conectando puntos
        line_path = QPainterPath()
        line_path.moveTo(points[0][0], points[0][1])
        for i in range(1, len(points)):
            line_path.lineTo(points[i][0], points[i][1])
        
        pen = QPen(QColor(255, 255, 255, 240), 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(line_path)
        
        # Dibujar puntos blancos
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        for p in points:
            painter.drawEllipse(QPointF(p[0], p[1]), 4, 4)


# ==============================================================================
# FALCON HERO CARD
# ==============================================================================

class FalconHeroCard(QFrame):
    """Card principal azul estilo Falcon con gráfico de línea blanco"""
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(280)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2c7be5;
                border-radius: {BorderRadius.LG}px;
                border: none;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 20)

        header = QHBoxLayout()
        title_col = QVBoxLayout()

        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: white; font-size: 28px; font-weight: 800; background: transparent;")
        title_col.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel(subtitle)
        self.lbl_subtitle.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 14px; background: transparent;")
        title_col.addWidget(self.lbl_subtitle)

        header.addLayout(title_col)
        header.addStretch()

        # Simular dropdown de la imagen
        btn_opt = QPushButton("Pagos Exitosos ▾")
        btn_opt.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }
        """)
        header.addWidget(btn_opt, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

        # Widget custom para el gráfico
        self.chart_area = HeroChartWidget()
        layout.addWidget(self.chart_area)

        # Labels de tiempo abajo
        times = QHBoxLayout()
        for t in ["9:00", "10:00", "11:00", "12:00", "1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00"]:
            lbl = QLabel(t)
            lbl.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 11px; background: transparent;")
            times.addWidget(lbl)
            if t != "8:00": times.addStretch()
        layout.addLayout(times)


# ==============================================================================
# FALCON METRIC CARD (Blanca con acento geométrico)
# ==============================================================================

class FalconMetricCard(QFrame):
    """Métrica blanca individual estilo Falcon"""
    def __init__(self, title, value, badge_text, badge_color="#eef2ff", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: {BorderRadius.LG}px;
                border: 1px solid #edf2f9;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        
        header = QHBoxLayout()
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #5e6e82; font-size: 13px; font-weight: 600; background: transparent;")
        header.addWidget(self.lbl_title)
        
        self.badge = QLabel(badge_text)
        self.badge.setStyleSheet(f"""
            background-color: {badge_color};
            color: #2c7be5;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        """)
        header.addWidget(self.badge)
        header.addStretch()
        layout.addLayout(header)
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("color: #344050; font-size: 32px; font-weight: 700; margin-top: 5px; background: transparent;")
        layout.addWidget(self.lbl_value)
        
        layout.addStretch()
        
        self.lbl_link = QLabel("Ver todos ›")
        self.lbl_link.setStyleSheet("color: #2c7be5; font-size: 13px; font-weight: 600; background: transparent;")
        layout.addWidget(self.lbl_link)

    def paintEvent(self, event):
        super().paintEvent(event)
        # Dibujar forma geométrica sutil en el fondo derecho (como en la imagen)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(44, 123, 229, 15)) # Azul muy tenue
        
        w, h = self.width(), self.height()
        path = QPainterPath()
        path.moveTo(w * 0.7, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h * 0.6)
        path.closeSubpath()
        painter.drawPath(path)



# ==============================================================================
# CHART CARD MAXTON
# ==============================================================================

class ChartCardMaxton(QFrame):
    """Card premium con espacio para gráficos y acabado de cristal"""

    def __init__(self, title="Gráfico", subtitle="", parent=None):
        super().__init__(parent)
        from tucajero.ui.design_tokens import DarkColors
        self.colors = DarkColors

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.BG_CARD};
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-size: {Typography.H4}px;
                font-weight: {Typography.BOLD};
                background: transparent;
                letter-spacing: -0.2px;
            }}
        """)
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"""
                QLabel {{
                    color: {self.colors.TEXT_TERTIARY};
                    font-size: {Typography.CAPTION}px;
                    background: transparent;
                }}
            """)
            layout.addWidget(subtitle_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 16, 0, 0)
        self.content_layout.setSpacing(0)
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
