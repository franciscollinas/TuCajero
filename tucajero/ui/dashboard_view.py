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
    QPushButton,
    QMessageBox,
    QComboBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
import os
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

        # Outer wrapper: transparent, only provides padding so shadow is not clipped
        self.setStyleSheet("background: transparent; border: none;")
        self.setMinimumHeight(124)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 6, 6, 14)
        outer.setSpacing(0)

        # Inner card with scoped object-name so global QWidget { background } can't win
        inner = QWidget()
        inner.setObjectName("metricCard")
        inner.setStyleSheet(f"""
            QWidget#metricCard {{
                background-color: {c["bg_card"]};
                border-radius: 20px;
                border: none;
            }}
            QWidget#metricCard * {{
                background: transparent;
                border: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(36)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 60))
        inner.setGraphicsEffect(shadow)
        outer.addWidget(inner)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)

        # ── Top: icon pill + badge ─────────────────────────────────────
        top = QHBoxLayout()
        top.setSpacing(8)

        icon_pill = QLabel(icon)
        icon_pill.setFixedSize(48, 48)
        icon_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_pill.setObjectName("iconPill")
        icon_pill.setStyleSheet(f"""
            QLabel#iconPill {{
                background-color: {color}28 !important;
                color: {color};
                border-radius: 14px;
                font-size: 22px;
            }}
        """)
        top.addWidget(icon_pill)
        top.addStretch()

        if badge:
            badge_lbl = QLabel(badge)
            badge_lbl.setObjectName("badgeLbl")
            badge_lbl.setStyleSheet(f"""
                QLabel#badgeLbl {{
                    color: {c["success"]};
                    font-size: 11px;
                    font-weight: bold;
                    background-color: {c["success_light"]} !important;
                    border-radius: 9px;
                    padding: 3px 10px;
                }}
            """)
            top.addWidget(badge_lbl)
        layout.addLayout(top)

        # ── Value ───────────────────────────────────────────────────────
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: {c["text_primary"]};
            font-size: 28px;
            font-weight: bold;
        """)
        layout.addWidget(self.value_label)

        # ── Title ───────────────────────────────────────────────────────
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"""
            color: {c["text_muted"]};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
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

        self.card_ventas_hoy = MetricCard(
            "📈", "Ventas hoy", fmt_moneda(0), c["accent"], badge="+12%"
        )
        self.card_ventas_mes = MetricCard(
            "📅", "Ventas del mes", fmt_moneda(0), c["info"], badge="+5.2%"
        )
        self.card_clientes = MetricCard("👥", "Clientes", "0", c["success"])
        self.card_productos = MetricCard("📦", "Productos activos", "0", c["warning"])

        for card in [
            self.card_ventas_hoy,
            self.card_ventas_mes,
            self.card_clientes,
            self.card_productos,
        ]:
            grid.addWidget(card)
        layout.addLayout(grid)

        section_label = QLabel("Acciones rápidas")
        section_label.setStyleSheet(label_style("lg", "bold"))
        layout.addWidget(section_label)

        actions_grid = QHBoxLayout()
        actions_grid.setSpacing(16)

        self.btn_ventas_dia = self._crear_accion_card(
            "💰", "Ventas del día", "Corte de caja hoy", c["accent"]
        )
        self.btn_ventas_dia.clicked.connect(self._ir_a_corte)

        self.btn_ventas_mes = self._crear_accion_card(
            "📊", "Ventas del mes", "Reporte mensual", c["info"]
        )
        self.btn_ventas_mes.clicked.connect(self._ir_a_historial)

        self.btn_facturas = self._crear_accion_card(
            "🧾", "Facturas", "Ver facturas PDF", c["purple"]
        )
        self.btn_facturas.clicked.connect(self._abrir_facturas)

        self.btn_backup = self._crear_accion_card(
            "💾", "Backup", "Respaldar datos", c["success"]
        )
        self.btn_backup.clicked.connect(self._hacer_backup)

        self.btn_actualizar = self._crear_accion_card(
            "🔄", "Actualizar", "Nueva versión", c["warning"]
        )
        self.btn_actualizar.clicked.connect(self._mostrar_actualizacion)

        self.btn_restaurar = self._crear_accion_card(
            "📥", "Restaurar", "Cargar backup", c["danger"]
        )
        self.btn_restaurar.clicked.connect(self._restaurar_backup)

        self.btn_exportar = self._crear_accion_card(
            "📤", "Exportar", "Copiar a USB", c["info"]
        )
        self.btn_exportar.clicked.connect(self._exportar_backup)

        for btn in [
            self.btn_ventas_dia,
            self.btn_ventas_mes,
            self.btn_facturas,
            self.btn_backup,
            self.btn_actualizar,
            self.btn_restaurar,
            self.btn_exportar,
        ]:
            actions_grid.addWidget(btn)
        layout.addLayout(actions_grid)

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

    def _crear_accion_card(self, icon, titulo, desc, color):
        """Crea una tarjeta botón estilizada para acciones"""
        from PySide6.QtWidgets import QPushButton

        btn = QPushButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(80)

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_colors()["bg_card"]};
                border: 2px solid {color}40;
                border-radius: 16px;
                padding: 16px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {color}20;
                border: 2px solid {color};
            }}
        """)

        layout = QHBoxLayout(btn)
        layout.setContentsMargins(20, 12, 20, 12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 32px;")
        layout.addWidget(icon_lbl)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        titulo_lbl = QLabel(titulo)
        titulo_lbl.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {get_colors()['text_primary']};"
        )
        text_layout.addWidget(titulo_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(
            f"font-size: 12px; color: {get_colors()['text_secondary']};"
        )
        text_layout.addWidget(desc_lbl)

        layout.addLayout(text_layout)
        layout.addStretch()

        return btn

    def _abrir_facturas(self):
        """Abre la carpeta de facturas"""
        ruta = os.path.join(os.environ.get("LOCALAPPDATA", ""), "TuCajero", "facturas")
        os.makedirs(ruta, exist_ok=True)
        os.startfile(ruta)

    def _ir_a_corte(self):
        """Navega a corte de caja"""
        parent = self.window() if self.parent() else None
        if parent and hasattr(parent, "switch_view_by_name"):
            parent.switch_view_by_name("corte")

    def _ir_a_historial(self):
        """Navega a historial"""
        parent = self.window() if self.parent() else None
        if parent and hasattr(parent, "switch_view_by_name"):
            parent.switch_view_by_name("historial")

    def _hacer_backup(self):
        """Ejecuta backup manual"""
        try:
            from utils.backup import backup_database

            backup_database()
            QMessageBox.information(self, "✅ Backup", "Backup creado exitosamente")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al crear backup: {e}")

    def _mostrar_actualizacion(self):
        """Muestra instrucciones para actualizar"""
        msg = (
            "🔄 Actualizar TuCajero\n\n"
            "Tus datos están seguros porque se almacenan en:\n"
            f"%LOCALAPPDATA%\\TuCajero\\database\\pos.db\n\n"
            "Para actualizar:\n"
            "1. Haz clic en el botón 'Backup' para respaldar tus datos\n"
            "2. Descarga la nueva versión de TuCajero\n"
            "3. Ejecuta el nuevo instalador\n"
            "4. Tus datos se cargarán automáticamente\n\n"
            "💡 Tus ventas, productos y clientes están seguros."
        )
        QMessageBox.information(self, "🔄 Actualizar sistema", msg)

    def _restaurar_backup(self):
        """Permite restaurar un backup existente"""
        from PySide6.QtWidgets import QFileDialog

        respuesta = QMessageBox.warning(
            self,
            "⚠️ Restaurar Backup",
            "Esto reemplazará TODOS los datos actuales.\n\n¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de backup",
            "",
            "Base de datos (*.db)",
        )

        if not ruta:
            return

        try:
            from utils.backup import restaurar_backup

            restaurar_backup(ruta)
            reply = QMessageBox.information(
                self,
                "✅ Restauración exitosa",
                "El backup ha sido restaurado.\n\n"
                "La aplicación se cerrará. Reinicie manualmente.",
            )
            from PySide6.QtWidgets import QApplication

            QApplication.instance().quit()
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Error",
                f"No se pudo restaurar el backup:\n{e}",
            )

    def _exportar_backup(self):
        """Exporta el backup más reciente a una ubicación externa"""
        from PySide6.QtWidgets import QFileDialog
        from utils.backup import get_backups_dir
        import shutil

        backup_dir = get_backups_dir()

        if not os.path.exists(backup_dir):
            QMessageBox.warning(self, "⚠️ Sin backups", "No hay backups disponibles")
            return

        archivos = [f for f in os.listdir(backup_dir) if f.endswith(".db")]

        if not archivos:
            QMessageBox.warning(self, "⚠️ Sin backups", "No hay backups disponibles")
            return

        ultimo = sorted(archivos)[-1]

        ruta_destino = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar destino (USB o carpeta)",
        )

        if not ruta_destino:
            return

        origen = os.path.join(backup_dir, ultimo)
        destino = os.path.join(ruta_destino, ultimo)

        try:
            shutil.copy2(origen, destino)
            QMessageBox.information(
                self,
                "✅ Exportado",
                f"Backup copiado a:\n{destino}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Error",
                f"No se pudo exportar el backup:\n{e}",
            )

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


class DashboardViewWithCharts(DashboardView):
    """Dashboard con gráficos visuales"""

    def _init_ui(self):
        super()._init_ui()

        self.chart_type = "bar"
        self.chart_periodo = "dia"

        chart_section = QLabel("📊 Análisis de Ventas")
        chart_section.setStyleSheet(label_style("lg", "bold"))
        self.layout().insertWidget(4, chart_section)

        controls = QHBoxLayout()
        controls.setSpacing(12)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["📊 Barras", "🍰 Torta"])
        self.combo_tipo.setFixedWidth(120)
        self.combo_tipo.currentTextChanged.connect(self._actualizar_tipo_grafico)

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Hoy", "Este mes", "Este año"])
        self.combo_periodo.setFixedWidth(120)
        self.combo_periodo.currentTextChanged.connect(self._actualizar_periodo_grafico)

        controls.addWidget(QLabel("Tipo:"))
        controls.addWidget(self.combo_tipo)
        controls.addWidget(QLabel("Período:"))
        controls.addWidget(self.combo_periodo)
        controls.addStretch()

        self.layout().insertLayout(5, controls)

        from ui.chart_widget import (
            ChartWidget,
            get_ventas_por_periodo,
            get_ventas_por_metodo,
            get_chart_colors,
        )

        self.get_ventas_por_periodo = get_ventas_por_periodo
        self.get_ventas_por_metodo = get_ventas_por_metodo

        chart_card = QWidget()
        chart_card.setStyleSheet(f"""
            QWidget {{
                {card_style()}
            }}
        """)
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(16, 16, 16, 16)

        self.chart_widget = ChartWidget()
        chart_layout.addWidget(self.chart_widget)

        self.layout().insertWidget(6, chart_card)

    def _actualizar_tipo_grafico(self, texto):
        self.chart_type = "bar" if "Barras" in texto else "pie"
        self._actualizar_grafico()

    def _actualizar_periodo_grafico(self, texto):
        periodo_map = {"Hoy": "dia", "Este mes": "mes", "Este año": "año"}
        self.chart_periodo = periodo_map.get(texto, "dia")
        self._actualizar_grafico()

    def _actualizar_grafico(self):
        try:
            labels, values = self.get_ventas_por_periodo(
                self.session, self.chart_periodo
            )

            if not labels or sum(values) == 0:
                labels, values = self.get_ventas_por_metodo(self.session)
                titulo = "Ventas por método de pago"
            else:
                titulo = f"Ventas por {self.chart_periodo}"

            if self.chart_type == "bar":
                self.chart_widget.plot_bar(labels, values, titulo)
            else:
                self.chart_widget.plot_pie(labels, values, titulo)
        except Exception as e:
            self.chart_widget.clear()
