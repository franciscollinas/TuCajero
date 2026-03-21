from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from utils.theme import get_colors, card_style, label_style
from utils.formato import fmt_moneda


def add_shadow(widget, blur=20, offset_y=4, opacity=80):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset_y)
    shadow.setColor(QColor(0, 0, 0, opacity))
    widget.setGraphicsEffect(shadow)


class MetricCard(QWidget):
    def __init__(self, icon, title, value, color, badge=None, parent=None):
        super().__init__(parent)
        from utils.theme import get_colors
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        c = get_colors()

        self.setMinimumHeight(110)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_card']};
                border-radius: 12px;
                border: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Fila top: ícono + badge
        top = QHBoxLayout()
        icon_box = QLabel(icon)
        icon_box.setFixedSize(44, 44)
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setStyleSheet(f"""
            background-color: {color}22;
            color: {color};
            border-radius: 10px;
            font-size: 20px;
            border: none;
        """)
        top.addWidget(icon_box)
        top.addStretch()

        if badge:
            badge_lbl = QLabel(badge)
            badge_lbl.setStyleSheet(f"""
                color: {c['success']};
                font-size: 11px;
                font-weight: bold;
                background: {c['success_light']};
                border-radius: 8px;
                padding: 2px 8px;
                border: none;
            """)
            top.addWidget(badge_lbl)
        layout.addLayout(top)

        # Valor principal
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: {c['text_primary']};
            font-size: 26px;
            font-weight: bold;
            border: none;
            background: transparent;
        """)
        layout.addWidget(self.value_label)

        # Título
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"""
            color: {c['text_muted']};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 0.8px;
            border: none;
            background: transparent;
        """)
        layout.addWidget(title_lbl)

    def update_value(self, value):
        self.value_label.setText(value)


class DashboardView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self._init_ui()

    def _init_ui(self):
        c = get_colors()
        self.setStyleSheet(f"background-color: {c['bg_app']};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(24)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        title = QLabel("Escritorio")
        title.setStyleSheet(label_style("xl", "bold"))
        from datetime import datetime

        sub = QLabel(f"Bienvenido — {datetime.now().strftime('%A %d de %B, %Y')}")
        sub.setStyleSheet(label_style("sm", color_key="text_secondary"))
        title_layout.addWidget(title)
        title_layout.addWidget(sub)
        layout.addLayout(title_layout)

        grid = QHBoxLayout()
        grid.setSpacing(16)

        self.card_ventas_hoy  = MetricCard("📈", "Ventas hoy",        fmt_moneda(0), c['accent'],   badge="+12%")
        self.card_ventas_mes  = MetricCard("📅", "Ventas del mes",    fmt_moneda(0), c['info'],    badge="+5.2%")
        self.card_clientes    = MetricCard("👥", "Clientes",          "0",           c['success'])
        self.card_productos   = MetricCard("📦", "Productos activos", "0",           c['warning'])

        for card in [
            self.card_ventas_hoy,
            self.card_ventas_mes,
            self.card_clientes,
            self.card_productos,
        ]:
            grid.addWidget(card)
        layout.addLayout(grid)

        section_label = QLabel("Artículos más vendidos")
        section_label.setStyleSheet(label_style("lg", "bold"))
        layout.addWidget(section_label)

        table_container = QWidget()
        table_container.setStyleSheet(f"""
            QWidget {{
                {card_style()}
            }}
        """)
        add_shadow(table_container, blur=16, offset_y=4, opacity=40)
        tc_layout = QVBoxLayout(table_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)

        self.tabla_top = QTableWidget()
        self.tabla_top.setColumnCount(4)
        self.tabla_top.setHorizontalHeaderLabels(
            ["Artículo", "Stock", "Cantidad vendida", "Ingresos"]
        )
        self.tabla_top.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_top.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_top.setAlternatingRowColors(True)
        self.tabla_top.verticalHeader().setVisible(False)
        self.tabla_top.setMinimumHeight(200)
        self.tabla_top.setStyleSheet("border: none; border-radius: 14px;")
        tc_layout.addWidget(self.tabla_top)
        layout.addWidget(table_container)

    def showEvent(self, event):
        super().showEvent(event)
        self._cargar_datos()

    def _cargar_datos(self):
        import logging

        try:
            from models.producto import Venta, Producto
            from models.cliente import Cliente
            from datetime import datetime, date

            hoy_inicio = datetime.combine(date.today(), datetime.min.time())
            mes_inicio = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            ventas_hoy = (
                self.session.query(Venta)
                .filter(Venta.fecha >= hoy_inicio, Venta.anulada == False)
                .all()
            )
            self.card_ventas_hoy.update_value(
                fmt_moneda(sum(v.total for v in ventas_hoy))
            )
            logging.info(f"Dashboard: ventas hoy = {len(ventas_hoy)}")

            ventas_mes = (
                self.session.query(Venta)
                .filter(Venta.fecha >= mes_inicio, Venta.anulada == False)
                .all()
            )
            self.card_ventas_mes.update_value(
                fmt_moneda(sum(v.total for v in ventas_mes))
            )

            num_clientes = 0
            try:
                num_clientes = self.session.query(Cliente).count()
            except Exception:
                pass
            self.card_clientes.update_value(str(num_clientes))

            try:
                num_prod = (
                    self.session.query(Producto).filter(Producto.activo == True).count()
                )
                self.card_productos.update_value(str(num_prod))
            except Exception:
                self.card_productos.update_value("—")

            self._cargar_top_productos(ventas_mes)

        except Exception as e:
            logging.error(f"Dashboard._cargar_datos FATAL: {e}", exc_info=True)

    def _cargar_top_productos(self, ventas):
        from collections import defaultdict

        conteo = defaultdict(
            lambda: {"nombre": "", "stock": 0, "cantidad": 0, "ingresos": 0.0}
        )
        for v in ventas:
            if v.anulada:
                continue
            for item in v.items if hasattr(v, "items") else []:
                k = item.producto_id
                conteo[k]["nombre"] = item.producto.nombre if item.producto else str(k)
                conteo[k]["stock"] = item.producto.stock if item.producto else 0
                conteo[k]["cantidad"] += item.cantidad
                conteo[k]["ingresos"] += item.cantidad * item.precio

        top = sorted(conteo.values(), key=lambda x: x["cantidad"], reverse=True)[:8]
        self.tabla_top.setRowCount(len(top))
        c = get_colors()
        for i, p in enumerate(top):
            self.tabla_top.setItem(i, 0, QTableWidgetItem(p["nombre"]))
            stock_item = QTableWidgetItem(str(p["stock"]))
            if p["stock"] <= 0:
                stock_item.setForeground(QColor(c["danger"]))
            elif p["stock"] < 5:
                stock_item.setForeground(QColor(c["warning"]))
            else:
                stock_item.setForeground(QColor(c["success"]))
            self.tabla_top.setItem(i, 1, stock_item)
            self.tabla_top.setItem(i, 2, QTableWidgetItem(str(p["cantidad"])))
            self.tabla_top.setItem(i, 3, QTableWidgetItem(fmt_moneda(p["ingresos"])))

    def refresh(self):
        self._cargar_datos()
