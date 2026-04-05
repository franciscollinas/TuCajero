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
from tucajero.ui.design_tokens import Typography, Colors


class DashboardView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Layout principal del dashboard estilo Maxton"""
        c = Colors

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c.BG_APP};
                color: {c.TEXT_PRIMARY};
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 32)
        root.setSpacing(24)

        # HEADER (título + fecha + botón refresh)
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        # Título
        title = QLabel("Dashboard")
        title.setStyleSheet(f"color: {c.TEXT_PRIMARY}; font-size: {Typography.H2}px; font-weight: {Typography.BOLD}; background: transparent;")
        header_layout.addWidget(title)

        # Fecha actual
        from datetime import datetime
        now = datetime.now()
        fecha = QLabel(now.strftime("%A, %d de %B %Y"))
        fecha.setStyleSheet(f"color: {c.TEXT_SECONDARY}; font-size: {Typography.BODY}px; background: transparent;")
        header_layout.addWidget(fecha)

        header_layout.addStretch()

        # Botón refresh
        btn_refresh = ButtonPremium("🔄 Actualizar", style="secondary")
        btn_refresh.clicked.connect(self.refresh_data)
        header_layout.addWidget(btn_refresh)

        root.addWidget(header)

        # GRID PRINCIPAL (2x2)
        grid = QGridLayout()
        grid.setSpacing(24)

        # FILA 1
        # Card 1: Ventas hoy (arriba izquierda)
        self.card_ventas_hoy = MetricCardMaxton(
            value="$0",
            label="Ventas Hoy",
            gradient_colors="green"
        )
        self.card_ventas_hoy.setMinimumHeight(160)
        grid.addWidget(self.card_ventas_hoy, 0, 0)

        # Card 2: Gráfico de barras (arriba derecha - ocupa 2 filas)
        self.card_chart_ventas = ChartCardMaxton(
            title="Ventas últimos 7 días",
            subtitle="Comparación diaria"
        )
        self.card_chart_ventas.setMinimumHeight(320)
        grid.addWidget(self.card_chart_ventas, 0, 1, 2, 1)

        # FILA 2
        # Card 3: Métodos de pago (abajo izquierda)
        self.card_metodos_pago = ChartCardMaxton(
            title="Métodos de pago"
        )
        self.card_metodos_pago.setMinimumHeight(320)
        grid.addWidget(self.card_metodos_pago, 1, 0)

        root.addLayout(grid)

        # FILA 3: Cards de métricas pequeñas (horizontal)
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(24)

        self.card_ventas_mes = MetricCardMaxton(
            value="$0",
            label="Ventas Mes",
            gradient_colors="blue"
        )
        self.card_ventas_mes.setMinimumHeight(140)
        metrics_row.addWidget(self.card_ventas_mes)

        self.card_ticket = MetricCardMaxton(
            value="$0",
            label="Ticket Promedio",
            gradient_colors="cyan"
        )
        self.card_ticket.setMinimumHeight(140)
        metrics_row.addWidget(self.card_ticket)

        self.card_num_ventas = MetricCardMaxton(
            value="0",
            label="Nº Ventas",
            gradient_colors="purple"
        )
        self.card_num_ventas.setMinimumHeight(140)
        metrics_row.addWidget(self.card_num_ventas)

        root.addLayout(metrics_row)

        # FILA 4: Tabla de ventas recientes
        table_card = ChartCardMaxton(title="Ventas Recientes")
        table_card.setMinimumHeight(400)

        # Tabla dentro de la card
        self.table_ventas = QTableWidget()
        self.table_ventas.setColumnCount(5)
        self.table_ventas.setHorizontalHeaderLabels([
            "Fecha", "Cliente", "Total", "Método", "Productos"
        ])
        self.table_ventas.setStyleSheet(TABLE_STYLE_PREMIUM)
        self.table_ventas.setShowGrid(False)
        self.table_ventas.verticalHeader().setVisible(False)
        self.table_ventas.horizontalHeader().setStretchLastSection(True)

        table_card.content_layout.addWidget(self.table_ventas)

        root.addWidget(table_card)

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
                tendencia_hoy = f"{'+' if cambio_hoy >= 0 else ''}{cambio_hoy:.0f}% vs ayer"
            else:
                tendencia_hoy = "Sin datos ayer" if total_hoy == 0 else "Nuevo registro"

            total_mes_ant = venta_service.get_total_mes_anterior()
            if total_mes_ant > 0:
                cambio_mes = ((total_mes - total_mes_ant) / total_mes_ant) * 100
                tendencia_mes = f"{'+' if cambio_mes >= 0 else ''}{cambio_mes:.0f}% vs mes anterior"
            else:
                tendencia_mes = "Sin datos mes anterior" if total_mes == 0 else "Nuevo registro"

            num_ventas_ayer = venta_service.get_num_ventas_ayer()
            if num_ventas_ayer > 0:
                cambio_num = ((num_ventas_hoy - num_ventas_ayer) / num_ventas_ayer) * 100
                tendencia_num = f"{'+' if cambio_num >= 0 else ''}{cambio_num:.0f}% vs ayer"
            else:
                tendencia_num = "Sin datos ayer" if num_ventas_hoy == 0 else "Nuevo registro"

            # Calcular tendencia de ticket promedio (semana actual vs anterior)
            num_sem_actual = venta_service.get_num_ventas_semana_actual()
            num_sem_anterior = venta_service.get_num_ventas_ultima_semana()
            total_sem_actual = total_hoy  # Aproximación: usamos hoy como referencia
            if num_sem_anterior > 0:
                ticket_sem_ant = total_mes_ant / max(num_sem_anterior, 1)  # Aproximación
                if ticket_sem_ant > 0:
                    cambio_ticket = ((ticket_prom - ticket_sem_ant) / ticket_sem_ant) * 100
                    tendencia_ticket = f"{'+' if cambio_ticket >= 0 else ''}{cambio_ticket:.0f}% vs semana anterior"
                else:
                    tendencia_ticket = ""
            else:
                tendencia_ticket = ""

            # Actualizar cards con tendencias
            hoy_positivo = total_hoy >= total_ayer if total_ayer > 0 else True
            self.card_ventas_hoy.set_value(f"${total_hoy:,.0f}")
            self.card_ventas_hoy.set_change(tendencia_hoy, hoy_positivo)

            mes_positivo = total_mes >= total_mes_ant if total_mes_ant > 0 else True
            self.card_ventas_mes.set_value(f"${total_mes:,.0f}")
            self.card_ventas_mes.set_change(tendencia_mes, mes_positivo)

            self.card_ticket.set_value(f"${ticket_prom:,.0f}")
            if tendencia_ticket:
                self.card_ticket.set_change(tendencia_ticket, True)

            self.card_num_ventas.set_value(str(num_ventas_hoy))
            num_positivo = num_ventas_hoy >= num_ventas_ayer if num_ventas_ayer > 0 else True
            self.card_num_ventas.set_change(tendencia_num, num_positivo)
        except Exception as e:
            print(f"Error in get_kpis: {e}")

    def get_ventas_7_dias(self):
        try:
            from tucajero.services.venta_service import VentaService

            venta_service = VentaService(self.session)
            labels, valores = venta_service.get_ventas_ultimos_7_dias()

            # Limpiar contenido previo
            chart_widget = ChartWidget()
            chart_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            chart_widget.setMinimumHeight(250)
            chart_widget.plot_bar(labels, valores, "")

            # Limpiar layout y agregar nuevo widget
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

            # Limpiar contenido previo
            pie_chart = ChartWidget()
            pie_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            pie_chart.setMinimumHeight(250)
            pie_chart.plot_pie(metodos_labels, metodos_valores, "")

            # Limpiar layout y agregar nuevo widget
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
                    item.setForeground(Qt.GlobalColor.white)
                    self.table_ventas.setItem(i, j, item)

            self.table_ventas.resizeColumnsToContents()
        except Exception as e:
            print(f"Error in get_ventas_recientes: {e}")
