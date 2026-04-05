from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QGridLayout,
    QHeaderView,
)
from PySide6.QtCore import Qt

from tucajero.app.ui.theme.theme import app_style, PRIMARY, SECONDARY, SUCCESS, WARNING, ACCENT
from tucajero.ui.chart_widget import ChartWidget
from tucajero.ui.components_premium import (
    MetricCardMaxton,
    ChartCardMaxton,
    ButtonPremium,
    TABLE_STYLE_PREMIUM,
)
from tucajero.ui.chart_revenue import RevenueChartCard
from tucajero.ui.period_selector import PeriodSelector
from tucajero.ui.design_tokens import Typography, Colors, Spacing, BorderRadius


class DashboardView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Layout principal del dashboard estilo Falcon"""
        c = Colors

        self.setStyleSheet(f"""
            QWidget {{
                background-color: #ffffff;
                color: #1a1a1a;
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 32)
        root.setSpacing(20)

        # ===================== HEADER =====================
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        title = QLabel("Dashboard")
        title.setStyleSheet(f"color: {c.TEXT_PRIMARY}; font-size: {Typography.H2}px; font-weight: {Typography.BOLD}; background: transparent;")
        header_layout.addWidget(title)

        from datetime import datetime
        now = datetime.now()
        fecha = QLabel(now.strftime("%A, %d de %B %Y"))
        fecha.setStyleSheet(f"color: {c.TEXT_SECONDARY}; font-size: {Typography.BODY}px; background: transparent;")
        header_layout.addWidget(fecha)

        header_layout.addStretch()

        btn_refresh = ButtonPremium("🔄 Actualizar", style="secondary")
        btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(btn_refresh)

        root.addWidget(header)

        # ===================== PERÍODO SELECTOR =====================
        self.period_selector = PeriodSelector()
        self.period_selector.period_changed.connect(self.on_period_changed)
        root.addWidget(self.period_selector)

        # ===================== GRÁFICO DE INGRESOS SUPERIOR =====================
        self.revenue_chart = RevenueChartCard(
            title="Ventas de Hoy",
            amount="$0.00",
            subtitle="Comparación con ayer",
            data_points=[100, 150, 120, 180, 140, 160, 190, 170, 200]
        )
        root.addWidget(self.revenue_chart)

        # ===================== METRIC CARDS (Estilo Falcon) =====================
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        self.card_ventas_hoy = MetricCardMaxton(
            title="Ventas Hoy",
            value="$0",
            change_percent=0,
            change_positive=True,
            accent_color="#10b981"  # Verde
        )
        cards_row.addWidget(self.card_ventas_hoy)

        self.card_ventas_mes = MetricCardMaxton(
            title="Ventas Mes",
            value="$0",
            change_percent=0,
            change_positive=True,
            accent_color="#3b82f6"  # Azul
        )
        cards_row.addWidget(self.card_ventas_mes)

        self.card_ticket = MetricCardMaxton(
            title="Ticket Prom.",
            value="$0",
            change_percent=0,
            change_positive=True,
            accent_color="#8b5cf6"  # Púrpura
        )
        cards_row.addWidget(self.card_ticket)

        self.card_num_ventas = MetricCardMaxton(
            title="Nº Ventas",
            value="0",
            change_percent=0,
            change_positive=True,
            accent_color="#f59e0b"  # Ámbar
        )
        cards_row.addWidget(self.card_num_ventas)

        cards_row.setStretch(0, 1)
        cards_row.setStretch(1, 1)
        cards_row.setStretch(2, 1)
        cards_row.setStretch(3, 1)

        root.addLayout(cards_row)

        # ===================== GRÁFICOS INFERIORES =====================
        grid = QGridLayout()
        grid.setSpacing(24)

        self.card_chart_ventas = ChartCardMaxton(
            title="Ventas últimos 7 días",
            subtitle="Comparación diaria"
        )
        self.card_chart_ventas.setMinimumHeight(300)
        grid.addWidget(self.card_chart_ventas, 0, 0)

        self.card_metodos_pago = ChartCardMaxton(
            title="Métodos de pago"
        )
        self.card_metodos_pago.setMinimumHeight(300)
        grid.addWidget(self.card_metodos_pago, 0, 1)

        root.addLayout(grid)

        # ===================== TABLA DE VENTAS RECIENTES =====================
        table_card = QFrame()
        table_card.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.XL}px;
            }}
        """)
        table_card_layout = QVBoxLayout()
        table_card_layout.setContentsMargins(8, 8, 8, 8)
        table_card_layout.setSpacing(0)
        table_card.setLayout(table_card_layout)

        table_title = QLabel("Ventas Recientes")
        table_title.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H4}px;
                font-weight: {Typography.BOLD};
                background: transparent;
                padding: {Spacing.LG}px {Spacing.XL}px {Spacing.SM}px {Spacing.XL}px;
            }}
        """)
        table_card_layout.addWidget(table_title)

        self.table_ventas = QTableWidget()
        self.table_ventas.setColumnCount(5)
        self.table_ventas.setHorizontalHeaderLabels([
            "Fecha", "Cliente", "Total", "Método", "Productos"
        ])
        self.table_ventas.setStyleSheet(TABLE_STYLE_PREMIUM)
        self.table_ventas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_ventas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_ventas.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        table_card_layout.addWidget(self.table_ventas)
        root.addWidget(table_card)

    # =========================
    # PERÍODO SELECTOR CALLBACK
    # =========================
    def on_period_changed(self, period):
        """Llamado cuando el usuario cambia el período"""
        print(f"Período cambiado a: {period}")
        # Aquí llamarías a tu lógica de BD para traer datos del período
        self.load_data()

    # =========================
    # LOAD DATA
    # =========================
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

    def refresh_data(self):
        """Método para actualizar los datos del dashboard"""
        self.load_data()

    def get_kpis(self):
        try:
            from tucajero.services.venta_service import VentaService

            venta_service = VentaService(self.session)

            total_hoy = venta_service.get_total_hoy()
            total_mes = venta_service.get_total_mes()
            num_ventas_hoy = venta_service.get_num_ventas_hoy()
            ticket_prom = total_hoy / num_ventas_hoy if num_ventas_hoy > 0 else 0

            # Calcular tendencias comparando con período anterior
            total_ayer = venta_service.get_total_ayer()
            if total_ayer > 0:
                cambio_hoy = ((total_hoy - total_ayer) / total_ayer) * 100
                tendencia_hoy = round(cambio_hoy)
                hoy_positivo = cambio_hoy >= 0
            else:
                tendencia_hoy = 0
                hoy_positivo = True

            total_mes_ant = venta_service.get_total_mes_anterior()
            if total_mes_ant > 0:
                cambio_mes = ((total_mes - total_mes_ant) / total_mes_ant) * 100
                tendencia_mes = round(cambio_mes)
                mes_positivo = cambio_mes >= 0
            else:
                tendencia_mes = 0
                mes_positivo = True

            num_ventas_ayer = venta_service.get_num_ventas_ayer()
            if num_ventas_ayer > 0:
                cambio_num = ((num_ventas_hoy - num_ventas_ayer) / num_ventas_ayer) * 100
                tendencia_num = round(cambio_num)
                num_positivo = cambio_num >= 0
            else:
                tendencia_num = 0
                num_positivo = True

            # Calcular tendencia de ticket promedio
            tendencia_ticket = 0

            # Actualizar cards con tendencias (estilo Falcon)
            self.card_ventas_hoy.set_value(f"${total_hoy:,.0f}")
            self.card_ventas_hoy.set_change(tendencia_hoy, hoy_positivo)

            self.card_ventas_mes.set_value(f"${total_mes:,.0f}")
            self.card_ventas_mes.set_change(tendencia_mes, mes_positivo)

            self.card_ticket.set_value(f"${ticket_prom:,.0f}")
            if tendencia_ticket:
                self.card_ticket.set_change(tendencia_ticket, True)

            self.card_num_ventas.set_value(str(num_ventas_hoy))
            self.card_num_ventas.set_change(tendencia_num, num_positivo)

            # Actualizar gráfico de ingresos
            self.revenue_chart.update_data(
                amount=f"${total_hoy:,.2f}",
                subtitle=f"Ayer: ${total_ayer:,.2f}" if total_ayer > 0 else "Sin datos ayer"
            )

        except Exception as e:
            print(f"Error in get_kpis: {e}")

    def get_ventas_7_dias(self):
        try:
            from tucajero.services.venta_service import VentaService

            venta_service = VentaService(self.session)
            labels, valores = venta_service.get_ventas_ultimos_7_dias()

            chart_widget = ChartWidget()
            chart_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            chart_widget.setMinimumHeight(250)
            chart_widget.plot_bar(labels, valores, "")

            while self.card_chart_ventas.content_layout.count():
                item = self.card_chart_ventas.content_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.card_chart_ventas.content_layout.addWidget(chart_widget)
        except Exception as e:
            print(f"Error in get_ventas_7_dias: {e}")

    def get_metodos_pago(self):
        try:
            from tucajero.services.venta_service import VentaService

            venta_service = VentaService(self.session)
            metodos_labels, metodos_valores = venta_service.get_ventas_por_metodo()

            pie_chart = ChartWidget()
            pie_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            pie_chart.setMinimumHeight(250)
            pie_chart.plot_pie(metodos_labels, metodos_valores, "")

            while self.card_metodos_pago.content_layout.count():
                item = self.card_metodos_pago.content_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.card_metodos_pago.content_layout.addWidget(pie_chart)
        except Exception as e:
            print(f"Error in get_metodos_pago: {e}")

    def get_ventas_recientes(self):
        try:
            from tucajero.models.producto import Venta, VentaItem, Producto
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

            self.table_ventas.setRowCount(len(ventas))

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
                    productos_nombres = []
                    for vp in items_venta:
                        if vp.producto:
                            productos_nombres.append(vp.producto.nombre)
                    productos_str = ", ".join(productos_nombres[:3])
                    if len(productos_nombres) > 3:
                        productos_str += f" +{len(productos_nombres) - 3}"
                    if not productos_str:
                        productos_str = "Sin detalle"
                except Exception as e:
                    print(f"Error obteniendo productos: {e}")
                    productos_str = "Sin detalle"

                items = [fecha, cliente, total, metodo, productos_str]
                for j, text in enumerate(items):
                    item = QTableWidgetItem(text)
                    item.setForeground(Qt.GlobalColor.black)
                    self.table_ventas.setItem(i, j, item)

            self.table_ventas.resizeColumnsToContents()
        except Exception as e:
            print(f"Error in get_ventas_recientes: {e}")
