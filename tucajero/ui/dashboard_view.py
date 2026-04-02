"""Dashboard Premium - NO MODIFICAR"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from datetime import datetime, timedelta
from sqlalchemy import and_, func, desc

from tucajero.models.producto import Producto, Venta, VentaItem
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import (
    MetricCardPremium, CardPremium, SectionHeaderPremium,
    ButtonPremium, TABLE_STYLE_PREMIUM
)
from tucajero.utils.formato import fmt_moneda


class DashboardView(QWidget):
    """Dashboard premium con métricas y análisis"""
    
    def __init__(self, session):
        super().__init__()
        self.session = session
        
        # Estilo de fondo
        self.setStyleSheet(f"""
            QWidget {{
                background: {Colors.BG_APP};
            }}
        """)
        
        self.init_ui()
        self.setup_refresh_timer()
        self.refresh_data()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.XXXL, Spacing.XXL, Spacing.XXXL, Spacing.XXL
        )
        layout.setSpacing(Spacing.XXL)
        
        # HEADER
        header = self.create_header()
        layout.addWidget(header)
        
        # MÉTRICAS (4 cards en grid 2x2)
        metrics_grid = self.create_metrics_grid()
        layout.addLayout(metrics_grid)
        
        # CONTENIDO PRINCIPAL (2 columnas)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(Spacing.XXL)
        
        # Columna izquierda: Productos más vendidos
        left_col = self.create_left_column()
        content_layout.addWidget(left_col, 2)
        
        # Columna derecha: Actividad reciente
        right_col = self.create_right_column()
        content_layout.addWidget(right_col, 3)
        
        layout.addLayout(content_layout)
        
        # FILA INFERIOR: Alertas de stock
        alerts_section = self.create_alerts_section()
        layout.addWidget(alerts_section)
        
        layout.addStretch()
    
    def create_header(self):
        """Header con título y última actualización"""
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(Spacing.LG)
        
        # Título
        title = QLabel("Dashboard")
        title.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H1}px;
                font-weight: {Typography.BOLD};
                background: transparent;
            }}
        """)
        header_layout.addWidget(title)
        
        # Fecha actual
        now = datetime.now()
        date_label = QLabel(now.strftime("%A, %d de %B %Y"))
        date_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_TERTIARY};
                font-size: {Typography.BODY}px;
                background: transparent;
            }}
        """)
        header_layout.addWidget(date_label)
        
        header_layout.addStretch()
        
        # Botón actualizar
        refresh_btn = ButtonPremium("🔄 Actualizar", style="secondary")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        return header
    
    def create_metrics_grid(self):
        """Grid 2x2 de métricas principales"""
        grid = QGridLayout()
        grid.setSpacing(Spacing.XL)
        
        # Card 1: Ventas hoy
        self.card_ventas_hoy = MetricCardPremium(
            title="Ventas Hoy",
            value="$0",
            change=None,
            gradient_type="green",
            icon="💰"
        )
        self.card_ventas_hoy.setMinimumHeight(160)
        grid.addWidget(self.card_ventas_hoy, 0, 0)
        
        # Card 2: Ventas mes
        self.card_ventas_mes = MetricCardPremium(
            title="Ventas Este Mes",
            value="$0",
            change=None,
            gradient_type="blue",
            icon="📊"
        )
        self.card_ventas_mes.setMinimumHeight(160)
        grid.addWidget(self.card_ventas_mes, 0, 1)
        
        # Card 3: Ticket promedio
        self.card_ticket = MetricCardPremium(
            title="Ticket Promedio",
            value="$0",
            change=None,
            gradient_type="cyan",
            icon="🛒"
        )
        self.card_ticket.setMinimumHeight(160)
        grid.addWidget(self.card_ticket, 1, 0)
        
        # Card 4: Total ventas
        self.card_num_ventas = MetricCardPremium(
            title="Nº de Ventas",
            value="0",
            change=None,
            gradient_type="purple",
            icon="📈"
        )
        self.card_num_ventas.setMinimumHeight(160)
        grid.addWidget(self.card_num_ventas, 1, 1)
        
        return grid
    
    def create_left_column(self):
        """Columna izquierda: Productos más vendidos"""
        card = CardPremium()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(Spacing.LG)
        
        # Header
        header = SectionHeaderPremium("🔥 Productos Más Vendidos", "Ver reporte →")
        card_layout.addWidget(header)
        
        # Tabla
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(4)
        self.tabla_productos.setHorizontalHeaderLabels([
            "PRODUCTO", "VENDIDOS", "INGRESOS", "STOCK"
        ])
        self.tabla_productos.setStyleSheet(TABLE_STYLE_PREMIUM)
        self.tabla_productos.horizontalHeader().setStretchLastSection(True)
        self.tabla_productos.setMinimumHeight(400)
        self.tabla_productos.setShowGrid(False)
        self.tabla_productos.setAlternatingRowColors(False)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_productos.verticalHeader().setVisible(False)
        
        card_layout.addWidget(self.tabla_productos)
        
        return card
    
    def create_right_column(self):
        """Columna derecha: Últimas ventas"""
        card = CardPremium()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(Spacing.LG)
        
        # Header
        header = SectionHeaderPremium("⚡ Actividad Reciente")
        card_layout.addWidget(header)
        
        # Tabla
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(5)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "HORA", "CLIENTE", "PRODUCTOS", "MÉTODO", "TOTAL"
        ])
        self.tabla_ventas.setStyleSheet(TABLE_STYLE_PREMIUM)
        self.tabla_ventas.horizontalHeader().setStretchLastSection(True)
        self.tabla_ventas.setMinimumHeight(400)
        self.tabla_ventas.setShowGrid(False)
        self.tabla_ventas.setAlternatingRowColors(False)
        self.tabla_ventas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_ventas.verticalHeader().setVisible(False)
        
        card_layout.addWidget(self.tabla_ventas)
        
        return card
    
    def create_alerts_section(self):
        """Sección de alertas de stock bajo"""
        card = CardPremium()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(Spacing.LG)
        
        # Header
        header = SectionHeaderPremium("⚠️ Alertas de Inventario", "Ir a inventario →")
        card_layout.addWidget(header)
        
        # Tabla
        self.tabla_alertas = QTableWidget()
        self.tabla_alertas.setColumnCount(4)
        self.tabla_alertas.setHorizontalHeaderLabels([
            "CÓDIGO", "PRODUCTO", "STOCK ACTUAL", "STOCK MÍNIMO"
        ])
        self.tabla_alertas.setStyleSheet(TABLE_STYLE_PREMIUM)
        self.tabla_alertas.horizontalHeader().setStretchLastSection(True)
        self.tabla_alertas.setMaximumHeight(250)
        self.tabla_alertas.setShowGrid(False)
        self.tabla_alertas.setAlternatingRowColors(False)
        self.tabla_alertas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_alertas.verticalHeader().setVisible(False)
        
        card_layout.addWidget(self.tabla_alertas)
        
        return card
    
    def setup_refresh_timer(self):
        """Configura timer de actualización automática"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(30000)  # 30 segundos
    
    def refresh_data(self):
        """Actualiza todos los datos del dashboard"""
        self.actualizar_metricas()
        self.actualizar_productos_vendidos()
        self.actualizar_ventas_recientes()
        self.actualizar_alertas_stock()
    
    def actualizar_metricas(self):
        """Actualiza las 4 cards de métricas"""
        hoy = datetime.now().date()
        inicio_mes = datetime.now().replace(day=1).date()
        
        # Ventas de hoy
        ventas_hoy = self.session.query(Venta).filter(
            and_(
                func.date(Venta.fecha) == hoy,
                Venta.anulada == False
            )
        ).all()
        
        total_hoy = sum(v.total for v in ventas_hoy)
        num_ventas_hoy = len(ventas_hoy)
        
        # Ventas del mes
        ventas_mes = self.session.query(Venta).filter(
            and_(
                func.date(Venta.fecha) >= inicio_mes,
                Venta.anulada == False
            )
        ).all()
        
        total_mes = sum(v.total for v in ventas_mes)
        
        # Ticket promedio
        ticket_prom = total_hoy / num_ventas_hoy if num_ventas_hoy > 0 else 0
        
        # Actualizar labels (necesitas acceder a los widgets internos)
        # Por simplicidad, recrear las cards
        # TODO: Implementar método update() en MetricCardPremium
    
    def actualizar_productos_vendidos(self):
        """Actualiza tabla de productos más vendidos"""
        # Query productos más vendidos
        hoy = datetime.now().date()
        
        query = self.session.query(
            Producto.nombre,
            func.sum(VentaItem.cantidad).label('total_vendido'),
            func.sum(VentaItem.precio * VentaItem.cantidad).label('ingresos'),
            Producto.stock
        ).join(
            VentaItem, VentaItem.producto_id == Producto.id
        ).join(
            Venta, Venta.id == VentaItem.venta_id
        ).filter(
            and_(
                func.date(Venta.fecha) == hoy,
                Venta.anulada == False
            )
        ).group_by(
            Producto.id
        ).order_by(
            desc('total_vendido')
        ).limit(10)
        
        resultados = query.all()
        
        # Llenar tabla
        self.tabla_productos.setRowCount(len(resultados))
        
        for row, (nombre, vendidos, ingresos, stock) in enumerate(resultados):
            # Producto
            item_nombre = QTableWidgetItem(nombre)
            item_nombre.setFont(QFont("Inter", Typography.BODY_SM, Typography.SEMIBOLD))
            self.tabla_productos.setItem(row, 0, item_nombre)
            
            # Vendidos
            item_vendidos = QTableWidgetItem(str(int(vendidos)))
            item_vendidos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_productos.setItem(row, 1, item_vendidos)
            
            # Ingresos
            item_ingresos = QTableWidgetItem(fmt_moneda(ingresos))
            item_ingresos.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_productos.setItem(row, 2, item_ingresos)
            
            # Stock
            item_stock = QTableWidgetItem(str(stock))
            item_stock.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Colorear según stock
            if stock < 10:
                item_stock.setForeground(QColor(Colors.DANGER_LIGHT))
            elif stock < 30:
                item_stock.setForeground(QColor(Colors.WARNING_LIGHT))
            else:
                item_stock.setForeground(QColor(Colors.SUCCESS_LIGHT))
            
            self.tabla_productos.setItem(row, 3, item_stock)
    
    def actualizar_ventas_recientes(self):
        """Actualiza tabla de ventas recientes"""
        hoy = datetime.now().date()
        
        ventas = self.session.query(Venta).filter(
            and_(
                func.date(Venta.fecha) == hoy,
                Venta.anulada == False
            )
        ).order_by(
            desc(Venta.fecha)
        ).limit(15).all()
        
        self.tabla_ventas.setRowCount(len(ventas))
        
        for row, venta in enumerate(ventas):
            # Hora
            hora = venta.fecha.strftime("%H:%M")
            item_hora = QTableWidgetItem(hora)
            self.tabla_ventas.setItem(row, 0, item_hora)
            
            # Cliente
            cliente = venta.cliente.nombre if venta.cliente else "Consumidor Final"
            item_cliente = QTableWidgetItem(cliente)
            self.tabla_ventas.setItem(row, 1, item_cliente)
            
            # Productos (resumen)
            num_items = len(venta.items)
            productos_text = f"{num_items} producto{'s' if num_items > 1 else ''}"
            item_productos = QTableWidgetItem(productos_text)
            self.tabla_ventas.setItem(row, 2, item_productos)
            
            # Método
            metodo = venta.metodo_pago or "Efectivo"
            item_metodo = QTableWidgetItem(metodo)
            self.tabla_ventas.setItem(row, 3, item_metodo)
            
            # Total
            item_total = QTableWidgetItem(fmt_moneda(venta.total))
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_total.setFont(QFont("Inter", Typography.BODY_SM, Typography.SEMIBOLD))
            self.tabla_ventas.setItem(row, 4, item_total)
    
    def actualizar_alertas_stock(self):
        """Actualiza tabla de alertas de stock"""
        productos_bajo_stock = self.session.query(Producto).filter(
            and_(
                Producto.activo == True,
                Producto.stock_minimo.isnot(None),
                Producto.stock <= Producto.stock_minimo
            )
        ).order_by(
            Producto.stock
        ).limit(10).all()
        
        self.tabla_alertas.setRowCount(len(productos_bajo_stock))
        
        for row, producto in enumerate(productos_bajo_stock):
            # Código
            item_codigo = QTableWidgetItem(producto.codigo)
            self.tabla_alertas.setItem(row, 0, item_codigo)
            
            # Nombre
            item_nombre = QTableWidgetItem(producto.nombre)
            item_nombre.setFont(QFont("Inter", Typography.BODY_SM, Typography.SEMIBOLD))
            self.tabla_alertas.setItem(row, 1, item_nombre)
            
            # Stock actual (con color de alerta)
            item_stock = QTableWidgetItem(str(producto.stock))
            item_stock.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if producto.stock == 0:
                item_stock.setForeground(QColor(Colors.DANGER))
                item_stock.setFont(QFont("Inter", Typography.BODY_SM, Typography.BOLD))
            else:
                item_stock.setForeground(QColor(Colors.WARNING))
            
            self.tabla_alertas.setItem(row, 2, item_stock)
            
            # Stock mínimo
            item_minimo = QTableWidgetItem(str(producto.stock_minimo))
            item_minimo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_minimo.setForeground(QColor(Colors.TEXT_TERTIARY))
            self.tabla_alertas.setItem(row, 3, item_minimo)
