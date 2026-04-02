from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt
from datetime import datetime
from tucajero.utils.formato import fmt_moneda
from tucajero.utils.theme import btn_primary, btn_secondary, btn_danger, get_colors


class CorteView(QWidget):
    """Vista de corte de caja"""

    def __init__(self, session, parent=None, cajero_activo=None):
        super().__init__(parent)
        self.session = session
        self.cajero_activo = cajero_activo
        self.init_ui()
        self.cargar_estadisticas()

    def init_ui(self):
        """Inicializa la interfaz"""
        from tucajero.utils.theme import get_colors

        c = get_colors()
        self.setStyleSheet(f"background-color: {c['bg_app']};")

        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Corte de Caja")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        from tucajero.utils.theme import card_style

        self.info_widget = QWidget()
        self.info_widget.setObjectName("infoCard")
        self.info_widget.setStyleSheet(f"""
            QWidget#infoCard {{
                background-color: {c["bg_card"]};
                border-radius: 16px;
                border: 1.5px solid {c["border"]};
            }}
        """)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 20, 20, 20)
        self.info_widget.setLayout(info_layout)

        self.lbl_fecha = QLabel(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        self.lbl_fecha.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 13px; background: transparent;"
        )
        info_layout.addWidget(self.lbl_fecha)

        self.lbl_estado = QLabel("Caja: ABIERTA")
        self.lbl_estado.setStyleSheet(
            f"color: {c['success']}; font-size: 15px; font-weight: bold; background: transparent;"
        )
        info_layout.addWidget(self.lbl_estado)

        self.lbl_total = QLabel(f"Total vendido: {fmt_moneda(0)}")
        self.lbl_total.setStyleSheet(
            f"color: {c['success']}; font-size: 26px; font-weight: bold; background: transparent;"
        )
        info_layout.addWidget(self.lbl_total)

        self.lbl_num_ventas = QLabel("Número de ventas: 0")
        self.lbl_num_ventas.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 13px; background: transparent;"
        )
        info_layout.addWidget(self.lbl_num_ventas)

        layout.addWidget(self.info_widget)

        fila1 = QHBoxLayout()
        fila1.setSpacing(8)

        self.btn_abrir = QPushButton("ABRIR CAJA")
        self.btn_abrir.setFixedHeight(32)
        self.btn_abrir.setMinimumWidth(160)
        self.btn_abrir.setMaximumWidth(280)
        self.btn_abrir.setStyleSheet(btn_primary())
        self.btn_abrir.clicked.connect(self.abrir_caja)
        fila1.addWidget(self.btn_abrir)

        self.btn_cerrar = QPushButton("CERRAR CAJA")
        self.btn_cerrar.setFixedHeight(32)
        self.btn_cerrar.setMinimumWidth(160)
        self.btn_cerrar.setMaximumWidth(280)
        self.btn_cerrar.setStyleSheet(btn_danger())
        self.btn_cerrar.clicked.connect(self.cerrar_caja)
        fila1.addWidget(self.btn_cerrar)

        self.btn_gasto = QPushButton("Registrar Gasto de Caja")
        self.btn_gasto.setFixedHeight(32)
        self.btn_gasto.setMinimumWidth(160)
        self.btn_gasto.setMaximumWidth(280)
        self.btn_gasto.setStyleSheet(btn_primary())
        self.btn_gasto.clicked.connect(self.registrar_gasto)
        fila1.addWidget(self.btn_gasto)

        fila2 = QHBoxLayout()
        fila2.setSpacing(8)

        self.btn_anular = QPushButton("Anular Venta")
        self.btn_anular.setFixedHeight(32)
        self.btn_anular.setMinimumWidth(160)
        self.btn_anular.setMaximumWidth(280)
        self.btn_anular.setStyleSheet(btn_danger())
        self.btn_anular.clicked.connect(self.anular_venta)
        fila2.addWidget(self.btn_anular)

        self.btn_facturas = QPushButton("Ver Facturas del Dia")
        self.btn_facturas.setFixedHeight(32)
        self.btn_facturas.setMinimumWidth(160)
        self.btn_facturas.setMaximumWidth(280)
        self.btn_facturas.setStyleSheet(btn_primary())
        self.btn_facturas.clicked.connect(self.ver_facturas_dia)
        fila2.addWidget(self.btn_facturas)

        self.btn_reimprimir = QPushButton("Reimprimir ultimo ticket")
        self.btn_reimprimir.setFixedHeight(32)
        self.btn_reimprimir.setMinimumWidth(160)
        self.btn_reimprimir.setMaximumWidth(280)
        self.btn_reimprimir.setStyleSheet(btn_secondary())
        self.btn_reimprimir.clicked.connect(self.reimprimir_ultimo)
        fila2.addWidget(self.btn_reimprimir)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(4)
        btn_layout.addLayout(fila1)
        btn_layout.addLayout(fila2)
        layout.addLayout(btn_layout, stretch=0)

        self.lbl_ganancia = QLabel(f"Ganancia neta: {fmt_moneda(0)}")
        self.lbl_ganancia.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {c['purple']}; padding: 6px;"
        )
        layout.addWidget(self.lbl_ganancia, stretch=0)

        historial_label = QLabel("Ventas del dia")
        historial_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-top: 10px;"
        )
        layout.addWidget(historial_label, stretch=0)

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(3)
        self.tabla_ventas.setHorizontalHeaderLabels(["ID", "Hora", "Total"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_ventas.setStyleSheet("font-size: 14px;")
        self.tabla_ventas.setMinimumHeight(120)
        layout.addWidget(self.tabla_ventas, stretch=3)

        gastos_label = QLabel("Gastos del dia")
        gastos_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-top: 10px;"
        )
        layout.addWidget(gastos_label, stretch=0)

        self.tabla_gastos = QTableWidget()
        self.tabla_gastos.setColumnCount(3)
        self.tabla_gastos.setHorizontalHeaderLabels(["Hora", "Concepto", "Monto"])
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_gastos.setStyleSheet("font-size: 13px;")
        self.tabla_gastos.setMinimumHeight(80)
        layout.addWidget(self.tabla_gastos, stretch=2)

    def cargar_estadisticas(self):
        """Carga las estadísticas del día"""
        from tucajero.services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        caja_abierta = service.esta_caja_abierta()

        if caja_abierta:
            self.lbl_estado.setText("Caja: ABIERTA")
            self.lbl_estado.setStyleSheet(
                f"font-size: 18px; font-weight: bold; color: {get_colors()['success']};"
            )
            self.btn_abrir.setEnabled(False)
            self.btn_cerrar.setEnabled(True)
            self.btn_gasto.setEnabled(True)
            self.btn_anular.setEnabled(True)
        else:
            self.lbl_estado.setText("Caja: CERRADA")
            self.lbl_estado.setStyleSheet(
                f"font-size: 18px; font-weight: bold; color: {get_colors()['danger']};"
            )
            self.btn_abrir.setEnabled(True)
            self.btn_cerrar.setEnabled(False)
            self.btn_gasto.setEnabled(False)
            self.btn_anular.setEnabled(False)

        self.lbl_total.setText(f"Total vendido: {fmt_moneda(stats['total'])}")
        self.lbl_num_ventas.setText(f"Número de ventas: {stats['num_ventas']}")
        self.lbl_ganancia.setText(
            f"Ganancia neta: {fmt_moneda(stats['ganancia_neta'])} "
            f"(Gastos: {fmt_moneda(stats['total_gastos'])})"
        )

        ventas = stats["ventas"]
        self.tabla_ventas.setRowCount(len(ventas))

        for i, venta in enumerate(ventas):
            self.tabla_ventas.setItem(i, 0, QTableWidgetItem(str(venta.id)))
            self.tabla_ventas.setItem(
                i, 1, QTableWidgetItem(venta.fecha.strftime("%I:%M:%S %p"))
            )
            self.tabla_ventas.setItem(i, 2, QTableWidgetItem(fmt_moneda(venta.total)))

        gastos = stats["gastos"]
        self.tabla_gastos.setRowCount(len(gastos))

        for i, gasto in enumerate(gastos):
            self.tabla_gastos.setItem(
                i, 0, QTableWidgetItem(gasto.fecha.strftime("%I:%M %p"))
            )
            self.tabla_gastos.setItem(i, 1, QTableWidgetItem(gasto.concepto))
            self.tabla_gastos.setItem(i, 2, QTableWidgetItem(fmt_moneda(gasto.monto)))

    def abrir_caja(self):
        """Abre la caja"""
        from tucajero.services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        service.abrir_caja()

        QMessageBox.information(
            self,
            "Caja Abierta",
            "La caja ha sido abierta correctamente.\n\nYa puedes comenzar a registrar ventas.",
        )

        self.cargar_estadisticas()

    def registrar_gasto(self):
        """Abre diálogo para registrar gasto"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Gasto de Caja")
        dialog.setMinimumWidth(380)
        layout = QFormLayout()
        dialog.setLayout(layout)

        info = QLabel("El monto será descontado de la ganancia del día.")
        info.setObjectName("info_label")
        layout.addRow("", info)

        concepto_input = QLineEdit()
        concepto_input.setPlaceholderText("Ej: Compra de bolsas, Pasaje, Luz...")
        concepto_input.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addRow("Concepto:", concepto_input)

        monto_input = QDoubleSpinBox()
        monto_input.setRange(0.01, 999999)
        monto_input.setDecimals(2)
        monto_input.setStyleSheet("padding: 8px; font-size: 16px;")
        layout.addRow("Monto:", monto_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("REGISTRAR")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(btn_primary())
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow("", buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            concepto = concepto_input.text().strip()
            monto = monto_input.value()
            if not concepto:
                QMessageBox.warning(self, "Error", "El concepto es obligatorio")
                return
            if monto <= 0:
                QMessageBox.warning(self, "Error", "El monto debe ser mayor a cero")
                return
            try:
                from tucajero.services.corte_service import CorteCajaService

                service = CorteCajaService(self.session)
                service.registrar_gasto(concepto, monto)
                self.cargar_estadisticas()
                QMessageBox.information(
                    self,
                    "Gasto Registrado",
                    f"Gasto registrado:\n{concepto}: {fmt_moneda(monto)}",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def cerrar_caja(self):
        """Cierra la caja con validación de diferencias"""
        from tucajero.services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        
        # Calcular total esperado en caja
        total_esperado = stats['total']
        total_gastos = stats['total_gastos']
        
        # Dialogo para ingresar el monto físico en caja
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        from PySide6.QtGui import QDoubleValidator
        
        # Calcular efectivo esperado (ventas - gastos)
        efectivo_esperado = total_esperado - total_gastos
        
        mensaje = (
            f"Total vendido hoy: {fmt_moneda(total_esperado)}\n"
            f"Total gastos: {fmt_moneda(total_gastos)}\n"
            f"--------------------------------\n"
            f"Efectivo esperado en caja: {fmt_moneda(efectivo_esperado)}\n\n"
            "Ingrese el monto físico contado en caja:"
        )
        
        efectivo_real, ok = QInputDialog.getDouble(
            self,
            "Cerrar Caja - Arqueo",
            mensaje,
            value=efectivo_esperado,
            min=0,
            max=9999999,
            decimals=2,
        )
        
        if not ok:
            return
        
        # Calcular diferencia
        diferencia = efectivo_real - efectivo_esperado
        
        # Mostrar confirmación con la diferencia
        if abs(diferencia) > 0.01:
            tipo_diferencia = "SOBRANTE" if diferencia > 0 else "FALTANTE"
            color_diferencia = "verde" if diferencia > 0 else "rojo"
            mensaje_confirmacion = (
                f"⚠️ ATENCIÓN: Hay un(a) {tipo_diferencia} de {fmt_moneda(abs(diferencia))}\n\n"
                f"Efectivo esperado: {fmt_moneda(efectivo_esperado)}\n"
                f"Efectivo contado: {fmt_moneda(efectivo_real)}\n"
                f"Diferencia: {fmt_moneda(diferencia)} ({color_diferencia})\n\n"
                "¿Desea continuar con el cierre de caja?"
            )
        else:
            mensaje_confirmacion = (
                f"✅ CUADRE PERFECTO\n\n"
                f"Efectivo esperado: {fmt_moneda(efectivo_esperado)}\n"
                f"Efectivo contado: {fmt_moneda(efectivo_real)}\n\n"
                "¿Desea continuar con el cierre de caja?"
            )
        
        respuesta = QMessageBox.question(
            self,
            "Confirmar Cierre",
            mensaje_confirmacion,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        
        # Registrar el cierre con la diferencia
        try:
            corte = service.cerrar_caja(diferencia=diferencia)
            
            if corte:
                mensaje_final = (
                    f"Corte de caja cerrado!\n\n"
                    f"Total vendido: {fmt_moneda(corte.total_ventas)}\n"
                    f"Gastos: {fmt_moneda(total_gastos)}\n"
                    f"Ganancia neta: {fmt_moneda(stats['ganancia_neta'])}\n"
                    f"Ventas: {stats['num_ventas']}\n\n"
                )
                if abs(diferencia) > 0.01:
                    tipo = "Sobrante" if diferencia > 0 else "Faltante"
                    mensaje_final += f"\n⚠️ {tipo}: {fmt_moneda(abs(diferencia))}"
                
                QMessageBox.information(self, "Corte de Caja", mensaje_final)
            else:
                QMessageBox.warning(self, "Error", "No hay caja abierta")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cerrar caja: {str(e)}")
            return
        
        self.cargar_estadisticas()

    def anular_venta(self):
        """Anula una venta del día"""
        from tucajero.services.corte_service import CorteCajaService
        from tucajero.services.producto_service import VentaService
        from tucajero.ui.ventas_view import VentasView

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        ventas = stats["ventas"]

        if not ventas:
            QMessageBox.warning(self, "Sin ventas", "No hay ventas registradas hoy")
            return

        from PySide6.QtWidgets import QInputDialog

        venta_ids = [str(v.id) for v in ventas]
        venta_id_str, ok = QInputDialog.getItem(
            self,
            "Anular Venta",
            "Seleccione la venta a anular:",
            venta_ids,
            0,
            False,
        )

        if not ok or not venta_id_str:
            return

        venta_id = int(venta_id_str)

        # Solicitar motivo de anulación
        motivo, ok = QInputDialog.getText(
            self,
            "Motivo de Anulación",
            "Ingrese el motivo de la anulación (obligatorio):",
        )

        if not ok or not motivo.strip():
            QMessageBox.warning(
                self,
                "Motivo requerido",
                "Es obligatorio ingresar el motivo de la anulación.",
            )
            return

        # Confirmación antes de anular
        respuesta = QMessageBox.question(
            self,
            "Confirmar Anulación",
            f"¿Está seguro de anular la venta #{venta_id}?\n"
            f"Motivo: {motivo}\n"
            "El stock de los productos será restaurado.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            venta_service = VentaService(self.session)
            # Obtener usuario activo del cajero
            usuario_id = self.cajero_activo.id if self.cajero_activo else None
            venta_service.anular_venta(venta_id, motivo=motivo, usuario_id=usuario_id)
            QMessageBox.information(
                self,
                "Venta Anulada",
                f"Venta #{venta_id} ha sido anulada.\n"
                f"Motivo: {motivo}\n"
                "El stock ha sido restaurado.",
            )
            self.cargar_estadisticas()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al anular venta: {str(e)}")

    def ver_facturas_dia(self):
        """Abre o genera el PDF de facturas del día"""
        from tucajero.utils.factura_diaria import get_factura_diaria_path
        import subprocess
        import os

        pdf_path = get_factura_diaria_path()
        if not os.path.exists(pdf_path):
            QMessageBox.information(
                self,
                "Sin facturas",
                "No hay facturas registradas para el día de hoy.",
            )
            return

        try:
            if os.name == "nt":
                os.startfile(pdf_path)
            else:
                subprocess.run(["xdg-open", pdf_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def reimprimir_ultimo(self):
        from tucajero.services.corte_service import CorteCajaService
        from tucajero.utils.store_config import get_printer_enabled

        if not get_printer_enabled():
            QMessageBox.warning(
                self,
                "Sin impresora",
                "No hay impresora termica configurada.\n"
                "Ve a Configuracion para anadir una.",
            )
            return
        try:
            service = CorteCajaService(self.session)
            stats = service.get_estadisticas_hoy()
            ventas = stats.get("ventas", [])
            if not ventas:
                QMessageBox.information(
                    self, "Sin ventas", "No hay ventas registradas hoy."
                )
                return
            ultima = ventas[-1]
            from tucajero.utils.impresora import get_impresora

            imp = get_impresora()
            imp.imprimir_ticket(ultima, ultima.items)
            imp.desconectar()
            QMessageBox.information(
                self, "Reimpreso", f"Ticket #{ultima.id} enviado a la impresora."
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo reimprimir:\n{str(e)}")
