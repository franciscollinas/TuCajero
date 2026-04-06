"""
Dashboard View — Réplica PIXEL PERFECT del diseño Falcon Light
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QScrollArea,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QBrush,
    QFont,
    QLinearGradient,
    QPainterPath,
)
from datetime import datetime, timedelta
from sqlalchemy import func, and_, desc

from tucajero.ui.design_tokens import LightColors as Colors, Typography, BorderRadius
from tucajero.ui.components_premium import FalconHeroCard, FalconMetricCard
from tucajero.models.producto import Venta, VentaItem, Producto
from tucajero.models.cliente import Cliente


class DashboardView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.colors = Colors
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        """Layout principal del dashboard estilo Falcon Light"""
        self.setStyleSheet(f"background-color: {Colors.BG_APP}; font-family: 'Inter', 'Segoe UI';")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Area de scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: {Colors.BG_APP}; border: none; }}")
        
        content = QWidget()
        content.setStyleSheet(f"background-color: {Colors.BG_APP};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(32, 24, 32, 32)
        content_layout.setSpacing(16)

        # 0. HEADER (Título + Refresh)
        header_layout = QHBoxLayout()
        self.title_lbl = QLabel("Panel de Control")
        self.title_lbl.setStyleSheet(f"color: #344050; font-size: 24px; font-weight: 800;")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        
        self.btn_refresh = QPushButton("Refrescar Datos")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2c7be5;
                font-weight: 700;
                padding: 10px 20px;
                border-radius: 6px;
                border: 1px solid #d8e2ef;
            }
            QPushButton:hover { background-color: #f9fafd; border-color: #2c7be5; }
        """)
        self.btn_refresh.clicked.connect(self.refresh)
        header_layout.addWidget(self.btn_refresh)
        content_layout.addLayout(header_layout)

        # 1. HERO CARD (Azul con gráfico de línea)
        self.hero_card = FalconHeroCard(
            title="Hoy $0.00",
            subtitle="Ayer $0.00"
        )
        # Conectar señal de cambio de periodo
        self.hero_card.period_changed.connect(self._on_period_changed)
        content_layout.addWidget(self.hero_card)

        # 2. INFO BAR (Payout info)
        self.info_bar = QFrame()
        self.info_bar.setMinimumHeight(48)
        self.info_bar.setStyleSheet(f"""
            QFrame {{
                background-color: #edf2f9;
                border: 1px solid #d8e2ef;
                border-radius: {BorderRadius.MD}px;
            }}
        """)
        info_layout = QHBoxLayout(self.info_bar)
        info_layout.setContentsMargins(15, 0, 15, 0)
        
        icon_lbl = QLabel("⇅")
        icon_lbl.setStyleSheet("color: #2c7be5; font-weight: bold; font-size: 16px;")
        info_layout.addWidget(icon_lbl)
        
        self.info_text = QLabel("Un pago de $0.00 fue depositado hace 0 días. Tu próximo depósito se espera pronto.")
        self.info_text.setStyleSheet("color: #5e6e82; font-size: 13px; font-weight: 500;")
        info_layout.addWidget(self.info_text)
        info_layout.addStretch()
        content_layout.addWidget(self.info_bar)

        # 3. METRICS ROW (3 Cards)
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(16)
        
        self.card_customers = FalconMetricCard("Clientes", "0", "0.0%", "#f97316") # Naranja
        self.card_orders = FalconMetricCard("Ventas", "0", "0.0%", "#2c7be5")     # Azul
        self.card_revenue = FalconMetricCard("Ingresos", "$0", "0.0%", "#10b981") # Verde
        
        metrics_row.addWidget(self.card_customers)
        metrics_row.addWidget(self.card_orders)
        metrics_row.addWidget(self.card_revenue)
        content_layout.addLayout(metrics_row)

        # 4. TABLA DE COMPRAS RECIENTES
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #edf2f9;
                border-radius: {BorderRadius.LG}px;
            }}
        """)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header de tabla
        t_header = QHBoxLayout()
        t_title = QLabel("Ventas Recientes")
        t_title.setStyleSheet("color: #344050; font-size: 18px; font-weight: 700;")
        t_header.addWidget(t_title)
        t_header.addStretch()
        
        for action in ["+ Nueva", "Filtrar", "Exportar"]:
            act_btn = QPushButton(action)
            act_btn.setStyleSheet("""
                QPushButton { background: #f9fafd; color: #5e6e82; border: 1px solid #d8e2ef; 
                padding: 6px 12px; border-radius: 6px; font-weight: 600; font-size: 12px; }
                QPushButton:hover { background: #edf2f9; }
            """)
            t_header.addWidget(act_btn)
        table_layout.addLayout(t_header)

        # Configuración de tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["", "Cliente", "Teléfono", "Producto", "Estado", "Monto"])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                gridline-color: transparent;
                color: #5e6e82;
                font-family: 'Inter';
                selection-background-color: #f0f7ff;
                selection-color: #344050;
            }}
            QHeaderView::section {{
                background-color: #f9fafd;
                color: #5e6e82;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #edf2f9;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid #edf2f9;
                background-color: white;
            }}
            QTableWidget::item:selected {{
                background-color: #f0f7ff;
                color: #344050;
            }}
        """)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        h_header = self.table.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 40)
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 120)
        h_header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 100)
        
        self.table.setMinimumHeight(550)
        
        table_layout.addWidget(self.table)
        content_layout.addWidget(table_container)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def refresh(self):
        """Actualizar datos reales en layout Falcon"""
        try:
            # Consultar ventas de hoy y ayer
            hoy = datetime.now().date()
            ayer = hoy - timedelta(days=1)

            total_hoy = self.session.query(func.sum(Venta.total)).filter(and_(func.date(Venta.fecha) == hoy, Venta.anulada == False)).scalar() or 0
            total_ayer = self.session.query(func.sum(Venta.total)).filter(and_(func.date(Venta.fecha) == ayer, Venta.anulada == False)).scalar() or 0

            # Actualizar Hero
            self.hero_card.lbl_title.setText(f"Hoy ${total_hoy:,.2f}")
            self.hero_card.lbl_subtitle.setText(f"Ayer ${total_ayer:,.2f}")

            # Cargar gráfico de ventas por periodo (por defecto: semana)
            self._cargar_grafico_ventas("semana")

            # Métricas
            n_cust = self.session.query(func.count(func.distinct(Venta.cliente_id))).filter(Venta.anulada == False).scalar() or 0
            n_orders = self.session.query(func.count(Venta.id)).filter(Venta.anulada == False).scalar() or 0
            total_rev = self.session.query(func.sum(Venta.total)).filter(Venta.anulada == False).scalar() or 0

            self.card_customers.lbl_value.setText(f"{n_cust:,}")
            self.card_orders.lbl_value.setText(f"{n_orders:,}")
            self.card_revenue.lbl_value.setText(f"${total_rev:,.0f}")

            self.info_text.setText(f"Un pago de ${total_hoy:,.2f} fue depositado hace 0 días. Tu próximo depósito se espera pronto.")

            # Actualizar Tabla
            self._update_table()

        except Exception as e:
            print(f"Error refreshing dashboard: {e}")

    def _on_period_changed(self, periodo):
        """Maneja el cambio de periodo en el gráfico"""
        print(f"Cambiando gráfico a: {periodo}")
        self._cargar_grafico_ventas(periodo)

    def _cargar_grafico_ventas(self, periodo="semana"):
        """Carga ventas agrupadas según el periodo seleccionado"""
        try:
            hoy = datetime.now().date()
            data_points = []
            
            if periodo == "semana":
                # Últimos 7 días
                inicio = hoy - timedelta(days=6)
                resultados = self._consultar_ventas_por_dia(inicio, hoy)
                data_points = [(f.strftime("%d/%m"), v) for f, v in resultados]
                
            elif periodo == "mes":
                # Todos los días del mes actual
                import calendar
                _, dias_en_mes = calendar.monthrange(hoy.year, hoy.month)
                inicio = hoy.replace(day=1)
                fin = hoy.replace(day=dias_en_mes)
                resultados = self._consultar_ventas_por_dia(inicio, fin)
                data_points = [(f.strftime("%d/%m"), v) for f, v in resultados]
                
            elif periodo == "trimestre":
                # Últimos 3 meses agrupados por semana (~13 semanas)
                inicio = hoy - timedelta(days=90)
                current = inicio
                semanas = []
                while current <= hoy:
                    week_end = min(current + timedelta(days=6), hoy)
                    
                    total = (
                        self.session.query(func.sum(Venta.total))
                        .filter(and_(
                            func.date(Venta.fecha) >= current.isoformat(),
                            func.date(Venta.fecha) <= week_end.isoformat(),
                            Venta.anulada == False
                        ))
                        .scalar() or 0
                    )
                    semanas.append((current.strftime("%d/%m"), float(total)))
                    current = week_end + timedelta(days=1)
                data_points = semanas
                
            elif periodo == "semestre":
                # Últimos 6 meses
                meses_espanol = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                inicio = hoy.replace(day=1)
                # Retroceder 5 meses desde el mes actual
                mes_inicio = hoy.month - 5
                año_inicio = hoy.year
                if mes_inicio <= 0:
                    mes_inicio += 12
                    año_inicio -= 1
                inicio = datetime(año_inicio, mes_inicio, 1).date()
                resultados = self._consultar_ventas_por_mes(inicio, hoy)
                data_points = [(meses_espanol[f.month - 1], v) for f, v in resultados]

            elif periodo == "año":
                # Últimos 12 meses (rolante, no solo año calendario)
                meses_espanol = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                # Retroceder 11 meses desde el mes actual
                inicio = hoy.replace(day=1)
                mes_inicio = hoy.month - 11
                año_inicio = hoy.year
                while mes_inicio <= 0:
                    mes_inicio += 12
                    año_inicio -= 1
                inicio = datetime(año_inicio, mes_inicio, 1).date()
                resultados = self._consultar_ventas_por_mes(inicio, hoy)
                data_points = [(meses_espanol[f.month - 1], v) for f, v in resultados]
            
            # Si no hay datos, generar placeholders vacíos
            if not data_points:
                if periodo == "semana":
                    for i in range(7):
                        dia = (hoy - timedelta(days=6-i)).strftime("%d/%m")
                        data_points.append((dia, 0))
                elif periodo == "mes":
                    import calendar
                    _, dias_en_mes = calendar.monthrange(hoy.year, hoy.month)
                    data_points = [(f"{d:02d}/{hoy.month:02d}", 0) for d in range(1, dias_en_mes + 1)]
                elif periodo == "trimestre":
                    inicio = hoy - timedelta(days=90)
                    current = inicio
                    data_points = []
                    while current <= hoy:
                        data_points.append((current.strftime("%d/%m"), 0))
                        current += timedelta(days=7)
                elif periodo == "semestre":
                    meses_espanol = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                    # Últimos 6 meses desde el mes actual
                    data_points = []
                    for i in range(6):
                        mes_idx = (hoy.month - 6 + i) % 12
                        data_points.append((meses_espanol[mes_idx], 0))
                elif periodo == "año":
                    meses_espanol = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
                    # Últimos 12 meses
                    data_points = []
                    for i in range(12):
                        mes_idx = (hoy.month - 12 + i) % 12
                        data_points.append((meses_espanol[mes_idx], 0))
            
            self.hero_card.update_chart(data_points)
            
        except Exception as e:
            print(f"Error cargando gráfico: {e}")
            import traceback
            traceback.print_exc()

    def _consultar_ventas_por_dia(self, fecha_inicio, fecha_fin):
        """Consulta ventas agrupadas por día"""
        from datetime import timedelta as td
        
        resultados = (
            self.session.query(
                func.date(Venta.fecha).label('fecha'),
                func.sum(Venta.total).label('total')
            )
            .filter(and_(
                func.date(Venta.fecha) >= fecha_inicio.isoformat(),
                func.date(Venta.fecha) <= fecha_fin.isoformat(),
                Venta.anulada == False
            ))
            .group_by(func.date(Venta.fecha))
            .order_by(func.date(Venta.fecha))
            .all()
        )

        # Generar todos los días del rango
        todos_los_dias = []
        current = fecha_inicio
        while current <= fecha_fin:
            todos_los_dias.append(current)
            current += td(days=1)

        # Convertir resultados a dict con fecha como date object
        ventas_dict = {}
        for fecha_str, total in resultados:
            try:
                if isinstance(fecha_str, str):
                    fecha_date = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                else:
                    fecha_date = fecha_str
                ventas_dict[fecha_date] = float(total or 0)
            except:
                pass

        # Retornar lista con todos los días (0 si no hay ventas)
        return [(dia, ventas_dict.get(dia, 0)) for dia in todos_los_dias]

    def _consultar_ventas_por_mes(self, fecha_inicio, fecha_fin):
        """Consulta ventas agrupadas por mes"""
        from sqlalchemy import extract
        
        # Determinar años involucrados
        anios = list(range(fecha_inicio.year, fecha_fin.year + 1))
        
        resultados = []
        for anio in anios:
            mes_inicio = fecha_inicio.month if anio == fecha_inicio.year else 1
            mes_fin = fecha_fin.month if anio == fecha_fin.year else 12
            
            for mes in range(mes_inicio, mes_fin + 1):
                total = (
                    self.session.query(func.sum(Venta.total))
                    .filter(and_(
                        extract('year', Venta.fecha) == anio,
                        extract('month', Venta.fecha) == mes,
                        Venta.anulada == False
                    ))
                    .scalar() or 0
                )
                resultados.append((datetime(anio, mes, 1).date(), float(total)))
        
        return resultados

    def _update_table(self):
        # Obtener las últimas 10 ventas reales
        ventas_q = (self.session.query(Venta)
                   .order_by(desc(Venta.fecha)).limit(10).all())

        self.table.setRowCount(len(ventas_q))
        for i, v in enumerate(ventas_q):
            # 0. Estrella de David azul
            star_widget = QWidget()
            star_widget.setStyleSheet("background: transparent;")
            star_layout = QHBoxLayout(star_widget)
            star_layout.setContentsMargins(0, 0, 0, 0)
            star_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            star_lbl = QLabel("✡")
            star_lbl.setStyleSheet("""
                QLabel {
                    color: #2c7be5;
                    font-size: 14px;
                    background: transparent;
                    padding: 0px;
                }
            """)
            star_layout.addWidget(star_lbl)
            self.table.setCellWidget(i, 0, star_widget)

            # 1. Customer (Bold Blue)
            cliente = getattr(v, 'cliente', None)
            cliente_nombre = getattr(cliente, 'nombre', None) or "Mostrador"
            it_name = QTableWidgetItem(cliente_nombre)
            it_name.setForeground(QColor("#2c7be5"))
            it_name.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.table.setItem(i, 1, it_name)

            # 2. Teléfono del cliente
            telefono = getattr(cliente, 'telefono', None) or "N/A"
            it_tel = QTableWidgetItem(telefono)
            it_tel.setForeground(QColor("#5e6e82"))
            self.table.setItem(i, 2, it_tel)

            # 3. Product (Summary)
            prod_summary = "Sin productos"
            items = getattr(v, 'items', [])
            if items and len(items) > 0:
                primer_item = items[0]
                producto = getattr(primer_item, 'producto', None)
                if producto and getattr(producto, 'nombre', None):
                    nombre_prod = producto.nombre
                    prod_summary = nombre_prod[:25] + "..." if len(nombre_prod) > 25 else nombre_prod
            it_prod = QTableWidgetItem(prod_summary)
            it_prod.setForeground(QColor("#5e6e82"))
            self.table.setItem(i, 3, it_prod)
            
            # 4. Payment (Badge style pill)
            status_widget = QWidget()
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(0, 0, 0, 0)
            status_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            badge = QLabel("EXITOSA" if not v.anulada else "ANULADA")
            bg_color = "#eaf6f1" if not v.anulada else "#fdf2f2"
            text_color = "#00a65a" if not v.anulada else "#dd4b39"
            
            badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    color: {text_color};
                    border-radius: 10px;
                    padding: 4px 10px;
                    font-size: 10px;
                    font-weight: 800;
                    min-width: 70px;
                }}
            """)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_layout.addWidget(badge)
            self.table.setCellWidget(i, 4, status_widget)
            
            # 5. Amount
            total = getattr(v, 'total', 0) or 0
            it_amt = QTableWidgetItem(f"${total:,.2f}")
            it_amt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it_amt.setForeground(QColor("#344050"))
            it_amt.setFont(QFont("Inter", 10, QFont.Weight.Medium))
            self.table.setItem(i, 5, it_amt)
            
            self.table.setRowHeight(i, 58)
