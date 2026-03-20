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
    QInputDialog,
)
from PySide6.QtCore import Qt, Signal
from utils.formato import fmt_moneda

IVA_RATE = 0.19


class PaymentDialog(QDialog):
    """Dialog for payment with multiple payment methods"""

    def __init__(self, subtotal, iva, total, parent=None, cliente=None, descuento=0):
        super().__init__(parent)
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.payment_amount = 0
        self.metodo_pago = "Efectivo"
        self.cliente = cliente
        self.descuento = descuento
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
        total_label.setObjectName("total_label")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(total_label)

        self.lbl_total = QLabel(fmt_moneda(self.total))
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #27ae60;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_total)

        if self.descuento > 0:
            lbl_desc = QLabel(f"Descuento: -{fmt_moneda(self.descuento)}")
            lbl_desc.setStyleSheet("font-size:14px;color:#e74c3c;")
            lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_desc)

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
        if self.cliente:
            metodos.append(("🔴 Fiado (crédito)", "Fiado"))
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

        self.lbl_cambio = QLabel(f"Cambio: {fmt_moneda(0)}")
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
            self.lbl_cambio.setText(f"Cambio: {fmt_moneda(cambio)}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #27ae60;"
            )
            self.payment_amount = pago
        else:
            self.lbl_cambio.setText(f"Faltan: {fmt_moneda(abs(cambio))}")
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
    cotizacion_creada = Signal()

    def __init__(self, session, parent=None, cajero_activo=None):
        super().__init__(parent)
        self.session = session
        self.cajero_activo = cajero_activo
        self.carrito = []
        self.productos = []
        self.descuento = {"tipo": None, "valor": 0, "total": 0}
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
            addr_label.setObjectName("addr_label")
            header_layout.addWidget(addr_label)

        if phone:
            phone_label = QLabel(f"Tel: {phone}")
            phone_label.setObjectName("phone_label")
            header_layout.addWidget(phone_label)

        layout.addWidget(header_widget)

        cliente_bar = QHBoxLayout()
        self.lbl_cliente = QLabel("👤 Sin cliente")
        self.lbl_cliente.setStyleSheet("font-size:13px;color:#7f8c8d;padding:4px;")
        cliente_bar.addWidget(self.lbl_cliente)

        btn_cliente = QPushButton("Seleccionar cliente")
        btn_cliente.setStyleSheet(
            "background:#8e44ad;color:white;padding:6px 12px;font-size:12px;"
        )
        btn_cliente.clicked.connect(self.seleccionar_cliente)
        cliente_bar.addWidget(btn_cliente)

        self.btn_quitar_cliente = QPushButton("✕")
        self.btn_quitar_cliente.setFixedWidth(30)
        self.btn_quitar_cliente.setStyleSheet(
            "background:#bdc3c7;color:white;padding:6px;"
        )
        self.btn_quitar_cliente.setVisible(False)
        self.btn_quitar_cliente.clicked.connect(self.quitar_cliente)
        cliente_bar.addWidget(self.btn_quitar_cliente)

        cliente_bar.addStretch()
        layout.addLayout(cliente_bar)

        self.cliente_seleccionado = None

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

        self.btn_menos = QPushButton("−")
        self.btn_menos.setFixedSize(34, 34)
        self.btn_menos.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["danger"]};
                color: white; border-radius: 17px;
                font-size: 18px; font-weight: bold; border: none;
            }}
            QPushButton:hover {{ background-color: {c["danger"]}cc; }}
        """)
        self.btn_menos.clicked.connect(self.disminuir_cantidad)
        btn_layout.addWidget(self.btn_menos)

        self.btn_mas = QPushButton("+")
        self.btn_mas.setFixedSize(34, 34)
        self.btn_mas.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["success"]};
                color: white; border-radius: 17px;
                font-size: 18px; font-weight: bold; border: none;
            }}
            QPushButton:hover {{ background-color: {c["success"]}cc; }}
        """)
        self.btn_mas.clicked.connect(self.aumentar_cantidad)
        btn_layout.addWidget(self.btn_mas)

        btn_layout.addStretch()

        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px;"
        )
        self.btn_eliminar.clicked.connect(self.eliminar_item)
        btn_layout.addWidget(self.btn_eliminar)

        self.btn_descuento = QPushButton("🏷 Descuento")
        self.btn_descuento.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white; padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.btn_descuento.clicked.connect(self.aplicar_descuento)
        btn_layout.addWidget(self.btn_descuento)

        layout.addLayout(btn_layout)

        resumen_layout = QVBoxLayout()

        self.lbl_subtotal = QLabel(f"Subtotal: {fmt_moneda(0)}")
        self.lbl_subtotal.setObjectName("lbl_subtotal")
        self.lbl_subtotal.setAlignment(Qt.AlignmentFlag.AlignRight)
        resumen_layout.addWidget(self.lbl_subtotal)

        self.lbl_descuento = QLabel("")
        self.lbl_descuento.setStyleSheet(
            "font-size: 15px; color: #e74c3c; padding-right: 15px;"
        )
        self.lbl_descuento.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_descuento.setVisible(False)
        resumen_layout.addWidget(self.lbl_descuento)

        self.lbl_iva = QLabel(f"IVA (19%): {fmt_moneda(0)}")
        self.lbl_iva.setObjectName("lbl_iva")
        self.lbl_iva.setAlignment(Qt.AlignmentFlag.AlignRight)
        resumen_layout.addWidget(self.lbl_iva)

        self.lbl_total = QLabel(f"TOTAL: {fmt_moneda(0)}")
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

        self.btn_cotizar = QPushButton("Cotización")
        self.btn_cotizar.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #9b59b6;
            }
        """)
        self.btn_cotizar.clicked.connect(self.guardar_cotizacion)
        botones_layout.addWidget(self.btn_cotizar)

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

        dialog = BuscadorProductosDialog(
            self.productos, session=self.session, parent=self
        )
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.producto_seleccionado
        ):
            producto = dialog.producto_seleccionado
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.codigo_input.setFocus()

    def seleccionar_cliente(self):
        from ui.selector_cliente import SelectorClienteDialog

        dialog = SelectorClienteDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.cliente:
            self.cliente_seleccionado = dialog.cliente
            self.lbl_cliente.setText(
                f"👤 {dialog.cliente.nombre}"
                + (
                    f" — 🔴 Debe {fmt_moneda(dialog.cliente.saldo_credito)}"
                    if dialog.cliente.saldo_credito > 0
                    else ""
                )
            )
            self.lbl_cliente.setStyleSheet(
                "font-size:13px;color:#2c3e50;font-weight:bold;padding:4px;"
            )
            self.btn_quitar_cliente.setVisible(True)

    def quitar_cliente(self):
        self.cliente_seleccionado = None
        self.lbl_cliente.setText("👤 Sin cliente")
        self.btn_quitar_cliente.setVisible(False)

    def mostrar_buscador_productos(self, productos):
        """Show custom product list when multiple matches"""
        from ui.buscador_productos import BuscadorProductosDialog

        dialog = BuscadorProductosDialog(productos, session=self.session, parent=self)
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
            self.tabla.setItem(i, 3, QTableWidgetItem(fmt_moneda(precio)))
            self.tabla.setItem(
                i, 4, QTableWidgetItem(fmt_moneda(iva) if aplica_iva else "—")
            )
            self.tabla.setItem(i, 5, QTableWidgetItem(fmt_moneda(total_item)))

        subtotal_bruto = subtotal_total + iva_total
        if self.descuento["total"] > 0:
            self.lbl_descuento.setVisible(True)
            self.lbl_descuento.setText(
                f"Descuento: -{fmt_moneda(self.descuento['total'])}"
            )
            total_final = max(0, subtotal_bruto - self.descuento["total"])
        else:
            self.lbl_descuento.setVisible(False)
            total_final = subtotal_bruto

        self.lbl_subtotal.setText(f"Subtotal: {fmt_moneda(subtotal_total)}")
        self.lbl_iva.setText(f"IVA (19%): {fmt_moneda(iva_total)}")
        self.lbl_total.setText(f"TOTAL: {fmt_moneda(total_final)}")

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

    def aplicar_descuento(self):
        if not self.carrito:
            QMessageBox.warning(
                self, "Carrito vacío", "Agrega productos antes de aplicar un descuento."
            )
            return
        subtotal = sum(item["cantidad"] * item["precio"] for item in self.carrito)
        iva = sum(
            round(item["cantidad"] * item["precio"] * 0.19, 2)
            for item in self.carrito
            if item.get("aplica_iva", True)
        )
        total_bruto = subtotal + iva

        from ui.descuento_dialog import DescuentoDialog

        dialog = DescuentoDialog(total_bruto, self.descuento.copy(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.descuento = dialog.descuento_resultado
            self.actualizar_tabla()
            if self.descuento["total"] > 0:
                self.btn_descuento.setText(f"🏷 -{fmt_moneda(self.descuento['total'])}")
                self.btn_descuento.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white; padding: 10px;
                        font-weight: bold;
                    }
                """)
            else:
                self.btn_descuento.setText("🏷 Descuento")
                self.btn_descuento.setStyleSheet("""
                    QPushButton {
                        background-color: #e67e22;
                        color: white; padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover { background-color: #d35400; }
                """)

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
            self.descuento = {"tipo": None, "valor": 0, "total": 0}
            self.btn_descuento.setText("🏷 Descuento")
            self.btn_descuento.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white; padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #d35400; }
            """)
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

        descuento_total = self.descuento.get("total", 0)
        total = max(0, (subtotal + iva) - descuento_total)

        dialog = PaymentDialog(
            subtotal,
            iva,
            total,
            self,
            cliente=self.cliente_seleccionado,
            descuento=descuento_total,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            service = VentaService(self.session)
            cliente_id = (
                self.cliente_seleccionado.id if self.cliente_seleccionado else None
            )
            es_credito = dialog.metodo_pago == "Fiado"
            venta = service.registrar_venta(
                self.carrito,
                metodo_pago=dialog.metodo_pago,
                cliente_id=cliente_id,
                es_credito=es_credito,
                descuento_tipo=self.descuento.get("tipo"),
                descuento_valor=self.descuento.get("valor", 0),
                descuento_total=descuento_total,
            )

            generador = GeneradorTicket()
            generador.imprimir(venta, venta.items)

            try:
                from utils.store_config import get_printer_enabled
                from utils.impresora import get_impresora

                if get_printer_enabled():
                    imp = get_impresora()
                    imp.imprimir_ticket(venta, venta.items)
                    imp.desconectar()
            except Exception as e:
                import logging

                logging.warning(f"No se pudo imprimir en termica: {e}")

            cambio = dialog.payment_amount - total

            self.carrito = []
            self.descuento = {"tipo": None, "valor": 0, "total": 0}
            self.btn_descuento.setText("🏷 Descuento")
            self.btn_descuento.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white; padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #d35400; }
            """)
            self.actualizar_tabla()

            QMessageBox.information(
                self,
                "Venta Registrada",
                f"Venta #{venta.id}\n"
                f"Subtotal: {fmt_moneda(subtotal)}\n"
                f"IVA: {fmt_moneda(iva)}\n"
                f"Total: {fmt_moneda(total)}\n"
                f"Pago: {fmt_moneda(dialog.payment_amount)}\n"
                f"Cambio: {fmt_moneda(cambio)}\n\n"
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

    def guardar_cotizacion(self):
        """Save current cart as a quotation"""
        if not self.carrito:
            QMessageBox.warning(
                self, "Cotización vacía", "Agrega productos al carrito primero"
            )
            return

        from services.cotizacion_service import CotizacionService

        notas = ""
        if self.cliente_seleccionado:
            texto, ok = QInputDialog.getText(
                self,
                "Notas de cotización",
                f"Cliente: {self.cliente_seleccionado.nombre}\n\nNotas opcionales:",
            )
            if ok:
                notas = texto
        else:
            texto, ok = QInputDialog.getText(
                self, "Notas de cotización", "Notas opcionales:"
            )
            if ok:
                notas = texto

        try:
            service = CotizacionService(self.session)
            cliente_id = (
                self.cliente_seleccionado.id if self.cliente_seleccionado else None
            )
            subtotal = sum(item["cantidad"] * item["precio"] for item in self.carrito)

            cotizacion = service.crear(self.carrito, cliente_id=cliente_id, notas=notas)

            QMessageBox.information(
                self,
                "Cotización guardada",
                f"Cotización #{cotizacion.id} guardada exitosamente.\n"
                f"Cliente: {self.cliente_seleccionado.nombre if self.cliente_seleccionado else 'Sin cliente'}\n"
                f"Total: {fmt_moneda(cotizacion.total)}",
            )

            self.cotizacion_creada.emit()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo guardar la cotización: {str(e)}"
            )

    def cargar_carrito_desde_cotizacion(self, carrito, cliente):
        """Load items from a quotation into the cart"""
        self.carrito = []
        for item in carrito:
            self.carrito.append(
                {
                    "producto_id": item["producto_id"],
                    "codigo": item["codigo"],
                    "nombre": item["nombre"],
                    "precio": item["precio"],
                    "cantidad": item["cantidad"],
                    "aplica_iva": item.get("aplica_iva", True),
                }
            )

        if cliente:
            self.cliente_seleccionado = cliente
            self.lbl_cliente.setText(f"Cliente: {cliente.nombre}")
        else:
            self.cliente_seleccionado = None
            self.lbl_cliente.setText("Sin cliente")

        self.descuento = {"tipo": None, "valor": 0, "total": 0}
        self.btn_descuento.setText("🏷 Descuento")
        self.btn_descuento.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white; padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.actualizar_tabla()
        self.codigo_input.setFocus()

        QMessageBox.information(
            self,
            "Cotización cargada",
            f"Se cargaron {len(self.carrito)} productos desde la cotización.\n"
            "Puedes modificar cantidades o proceder al cobro.",
        )
