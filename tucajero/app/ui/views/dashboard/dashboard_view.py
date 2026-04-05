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
        
        self.card_customers = FalconMetricCard("Clientes", "0", "0.0%", "#fef2f2")
        self.card_orders = FalconMetricCard("Ventas", "0", "0.0%", "#ffffff")
        self.card_revenue = FalconMetricCard("Ingresos", "$0", "0.0%", "#ecfdf5")
        
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
        self.table.setHorizontalHeaderLabels(["", "Cliente", "Email", "Producto", "Estado", "Monto"])
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: white;
                border: none;
                gridline-color: transparent;
                color: #5e6e82;
                font-family: 'Inter';
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
        """)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
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

    def _update_table(self):
        # Obtener las últimas 10 ventas reales
        ventas_q = (self.session.query(Venta)
                   .order_by(desc(Venta.fecha)).limit(10).all())
        
        self.table.setRowCount(len(ventas_q))
        for i, v in enumerate(ventas_q):
            # 0. Checkbox
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(10, 0, 0, 0)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            from PySide6.QtWidgets import QCheckBox
            chk = QCheckBox()
            chk_layout.addWidget(chk)
            self.table.setCellWidget(i, 0, chk_widget)
            
            # 1. Customer (Bold Blue)
            cliente_nombre = v.cliente.nombre if v.cliente else "Mostrador"
            it_name = QTableWidgetItem(cliente_nombre)
            it_name.setForeground(QColor("#2c7be5"))
            it_name.setFont(QFont("Inter", 10, QFont.Weight.Bold))
            self.table.setItem(i, 1, it_name)
            
            # 2. Email
            it_mail = QTableWidgetItem("N/A")
            self.table.setItem(i, 2, it_mail)
            
            # 3. Product (Summary)
            prod_summary = "Varios productos"
            if v.items:
                prod_summary = v.items[0].producto.nombre[:25] + "..." if len(v.items[0].producto.nombre) > 25 else v.items[0].producto.nombre
            it_prod = QTableWidgetItem(prod_summary)
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
            it_amt = QTableWidgetItem(f"${v.total:,.2f}")
            it_amt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it_amt.setForeground(QColor("#344050"))
            it_amt.setFont(QFont("Inter", 10, QFont.Weight.Medium))
            self.table.setItem(i, 5, it_amt)
            
            self.table.setRowHeight(i, 58)
