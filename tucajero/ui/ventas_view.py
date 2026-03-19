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
    QButtonGroup,
    QRadioButton,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal

IVA_RATE = 0.19


class PaymentDialog(QDialog):
    """Dialog for payment with multiple payment methods"""

    def __init__(self, subtotal, iva, total, parent=None):
        super().__init__(parent)
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.payment_amount = 0
        self.metodo_pago = "Efectivo"
        self.init_ui()

    def init_ui(self):
        """Initialize the payment dialog UI"""
        self.setWindowTitle("Cobro")
        self.setMinimumSize(420, 500)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        self.setLayout(layout)

        from utils.store_config import get_store_name

        store_name_label = QLabel(get_store_name())
        store_name_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50;"
        )
        store_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(store_name_label)

        total_label = QLabel("TOTAL A PAGAR")
        total_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(total_label)

        self.lbl_total = QLabel(f"${self.total:.2f}")
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #27ae60;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_total)

        metodo_label = QLabel("Método de pago:")
        metodo_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(metodo_label)

        self.metodo_group = QButtonGroup()
        metodos = [
            ("Efectivo", "Efectivo"),
            ("Nequi", "Nequi"),
            ("Daviplata", "Daviplata"),
            ("Transferencia", "Transferencia"),
        ]
        for texto, valor in metodos:
            radio = QRadioButton(texto)
            radio.setStyleSheet("padding: 6px; font-size: 14px;")
            self.metodo_group.addButton(radio)
            self.metodo_group.setId(radio, len(self.metodo_group.buttons()))
            radio.metodo_valor = valor
            radio.toggled.connect(self.on_metodo_changed)
            layout.addWidget(radio)

        self.metodo_group.buttons()[0].setChecked(True)

        self.efectivo_container = QWidget()
        efectivo_layout = QVBoxLayout()
        self.efectivo_container.setLayout(efectivo_layout)

        pago_label = QLabel("Monto recibido:")
        pago_label.setStyleSheet("font-size: 14px;")
        efectivo_layout.addWidget(pago_label)

        self.pago_input = QDoubleSpinBox()
        self.pago_input.setRange(0, 999999999)
        self.pago_input.setDecimals(2)
        self.pago_input.setStyleSheet("font-size: 18px; padding: 8px;")
        self.pago_input.setMinimumWidth(200)
        self.pago_input.setFocus()
        self.pago_input.valueChanged.connect(self.calcular_cambio)
        efectivo_layout.addWidget(self.pago_input)

        self.lbl_cambio = QLabel("Cambio: $0.00")
        self.lbl_cambio.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #27ae60;"
        )
        self.lbl_cambio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        efectivo_layout.addWidget(self.lbl_cambio)

        layout.addWidget(self.efectivo_container)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("CONFIRMAR PAGO")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("CANCELAR")
        layout.addWidget(buttons)

    def on_metodo_changed(self):
        """Handle payment method change"""
        for radio in self.metodo_group.buttons():
            if radio.isChecked():
                self.metodo_pago = radio.metodo_valor
                break
        if self.metodo_pago == "Efectivo":
            self.efectivo_container.setVisible(True)
        else:
            self.efectivo_container.setVisible(False)

    def calcular_cambio(self):
        """Calculate change from payment"""
        pago = self.pago_input.value()
        cambio = pago - self.total
        if cambio >= 0:
            self.lbl_cambio.setText(f"Cambio: ${cambio:.2f}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #27ae60;"
            )
            self.payment_amount = pago
        else:
            self.lbl_cambio.setText(f"Faltan: ${abs(cambio):.2f}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #e74c3c;"
            )
            self.payment_amount = 0

    def accept(self):
        """Handle dialog acceptance"""
        if self.metodo_pago == "Efectivo" and self.pago_input.value() < self.total:
            QMessageBox.warning(
                self, "Pago insuficiente", "El monto recibido es menor al total"
            )
            return
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
        self.codigo_input.setPlaceholderText("Código o nombre de producto")
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
            ["Código", "Producto", "Cantidad", "Precio", "IVA", "Subtotal"]
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

        layout.addLayout(btn_layout)

        resumen_layout = QVBoxLayout()

        self.lbl_subtotal = QLabel("Subtotal: $0.00")
        self.lbl_subtotal.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        self.lbl_subtotal.setAlignment(Qt.AlignmentFlag.AlignRight)
        resumen_layout.addWidget(self.lbl_subtotal)

        self.lbl_iva = QLabel("IVA (19%): $0.00")
        self.lbl_iva.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        self.lbl_iva.setAlignment(Qt.AlignmentFlag.AlignRight)
        resumen_layout.addWidget(self.lbl_iva)

        self.lbl_total = QLabel("TOTAL: $0.00")
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; padding: 15px; color: #27ae60;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        resumen_layout.addWidget(self.lbl_total)

        layout.addLayout(resumen_layout)

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
        self.session.commit()
        self.cargar_productos()

    def buscar_producto(self):
        """Search product by code or name"""
        from services.producto_service import ProductoService

        texto = self.codigo_input.text().strip()
        if not texto:
            return

        service = ProductoService(self.session)

        producto = service.get_producto_by_codigo(texto)
        if producto and producto.stock > 0:
            self.agregar_al_carrito(producto)
            self.codigo_input.clear()
            self.codigo_input.setFocus()
            return

        productos = service.get_producto_by_nombre(texto)
        if len(productos) == 1:
            producto = productos[0]
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.codigo_input.clear()
                self.codigo_input.setFocus()
                return
        elif len(productos) > 1:
            self.codigo_input.clear()
            self.mostrar_buscador_productos(productos)
            return

        QMessageBox.warning(self, "No encontrado", f"No se encontró '{texto}'")
        self.codigo_input.selectAll()
        self.codigo_input.setFocus()

    def mostrar_buscador(self):
        """Show product search dialog"""
        from ui.buscador_productos import BuscadorProductosDialog

        dialog = BuscadorProductosDialog(self.productos, self)
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.producto_seleccionado
        ):
            producto = dialog.producto_seleccionado
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.codigo_input.setFocus()

    def mostrar_buscador_productos(self, productos):
        """Show custom product list when multiple matches"""
        from ui.buscador_productos import BuscadorProductosDialog

        dialog = BuscadorProductosDialog(productos, self)
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
                "aplica_iva": getattr(producto, "aplica_iva", True),
            }
        )
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Update cart table"""
        self.tabla.setRowCount(len(self.carrito))

        subtotal_total = 0
        iva_total = 0

        for i, item in enumerate(self.carrito):
            cantidad = item["cantidad"]
            precio = item["precio"]
            aplica_iva = item.get("aplica_iva", True)

            subtotal = cantidad * precio
            iva = round(subtotal * IVA_RATE, 2) if aplica_iva else 0
            total_item = subtotal + iva

            subtotal_total += subtotal
            iva_total += iva

            self.tabla.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self.tabla.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(cantidad)))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"${precio:.2f}"))
            self.tabla.setItem(
                i, 4, QTableWidgetItem(f"${iva:.2f}" if aplica_iva else "—")
            )
            self.tabla.setItem(i, 5, QTableWidgetItem(f"${total_item:.2f}"))

        total_final = subtotal_total + iva_total

        self.lbl_subtotal.setText(f"Subtotal: ${subtotal_total:.2f}")
        self.lbl_iva.setText(f"IVA (19%): ${iva_total:.2f}")
        self.lbl_total.setText(f"TOTAL: ${total_final:.2f}")

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

        from services.producto_service import VentaService
        from utils.ticket import GeneradorTicket

        subtotal = sum(item["cantidad"] * item["precio"] for item in self.carrito)
        iva = 0
        for item in self.carrito:
            if item.get("aplica_iva", True):
                iva += round(item["cantidad"] * item["precio"] * IVA_RATE, 2)
        total = subtotal + iva

        dialog = PaymentDialog(subtotal, iva, total, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            service = VentaService(self.session)
            venta = service.registrar_venta(
                self.carrito, metodo_pago=dialog.metodo_pago
            )

            generador = GeneradorTicket()
            generador.imprimir(venta, venta.items)

            cambio = dialog.payment_amount - total
            QMessageBox.information(
                self,
                "Venta Registrada",
                f"Venta #{venta.id}\n"
                f"Subtotal: ${subtotal:.2f}\n"
                f"IVA: ${iva:.2f}\n"
                f"Total: ${total:.2f}\n"
                f"Pago: ${dialog.payment_amount:.2f}\n"
                f"Cambio: ${cambio:.2f}\n\n"
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
