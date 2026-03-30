from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
)
from PySide6.QtCore import Qt

from app.ui.theme.theme import app_style, PRIMARY, SECONDARY, SUCCESS, WARNING, ACCENT
from ui.chart_widget import ChartWidget


class DashboardView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setStyleSheet(
            app_style()
            + """
            QWidget {
                background-color: #0F172A;
            }
        """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(20)

        # =========================
        # KPI ROW
        # =========================
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(20)

        self.kpi_ventas_hoy = self.create_kpi("Ventas hoy", "$0", "#22C55E")
        self.kpi_ventas_mes = self.create_kpi("Ventas mes", "$0", "#3B82F6")
        self.kpi_ticket = self.create_kpi("Ticket promedio", "$0", "#06B6D4")
        self.kpi_facturas = self.create_kpi("N° ventas", "0", "#F59E0B")

        kpi_row.addWidget(self.kpi_ventas_hoy)
        kpi_row.addWidget(self.kpi_ventas_mes)
        kpi_row.addWidget(self.kpi_ticket)
        kpi_row.addWidget(self.kpi_facturas)

        root.addLayout(kpi_row)

        # =========================
        # CHARTS ROW
        # =========================
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)

        self.chart_bar = self.create_card("Ventas últimos 7 días")
        self.chart_bar_layout = self.chart_bar.layout()

        self.chart_widget = ChartWidget()
        self.chart_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chart_widget.setMinimumHeight(300)
        self.chart_bar_layout.addWidget(self.chart_widget)

        self.chart_pie = self.create_card("Métodos de pago")
        self.chart_pie_layout = self.chart_pie.layout()

        self.pie_chart = ChartWidget()
        self.pie_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pie_chart.setMinimumHeight(300)
        self.chart_pie_layout.addWidget(self.pie_chart)

        charts_row.addWidget(self.chart_bar, 2)
        charts_row.addWidget(self.chart_pie, 1)

        root.addLayout(charts_row)

        # =========================
        # TABLE
        # =========================
        table_card = self.create_card("Ventas recientes")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Fecha", "Cliente", "Total", "Método", "Productos"]
        )
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                color: white;
                border: none;
                gridline-color: rgba(255,255,255,0.05);
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(255,255,255,0.05);
            }
            QTableWidget::item:hover {
                background: rgba(124, 58, 237, 0.2);
            }
            QTableWidget::item:selected {
                background: #7C3AED;
            }
            QHeaderView::section {
                background: rgba(255,255,255,0.08);
                color: #CBD5E1;
                padding: 14px;
                border: none;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                font-weight: 600;
                font-size: 12px;
            }
        """)

        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        table_card.layout().addWidget(self.table)

        root.addWidget(table_card)

    # =========================
    # COMPONENTES
    # =========================
    def create_kpi(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color}, stop:1 {color}CC);
                border-radius: 16px;
                border: 1px solid {color};
            }}
            QFrame:hover {{
                border: 1px solid white;
            }}
        """)
        card.setMinimumHeight(120)
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        label_value = QLabel(value)
        label_value.setStyleSheet(
            "color: white; font-size: 26px; font-weight: bold; background: transparent;"
        )

        label_title = QLabel(title)
        label_title.setStyleSheet(
            "color: rgba(255,255,255,0.8); font-size: 12px; font-weight: 500; background: transparent;"
        )

        layout.addWidget(label_value)
        layout.addWidget(label_title)

        return card

    def create_card(self, title):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border-radius: 16px;
                border: 1px solid #334155;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        label = QLabel(title)
        label.setStyleSheet(
            "color: white; font-weight: 600; font-size: 16px; background: transparent;"
        )

        layout.addWidget(label)

        return card

    def load_data(self):
        try:
            self.get_kpis()
        except Exception as e:
            print(f"Error loading KPIs: {e}")

        try:
            self.get_ventas_7_dias()
        except Exception as e:
            print(f"Error loading chart: {e}")

        try:
            self.get_metodos_pago()
        except Exception as e:
            print(f"Error loading payment methods: {e}")

        try:
            self.get_ventas_recientes()
        except Exception as e:
            print(f"Error loading recent sales: {e}")

    def refresh(self):
        self.load_data()

    def get_kpis(self):
        try:
            from services.venta_service import VentaService

            venta_service = VentaService(self.session)

            total_hoy = venta_service.get_total_hoy()
            total_mes = venta_service.get_total_mes()
            num_ventas_hoy = venta_service.get_num_ventas_hoy()
            ticket_prom = total_hoy / num_ventas_hoy if num_ventas_hoy > 0 else 0

            self.kpi_ventas_hoy.findChild(QLabel).setText(f"${total_hoy:,.0f}")
            self.kpi_ventas_mes.findChild(QLabel).setText(f"${total_mes:,.0f}")
            self.kpi_ticket.findChild(QLabel).setText(f"${ticket_prom:,.0f}")
            self.kpi_facturas.findChild(QLabel).setText(str(num_ventas_hoy))
        except Exception as e:
            print(f"Error in get_kpis: {e}")

    def get_ventas_7_dias(self):
        try:
            from services.venta_service import VentaService

            venta_service = VentaService(self.session)
            labels, valores = venta_service.get_ventas_ultimos_7_dias()

            self.chart_widget.plot_bar(labels, valores, "")
        except Exception as e:
            print(f"Error in get_ventas_7_dias: {e}")

    def get_metodos_pago(self):
        try:
            from services.venta_service import VentaService

            venta_service = VentaService(self.session)
            metodos_labels, metodos_valores = venta_service.get_ventas_por_metodo()

            self.pie_chart.plot_pie(metodos_labels, metodos_valores, "")
        except Exception as e:
            print(f"Error in get_metodos_pago: {e}")

    def get_ventas_recientes(self):
        try:
            from models.producto import Venta, VentaItem
            from sqlalchemy import desc

            try:
                ventas = (
                    self.session.query(Venta)
                    .order_by(desc(Venta.fecha))
                    .limit(10)
                    .all()
                )
            except:
                ventas = []

            self.table.setRowCount(len(ventas))

            for i, venta in enumerate(ventas):
                fecha = (
                    venta.fecha.strftime("%Y-%m-%d %H:%M")
                    if hasattr(venta.fecha, "strftime")
                    else str(venta.fecha)
                )
                cliente = getattr(venta, "cliente_nombre", "Mostrador") or "Mostrador"
                total = f"${venta.total:,.0f}"
                metodo = venta.metodo_pago or "Efectivo"

                try:
                    items_venta = (
                        self.session.query(VentaItem)
                        .filter(VentaItem.venta_id == venta.id)
                        .all()
                    )
                    productos_nombres = [
                        vp.producto_nombre for vp in items_venta if vp.producto_nombre
                    ]
                    productos_str = ", ".join(productos_nombres[:3])
                    if len(productos_nombres) > 3:
                        productos_str += f" +{len(productos_nombres) - 3}"
                    if not productos_str:
                        productos_str = "Sin detalle"
                except:
                    productos_str = "Sin detalle"

                items = [fecha, cliente, total, metodo, productos_str]
                for j, text in enumerate(items):
                    item = QTableWidgetItem(text)
                    item.setForeground(Qt.GlobalColor.white)
                    self.table.setItem(i, j, item)

            self.table.resizeColumnsToContents()
        except Exception as e:
            print(f"Error in get_ventas_recientes: {e}")
