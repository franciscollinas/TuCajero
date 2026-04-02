from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QFontMetrics
from tucajero.utils.theme import get_colors


class ChartWidget(QWidget):
    """Widget para mostrar gráficos dibujados nativamente con Qt (sin matplotlib)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.setStyleSheet("background: transparent;")
        self.labels = []
        self.values = []
        self.title = ""
        self.chart_type = "bar"  # "bar" o "pie"

    def plot_bar(self, labels, values, title="Ventas"):
        """Gráfico de barras"""
        self.labels = labels
        self.values = values
        self.title = title
        self.chart_type = "bar"
        self.update()  # Redibujar

    def plot_pie(self, labels, values, title="Distribución"):
        """Gráfico de torta"""
        self.labels = labels
        self.values = values
        self.title = title
        self.chart_type = "pie"
        self.update()  # Redibujar

    def paintEvent(self, event):
        """Dibuja el gráfico"""
        super().paintEvent(event)
        
        if not self.values or sum(self.values) == 0:
            self._draw_no_data()
            return
        
        if self.chart_type == "bar":
            self._draw_bar_chart()
        elif self.chart_type == "pie":
            self._draw_pie_chart()

    def _draw_no_data(self):
        """Dibuja mensaje de sin datos"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = get_colors()
        
        painter.setPen(QColor(c.get("text_muted", "#94a3b8")))
        painter.setFont(QFont("Segoe UI", 12))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Sin datos disponibles")

    def _draw_bar_chart(self):
        """Dibuja gráfico de barras"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = get_colors()
        
        # Márgenes
        margin_left = 60
        margin_right = 20
        margin_top = 40
        margin_bottom = 60
        
        # Área de dibujo
        chart_width = self.width() - margin_left - margin_right
        chart_height = self.height() - margin_top - margin_bottom
        
        if chart_width <= 0 or chart_height <= 0:
            return
        
        # Título
        painter.setPen(QColor(c.get("text_primary", "#1e293b")))
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.drawText(0, 0, self.width(), 30, Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Valor máximo
        max_value = max(self.values) if self.values else 1
        
        # Ancho de barras
        bar_width = (chart_width / len(self.values)) * 0.7 if self.values else 0
        spacing = (chart_width / len(self.values)) * 0.3 if self.values else 0
        
        # Colores para barras
        colors = self._get_colors(len(self.values))
        
        # Dibujar barras
        for i, (label, value) in enumerate(zip(self.labels, self.values)):
            x = margin_left + (i * (bar_width + spacing)) + spacing / 2
            bar_height = (value / max_value) * chart_height if max_value > 0 else 0
            y = margin_top + chart_height - bar_height
            
            # Barra
            painter.setBrush(QBrush(QColor(colors[i % len(colors)])))
            painter.setPen(QPen(QColor(colors[i % len(colors)]), 1))
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 4, 4)
            
            # Valor encima de la barra
            painter.setPen(QColor(c.get("text_primary", "#1e293b")))
            painter.setFont(QFont("Segoe UI", 9))
            value_text = f"${int(value):,}"
            fm = QFontMetrics(painter.font())
            text_width = fm.horizontalAdvance(value_text)
            painter.drawText(int(x + bar_width/2 - text_width/2), int(y - 5), value_text)
            
            # Etiqueta abajo
            painter.setPen(QColor(c.get("text_muted", "#94a3b8")))
            painter.setFont(QFont("Segoe UI", 8))
            label_text = label[:10] + "..." if len(label) > 10 else label
            fm = QFontMetrics(painter.font())
            text_width = fm.horizontalAdvance(label_text)
            
            # Rotar texto si es muy largo
            if len(label) > 8:
                painter.save()
                painter.translate(int(x + bar_width/2), int(margin_top + chart_height + 10))
                painter.rotate(-45)
                painter.drawText(0, 0, label_text)
                painter.restore()
            else:
                painter.drawText(int(x + bar_width/2 - text_width/2), 
                               int(margin_top + chart_height + 20), label_text)
        
        # Línea base
        painter.setPen(QPen(QColor(c.get("border", "#e2e8f0")), 1))
        painter.drawLine(margin_left, margin_top + chart_height, 
                        self.width() - margin_right, margin_top + chart_height)

    def _draw_pie_chart(self):
        """Dibuja gráfico de torta"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = get_colors()
        
        # Título
        painter.setPen(QColor(c.get("text_primary", "#1e293b")))
        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.drawText(0, 0, self.width(), 30, Qt.AlignmentFlag.AlignCenter, self.title)
        
        # Centro y radio
        center_x = self.width() // 3
        center_y = self.height() // 2 + 10
        radius = min(center_x - 40, self.height() // 2 - 40)
        
        if radius <= 0:
            return
        
        total = sum(self.values)
        if total == 0:
            return
        
        # Colores
        colors = self._get_colors(len(self.values))
        
        # Dibujar rebanadas
        start_angle = 0
        for i, (label, value) in enumerate(zip(self.labels, self.values)):
            span_angle = int((value / total) * 360 * 16)  # 16 = unidades de Qt
            
            painter.setBrush(QBrush(QColor(colors[i % len(colors)])))
            painter.setPen(QPen(QColor(c.get("bg_app", "#ffffff")), 2))
            
            painter.drawPie(center_x - radius, center_y - radius, 
                          radius * 2, radius * 2, 
                          start_angle * 16, span_angle)
            
            start_angle += span_angle
        
        # Leyenda a la derecha
        legend_x = self.width() // 2 + 20
        legend_y = 50
        
        painter.setFont(QFont("Segoe UI", 8))
        for i, (label, value) in enumerate(zip(self.labels, self.values)):
            # Cuadro de color
            painter.setBrush(QBrush(QColor(colors[i % len(colors)])))
            painter.setPen(QPen(QColor(colors[i % len(colors)]), 1))
            painter.drawRect(legend_x, legend_y + i * 22, 14, 14)
            
            # Texto
            painter.setPen(QColor(c.get("text_primary", "#1e293b")))
            percentage = (value / total) * 100
            text = f"{label[:15]}... ({percentage:.1f}%)" if len(label) > 15 else f"{label} ({percentage:.1f}%)"
            painter.drawText(legend_x + 20, legend_y + i * 22 + 12, text)

    def _get_colors(self, n):
        """Paleta de colores para gráficos"""
        palette = [
            "#3b82f6",  # blue
            "#10b981",  # green
            "#f59e0b",  # amber
            "#ef4444",  # red
            "#8b5cf6",  # purple
            "#06b6d4",  # cyan
            "#ec4899",  # pink
            "#84cc12",  # lime
            "#f97316",  # orange
            "#14b8a6",  # teal
        ]
        return [palette[i % len(palette)] for i in range(max(1, n))]

    def clear(self):
        """Limpia el gráfico"""
        self.labels = []
        self.values = []
        self.title = ""
        self.update()


def get_ventas_por_periodo(session, periodo="mes"):
    """Obtiene datos de ventas por periodo"""
    from datetime import datetime, timedelta
    from tucajero.models.producto import Venta
    from sqlalchemy import func, extract

    hoy = datetime.now()

    if periodo == "dia":
        inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
        group_by = extract("hour", Venta.fecha)
    elif periodo == "mes":
        inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        group_by = extract("day", Venta.fecha)
    elif periodo == "trimestre":
        month = hoy.month - 3
        year = hoy.year
        if month <= 0:
            month += 12
            year -= 1
        inicio = datetime(year, month, 1)
        group_by = extract("month", Venta.fecha)
    elif periodo == "semestre":
        month = hoy.month - 6
        year = hoy.year
        if month <= 0:
            month += 12
            year -= 1
        inicio = datetime(year, month, 1)
        group_by = extract("month", Venta.fecha)
    else:  # año
        inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        group_by = extract("month", Venta.fecha)

    resultados = (
        session.query(group_by, func.sum(Venta.total))
        .filter(Venta.fecha >= inicio, Venta.anulada == False)
        .group_by(group_by)
        .all()
    )

    if periodo == "dia":
        labels = [f"{int(r[0]):02d}:00" if r[0] is not None else "Sin hora" for r in resultados]
    elif periodo == "mes":
        labels = [str(int(r[0])) if r[0] is not None else "" for r in resultados]
    else:
        meses = [
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
        ]
        labels = [meses[int(r[0]) - 1] if r[0] is not None else "" for r in resultados]

    values = [float(r[1] or 0) for r in resultados]

    return labels, values


def get_ventas_por_metodo(session):
    """Obtiene ventas por método de pago"""
    from tucajero.models.producto import Venta
    from sqlalchemy import func

    resultados = (
        session.query(Venta.metodo_pago, func.sum(Venta.total))
        .filter(Venta.metodo_pago.isnot(None), Venta.anulada == False)
        .group_by(Venta.metodo_pago)
        .all()
    )

    labels = [r[0] or "Efectivo" for r in resultados]
    values = [float(r[1] or 0) for r in resultados]

    return labels, values


def get_ventas_por_cliente(session):
    """Obtiene sumatoria de ventas por cliente para el KPI"""
    from tucajero.models.producto import Venta
    from tucajero.models.cliente import Cliente
    from sqlalchemy import func

    resultados = (
        session.query(Cliente.nombre, func.sum(Venta.total))
        .join(Venta, Venta.cliente_id == Cliente.id)
        .filter(Venta.anulada == False)
        .group_by(Cliente.nombre)
        .order_by(func.sum(Venta.total).desc())
        .limit(10)
        .all()
    )

    labels = [r[0] or "Desconocido" for r in resultados]
    values = [float(r[1] or 0) for r in resultados]

    # Include anonymous sales
    anonimas = session.query(func.sum(Venta.total)).filter(
        Venta.cliente_id == None, Venta.anulada == False
    ).scalar()
    if anonimas and float(anonimas) > 0:
        labels.append("Consumidor Final")
        values.append(float(anonimas))

    return labels, values
