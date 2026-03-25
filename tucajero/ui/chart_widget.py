from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt
from utils.theme import get_colors

try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
    from matplotlib.figure import Figure

    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False


class ChartWidget(QWidget):
    """Widget para mostrar gráficos de matplotlib embebidos en Qt"""

    def __init__(self, parent=None):
        super().__init__(parent)

        if not MATPLOTLIB_OK:
            layout = QVBoxLayout(self)
            msg = QLabel("📊 Gráficos no disponibles\nmatplotlib no está instalado")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("color: #666; padding: 40px;")
            layout.addWidget(msg)
            return

        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from matplotlib.figure import Figure

        self.FigureCanvasQTAgg = FigureCanvasQTAgg
        self.Figure = Figure

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = FigureCanvasQTAgg(Figure(figsize=(6, 4)))
        layout.addWidget(self.canvas)

    def plot_bar(self, labels, values, title="Ventas"):
        """Gráfico de barras"""
        if not MATPLOTLIB_OK:
            return
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        colors = get_chart_colors(len(values))
        bars = ax.bar(range(len(labels)), values, color=colors)

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)

        ax.set_ylabel("Total ($)", fontsize=9)
        ax.set_title(title, fontsize=12, fontweight="bold")

        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"${int(val):,}",
                ha="center",
                va="bottom",
                fontsize=7,
            )

        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def plot_pie(self, labels, values, title="Distribución"):
        """Gráfico de torta"""
        if not MATPLOTLIB_OK:
            return
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)

        colors = get_chart_colors(len(values))

        if sum(values) == 0:
            ax.text(0.5, 0.5, "Sin datos", ha="center", va="center", fontsize=14)
            self.canvas.draw()
            return

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors,
            textprops={"fontsize": 8},
        )

        ax.set_title(title, fontsize=12, fontweight="bold")
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        """Limpia el gráfico"""
        if not MATPLOTLIB_OK:
            return
        self.canvas.figure.clear()
        self.canvas.draw()


def get_chart_colors(n):
    """Paleta de colores para gráficos"""
    palette = [
        "#3b82f6",  # blue
        "#10b981",  # green
        "#f59e0b",  # amber
        "#ef4444",  # red
        "#8b5cf6",  # purple
        "#06b6d4",  # cyan
        "#ec4899",  # pink
        "#84cc16",  # lime
    ]
    return [palette[i % len(palette)] for i in range(n)]


def get_ventas_por_periodo(session, periodo="dia"):
    """Obtiene datos de ventas por periodo"""
    from datetime import datetime, timedelta
    from models.venta import Venta
    from sqlalchemy import func, extract

    hoy = datetime.now()

    if periodo == "dia":
        inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fmt = "%H:00"
        group_by = extract("hour", Venta.fecha)
    elif periodo == "mes":
        inicio = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fmt = "%d"
        group_by = extract("day", Venta.fecha)
    else:
        inicio = hoy.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_fmt = "%b"
        group_by = extract("month", Venta.fecha)

    resultados = (
        session.query(group_by, func.sum(Venta.total))
        .filter(Venta.fecha >= inicio)
        .group_by(group_by)
        .all()
    )

    if periodo == "dia":
        labels = [f"{r[0]:02d}:00" if r[0] else "Sin hora" for r in resultados]
    elif periodo == "mes":
        labels = [str(r[0]) if r[0] else "" for r in resultados]
    else:
        meses = [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
        ]
        labels = [meses[int(r[0]) - 1] if r[0] else "" for r in resultados]

    values = [float(r[1] or 0) for r in resultados]

    return labels, values


def get_ventas_por_metodo(session):
    """Obtiene ventas por método de pago"""
    from models.venta import Venta
    from sqlalchemy import func

    resultados = (
        session.query(Venta.metodo_pago, func.sum(Venta.total))
        .filter(Venta.metodo_pago.isnot(None))
        .group_by(Venta.metodo_pago)
        .all()
    )

    labels = [r[0] or "Sin método" for r in resultados]
    values = [float(r[1] or 0) for r in resultados]

    return labels, values
