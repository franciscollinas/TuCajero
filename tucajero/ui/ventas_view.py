from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
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
    QFrame,
)
from PySide6.QtCore import Qt, Signal, QTimer
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
        self.txt_codigo.setFocus()

    def init_ui(self):
        """Initialize the interface"""
        from utils.theme import get_colors

        c = get_colors()
        self.setStyleSheet(f"background-color: {c['bg_app']};")

        self.cliente_seleccionado = None

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)

        right_panel = QWidget()
        right_panel.setFixedWidth(280)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(12)

        main_layout.addWidget(left_panel, 7)
        main_layout.addWidget(right_panel, 3)

        # SECTION 1: Header
        header = QWidget()
        header.setStyleSheet(f"background-color: {c['bg_card']}; border-radius: 12px;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("🛒  Nueva Venta")
        title.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 16px; font-weight: bold;"
        )
        h_layout.addWidget(title)
        h_layout.addStretch()

        self.lbl_cliente = QLabel("👤 Sin cliente")
        self.lbl_cliente.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 12px;"
        )
        h_layout.addWidget(self.lbl_cliente)

        self.btn_cliente = QPushButton("Seleccionar cliente")
        self.btn_cliente.setFixedHeight(30)
        self.btn_cliente.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["accent_light"]};
                color: {c["accent"]};
                border: 1px solid {c["accent"]};
                border-radius: 6px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {c["accent"]}; color: white; }}
        """)
        self.btn_cliente.clicked.connect(self.seleccionar_cliente)
        h_layout.addWidget(self.btn_cliente)
        left_layout.addWidget(header)

        # SECTION 2: Search bar
        search_widget = QWidget()
        search_widget.setStyleSheet(
            f"background-color: {c['bg_card']}; border-radius: 12px;"
        )
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(12, 10, 12, 10)
        search_layout.setSpacing(8)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; background: transparent;")
        search_layout.addWidget(search_icon)

        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Buscar por código o nombre de producto...")
        self.txt_codigo.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {c["text_primary"]};
                font-size: 14px;
            }}
        """)
        self.txt_codigo.returnPressed.connect(self.buscar_producto)
        search_layout.addWidget(self.txt_codigo)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedSize(80, 34)
        btn_buscar.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["accent"]};
                color: white;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{ background-color: {c["accent_hover"]}; }}
        """)
        btn_buscar.clicked.connect(self.mostrar_buscador)
        search_layout.addWidget(btn_buscar)
        left_layout.addWidget(search_widget)

        # SECTION 3: Cart table
        cart_container = QWidget()
        cart_container.setStyleSheet(
            f"background-color: {c['bg_card']}; border-radius: 12px;"
        )
        cart_layout = QVBoxLayout(cart_container)
        cart_layout.setContentsMargins(0, 0, 0, 0)

        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(6)
        self.tabla_carrito.setHorizontalHeaderLabels(
            ["Código", "Producto", "Cant.", "Precio", "IVA", "Subtotal"]
        )
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_carrito.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_carrito.setAlternatingRowColors(True)
        self.tabla_carrito.verticalHeader().setVisible(False)
        self.tabla_carrito.setStyleSheet("border: none; border-radius: 12px;")
        self.tabla_carrito.setMinimumHeight(300)
        self.tabla_carrito.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        cart_layout.addWidget(self.tabla_carrito)

        qty_bar = QWidget()
        qty_bar.setStyleSheet(
            f"background-color: {c['bg_input']}; border-radius: 0 0 12px 12px;"
        )
        qty_layout = QHBoxLayout(qty_bar)
        qty_layout.setContentsMargins(12, 8, 12, 8)
        qty_layout.setSpacing(8)

        self.btn_menos = QPushButton("−")
        self.btn_menos.setFixedSize(34, 34)
        self.btn_menos.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["danger"]};
                color: white; border-radius: 17px;
                font-size: 18px; font-weight: bold; border: none; padding: 0;
            }}
            QPushButton:hover {{ background-color: #ff3a3a; }}
        """)
        self.btn_menos.clicked.connect(self.disminuir_cantidad)

        self.btn_mas = QPushButton("+")
        self.btn_mas.setFixedSize(34, 34)
        self.btn_mas.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["success"]};
                color: white; border-radius: 17px;
                font-size: 18px; font-weight: bold; border: none; padding: 0;
            }}
            QPushButton:hover {{ background-color: #00d699; }}
        """)
        self.btn_mas.clicked.connect(self.aumentar_cantidad)

        self.btn_eliminar = QPushButton("🗑 Eliminar")
        self.btn_eliminar.setFixedHeight(34)
        self.btn_eliminar.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["danger_light"]};
                color: {c["danger"]};
                border: 1px solid {c["danger"]};
                border-radius: 8px; padding: 4px 12px;
                font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {c["danger"]}; color: white; }}
        """)
        self.btn_eliminar.clicked.connect(self.eliminar_item)

        self.btn_descuento = QPushButton("% Descuento")
        self.btn_descuento.setFixedHeight(34)
        self.btn_descuento.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["warning_light"]};
                color: {c["warning"]};
                border: 1px solid {c["warning"]};
                border-radius: 8px; padding: 4px 12px;
                font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {c["warning"]}; color: white; }}
        """)
        self.btn_descuento.clicked.connect(self.aplicar_descuento)

        qty_layout.addWidget(self.btn_menos)
        qty_layout.addWidget(self.btn_mas)
        qty_layout.addStretch()
        qty_layout.addWidget(self.btn_descuento)
        qty_layout.addWidget(self.btn_eliminar)
        cart_layout.addWidget(qty_bar)
        left_layout.addWidget(cart_container)

        # RIGHT PANEL
        right_panel.setStyleSheet(
            f"background-color: {c['bg_card']}; border-radius: 14px;"
        )

        panel_title = QLabel("Resumen")
        panel_title.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;"
        )
        right_layout.addWidget(panel_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {c['border']}; border: none; max-height: 1px;")
        right_layout.addWidget(sep)

        sub_row = QHBoxLayout()
        sub_row.addWidget(QLabel("Subtotal"))
        self.lbl_subtotal = QLabel(fmt_moneda(0))
        self.lbl_subtotal.setStyleSheet(
            f"color: {c['text_primary']}; font-weight: bold;"
        )
        self.lbl_subtotal.setAlignment(Qt.AlignmentFlag.AlignRight)
        sub_row.addWidget(self.lbl_subtotal)
        right_layout.addLayout(sub_row)

        iva_row = QHBoxLayout()
        iva_row.addWidget(QLabel("IVA (19%)"))
        self.lbl_iva = QLabel(fmt_moneda(0))
        self.lbl_iva.setAlignment(Qt.AlignmentFlag.AlignRight)
        iva_row.addWidget(self.lbl_iva)
        right_layout.addLayout(iva_row)

        self.descuento_row = QHBoxLayout()
        desc_label = QLabel("Descuento")
        desc_label.setStyleSheet(f"color: {c['success']};")
        self.descuento_row.addWidget(desc_label)
        self.lbl_descuento_val = QLabel("")
        self.lbl_descuento_val.setStyleSheet(
            f"color: {c['success']}; font-weight: bold;"
        )
        self.lbl_descuento_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.descuento_row.addWidget(self.lbl_descuento_val)
        right_layout.addLayout(self.descuento_row)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background: {c['border']}; border: none; max-height: 1px;")
        right_layout.addWidget(sep2)

        total_container = QWidget()
        total_container.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 {c["accent"]}22, stop:1 {c["success"]}22);
            border-radius: 10px;
            border: 1px solid {c["border"]};
        """)
        total_layout = QVBoxLayout(total_container)
        total_layout.setContentsMargins(12, 12, 12, 12)
        lbl_total_title = QLabel("TOTAL")
        lbl_total_title.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 11px; font-weight: bold;"
        )
        self.lbl_total = QLabel(fmt_moneda(0))
        self.lbl_total.setStyleSheet(f"""
            color: {c["success"]};
            font-size: 32px;
            font-weight: bold;
            background: transparent;
        """)
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_layout.addWidget(lbl_total_title)
        total_layout.addWidget(self.lbl_total)
        right_layout.addWidget(total_container)

        right_layout.addStretch()

        metodo_label = QLabel("Método de pago")
        metodo_label.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 11px; font-weight: bold;"
        )
        right_layout.addWidget(metodo_label)

        self.metodo_grupo = QButtonGroup()
        metodos = [
            ("💵", "Efectivo"),
            ("📱", "Nequi"),
            ("📱", "Daviplata"),
            ("🏦", "Transferencia"),
        ]
        metodo_grid = QGridLayout()
        metodo_grid.setSpacing(6)
        for i, (icon, nombre) in enumerate(metodos):
            rb = QRadioButton(f"{icon} {nombre}")
            rb.setStyleSheet(f"""
                QRadioButton {{
                    color: {c["text_primary"]};
                    font-size: 12px;
                    padding: 6px 8px;
                    border-radius: 6px;
                    background: {c["bg_input"]};
                }}
                QRadioButton::indicator {{ width: 14px; height: 14px; }}
                QRadioButton:checked {{
                    background: {c["accent_light"]};
                    color: {c["accent"]};
                }}
            """)
            if i == 0:
                rb.setChecked(True)
            self.metodo_grupo.addButton(rb, i)
            metodo_grid.addWidget(rb, i // 2, i % 2)
        right_layout.addLayout(metodo_grid)

        right_layout.addSpacing(8)

        self.btn_cobrar = QPushButton("💳  COBRAR")
        self.btn_cobrar.setFixedHeight(52)
        self.btn_cobrar.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {c["success"]}, stop:1 #00a876);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00d699, stop:1 {c["success"]});
            }}
            QPushButton:disabled {{
                background: {c["border"]};
                color: {c["text_muted"]};
            }}
        """)
        self.btn_cobrar.clicked.connect(self.cobrar)
        right_layout.addWidget(self.btn_cobrar)

        sec_layout = QHBoxLayout()
        sec_layout.setSpacing(6)

        self.btn_cancelar = QPushButton("✕ Cancelar")
        self.btn_cancelar.setFixedHeight(34)
        self.btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {c["text_secondary"]};
                border: 1px solid {c["border"]};
                border-radius: 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {c["danger_light"]};
                color: {c["danger"]};
                border-color: {c["danger"]};
            }}
        """)
        self.btn_cancelar.clicked.connect(self.cancelar_venta)

        self.btn_cotizar = QPushButton("📋 Cotizar")
        self.btn_cotizar.setFixedHeight(34)
        self.btn_cotizar.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {c["text_secondary"]};
                border: 1px solid {c["border"]};
                border-radius: 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {c["accent_light"]};
                color: {c["accent"]};
                border-color: {c["accent"]};
            }}
        """)
        self.btn_cotizar.clicked.connect(self.guardar_cotizacion)

        sec_layout.addWidget(self.btn_cancelar)
        sec_layout.addWidget(self.btn_cotizar)
        right_layout.addLayout(sec_layout)

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

        texto = self.txt_codigo.text().strip()
        if not texto:
            return

        service = ProductoService(self.session)

        producto = service.get_producto_by_codigo(texto)
        if producto and producto.stock > 0:
            self.agregar_al_carrito(producto)
            self.txt_codigo.clear()
            self.txt_codigo.setFocus()
            return

        productos = service.get_producto_by_nombre(texto)
        if len(productos) == 1:
            producto = productos[0]
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.txt_codigo.clear()
                self.txt_codigo.setFocus()
                return
        elif len(productos) > 1:
            self.txt_codigo.clear()
            self.mostrar_buscador_productos(productos)
            return

        QMessageBox.warning(self, "No encontrado", f"No se encontró '{texto}'")
        self.txt_codigo.selectAll()
        self.txt_codigo.setFocus()

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
                self.txt_codigo.setFocus()

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
            from utils.theme import get_colors

            c = get_colors()
            self.lbl_cliente.setStyleSheet(
                f"color: {c['accent']}; font-size: 12px; font-weight: bold;"
            )

    def quitar_cliente(self):
        from utils.theme import get_colors

        c = get_colors()
        self.cliente_seleccionado = None
        self.lbl_cliente.setText("👤 Sin cliente")
        self.lbl_cliente.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 12px;"
        )

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
                self.txt_codigo.setFocus()

    def agregar_al_carrito(self, producto):
        """Add product to cart"""
        for item in self.carrito:
            if item["producto_id"] == producto.id:
                item["cantidad"] += 1
                self.actualizar_tabla()
                self.mostrar_feedback(f"{producto.nombre} x{item['cantidad']}")
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
        self.mostrar_feedback(f"{producto.nombre} agregado")

    def mostrar_feedback(self, mensaje, tipo="success"):
        from utils.theme import get_colors

        c = get_colors()
        color = c["success"] if tipo == "success" else c["danger"]

        notif = QLabel(f"✓  {mensaje}", self)
        notif.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
        """)
        notif.adjustSize()
        notif.move(
            (self.width() - notif.width()) // 2, self.height() - notif.height() - 80
        )
        notif.show()
        QTimer.singleShot(2000, notif.deleteLater)

    def actualizar_tabla(self):
        """Update cart table"""
        self.tabla_carrito.setRowCount(len(self.carrito))

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

            self.tabla_carrito.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self.tabla_carrito.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            self.tabla_carrito.setItem(i, 2, QTableWidgetItem(str(cantidad)))
            self.tabla_carrito.setItem(i, 3, QTableWidgetItem(fmt_moneda(precio)))
            self.tabla_carrito.setItem(
                i, 4, QTableWidgetItem(fmt_moneda(iva) if aplica_iva else "—")
            )
            self.tabla_carrito.setItem(i, 5, QTableWidgetItem(fmt_moneda(total_item)))

        subtotal_bruto = subtotal_total + iva_total
        if self.descuento["total"] > 0:
            self.lbl_descuento_val.setText(f"-{fmt_moneda(self.descuento['total'])}")
            total_final = max(0, subtotal_bruto - self.descuento["total"])
        else:
            self.lbl_descuento_val.setText("")
            total_final = subtotal_bruto

        self.lbl_subtotal.setText(fmt_moneda(subtotal_total))
        self.lbl_iva.setText(fmt_moneda(iva_total))
        self.lbl_total.setText(fmt_moneda(total_final))

    def aumentar_cantidad(self):
        """Increase quantity of selected product"""
        row = self.tabla_carrito.currentRow()
        if row >= 0 and row < len(self.carrito):
            self.carrito[row]["cantidad"] += 1
            self.actualizar_tabla()

    def disminuir_cantidad(self):
        """Decrease quantity of selected product"""
        row = self.tabla_carrito.currentRow()
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
            from utils.theme import get_colors

            c = get_colors()
            if self.descuento["total"] > 0:
                self.btn_descuento.setText(f"🏷 -{fmt_moneda(self.descuento['total'])}")
                self.btn_descuento.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c["success"]};
                        color: white; padding: 4px 12px;
                        font-weight: bold; border-radius: 8px; border: none;
                    }}
                """)
            else:
                self.btn_descuento.setText("% Descuento")
                self.btn_descuento.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c["warning_light"]};
                        color: {c["warning"]};
                        border: 1px solid {c["warning"]};
                        border-radius: 8px; padding: 4px 12px;
                        font-size: 12px; font-weight: bold;
                    }}
                    QPushButton:hover {{ background-color: {c["warning"]}; color: white; }}
                """)

    def eliminar_item(self):
        """Remove item from cart"""
        row = self.tabla_carrito.currentRow()
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
            from utils.theme import get_colors

            c = get_colors()
            self.btn_descuento.setText("% Descuento")
            self.btn_descuento.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c["warning_light"]};
                    color: {c["warning"]};
                    border: 1px solid {c["warning"]};
                    border-radius: 8px; padding: 4px 12px;
                    font-size: 12px; font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {c["warning"]}; color: white; }}
            """)
            self.actualizar_tabla()
            self.txt_codigo.setFocus()

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
            from utils.theme import get_colors

            c = get_colors()
            self.btn_descuento.setText("% Descuento")
            self.btn_descuento.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c["warning_light"]};
                    color: {c["warning"]};
                    border: 1px solid {c["warning"]};
                    border-radius: 8px; padding: 4px 12px;
                    font-size: 12px; font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {c["warning"]}; color: white; }}
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

            self.txt_codigo.setFocus()

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
            from utils.theme import get_colors

            c = get_colors()
            self.lbl_cliente.setText(f"👤 {cliente.nombre}")
            self.lbl_cliente.setStyleSheet(
                f"color: {c['accent']}; font-size: 12px; font-weight: bold;"
            )
        else:
            self.cliente_seleccionado = None
            from utils.theme import get_colors

            c = get_colors()
            self.lbl_cliente.setText("👤 Sin cliente")
            self.lbl_cliente.setStyleSheet(
                f"color: {c['text_secondary']}; font-size: 12px;"
            )

        self.descuento = {"tipo": None, "valor": 0, "total": 0}
        self.btn_descuento.setText("% Descuento")
        self.btn_descuento.setStyleSheet(f"""
            QPushButton {{
                background-color: {c["warning_light"]};
                color: {c["warning"]};
                border: 1px solid {c["warning"]};
                border-radius: 8px; padding: 4px 12px;
                font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {c["warning"]}; color: white; }}
        """)
        self.actualizar_tabla()
        self.txt_codigo.setFocus()

        QMessageBox.information(
            self,
            "Cotización cargada",
            f"Se cargaron {len(self.carrito)} productos desde la cotización.\n"
            "Puedes modificar cantidades o proceder al cobro.",
        )
