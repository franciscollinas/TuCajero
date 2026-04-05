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
    QFrame,
)
from PySide6.QtCore import Qt
from datetime import datetime
from tucajero.utils.formato import fmt_moneda
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium, TABLE_STYLE_PREMIUM


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
        self.setStyleSheet(f"background-color: {Colors.BG_APP};")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(Spacing.XXXL, Spacing.XXL, Spacing.XXXL, Spacing.XXL)
        main_layout.setSpacing(Spacing.XL)
        self.setLayout(main_layout)

        # Title
        titulo = QLabel("Corte de Caja")
        titulo.setStyleSheet(
            f"font-size: {Typography.H2}px; font-weight: {Typography.EXTRABOLD}; color: {Colors.TEXT_PRIMARY}; "
            f"background: transparent;"
        )
        main_layout.addWidget(titulo)

        # --- Info Card ---
        self.info_widget = QFrame()
        self.info_widget.setObjectName("infoCard")
        self.info_widget.setStyleSheet(f"""
            QFrame#infoCard {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.MD}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        info_inner = QVBoxLayout()
        info_inner.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        info_inner.setSpacing(Spacing.SM)
        self.info_widget.setLayout(info_inner)

        self.lbl_fecha = QLabel(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        self.lbl_fecha.setStyleSheet(
            f"color: {Colors.TEXT_TERTIARY}; font-size: {Typography.H5}px; background: transparent;"
        )
        info_inner.addWidget(self.lbl_fecha)

        self.lbl_estado = QLabel("Caja: ABIERTA")
        self.lbl_estado.setStyleSheet(
            f"color: {Colors.SUCCESS}; font-size: {Typography.H5}px; font-weight: {Typography.SEMIBOLD}; background: transparent;"
        )
        info_inner.addWidget(self.lbl_estado)

        self.lbl_total = QLabel(f"Total vendido: {fmt_moneda(0)}")
        self.lbl_total.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.H2}px; font-weight: {Typography.EXTRABOLD}; background: transparent;"
        )
        info_inner.addWidget(self.lbl_total)

        self.lbl_num_ventas = QLabel("Numero de ventas: 0")
        self.lbl_num_ventas.setStyleSheet(
            f"color: {Colors.TEXT_TERTIARY}; font-size: {Typography.H5}px; background: transparent;"
        )
        info_inner.addWidget(self.lbl_num_ventas)

        main_layout.addWidget(self.info_widget)

        # --- Buttons Card ---
        buttons_card = QFrame()
        buttons_card.setObjectName("buttonsCard")
        buttons_card.setStyleSheet(f"""
            QFrame#buttonsCard {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.MD}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        buttons_inner = QVBoxLayout()
        buttons_inner.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        buttons_inner.setSpacing(Spacing.SM)
        buttons_card.setLayout(buttons_inner)

        # Row 1: Abrir + Cerrar
        fila1 = QHBoxLayout()
        fila1.setSpacing(Spacing.SM)

        self.btn_abrir = ButtonPremium("ABRIR CAJA", style="primary")
        self.btn_abrir.setFixedHeight(44)
        self.btn_abrir.clicked.connect(self.abrir_caja)
        fila1.addWidget(self.btn_abrir)

        self.btn_cerrar = ButtonPremium("CERRAR CAJA", style="danger")
        self.btn_cerrar.setFixedHeight(44)
        self.btn_cerrar.clicked.connect(self.cerrar_caja)
        fila1.addWidget(self.btn_cerrar)

        buttons_inner.addLayout(fila1)

        # Row 2: Gasto
        fila1b = QHBoxLayout()
        fila1b.setSpacing(Spacing.SM)

        self.btn_gasto = ButtonPremium("Registrar Gasto de Caja", style="primary")
        self.btn_gasto.setFixedHeight(44)
        self.btn_gasto.clicked.connect(self.registrar_gasto)
        fila1b.addWidget(self.btn_gasto)

        buttons_inner.addLayout(fila1b)

        # Row 3: Anular + Facturas
        fila2 = QHBoxLayout()
        fila2.setSpacing(Spacing.SM)

        self.btn_anular = ButtonPremium("Anular Venta", style="danger")
        self.btn_anular.setFixedHeight(44)
        self.btn_anular.clicked.connect(self.anular_venta)
        fila2.addWidget(self.btn_anular)

        self.btn_facturas = ButtonPremium("Ver Facturas del Dia", style="primary")
        self.btn_facturas.setFixedHeight(44)
        self.btn_facturas.clicked.connect(self.ver_facturas_dia)
        fila2.addWidget(self.btn_facturas)

        buttons_inner.addLayout(fila2)

        # Row 4: Reimprimir
        fila2b = QHBoxLayout()
        fila2b.setSpacing(Spacing.SM)

        self.btn_reimprimir = ButtonPremium("Reimprimir ultimo ticket", style="secondary")
        self.btn_reimprimir.setFixedHeight(44)
        self.btn_reimprimir.clicked.connect(self.reimprimir_ultimo)
        fila2b.addWidget(self.btn_reimprimir)

        buttons_inner.addLayout(fila2b)

        main_layout.addWidget(buttons_card)

        # --- Ganancia Card ---
        ganancia_card = QFrame()
        ganancia_card.setObjectName("gananciaCard")
        ganancia_card.setStyleSheet(f"""
            QFrame#gananciaCard {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.MD}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        ganancia_inner = QVBoxLayout()
        ganancia_inner.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.LG)
        ganancia_card.setLayout(ganancia_inner)

        self.lbl_ganancia = QLabel(f"Ganancia neta: {fmt_moneda(0)}")
        self.lbl_ganancia.setStyleSheet(
            f"font-size: {Typography.H4}px; font-weight: {Typography.EXTRABOLD}; color: {Colors.PURPLE}; background: transparent;"
        )
        self.lbl_ganancia.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ganancia_inner.addWidget(self.lbl_ganancia)

        main_layout.addWidget(ganancia_card)

        # --- Ventas Table Card ---
        ventas_card = QFrame()
        ventas_card.setObjectName("ventasCard")
        ventas_card.setStyleSheet(f"""
            QFrame#ventasCard {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.MD}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        ventas_inner = QVBoxLayout()
        ventas_inner.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.XL)
        ventas_inner.setSpacing(Spacing.MD)
        ventas_card.setLayout(ventas_inner)

        historial_label = QLabel("Ventas del dia")
        historial_label.setStyleSheet(
            f"font-size: {Typography.H5}px; font-weight: {Typography.SEMIBOLD}; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        ventas_inner.addWidget(historial_label)

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(3)
        self.tabla_ventas.setHorizontalHeaderLabels(["ID", "Hora", "Total"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_ventas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_ventas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_ventas.setStyleSheet(TABLE_STYLE_PREMIUM)
        self.tabla_ventas.setMinimumHeight(120)
        ventas_inner.addWidget(self.tabla_ventas)

        main_layout.addWidget(ventas_card)

        # --- Gastos Table Card ---
        gastos_card = QFrame()
        gastos_card.setObjectName("gastosCard")
        gastos_card.setStyleSheet(f"""
            QFrame#gastosCard {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.MD}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        gastos_inner = QVBoxLayout()
        gastos_inner.setContentsMargins(Spacing.XL, Spacing.LG, Spacing.XL, Spacing.XL)
        gastos_inner.setSpacing(Spacing.MD)
        gastos_card.setLayout(gastos_inner)

        gastos_label = QLabel("Gastos del dia")
        gastos_label.setStyleSheet(
            f"font-size: {Typography.H5}px; font-weight: {Typography.SEMIBOLD}; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        gastos_inner.addWidget(gastos_label)

        self.tabla_gastos = QTableWidget()
        self.tabla_gastos.setColumnCount(3)
        self.tabla_gastos.setHorizontalHeaderLabels(["Hora", "Concepto", "Monto"])
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_gastos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_gastos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_gastos.setStyleSheet(TABLE_STYLE_PREMIUM)
        self.tabla_gastos.setMinimumHeight(80)
        gastos_inner.addWidget(self.tabla_gastos)

        main_layout.addWidget(gastos_card)

    def cargar_estadisticas(self):
        """Carga las estadisticas del dia"""
        from tucajero.services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        caja_abierta = service.esta_caja_abierta()

        if caja_abierta:
            self.lbl_estado.setText("Caja: ABIERTA")
            self.lbl_estado.setStyleSheet(
                f"font-size: {Typography.H5}px; font-weight: {Typography.SEMIBOLD}; color: {Colors.SUCCESS};"
            )
            self.btn_abrir.setEnabled(False)
            self.btn_cerrar.setEnabled(True)
            self.btn_gasto.setEnabled(True)
            self.btn_anular.setEnabled(True)
        else:
            self.lbl_estado.setText("Caja: CERRADA")
            self.lbl_estado.setStyleSheet(
                f"font-size: {Typography.H5}px; font-weight: {Typography.SEMIBOLD}; color: {Colors.DANGER};"
            )
            self.btn_abrir.setEnabled(True)
            self.btn_cerrar.setEnabled(False)
            self.btn_gasto.setEnabled(False)
            self.btn_anular.setEnabled(False)

        self.lbl_total.setText(f"Total vendido: {fmt_moneda(stats['total'])}")
        self.lbl_num_ventas.setText(f"Numero de ventas: {stats['num_ventas']}")
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
        """Abre dialogo para registrar gasto"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Gasto de Caja")
        dialog.setMinimumWidth(380)
        layout = QFormLayout()
        dialog.setLayout(layout)

        info = QLabel("El monto sera descontado de la ganancia del dia.")
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
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(
            f"""
            QPushButton {{
                background: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.SM}px {Spacing.XXL}px;
                font-size: {Typography.BODY}px;
                font-weight: {Typography.SEMIBOLD};
            }}
            QPushButton:hover {{ background: {Colors.PRIMARY_DARK}; }}
            """
        )
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
        """Cierra la caja con validacion de diferencias"""
        from tucajero.services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()

        # Calcular total esperado en caja
        total_esperado = stats['total']
        total_gastos = stats['total_gastos']

        # Dialogo para ingresar el monto fisico en caja
        from PySide6.QtWidgets import QInputDialog, QMessageBox

        # Calcular efectivo esperado (ventas - gastos)
        efectivo_esperado = total_esperado - total_gastos

        mensaje = (
            f"Total vendido hoy: {fmt_moneda(total_esperado)}\n"
            f"Total gastos: {fmt_moneda(total_gastos)}\n"
            f"--------------------------------\n"
            f"Efectivo esperado en caja: {fmt_moneda(efectivo_esperado)}\n\n"
            "Ingrese el monto fisico contado en caja:"
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

        # Mostrar confirmacion con la diferencia
        if abs(diferencia) > 0.01:
            tipo_diferencia = "SOBRANTE" if diferencia > 0 else "FALTANTE"
            color_diferencia = "verde" if diferencia > 0 else "rojo"
            mensaje_confirmacion = (
                f"\u26a0\ufe0f ATENCION: Hay un(a) {tipo_diferencia} de {fmt_moneda(abs(diferencia))}\n\n"
                f"Efectivo esperado: {fmt_moneda(efectivo_esperado)}\n"
                f"Efectivo contado: {fmt_moneda(efectivo_real)}\n"
                f"Diferencia: {fmt_moneda(diferencia)} ({color_diferencia})\n\n"
                "Desea continuar con el cierre de caja?"
            )
        else:
            mensaje_confirmacion = (
                f"\u2705 CUADRE PERFECTO\n\n"
                f"Efectivo esperado: {fmt_moneda(efectivo_esperado)}\n"
                f"Efectivo contado: {fmt_moneda(efectivo_real)}\n\n"
                "Desea continuar con el cierre de caja?"
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
                    mensaje_final += f"\n\u26a0\ufe0f {tipo}: {fmt_moneda(abs(diferencia))}"

                QMessageBox.information(self, "Corte de Caja", mensaje_final)
            else:
                QMessageBox.warning(self, "Error", "No hay caja abierta")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cerrar caja: {str(e)}")
            return

        self.cargar_estadisticas()

    def anular_venta(self):
        """Anula una venta del dia"""
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

        # Solicitar motivo de anulacion
        motivo, ok = QInputDialog.getText(
            self,
            "Motivo de Anulacion",
            "Ingrese el motivo de la anulacion (obligatorio):",
        )

        if not ok or not motivo.strip():
            QMessageBox.warning(
                self,
                "Motivo requerido",
                "Es obligatorio ingresar el motivo de la anulacion.",
            )
            return

        # Confirmacion antes de anular
        respuesta = QMessageBox.question(
            self,
            "Confirmar Anulacion",
            f"Esta seguro de anular la venta #{venta_id}?\n"
            f"Motivo: {motivo}\n"
            "El stock de los productos sera restaurado.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            venta_service = VentaService(self.session)
            # Obtener usuario activo del cajero
            usuario_id = self.cajero_activo.id if self.cajero_activo else None
            venta_service.anular_venta(venta_id, motivo=motivo, usuario_id=usuario_id)

            # Registrar en auditoría
            try:
                from tucajero.services.audit_service import AuditService
                audit = AuditService(self.session)
                audit.registrar(
                    AuditService.ANULACION,
                    f"Venta #{venta_id} anulada. Motivo: {motivo}",
                    usuario_id=usuario_id,
                    entidad_tipo="Venta",
                    entidad_id=venta_id,
                    valor_nuevo=motivo,
                )
            except Exception:
                pass

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
        """Abre o genera el PDF de facturas del dia"""
        from tucajero.utils.factura_diaria import get_factura_diaria_path
        import subprocess
        import os

        pdf_path = get_factura_diaria_path()

        # SEC-009 FIX: Validation 1 - Path must exist
        if not os.path.exists(pdf_path):
            QMessageBox.information(
                self,
                "Sin facturas",
                "No hay facturas registradas para el dia de hoy.",
            )
            return

        # SEC-009 FIX: Validation 2 - Must be a .pdf file (extension check)
        if not pdf_path.lower().endswith(".pdf"):
            QMessageBox.critical(
                self,
                "Error de seguridad",
                "El archivo no tiene un formato valido.",
            )
            return

        # SEC-009 FIX: Validation 3 - Resolve to absolute path to prevent path traversal
        pdf_path = os.path.realpath(pdf_path)
        expected_dir = os.path.realpath(os.path.join(os.environ.get("LOCALAPPDATA", "."), "TuCajero"))
        if not pdf_path.startswith(expected_dir):
            QMessageBox.critical(
                self,
                "Error de seguridad",
                "El archivo se encuentra en una ubicacion no esperada.",
            )
            return

        # SEC-009 FIX: Validation 4 - User confirmation before opening external file
        confirm = QMessageBox.question(
            self,
            "Abrir factura",
            "¿Desea abrir el archivo de facturas del dia?\n\n"
            f"Archivo: {os.path.basename(pdf_path)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            if os.name == "nt":
                os.startfile(pdf_path)
            else:
                subprocess.run(["xdg-open", pdf_path], check=True, timeout=5)
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Error", "La apertura del archivo tardo demasiado.")
        except Exception:
            # SEC-009 FIX: Do NOT expose the error details or path to the user
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo abrir el archivo. Intente abrirlo manualmente desde la carpeta de documentos.",
            )

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
