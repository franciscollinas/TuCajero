from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt
from services.producto_service import ProductoService
from services.producto_service import VentaService
from ui.chart_widget import ChartWidget


COLORS = {
    "primary": "#2563EB",
    "green": "#10B981",
    "orange": "#F59E0B",
    "red": "#EF4444",
}


class KpiCard(QFrame):
    def __init__(self, title, value, color):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                padding: 16px;
                border: 1px solid #E5E7EB;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #6B7280; font-size: 12px;")

        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"""
            color: {color};
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)


class DashboardPro(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session

        self.venta_service = VentaService(session)
        self.producto_service = ProductoService(session)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setStyleSheet("background: #F9FAFB;")

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # KPI ROW
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(16)

        self.kpi_ventas_hoy = KpiCard("Ventas hoy", "$0", COLORS["primary"])
        self.kpi_ventas_mes = KpiCard("Ventas mes", "$0", COLORS["green"])
        self.kpi_num_ventas = KpiCard("N° ventas", "0", COLORS["orange"])
        self.kpi_ticket = KpiCard("Ticket promedio", "$0", COLORS["red"])

        for kpi in [
            self.kpi_ventas_hoy,
            self.kpi_ventas_mes,
            self.kpi_num_ventas,
            self.kpi_ticket,
        ]:
            kpi.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            kpi_layout.addWidget(kpi)

        main_layout.addLayout(kpi_layout)

        # GRÁFICOS - Grid 2 columnas
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(16)

        self.chart_bar = ChartWidget()
        self.chart_bar.setMinimumHeight(280)

        self.chart_pie = ChartWidget()
        self.chart_pie.setMinimumHeight(280)

        charts_layout.addWidget(self.chart_bar, 1)
        charts_layout.addWidget(self.chart_pie, 1)

        main_layout.addLayout(charts_layout)

        # TITULO TABLA
        titulo_tabla = QLabel("Productos más vendidos")
        titulo_tabla.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #1F2937;
            padding: 8px 0;
        """)
        main_layout.addWidget(titulo_tabla)

        # TABLA
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Ingreso"])
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
                gridline-color: #E5E7EB;
            }
            QTableWidget::item {
                padding: 12px;
            }
            QTableWidget::item:alternate {
                background: #F9FAFB;
            }
            QHeaderView::section {
                background: #F3F4F6;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #E5E7EB;
                font-weight: bold;
                color: #374151;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setShowGrid(False)

        main_layout.addWidget(self.table)

    def load_data(self):
        try:
            ventas_hoy = self.venta_service.get_total_hoy()
            ventas_mes = self.venta_service.get_total_mes()
            num_ventas = self.venta_service.get_num_ventas_hoy()

            ticket = ventas_hoy / num_ventas if num_ventas else 0

            self.kpi_ventas_hoy.findChildren(QLabel)[1].setText(f"${ventas_hoy:,.0f}")
            self.kpi_ventas_mes.findChildren(QLabel)[1].setText(f"${ventas_mes:,.0f}")
            self.kpi_num_ventas.findChildren(QLabel)[1].setText(str(num_ventas))
            self.kpi_ticket.findChildren(QLabel)[1].setText(f"${ticket:,.0f}")

            # GRÁFICOS
            labels, valores = self.venta_service.get_ventas_ultimos_7_dias()
            self.chart_bar.plot_bar(
                labels, valores, "Ventas últimos 7 días", COLORS["primary"]
            )

            # Colores para métodos de pago
            metodo_colores = {
                "Efectivo": COLORS["green"],
                "Nequi": COLORS["primary"],
                "Daviplata": COLORS["orange"],
                "Transferencia": COLORS["red"],
                "Mixto": "#8B5CF6",
                "Tarjeta": "#EC4899",
            }
            labels_m, valores_m = self.venta_service.get_ventas_por_metodo()
            colores = [metodo_colores.get(m, COLORS["primary"]) for m in labels_m]
            self.chart_pie.plot_pie(labels_m, valores_m, "Métodos de pago", colores)

            # TABLA
            productos = self.producto_service.get_top_vendidos()

            if not productos:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No hay datos disponibles"))
                self.table.setSpan(0, 0, 1, 3)
                self.table.item(0, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                self.table.setRowCount(len(productos))
                for row, p in enumerate(productos):
                    self.table.setItem(row, 0, QTableWidgetItem(p.nombre))
                    self.table.setItem(row, 1, QTableWidgetItem(str(p.cantidad)))
                    self.table.setItem(row, 2, QTableWidgetItem(f"${p.ingreso:,.0f}"))

        except Exception as e:
            print("Dashboard error:", e)

    def refresh(self):
        try:
            self._load_kpis()
            self._load_charts()
        except Exception as e:
            import logging

            logging.error(f"Error refrescando dashboard: {e}")

    def _load_kpis(self):
        pass

    def _load_charts(self):
        pass
