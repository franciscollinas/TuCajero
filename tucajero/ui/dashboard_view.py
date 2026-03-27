from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QGraphicsDropShadowEffect,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QMessageBox,
    QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QColor
from datetime import datetime, date
import os

from utils.theme import (
    get_colors,
    card_style,
    label_style,
    btn_primary,
    btn_secondary,
    btn_danger,
)
from utils.formato import fmt_moneda


def add_shadow(widget, blur=20, offset_y=4, opacity=80):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset_y)
    shadow.setColor(QColor(0, 0, 0, opacity))
    widget.setGraphicsEffect(shadow)


class ClickableMetricCard(QWidget):
    clicked = Signal()

    def __init__(self, icon, title, value, color, badge=None, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        c = get_colors()

        self.setStyleSheet("background: transparent; border: none;")
        self.setMinimumHeight(120)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 8)
        outer.setSpacing(0)

        inner = QWidget()
        inner.setObjectName("metricCard")
        inner.setStyleSheet(f"""
            QWidget#metricCard {{
                background-color: {c["bg_card"]};
                border-radius: 16px;
                border: 1px solid {c["border"]};
            }}
            QWidget#metricCard:hover {{
                background-color: {c["bg_elevated"]};
                border: 1px solid {c["accent"]};
            }}
        """)
        add_shadow(inner, blur=20, offset_y=4, opacity=40)
        outer.addWidget(inner)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 20px; color: {color};")
        top.addWidget(icon_lbl)
        top.addStretch()

        if badge:
            b_lbl = QLabel(badge)
            b_lbl.setStyleSheet(
                f"background: {c['success_light']}; color: {c['success']}; border-radius: 8px; padding: 2px 8px; font-size: 10px; font-weight: bold;"
            )
            top.addWidget(b_lbl)
        layout.addLayout(top)

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 22px; font-weight: bold;"
        )
        layout.addWidget(self.value_label)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;"
        )
        layout.addWidget(title_lbl)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def update_value(self, value):
        self.value_label.setText(value)


class DashboardView(QWidget):
    """Dashboard unificado: KPIs + Gráficos + Historial Hoy"""

    AUTO_REFRESH_INTERVAL = 30000  # 30 segundos

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.chart_periodo = "mes"
        self._init_ui()
        self._setup_auto_refresh()

    def _setup_auto_refresh(self):
        """Configura el auto-refresh del dashboard"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(self.AUTO_REFRESH_INTERVAL)

    def _init_ui(self):
        c = get_colors()
        self.setStyleSheet(f"background-color: {c['bg_app']};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        main_layout.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_app']};")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        scroll.setWidget(content)

        # ── Encabezado ────────────────────────────────────────────────────────
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title = QLabel("Panel de Control")
        title.setStyleSheet(label_style("xl", "bold"))
        sub = QLabel(
            f"Resumen de actividad — {datetime.now().strftime('%d de %B, %Y')}"
        )
        sub.setStyleSheet(label_style("sm", color_key="text_secondary"))
        title_layout.addWidget(title)
        title_layout.addWidget(sub)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(
            ["Este mes", "Este trimestre", "Este semestre", "Este año"]
        )
        self.combo_periodo.setStyleSheet(
            f"background: {c['bg_card']}; color: {c['text_primary']}; padding: 8px; border-radius: 8px; border: 1px solid {c['border']}; font-weight: bold;"
        )
        self.combo_periodo.currentTextChanged.connect(self._actualizar_periodo_grafico)
        header_layout.addWidget(self.combo_periodo)

        layout.addLayout(header_layout)

        # ── KPI Cards ────────────────────────────────────────────────────────
        kpi_grid = QHBoxLayout()
        kpi_grid.setSpacing(16)

        self.card_hoy = ClickableMetricCard(
            "💰", "Ventas Hoy", fmt_moneda(0), c["accent"]
        )
        self.card_mes = ClickableMetricCard(
            "📊", "Ventas Mes", fmt_moneda(0), c["info"]
        )
        self.card_sistema = ClickableMetricCard(
            "⚙️", "Sistema", "Backup / Edit", c["success"]
        )
        self.card_vencimiento = ClickableMetricCard(
            "📦", "Vencimientos", "Alertas", c["warning"]
        )

        self.card_hoy.clicked.connect(self._ir_a_corte)
        self.card_mes.clicked.connect(self._ir_a_historial)
        self.card_sistema.clicked.connect(self._mostrar_sistema)
        self.card_vencimiento.clicked.connect(self._ir_a_productos)

        for card in [
            self.card_hoy,
            self.card_mes,
            self.card_sistema,
            self.card_vencimiento,
        ]:
            kpi_grid.addWidget(card)
        layout.addLayout(kpi_grid)

        # ── Gráficos ─────────────────────────────────────────────────────────
        charts_layout = QGridLayout()
        charts_layout.setSpacing(20)

        card1, self.chart_evolucion = self._crear_contenedor_grafico()
        charts_layout.addWidget(card1, 0, 0)

        card2, self.chart_metodos = self._crear_contenedor_grafico()
        charts_layout.addWidget(card2, 0, 1)

        card3, self.chart_clientes = self._crear_contenedor_grafico()
        charts_layout.addWidget(card3, 1, 0, 1, 2)

        layout.addLayout(charts_layout)

        # ── Tabla de Hoy ─────────────────────────────────────────────────────
        table_title = QLabel("Últimas Facturas de Hoy")
        table_title.setStyleSheet(label_style("lg", "bold"))
        layout.addWidget(table_title)

        table_container = QWidget()
        table_container.setStyleSheet(
            f"background-color: {c['bg_card']}; border-radius: 12px; border: 1px solid {c['border']};"
        )
        tc_layout = QVBoxLayout(table_container)
        tc_layout.setContentsMargins(0, 0, 0, 0)

        self.tabla_hoy = QTableWidget()
        self.tabla_hoy.setColumnCount(6)
        self.tabla_hoy.setHorizontalHeaderLabels(
            ["Hora", "Cliente", "Productos", "Método", "Total", "Estado"]
        )
        self.tabla_hoy.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_hoy.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_hoy.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_hoy.verticalHeader().setVisible(False)
        self.tabla_hoy.setMinimumHeight(300)
        self.tabla_hoy.setStyleSheet(f"""
            QTableWidget {{
                background: transparent;
                border: none;
                gridline-color: {c["border"]};
                color: {c["text_primary"]};
            }}
            QHeaderView::section {{
                background-color: {c["bg_sidebar"]};
                color: #cbd5e1;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 0.5px;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid {c["border"]};
                text-transform: uppercase;
            }}
        """)
        tc_layout.addWidget(self.tabla_hoy)
        layout.addWidget(table_container)

    def _crear_contenedor_grafico(self):
        from ui.chart_widget import ChartWidget

        container = QWidget()
        container.setStyleSheet(
            f"background-color: {get_colors()['bg_card']}; border-radius: 16px; border: 1px solid {get_colors()['border']};"
        )
        add_shadow(container, blur=24, offset_y=6, opacity=50)
        lyt = QVBoxLayout(container)
        lyt.setContentsMargins(12, 12, 12, 12)
        chart = ChartWidget()
        chart.setMinimumHeight(400)
        lyt.addWidget(chart)
        return container, chart

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
        # Reiniciar el timer cuando se muestra la vista
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.start(self.AUTO_REFRESH_INTERVAL)

    def hideEvent(self, event):
        super().hideEvent(event)
        # Detener el timer cuando se oculta la vista para ahorrar recursos
        if hasattr(self, "refresh_timer"):
            self.refresh_timer.stop()

    def _actualizar_periodo_grafico(self, texto):
        period_map = {
            "Este mes": "mes",
            "Este trimestre": "trimestre",
            "Este semestre": "semestre",
            "Este año": "año",
        }
        self.chart_periodo = period_map.get(texto, "mes")
        self.refresh()

    def refresh(self):
        """Actualiza todos los datos del dashboard."""
        import logging

        c = get_colors()
        try:
            from models.producto import Venta
            from PySide6.QtWidgets import QTableWidgetItem
            from PySide6.QtGui import QColor

            hoy_inicio = datetime.combine(date.today(), datetime.min.time())
            mes_inicio = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            # KPIs
            ventas_hoy = (
                self.session.query(Venta)
                .filter(Venta.fecha >= hoy_inicio)
                .order_by(Venta.fecha.desc())
                .all()
            )
            total_hoy = sum(v.total for v in ventas_hoy if not v.anulada)
            self.card_hoy.update_value(fmt_moneda(total_hoy))

            ventas_mes = (
                self.session.query(Venta)
                .filter(Venta.fecha >= mes_inicio, Venta.anulada == False)
                .all()
            )
            self.card_mes.update_value(fmt_moneda(sum(v.total for v in ventas_mes)))

            # Alertas Inventario
            try:
                from services.producto_service import ProductoService

                ps = ProductoService(self.session)
                bajos = ps.get_productos_bajo_stock_limite(5)
                criticos = ps.get_productos_stock_critico()
                total_alertas = len(bajos) + len(criticos)
                self.card_vencimiento.update_value(f"{total_alertas} Alertas")
                self.card_vencimiento.value_label.setStyleSheet(
                    f"color: {c['danger' if total_alertas > 0 else 'success']}; font-size: 22px; font-weight: bold;"
                )
            except Exception as e:
                logging.error(f"Error inventario dashboard: {e}")
                self.card_vencimiento.update_value("—")

            # Tabla Hoy - Con manejo de errores
            try:
                self.tabla_hoy.setRowCount(0)  # Limpiar tabla primero

                if not ventas_hoy:
                    logging.info("No hay ventas hoy para mostrar en el dashboard")
                else:
                    logging.info(f"Mostrando {len(ventas_hoy)} ventas en el dashboard")

                for i, v in enumerate(ventas_hoy):
                    self.tabla_hoy.setRowCount(i + 1)

                    # Hora
                    try:
                        hora = v.fecha.strftime("%I:%M %p")
                    except:
                        hora = "N/A"
                    self.tabla_hoy.setItem(i, 0, QTableWidgetItem(hora))

                    # Cliente (con manejo de errores)
                    try:
                        cliente = v.cliente.nombre if v.cliente else "Consumidor Final"
                    except Exception as e:
                        logging.warning(
                            f"Error obteniendo cliente de venta {v.id}: {e}"
                        )
                        cliente = "Consumidor Final"
                    self.tabla_hoy.setItem(i, 1, QTableWidgetItem(cliente))

                    # Productos (nueva columna)
                    try:
                        productos_text = ""
                        if hasattr(v, "items") and v.items:
                            productos_list = []
                            for item in v.items:
                                if hasattr(item, "producto") and item.producto:
                                    productos_list.append(
                                        f"{item.cantidad}x {item.producto.nombre}"
                                    )
                            productos_text = " | ".join(productos_list)
                        if not productos_text:
                            productos_text = "Sin productos"
                    except Exception as e:
                        logging.warning(
                            f"Error obteniendo productos de venta {v.id}: {e}"
                        )
                        productos_text = "Error al cargar"
                    productos_item = QTableWidgetItem(productos_text)
                    productos_item.setFlags(
                        productos_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                    )
                    self.tabla_hoy.setItem(i, 2, QTableWidgetItem(productos_text))

                    # Método de pago
                    metodo = v.metodo_pago or "Efectivo"
                    self.tabla_hoy.setItem(i, 3, QTableWidgetItem(metodo))

                    # Total
                    t_item = QTableWidgetItem(fmt_moneda(v.total))
                    t_item.setForeground(QColor(c["accent"]))
                    self.tabla_hoy.setItem(i, 4, t_item)

                    # Estado
                    e_item = QTableWidgetItem("Anulada" if v.anulada else "Completada")
                    e_item.setForeground(
                        QColor(c["danger"] if v.anulada else c["success"])
                    )
                    self.tabla_hoy.setItem(i, 5, e_item)

            except Exception as e:
                logging.error(f"Error llenando tabla de ventas: {e}")
                import traceback

                logging.error(traceback.format_exc())

            # Gráficos
            try:
                from ui.chart_widget import (
                    get_ventas_por_periodo,
                    get_ventas_por_metodo,
                    get_ventas_por_cliente,
                )

                l_t, v_t = get_ventas_por_periodo(self.session, self.chart_periodo)
                self.chart_evolucion.plot_bar(
                    l_t, v_t, f"Ventas: {self.combo_periodo.currentText()}"
                )

                l_m, v_m = get_ventas_por_metodo(self.session)
                self.chart_metodos.plot_pie(l_m, v_m, "Métodos de Pago")

                l_c, v_c = get_ventas_por_cliente(self.session)
                self.chart_clientes.plot_bar(l_c, v_c, "Top 10 Clientes")
            except Exception as e:
                logging.error(f"Error en gráficos: {e}")

        except Exception as e:
            logging.error(f"Dashboard error: {e}")
            import traceback

            logging.error(traceback.format_exc())

    def _ir_a_corte(self):
        self.window().switch_view_by_name("corte")

    def _ir_a_historial(self):
        self.window().switch_view_by_name("historial")

    def _ir_a_productos(self):
        self.window().switch_view_by_name("productos")

    def _mostrar_sistema(self):
        from PySide6.QtWidgets import QDialog

        c = get_colors()
        dialog = QDialog(self)
        dialog.setWindowTitle("Configuración de Sistema")
        dialog.setMinimumWidth(350)
        dialog.setStyleSheet(
            f"background-color: {c['bg_card']}; border: 1px solid {c['border']};"
        )
        layout = QVBoxLayout(dialog)

        title = QLabel("Opciones Rápidas")
        title.setStyleSheet(label_style("lg", "bold"))
        layout.addWidget(title)

        btns = [
            ("💾 Crear Backup", self._hacer_backup, btn_primary()),
            ("📥 Restaurar Datos", self._restaurar_backup, btn_danger()),
            ("📤 Exportar a USB", self._exportar_backup, btn_secondary()),
            ("🔄 Actualización", self._mostrar_actualizacion, btn_primary()),
        ]

        for text, func, style in btns:
            b = QPushButton(text)
            b.setStyleSheet(style)
            b.clicked.connect(lambda _, f=func: (dialog.accept(), f()))
            layout.addWidget(b)

        close = QPushButton("Cerrar")
        close.setStyleSheet(btn_secondary())
        close.clicked.connect(dialog.reject)
        layout.addWidget(close)
        dialog.exec()

    def _hacer_backup(self):
        try:
            from utils.backup import backup_database

            backup_database()
            QMessageBox.information(self, "✅ Backup", "Respaldo creado con éxito.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _mostrar_actualizacion(self):
        QMessageBox.information(
            self,
            "Actualizar",
            "Para actualizar, descargue la nueva versión e instálela.\nSus datos se conservan automáticamente.",
        )

    def _restaurar_backup(self):
        from PySide6.QtWidgets import QFileDialog, QApplication

        if (
            QMessageBox.warning(
                self,
                "⚠️ Alerta",
                "¿Desea reemplazar todos los datos con un backup?",
                QMessageBox.Yes | QMessageBox.No,
            )
            == QMessageBox.Yes
        ):
            path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar Backup", "", "DB (*.db)"
            )
            if path:
                try:
                    from utils.backup import restaurar_backup

                    restaurar_backup(path)
                    QMessageBox.information(self, "Éxito", "Reinicie la aplicación.")
                    QApplication.quit()
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def _exportar_backup(self):
        from PySide6.QtWidgets import QFileDialog
        from utils.backup import get_backups_dir
        import shutil

        b_dir = get_backups_dir()
        files = [f for f in os.listdir(b_dir) if f.endswith(".db")]
        if not files:
            return
        dest = QFileDialog.getExistingDirectory(self, "Destino Exportación")
        if dest:
            shutil.copy2(
                os.path.join(b_dir, sorted(files)[-1]),
                os.path.join(dest, sorted(files)[-1]),
            )
            QMessageBox.information(self, "Éxito", "Exportado correctamente.")
