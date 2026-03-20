from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt
from utils.theme import get_colors
from utils.formato import fmt_moneda


class MetricCard(QWidget):
    def __init__(self, icon, title, value, color, parent=None):
        super().__init__(parent)
        c = get_colors()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c["bg_card"]};
                border-radius: 12px;
                border: 1px solid {c["border"]};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {color}22;
            color: {color};
            border-radius: 24px;
            font-size: 22px;
        """)

        top_row = QHBoxLayout()
        top_row.addWidget(icon_label)
        top_row.addStretch()
        layout.addLayout(top_row)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 24px; font-weight: bold; border: none; background: transparent;"
        )
        layout.addWidget(self.value_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 12px; border: none; background: transparent;"
        )
        layout.addWidget(title_label)

    def update_value(self, value):
        self.value_label.setText(value)


class DashboardView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self._init_ui()
        self._cargar_datos()

    def _init_ui(self):
        c = get_colors()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Escritorio")
        title.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 22px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(16)

        self.card_ventas_hoy = MetricCard("🛒", "Ventas hoy", fmt_moneda(0), "#6c63ff")
        self.card_ventas_mes = MetricCard(
            "📈", "Ventas del mes", fmt_moneda(0), "#00c48c"
        )
        self.card_clientes = MetricCard("👥", "Clientes", "0", "#00b8d9")
        self.card_productos = MetricCard("📦", "Productos activos", "0", "#ffab2e")

        grid.addWidget(self.card_ventas_hoy, 0, 0)
        grid.addWidget(self.card_ventas_mes, 0, 1)
        grid.addWidget(self.card_clientes, 0, 2)
        grid.addWidget(self.card_productos, 0, 3)
        layout.addLayout(grid)

        sep_label = QLabel("Artículos más vendidos")
        sep_label.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 16px; font-weight: bold; margin-top: 8px; background: transparent;"
        )
        layout.addWidget(sep_label)

        self.tabla_top = QTableWidget()
        self.tabla_top.setColumnCount(4)
        self.tabla_top.setHorizontalHeaderLabels(
            ["Artículo", "Stock", "Cantidad vendida", "Ingresos"]
        )
        self.tabla_top.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_top.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_top.setMaximumHeight(220)
        layout.addWidget(self.tabla_top)

        layout.addStretch()

    def _cargar_datos(self):
        try:
            from services.venta_service import VentaService
            from services.producto_service import ProductoService
            from services.cliente_service import ClienteService
            from datetime import datetime

            vs = VentaService(self.session)
            ps = ProductoService(self.session)
            cs = ClienteService(self.session)

            ventas_hoy = vs.get_ventas_del_dia()
            total_hoy = sum(v.total for v in ventas_hoy if not v.anulada)
            self.card_ventas_hoy.update_value(fmt_moneda(total_hoy))

            todas = vs.get_all_ventas() if hasattr(vs, "get_all_ventas") else []
            inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            total_mes = sum(
                v.total for v in todas if not v.anulada and v.fecha >= inicio_mes
            )
            self.card_ventas_mes.update_value(fmt_moneda(total_mes))

            clientes = cs.get_all_clientes()
            self.card_clientes.update_value(str(len(clientes)))

            productos = ps.get_all_productos()
            self.card_productos.update_value(str(len(productos)))

            self._cargar_top_productos(todas)

        except Exception as e:
            import logging

            logging.error(f"Dashboard error: {e}")

    def _cargar_top_productos(self, ventas):
        from collections import defaultdict

        conteo = defaultdict(
            lambda: {"nombre": "", "stock": 0, "cantidad": 0, "ingresos": 0.0}
        )
        for v in ventas:
            if v.anulada:
                continue
            for item in v.items:
                k = item.producto_id
                conteo[k]["nombre"] = item.producto.nombre if item.producto else str(k)
                conteo[k]["stock"] = item.producto.stock if item.producto else 0
                conteo[k]["cantidad"] += item.cantidad
                conteo[k]["ingresos"] += item.cantidad * item.precio

        top = sorted(conteo.values(), key=lambda x: x["cantidad"], reverse=True)[:5]
        self.tabla_top.setRowCount(len(top))
        for i, p in enumerate(top):
            self.tabla_top.setItem(i, 0, QTableWidgetItem(p["nombre"]))
            self.tabla_top.setItem(i, 1, QTableWidgetItem(str(p["stock"])))
            self.tabla_top.setItem(i, 2, QTableWidgetItem(str(p["cantidad"])))
            self.tabla_top.setItem(i, 3, QTableWidgetItem(fmt_moneda(p["ingresos"])))

    def refresh(self):
        self._cargar_datos()
