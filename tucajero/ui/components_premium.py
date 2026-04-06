"""Componentes UI premium reutilizables - NO MODIFICAR SIN AUTORIZACIÓN"""

from PySide6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGridLayout, QComboBox, QMenu
)
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QBrush, QPen, QPainterPath, QFont, QAction
from PySide6.QtCore import QSize, QPointF, Qt, Signal

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
# HERO CHART WIDGET (Gráfico de línea personalizado con datos dinámicos)
# ==============================================================================

class HeroChartWidget(QWidget):
    """Widget que dibuja el gráfico de línea estilo Falcon con datos reales"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(170)  # Más espacio para fechas sin recortar
        self.data_points = []  # Lista de (fecha_str, valor)
    
    def set_data(self, data_points):
        """Recibe lista de tuplas: [("01/04", 1000), ("02/04", 1500), ...]"""
        self.data_points = data_points
        self.update()  # Redibujar
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        if w <= 0 or h <= 0 or len(self.data_points) < 2:
            return
        
        # Márgenes
        margin_left = 35  # Más espacio lateral para que las fechas no se recorten
        margin_right = 35
        margin_top = 15
        margin_bottom = 35
        
        chart_h = h - margin_top - margin_bottom
        
        # Obtener valores
        valores = [v for _, v in self.data_points]
        max_val = max(valores) if valores else 1
        min_val = min(valores) if valores else 0
        rango = max_val - min_val if max_val != min_val else 1
        
        # Calcular puntos
        num_points = len(self.data_points)
        points = []
        
        for i, (fecha, valor) in enumerate(self.data_points):
            x = margin_left + (w - margin_left - margin_right) * i / (num_points - 1)
            # Normalizar valor a altura del gráfico (invertido porque Y crece hacia abajo)
            y_ratio = (valor - min_val) / rango
            y = margin_top + chart_h * (1 - y_ratio * 0.85)
            points.append((x, y))
        
        if len(points) < 2:
            return
        
        # Dibujar área rellena con gradiente
        area_path = QPainterPath()
        area_path.moveTo(points[0][0], points[0][1])
        for i in range(1, len(points)):
            area_path.lineTo(points[i][0], points[i][1])
        area_path.lineTo(points[-1][0], margin_top + chart_h)
        area_path.lineTo(points[0][0], margin_top + chart_h)
        area_path.closeSubpath()
        
        gradient = QLinearGradient(0, margin_top, 0, margin_top + chart_h)
        gradient.setColorAt(0, QColor(255, 255, 255, 40))
        gradient.setColorAt(1, QColor(255, 255, 255, 5))
        painter.fillPath(area_path, QBrush(gradient))
        
        # Dibujar línea blanca conectando puntos
        line_path = QPainterPath()
        line_path.moveTo(points[0][0], points[0][1])
        for i in range(1, len(points)):
            line_path.lineTo(points[i][0], points[i][1])
        
        pen = QPen(QColor(255, 255, 255, 250), 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(line_path)
        
        # Dibujar puntos blancos
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        for p in points:
            painter.drawEllipse(QPointF(p[0], p[1]), 3.5, 3.5)
        
        # Dibujar etiquetas de fecha en el eje X
        painter.setPen(QColor(255, 255, 255, 200))
        painter.setFont(QFont("Inter", 9, QFont.Weight.Medium))
        
        for i, (fecha, _) in enumerate(self.data_points):
            x = margin_left + (w - margin_left - margin_right) * i / (num_points - 1)
            y_text = int(margin_top + chart_h + 18)  # Centrado en el espacio inferior
            painter.drawText(int(x) - 15, y_text, 30, 16, Qt.AlignmentFlag.AlignCenter, fecha)


# ==============================================================================
# FALCON HERO CARD
# ==============================================================================

class FalconHeroCard(QFrame):
    """Card principal azul estilo Falcon con gráfico de línea blanco"""
    
    # Señal para notificar cambio de periodo
    period_changed = Signal(str)  # "semana", "mes", "trimestre", "semestre", "año"
    
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(280)
        self.current_period = "semana"  # Periodo por defecto
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

        # Botón de periodo con menú desplegable personalizado
        self.btn_periodo = QPushButton("Semana ▾")
        self.btn_periodo.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.15);
                color: white;
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
                font-size: 12px;
                min-width: 110px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.25);
            }
            QPushButton:pressed {
                background-color: rgba(255,255,255,0.35);
            }
        """)
        
        # Menú personalizado
        self.menu_periodo = QMenu()
        self.menu_periodo.setStyleSheet("""
            QMenu {
                background-color: #2c7be5;
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 6px;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 8px 20px;
                margin: 0px 4px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(255,255,255,0.2);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255,255,255,0.2);
                margin: 4px 0px;
            }
        """)
        
        periodos = ["Semana", "Mes", "Trimestre", "Semestre", "Año"]
        for periodo in periodos:
            action = QAction(periodo, self.menu_periodo)
            action.triggered.connect(lambda checked, p=periodo.lower(): self._on_periodo_selected(p))
            self.menu_periodo.addAction(action)
        
        self.btn_periodo.setMenu(self.menu_periodo)
        header.addWidget(self.btn_periodo, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)
        
        # Variable para tracking
        self.current_period = "semana"

        # Widget custom para el gráfico
        self.chart_area = HeroChartWidget()
        layout.addWidget(self.chart_area)

    def _on_periodo_selected(self, periodo):
        """Maneja la selección de periodo desde el menú"""
        self.current_period = periodo
        self.btn_periodo.setText(f"{periodo.capitalize()} ▾")
        self.period_changed.emit(periodo)

    def update_chart(self, data_points):
        """Actualiza el gráfico con datos reales: [("01/04", 1000), ...]"""
        self.chart_area.set_data(data_points)


# ==============================================================================
# FALCON METRIC CARD (Blanca con acento geométrico coloreado)
# ==============================================================================

class FalconMetricCard(QFrame):
    """Métrica blanca individual estilo Falcon con acento de color"""
    def __init__(self, title, value, badge_text, accent_color="#2c7be5", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.accent_color = accent_color
        
        # Parsear color para opacidad
        try:
            from PySide6.QtGui import QColor
            c = QColor(accent_color)
            opacity = 12 # Muy sutil
            self.bg_color = QColor(c.red(), c.green(), c.blue(), opacity)
        except:
            self.bg_color = QColor(44, 123, 229, 12)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 16px;
                border: 1px solid #edf2f9;
            }}
            QFrame:hover {{
                border: 2px solid {accent_color};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0,0,0,0)
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: #5e6e82; font-size: 13px; font-weight: 600; background: transparent; border: none;")
        header.addWidget(self.lbl_title)
        header.addStretch()

        self.badge = QLabel(badge_text)
        self.badge.setStyleSheet("background: transparent; border: none;")
        header.addWidget(self.badge)

        layout.addLayout(header)

        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(f"color: {accent_color}; font-size: 34px; font-weight: 700; margin-top: 5px; background: transparent; letter-spacing: -0.5px; border: none;")
        layout.addWidget(self.lbl_value)

        layout.addStretch()

        self.lbl_link = QLabel("Ver todos ›")
        self.lbl_link.setStyleSheet(f"color: {accent_color}; font-size: 13px; font-weight: 600; background: transparent; border: none;")
        layout.addWidget(self.lbl_link)

    def update_badge_style(self, text, accent):
        is_negative = text.startswith("-")
        # Color de fondo tenue del acento, texto del acento
        self.badge.setStyleSheet(f"""
            background-color: {accent}15;
            color: {accent};
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 700;
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        # Dibujar formas geométricas sutiles en el fondo derecho (como en la imagen)
        # Usando el color de acento
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        try:
            from PySide6.QtGui import QColor
            c = QColor(self.accent_color)
            r, g, b = c.red(), c.green(), c.blue()
        except:
            r, g, b = 44, 123, 229

        w, h = self.width(), self.height()

        path1 = QPainterPath()
        path1.moveTo(w * 0.60, 0)
        path1.lineTo(w, 0)
        path1.lineTo(w, h * 0.55)
        path1.closeSubpath()
        painter.fillPath(path1, QBrush(QColor(r, g, b, 22)))

        path2 = QPainterPath()
        path2.moveTo(w * 0.70, 0)
        path2.lineTo(w, 0)
        path2.lineTo(w, h * 0.70)
        path2.closeSubpath()
        painter.fillPath(path2, QBrush(QColor(r, g, b, 15)))

        path3 = QPainterPath()
        path3.moveTo(w * 0.50, h * 0.50)
        path3.lineTo(w, h * 0.30)
        path3.lineTo(w, h)
        path3.closeSubpath()
        painter.fillPath(path3, QBrush(QColor(r, g, b, 12)))

        path4 = QPainterPath()
        path4.moveTo(w * 0.65, h * 0.60)
        path4.lineTo(w, h * 0.50)
        path4.lineTo(w, h)
        path4.lineTo(w * 0.55, h)
        path4.closeSubpath()
        painter.fillPath(path4, QBrush(QColor(r, g, b, 8)))



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
