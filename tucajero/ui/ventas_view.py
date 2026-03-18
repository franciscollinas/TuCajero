from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDoubleSpinBox,
    QHeaderView,
    QDialog,
    QDialogButtonBox,
    QComboBox,
    QFormLayout,
    QStackedWidget,
)
from PySide6.QtCore import Qt, Signal


METODOS_PAGO = [
    ("efectivo", "Efectivo"),
    ("nequi", "Nequi"),
    ("daviplata", "Daviplata"),
    ("transferencia", "Transferencia bancaria"),
    ("mixto", "Pago mixto (efectivo + transferencia)"),
]


class PaymentDialog(QDialog):
    """Diálogo de cobro con soporte múltiples métodos y pago mixto"""

    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.total = total
        self.payment_amount = 0
        self.metodo_pago = "efectivo"
        self.pagos = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cobro")
        self.setFixedSize(450, 420)
        layout = QVBoxLayout()
        self.setLayout(layout)

        from utils.store_config import get_store_name

        store_label = QLabel(get_store_name())
        store_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        store_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(store_label)

        lbl_total_titulo = QLabel("TOTAL A PAGAR")
        lbl_total_titulo.setStyleSheet("font-size: 13px; color: #7f8c8d;")
        lbl_total_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_total_titulo)

        self.lbl_total = QLabel(f"${self.total:.2f}")
        self.lbl_total.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: #27ae60;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_total)

        metodo_layout = QHBoxLayout()
        metodo_layout.addWidget(QLabel("Método de pago:"))
        self.combo_metodo = QComboBox()
        for valor, etiqueta in METODOS_PAGO:
            self.combo_metodo.addItem(etiqueta, valor)
        self.combo_metodo.currentIndexChanged.connect(self.cambiar_metodo)
        metodo_layout.addWidget(self.combo_metodo)
        layout.addLayout(metodo_layout)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        panel_efectivo = QWidget()
        pe_layout = QFormLayout()
        panel_efectivo.setLayout(pe_layout)
        self.pago_efectivo_input = QDoubleSpinBox()
        self.pago_efectivo_input.setRange(0, 9999999)
        self.pago_efectivo_input.setDecimals(2)
        self.pago_efectivo_input.setStyleSheet("font-size: 20px; padding: 8px;")
        self.pago_efectivo_input.valueChanged.connect(self.calcular_cambio_efectivo)
        pe_layout.addRow("Monto recibido:", self.pago_efectivo_input)
        self.lbl_cambio = QLabel("Cambio: $0.00")
        self.lbl_cambio.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #3498db;"
        )
        self.lbl_cambio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pe_layout.addRow("", self.lbl_cambio)
        self.stack.addWidget(panel_efectivo)

        panel_transfer = QWidget()
        pt_layout = QVBoxLayout()
        panel_transfer.setLayout(pt_layout)
        info_transfer = QLabel(
            "El cajero debe verificar manualmente\nla transferencia antes de confirmar."
        )
        info_transfer.setStyleSheet(
            "color: #e67e22; font-size: 13px; padding: 10px;"
            "background: #fef9e7; border-radius: 6px;"
        )
        info_transfer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pt_layout.addWidget(info_transfer)
        lbl_monto_transfer = QLabel(f"Monto a recibir: ${self.total:.2f}")
        lbl_monto_transfer.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #27ae60;"
        )
        lbl_monto_transfer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pt_layout.addWidget(lbl_monto_transfer)
        self.stack.addWidget(panel_transfer)

        panel_mixto = QWidget()
        pm_layout = QFormLayout()
        panel_mixto.setLayout(pm_layout)
        pm_layout.addRow(QLabel(f"Total a cubrir: ${self.total:.2f}"))
        self.mixto_combo_transfer = QComboBox()
        for valor, etiqueta in METODOS_PAGO[1:4]:
            self.mixto_combo_transfer.addItem(etiqueta, valor)
        pm_layout.addRow("Transferencia por:", self.mixto_combo_transfer)
        self.mixto_transfer_input = QDoubleSpinBox()
        self.mixto_transfer_input.setRange(0, 9999999)
        self.mixto_transfer_input.setDecimals(2)
        self.mixto_transfer_input.setStyleSheet("font-size: 16px; padding: 6px;")
        self.mixto_transfer_input.valueChanged.connect(self.calcular_mixto)
        pm_layout.addRow("Monto transferencia:", self.mixto_transfer_input)
        self.mixto_efectivo_input = QDoubleSpinBox()
        self.mixto_efectivo_input.setRange(0, 9999999)
        self.mixto_efectivo_input.setDecimals(2)
        self.mixto_efectivo_input.setStyleSheet("font-size: 16px; padding: 6px;")
        self.mixto_efectivo_input.valueChanged.connect(self.calcular_mixto)
        pm_layout.addRow("Monto efectivo:", self.mixto_efectivo_input)
        self.lbl_mixto_estado = QLabel("Pendiente: $0.00")
        self.lbl_mixto_estado.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #e74c3c;"
        )
        pm_layout.addRow("", self.lbl_mixto_estado)
        self.stack.addWidget(panel_mixto)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("CONFIRMAR PAGO")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(
            "background-color: #27ae60; color: white; "
            "font-size: 15px; font-weight: bold; padding: 10px;"
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("CANCELAR")
        buttons.accepted.connect(self.validar_y_aceptar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.pago_efectivo_input.setFocus()

    def cambiar_metodo(self, index):
        valor = self.combo_metodo.itemData(index)
        if valor == "efectivo":
            self.stack.setCurrentIndex(0)
        elif valor == "mixto":
            self.stack.setCurrentIndex(2)
        else:
            self.stack.setCurrentIndex(1)

    def calcular_cambio_efectivo(self):
        pago = self.pago_efectivo_input.value()
        cambio = pago - self.total
        if cambio >= 0:
            self.lbl_cambio.setText(f"Cambio: ${cambio:.2f}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: #27ae60;"
            )
        else:
            self.lbl_cambio.setText(f"Faltan: ${abs(cambio):.2f}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 20px; font-weight: bold; color: #e74c3c;"
            )

    def calcular_mixto(self):
        transfer = self.mixto_transfer_input.value()
        efectivo = self.mixto_efectivo_input.value()
        total_pagado = transfer + efectivo
        pendiente = self.total - total_pagado
        if pendiente <= 0:
            cambio = abs(pendiente)
            self.lbl_mixto_estado.setText(
                f"✅ Cubierto | Cambio efectivo: ${cambio:.2f}"
            )
            self.lbl_mixto_estado.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #27ae60;"
            )
        else:
            self.lbl_mixto_estado.setText(f"Pendiente: ${pendiente:.2f}")
            self.lbl_mixto_estado.setStyleSheet(
                "font-size: 14px; font-weight: bold; color: #e74c3c;"
            )

    def validar_y_aceptar(self):
        metodo = self.combo_metodo.currentData()
        if metodo == "efectivo":
            if self.pago_efectivo_input.value() < self.total:
                QMessageBox.warning(
                    self, "Pago insuficiente", "El monto recibido es menor al total"
                )
                return
            self.metodo_pago = "efectivo"
            self.payment_amount = self.pago_efectivo_input.value()
            self.pagos = [
                {"metodo": "efectivo", "monto": self.pago_efectivo_input.value()}
            ]
        elif metodo == "mixto":
            transfer = self.mixto_transfer_input.value()
            efectivo = self.mixto_efectivo_input.value()
            if transfer + efectivo < self.total:
                QMessageBox.warning(
                    self,
                    "Pago insuficiente",
                    f"La suma no cubre el total.\n"
                    f"Faltan: ${self.total - transfer - efectivo:.2f}",
                )
                return
            metodo_transfer = self.mixto_combo_transfer.currentData()
            self.metodo_pago = "mixto"
            self.payment_amount = efectivo
            self.pagos = [
                {"metodo": metodo_transfer, "monto": transfer},
                {"metodo": "efectivo", "monto": efectivo},
            ]
        else:
            self.metodo_pago = metodo
            self.payment_amount = self.total
            self.pagos = [{"metodo": metodo, "monto": self.total}]
        super().accept()


class VentasView(QWidget):
    """Sales view with auto-refresh support"""

    sale_completed = Signal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.carrito = []
        self.productos = []
        self.init_ui()
        self.cargar_productos()
        self.codigo_input.setFocus()

    def init_ui(self):
        """Initialize the interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        from utils.store_config import get_store_name, get_address, get_phone

        store_name = get_store_name()
        address = get_address()
        phone = get_phone()

        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #2c3e50; padding: 10px;")
        header_layout = QVBoxLayout()
        header_widget.setLayout(header_layout)

        title = QLabel(f"Nueva Venta - {store_name}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        header_layout.addWidget(title)

        if address:
            addr_label = QLabel(address)
            addr_label.setStyleSheet("font-size: 12px; color: #bdc3c7;")
            header_layout.addWidget(addr_label)

        if phone:
            phone_label = QLabel(f"Tel: {phone}")
            phone_label.setStyleSheet("font-size: 12px; color: #bdc3c7;")
            header_layout.addWidget(phone_label)

        layout.addWidget(header_widget)

        input_layout = QHBoxLayout()
        layout.addLayout(input_layout)

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código de producto o ESCANEAR")
        self.codigo_input.setStyleSheet("padding: 10px; font-size: 16px;")
        self.codigo_input.returnPressed.connect(self.buscar_producto)
        input_layout.addWidget(self.codigo_input)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedWidth(100)
        btn_buscar.setStyleSheet(
            "padding: 10px; background-color: #3498db; color: white;"
        )
        btn_buscar.clicked.connect(self.mostrar_buscador)
        input_layout.addWidget(btn_buscar)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Código", "Producto", "Cant.", "Precio base", "IVA 19%", "Total"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setStyleSheet("font-size: 14px;")
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()

        self.btn_menos = QPushButton("-")
        self.btn_menos.setFixedWidth(50)
        self.btn_menos.clicked.connect(self.disminuir_cantidad)
        btn_layout.addWidget(self.btn_menos)

        self.btn_mas = QPushButton("+")
        self.btn_mas.setFixedWidth(50)
        self.btn_mas.clicked.connect(self.aumentar_cantidad)
        btn_layout.addWidget(self.btn_mas)

        btn_layout.addStretch()

        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px;"
        )
        self.btn_eliminar.clicked.connect(self.eliminar_item)
        btn_layout.addWidget(self.btn_eliminar)

        self.btn_anular_venta = QPushButton("Anular Venta")
        self.btn_anular_venta.setStyleSheet(
            "background-color: #8e44ad; color: white; padding: 10px; font-weight: bold;"
        )
        self.btn_anular_venta.clicked.connect(self.anular_venta_del_dia)
        btn_layout.addWidget(self.btn_anular_venta)

        layout.addLayout(btn_layout)

        total_layout = QHBoxLayout()
        total_layout.addStretch()

        self.lbl_total = QLabel("TOTAL: $0.00")
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; padding: 15px; color: #2c3e50;"
        )
        total_layout.addWidget(self.lbl_total)

        layout.addLayout(total_layout)

        botones_layout = QHBoxLayout()

        self.btn_cancelar = QPushButton("CANCELAR")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_cancelar.clicked.connect(self.cancelar_venta)
        botones_layout.addWidget(self.btn_cancelar)

        self.btn_cobrar = QPushButton("COBRAR")
        self.btn_cobrar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_cobrar.clicked.connect(self.cobrar)
        botones_layout.addWidget(self.btn_cobrar)

        layout.addLayout(botones_layout)

    def cargar_productos(self):
        """Load all products for the search"""
        from services.producto_service import ProductoService

        service = ProductoService(self.session)
        self.productos = service.get_all_productos()

    def recargar_productos(self):
        """Reload products (called after sale)"""
        self.session.expire_all()
        self.cargar_productos()

    def buscar_producto(self):
        """Search product by code"""
        from services.producto_service import ProductoService

        codigo = self.codigo_input.text().strip()
        if not codigo:
            return

        service = ProductoService(self.session)
        producto = service.get_producto_by_codigo(codigo)

        if not producto:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            self.codigo_input.clear()
            self.codigo_input.setFocus()
            return

        if producto.stock <= 0:
            QMessageBox.warning(self, "Error", "Producto sin stock")
            self.codigo_input.clear()
            self.codigo_input.setFocus()
            return

        self.agregar_al_carrito(producto)
        self.codigo_input.clear()
        self.codigo_input.setFocus()

    def mostrar_buscador(self):
        """Show product search dialog"""
        from ui.buscador_productos import BuscadorProductosDialog

        dialog = BuscadorProductosDialog(self.productos, self.session, self)
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.producto_seleccionado
        ):
            producto = dialog.producto_seleccionado
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.codigo_input.setFocus()

    def agregar_al_carrito(self, producto):
        """Add product to cart"""
        for item in self.carrito:
            if item["producto_id"] == producto.id:
                item["cantidad"] += 1
                self.actualizar_tabla()
                return

        self.carrito.append(
            {
                "producto_id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "precio": producto.precio,
                "cantidad": 1,
            }
        )
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Update cart table with IVA breakdown"""
        IVA_RATE = 0.19
        self.tabla.setRowCount(len(self.carrito))
        subtotal_total = 0
        iva_total = 0
        for i, item in enumerate(self.carrito):
            subtotal = item["cantidad"] * item["precio"]
            iva = round(subtotal * IVA_RATE, 2)
            total_item = round(subtotal + iva, 2)
            subtotal_total += subtotal
            iva_total += iva
            self.tabla.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self.tabla.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(item["cantidad"])))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"${subtotal:,.2f}"))
            self.tabla.setItem(i, 4, QTableWidgetItem(f"${iva:,.2f}"))
            self.tabla.setItem(i, 5, QTableWidgetItem(f"${total_item:,.2f}"))
        total_final = round(subtotal_total + iva_total, 2)
        self.lbl_total.setText(f"TOTAL: ${total_final:,.2f}")
        self._subtotal_sin_iva = round(subtotal_total, 2)
        self._iva_calculado = round(iva_total, 2)

    def aumentar_cantidad(self):
        """Increase quantity of selected product"""
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.carrito):
            self.carrito[row]["cantidad"] += 1
            self.actualizar_tabla()

    def disminuir_cantidad(self):
        """Decrease quantity of selected product"""
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.carrito):
            if self.carrito[row]["cantidad"] > 1:
                self.carrito[row]["cantidad"] -= 1
            else:
                self.carrito.pop(row)
            self.actualizar_tabla()

    def eliminar_item(self):
        """Remove item from cart"""
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.carrito):
            self.carrito.pop(row)
            self.actualizar_tabla()

    def cancelar_venta(self):
        """Cancel current sale"""
        if not self.carrito:
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Cancelar la venta actual?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.carrito = []
            self.actualizar_tabla()
            self.codigo_input.setFocus()

    def cobrar(self):
        """Process sale payment"""
        if not self.carrito:
            QMessageBox.warning(self, "Error", "El carrito está vacío")
            return

        IVA_RATE = 0.19
        subtotal = sum(item["cantidad"] * item["precio"] for item in self.carrito)
        iva = round(subtotal * IVA_RATE, 2)
        total = round(subtotal + iva, 2)

        from services.producto_service import VentaService
        from utils.ticket import GeneradorTicket

        dialog = PaymentDialog(total, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            service = VentaService(self.session)
            venta = service.registrar_venta(
                self.carrito, pagos=dialog.pagos, metodo_pago=dialog.metodo_pago
            )
            generador = GeneradorTicket()
            generador.imprimir(venta, venta.items)
            cambio = (
                dialog.payment_amount - total
                if dialog.metodo_pago in ["efectivo", "mixto"]
                else 0
            )
            metodo_label = dict(METODOS_PAGO).get(
                dialog.metodo_pago, dialog.metodo_pago
            )
            QMessageBox.information(
                self,
                "Venta Registrada",
                f"Venta #{venta.id}\n"
                f"Subtotal: ${subtotal:,.2f}\n"
                f"IVA 19%:  ${iva:,.2f}\n"
                f"Total:    ${total:,.2f}\n"
                f"Método:   {metodo_label}\n"
                f"Cambio:   ${cambio:,.2f}\n\n"
                f"¡Gracias por su compra!",
            )
            self.carrito = []
            self.actualizar_tabla()
            self.recargar_productos()
            self.sale_completed.emit()
            self.codigo_input.setFocus()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar venta: {str(e)}")

    def anular_venta_del_dia(self):
        """Permite anular una venta del día ingresando su ID"""
        from PySide6.QtWidgets import QInputDialog
        from services.producto_service import VentaService

        id_venta, ok = QInputDialog.getInt(
            self, "Anular Venta", "Ingrese el número de venta a anular:", 1, 1, 999999
        )
        if not ok:
            return
        motivo, ok2 = QInputDialog.getText(
            self,
            "Motivo de anulación",
            "¿Por qué se anula esta venta?\n(Ej: Error de registro, Cliente sin dinero)",
        )
        if not ok2 or not motivo.strip():
            QMessageBox.warning(
                self, "Error", "Debe ingresar un motivo para anular la venta"
            )
            return
        respuesta = QMessageBox.question(
            self,
            "Confirmar anulación",
            f"¿Anular la venta #{id_venta}?\n"
            f"Motivo: {motivo}\n\n"
            f"El stock de los productos será restaurado.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if respuesta != QMessageBox.StandardButton.Yes:
            return
        try:
            service = VentaService(self.session)
            venta = service.anular_venta(id_venta, motivo)
            QMessageBox.information(
                self,
                "Venta Anulada",
                f"Venta #{id_venta} anulada correctamente.\nEl stock fue restaurado.",
            )
            self.recargar_productos()
            self.sale_completed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
