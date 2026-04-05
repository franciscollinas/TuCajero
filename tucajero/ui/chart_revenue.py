"""
Gráfico de área/línea con gradiente azul - estilo Falcon
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPainter, QColor, QPainterPath, QLinearGradient, QPen, QFont
from PySide6.QtCore import Qt, QPoint


class RevenueChartCard(QFrame):
    """
    Gráfico de área/línea con gradiente azul - estilo Falcon
    """

    def __init__(self, title="Today", amount="$764.39", subtitle="Yesterday $644.87",
                 data_points=None, parent=None):
        super().__init__(parent)

        self.title = title
        self.amount = amount
        self.subtitle = subtitle
        self.data_points = data_points or [100, 150, 120, 180, 140, 160, 190, 170, 200]

        # ===================== TAMAÑO =====================
        self.setMinimumHeight(200)
        self.setMaximumHeight(220)

        # ===================== ESTILOS =====================
        self.setStyleSheet("""
            QFrame {
                background-color: #1e88e5;
                border-radius: 8px;
                border: none;
            }
        """)

        # ===================== LAYOUT =====================
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(4)

        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)

        # Monto grande
        amount_label = QLabel(self.amount)
        amount_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 28px;
                font-weight: 700;
                background: transparent;
                letter-spacing: -0.5px;
            }
        """)
        layout.addWidget(amount_label)

        # Subtítulo (comparación)
        subtitle_label = QLabel(self.subtitle)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.75);
                font-size: 11px;
                background: transparent;
            }
        """)
        layout.addWidget(subtitle_label)

        layout.addStretch()

    def paintEvent(self, event):
        """Dibuja el gráfico de área en el fondo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Área del gráfico (parte derecha del widget)
        chart_width = self.width() * 0.55
        chart_height = self.height() * 0.5
        chart_x = self.width() - chart_width - 20
        chart_y = 60

        # Normalizar puntos de datos
        if self.data_points:
            max_val = max(self.data_points)
            min_val = min(self.data_points)
            range_val = max_val - min_val or 1

            # Crear puntos del gráfico
            points = []
            for i, val in enumerate(self.data_points):
                x = chart_x + (i / (len(self.data_points) - 1)) * chart_width
                y = chart_y + chart_height - ((val - min_val) / range_val) * chart_height
                points.append(QPoint(int(x), int(y)))

            # Dibujar área bajo la línea con gradiente
            path = QPainterPath()
            path.moveTo(points[0].x(), chart_y + chart_height)
            for point in points:
                path.lineTo(point.x(), point.y())
            path.lineTo(points[-1].x(), chart_y + chart_height)
            path.closeSubpath()

            # Gradiente azul oscuro → azul claro
            gradient = QLinearGradient(0, chart_y, 0, chart_y + chart_height)
            gradient.setColorAt(0, QColor(33, 150, 243, 120))  # Azul con transparencia
            gradient.setColorAt(1, QColor(33, 150, 243, 20))   # Más transparente abajo
            painter.fillPath(path, gradient)

            # Dibujar línea superior
            painter.setPen(QPen(QColor(255, 255, 255, 200), 2))
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

            # Dibujar puntos pequeños en la línea
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 255))
            for point in points:
                painter.drawEllipse(point, 3, 3)

    def update_data(self, title=None, amount=None, subtitle=None, data_points=None):
        """Actualiza los datos del gráfico"""
        if title:
            self.title = title
        if amount:
            self.amount = amount
        if subtitle:
            self.subtitle = subtitle
        if data_points:
            self.data_points = data_points
        self.update()
