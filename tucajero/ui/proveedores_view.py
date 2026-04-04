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
    QTabWidget,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QSpinBox,
    QComboBox,
    QDialogButtonBox,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from tucajero.utils.formato import fmt_moneda
from tucajero.utils.theme import btn_primary, btn_danger, btn_secondary, get_colors


class ProveedoresView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()

    def init_ui(self):
        c = get_colors()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

        # Scrollable container for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setMaximumWidth(600)
        container_layout = QVBoxLayout()
        container_layout.setSpacing(24)
        container_layout.setContentsMargins(0, 16, 0, 16)
        container.setLayout(container_layout)

        titulo = QLabel("Proveedores y Compras")
        titulo.setStyleSheet(
            f"font-size: 26px; font-weight: 700; color: {c['text_primary']}; "
            f"padding: 8px 0;"
        )
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(titulo)

        self.tabs = QTabWidget()
        self.tab_proveedores = self._crear_tab_proveedores()
        self.tab_ordenes = self._crear_tab_ordenes()
        self.tabs.addTab(self.tab_proveedores, "🏭 Proveedores")
        self.tabs.addTab(self.tab_ordenes, "📦 Órdenes de Compra")
        container_layout.addWidget(self.tabs)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _crear_tab_proveedores(self):
        c = get_colors()
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # Card wrapper
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['bg_card']}; border-radius: 12px; "
            f"border: 1px solid {c['border']}; padding: 0px;"
        )
        card_layout = QVBoxLayout()
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card.setLayout(card_layout)

        # Button row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_nuevo = QPushButton("+ Nuevo Proveedor")
        btn_nuevo.setFixedHeight(44)
        btn_nuevo.setStyleSheet(btn_primary())
        btn_nuevo.clicked.connect(self.nuevo_proveedor)
        btn_layout.addWidget(btn_nuevo)

        btn_editar = QPushButton("Editar")
        btn_editar.setFixedHeight(44)
        btn_editar.setStyleSheet(btn_secondary())
        btn_editar.clicked.connect(self.editar_proveedor)
        btn_layout.addWidget(btn_editar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setFixedHeight(44)
        btn_eliminar.setStyleSheet(btn_danger())
        btn_eliminar.clicked.connect(self.eliminar_proveedor)
        btn_layout.addWidget(btn_eliminar)

        card_layout.addLayout(btn_layout)

        # Table
        self.tabla_prov = QTableWidget()
        self.tabla_prov.setColumnCount(5)
        self.tabla_prov.setHorizontalHeaderLabels(
            ["ID", "Nombre", "NIT", "Teléfono", "Email"]
        )
        self.tabla_prov.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_prov.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_prov.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        card_layout.addWidget(self.tabla_prov)

        layout.addWidget(card)

        self.proveedores = []
        self.cargar_proveedores()
        return widget

    def cargar_proveedores(self):
        from tucajero.services.proveedor_service import ProveedorService

        self.proveedores = ProveedorService(self.session).get_all()
        self.tabla_prov.setRowCount(len(self.proveedores))
        for i, p in enumerate(self.proveedores):
            self.tabla_prov.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.tabla_prov.setItem(i, 1, QTableWidgetItem(p.nombre))
            self.tabla_prov.setItem(i, 2, QTableWidgetItem(p.nit or ""))
            self.tabla_prov.setItem(i, 3, QTableWidgetItem(p.telefono or ""))
            self.tabla_prov.setItem(i, 4, QTableWidgetItem(p.email or ""))

    def obtener_proveedor_seleccionado(self):
        row = self.tabla_prov.currentRow()
        if row >= 0 and row < len(self.proveedores):
            return self.proveedores[row]
        return None

    def nuevo_proveedor(self):
        dialog = ProveedorDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_proveedores()

    def editar_proveedor(self):
        p = self.obtener_proveedor_seleccionado()
        if not p:
            QMessageBox.warning(self, "Error", "Selecciona un proveedor")
            return
        dialog = ProveedorDialog(self.session, self, p.id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_proveedores()

    def eliminar_proveedor(self):
        p = self.obtener_proveedor_seleccionado()
        if not p:
            QMessageBox.warning(self, "Error", "Selecciona un proveedor")
            return
        resp = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar al proveedor '{p.nombre}'?"
        )
        if resp == QMessageBox.StandardButton.Yes:
            from tucajero.services.proveedor_service import ProveedorService

            ProveedorService(self.session).eliminar(p.id)
            self.cargar_proveedores()

    def _crear_tab_ordenes(self):
        c = get_colors()
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)

        # Card wrapper
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {c['bg_card']}; border-radius: 12px; "
            f"border: 1px solid {c['border']}; padding: 0px;"
        )
        card_layout = QVBoxLayout()
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card.setLayout(card_layout)

        # Button row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_nueva = QPushButton("+ Nueva Orden")
        btn_nueva.setFixedHeight(44)
        btn_nueva.setStyleSheet(btn_primary())
        btn_nueva.clicked.connect(self.nueva_orden)
        btn_layout.addWidget(btn_nueva)

        btn_recibir = QPushButton("✅ Recibir")
        btn_recibir.setFixedHeight(44)
        btn_recibir.setStyleSheet(btn_primary())
        btn_recibir.clicked.connect(self.recibir_orden)
        btn_layout.addWidget(btn_recibir)

        btn_cancelar = QPushButton("✕ Cancelar")
        btn_cancelar.setFixedHeight(44)
        btn_cancelar.setStyleSheet(btn_danger())
        btn_cancelar.clicked.connect(self.cancelar_orden)
        btn_layout.addWidget(btn_cancelar)

        card_layout.addLayout(btn_layout)

        # Table
        self.tabla_ord = QTableWidget()
        self.tabla_ord.setColumnCount(6)
        self.tabla_ord.setHorizontalHeaderLabels(
            ["ID", "Fecha", "Proveedor", "Total", "Estado", "Notas"]
        )
        self.tabla_ord.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_ord.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_ord.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_ord.doubleClicked.connect(self.ver_detalle_orden)
        card_layout.addWidget(self.tabla_ord)

        # Info label
        info = QLabel("💡 Doble clic en una orden para ver el detalle de productos")
        info.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 12px; padding: 4px 0 0 0;"
        )
        card_layout.addWidget(info)

        layout.addWidget(card)

        self.ordenes = []
        self.cargar_ordenes()
        return widget

    def cargar_ordenes(self):
        from tucajero.services.proveedor_service import OrdenCompraService
        from tucajero.utils.theme import get_colors

        c = get_colors()

        self.ordenes = OrdenCompraService(self.session).get_all()
        self.tabla_ord.setRowCount(len(self.ordenes))
        for i, o in enumerate(self.ordenes):
            self.tabla_ord.setItem(i, 0, QTableWidgetItem(str(o.id)))
            self.tabla_ord.setItem(i, 1, QTableWidgetItem(o.fecha.strftime("%d/%m/%Y")))
            self.tabla_ord.setItem(
                i, 2, QTableWidgetItem(o.proveedor.nombre if o.proveedor else "")
            )
            self.tabla_ord.setItem(i, 3, QTableWidgetItem(fmt_moneda(o.total)))

            estado_item = QTableWidgetItem(o.estado.capitalize())
            if o.estado == "pendiente":
                estado_item.setBackground(QColor(c["warning"] + "33"))
                estado_item.setForeground(QColor(c["warning"]))
            elif o.estado == "recibida":
                estado_item.setBackground(QColor(c["success"] + "33"))
                estado_item.setForeground(QColor(c["success"]))
            elif o.estado == "cancelada":
                estado_item.setBackground(QColor(c["danger"] + "33"))
                estado_item.setForeground(QColor(c["danger"]))
            self.tabla_ord.setItem(i, 4, estado_item)
            self.tabla_ord.setItem(i, 5, QTableWidgetItem(o.notas or ""))

    def obtener_orden_seleccionada(self):
        row = self.tabla_ord.currentRow()
        if row >= 0 and row < len(self.ordenes):
            return self.ordenes[row]
        return None

    def nueva_orden(self):
        dialog = OrdenCompraDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_ordenes()

    def recibir_orden(self):
        orden = self.obtener_orden_seleccionada()
        if not orden:
            QMessageBox.warning(self, "Error", "Selecciona una orden de compra")
            return

        resp = QMessageBox.question(
            self,
            "Recibir mercancía",
            f"¿Confirmar recepción de la orden #{orden.id}?\n\n"
            f"Proveedor: {orden.proveedor.nombre}\n"
            f"Total: {fmt_moneda(orden.total)}\n\n"
            f"⚠ El stock de todos los productos se actualizará "
            f"automáticamente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        from tucajero.services.proveedor_service import OrdenCompraService

        try:
            OrdenCompraService(self.session).recibir_orden(orden.id)
            QMessageBox.information(
                self,
                "Mercancía recibida",
                f"✅ Orden #{orden.id} recibida.\n"
                f"El inventario ha sido actualizado automáticamente.",
            )
            self.cargar_ordenes()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def cancelar_orden(self):
        orden = self.obtener_orden_seleccionada()
        if not orden:
            QMessageBox.warning(self, "Error", "Selecciona una orden de compra")
            return

        resp = QMessageBox.question(
            self,
            "Cancelar orden",
            f"¿Cancelar la orden #{orden.id} de {orden.proveedor.nombre}?",
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        from tucajero.services.proveedor_service import OrdenCompraService

        try:
            OrdenCompraService(self.session).cancelar(orden.id)
            self.cargar_ordenes()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def ver_detalle_orden(self):
        orden = self.obtener_orden_seleccionada()
        if not orden:
            return
        dialog = DetalleOrdenDialog(orden, self)
        dialog.exec()


class ProveedorDialog(QDialog):
    def __init__(self, session, parent=None, proveedor_id=None):
        super().__init__(parent)
        self.session = session
        self.proveedor_id = proveedor_id
        self.setWindowTitle(
            "Nuevo Proveedor" if not proveedor_id else "Editar Proveedor"
        )
        self.setMinimumWidth(480)
        c = get_colors()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

        # Card wrapper
        card = QFrame()
        card.setStyleSheet(
            f"background-color: #FFFFFF; border-radius: 12px; "
            f"border: 1px solid #E2E8F0;"
        )
        card_layout = QVBoxLayout()
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card.setLayout(card_layout)

        # Title
        titulo = QLabel(
            "Nuevo Proveedor" if not proveedor_id else "Editar Proveedor"
        )
        titulo.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {c['text_primary']}; "
            f"padding-bottom: 8px;"
        )
        card_layout.addWidget(titulo)

        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

        self.nombre = QLineEdit()
        self.nit = QLineEdit()
        self.telefono = QLineEdit()
        self.email = QLineEdit()
        self.direccion = QLineEdit()

        input_style = (
            f"background-color: #FFFFFF; color: {c['text_primary']}; "
            f"border: 1px solid #E2E8F0; border-radius: 8px; "
            f"padding: 8px 12px; font-size: 14px; min-height: 40px;"
        )
        label_style = (
            f"color: {c['text_secondary']}; font-size: 13px; font-weight: 500;"
        )

        for w in [self.nombre, self.nit, self.telefono, self.email, self.direccion]:
            w.setStyleSheet(input_style)

        nombre_label = QLabel("Nombre *")
        nombre_label.setStyleSheet(label_style)
        form_layout.addRow(nombre_label, self.nombre)

        nit_label = QLabel("NIT")
        nit_label.setStyleSheet(label_style)
        form_layout.addRow(nit_label, self.nit)

        telefono_label = QLabel("Teléfono")
        telefono_label.setStyleSheet(label_style)
        form_layout.addRow(telefono_label, self.telefono)

        email_label = QLabel("Email")
        email_label.setStyleSheet(label_style)
        form_layout.addRow(email_label, self.email)

        direccion_label = QLabel("Dirección")
        direccion_label.setStyleSheet(label_style)
        form_layout.addRow(direccion_label, self.direccion)

        card_layout.addLayout(form_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {c['border']}; border: none; max-height: 1px;")
        card_layout.addWidget(separator)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_g = QPushButton("Guardar")
        btn_g.setFixedHeight(44)
        btn_g.setStyleSheet(btn_primary())
        btn_g.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_g)

        btn_c = QPushButton("Cancelar")
        btn_c.setFixedHeight(44)
        btn_c.setStyleSheet(btn_secondary())
        btn_c.clicked.connect(self.reject)
        btn_layout.addWidget(btn_c)

        card_layout.addLayout(btn_layout)
        main_layout.addWidget(card)

        if proveedor_id:
            from tucajero.services.proveedor_service import ProveedorService

            p = ProveedorService(session).get_by_id(proveedor_id)
            if p:
                self.nombre.setText(p.nombre)
                self.nit.setText(p.nit or "")
                self.telefono.setText(p.telefono or "")
                self.email.setText(p.email or "")
                self.direccion.setText(p.direccion or "")

    def guardar(self):
        nombre = self.nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es requerido")
            return
        from tucajero.services.proveedor_service import ProveedorService

        service = ProveedorService(self.session)
        try:
            if self.proveedor_id:
                service.actualizar(
                    self.proveedor_id,
                    nombre=nombre,
                    nit=self.nit.text().strip(),
                    telefono=self.telefono.text().strip(),
                    email=self.email.text().strip(),
                    direccion=self.direccion.text().strip(),
                )
            else:
                service.crear(
                    nombre,
                    self.nit.text().strip(),
                    self.telefono.text().strip(),
                    self.email.text().strip(),
                    self.direccion.text().strip(),
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class OrdenCompraDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.items = []
        self.setWindowTitle("Nueva Orden de Compra")
        self.setMinimumSize(650, 600)
        self.init_ui()

    def init_ui(self):
        c = get_colors()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

        # Card wrapper
        card = QFrame()
        card.setStyleSheet(
            f"background-color: #FFFFFF; border-radius: 12px; "
            f"border: 1px solid #E2E8F0;"
        )
        card_layout = QVBoxLayout()
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card.setLayout(card_layout)

        # Title
        titulo = QLabel("Nueva Orden de Compra")
        titulo.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {c['text_primary']}; "
            f"padding-bottom: 8px;"
        )
        card_layout.addWidget(titulo)

        # Provider selector
        prov_layout = QHBoxLayout()
        prov_layout.setSpacing(12)
        prov_label = QLabel("Proveedor:")
        prov_label.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 13px; font-weight: 500;"
        )
        prov_layout.addWidget(prov_label)
        self.combo_prov = QComboBox()
        self.combo_prov.setStyleSheet(
            f"background-color: #FFFFFF; color: {c['text_primary']}; "
            f"border: 1px solid #E2E8F0; border-radius: 8px; "
            f"padding: 8px 12px; font-size: 14px; min-height: 40px;"
        )
        self._cargar_proveedores()
        prov_layout.addWidget(self.combo_prov, 1)
        card_layout.addLayout(prov_layout)

        # Add product section
        agregar_label = QLabel("Agregar productos")
        agregar_label.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 13px; font-weight: 600; "
            f"text-transform: uppercase; letter-spacing: 0.5px; padding-top: 8px;"
        )
        card_layout.addWidget(agregar_label)

        agregar_layout = QHBoxLayout()
        agregar_layout.setSpacing(12)

        self.combo_prod = QComboBox()
        self.combo_prod.setStyleSheet(
            f"background-color: #FFFFFF; color: {c['text_primary']}; "
            f"border: 1px solid #E2E8F0; border-radius: 8px; "
            f"padding: 8px 12px; font-size: 14px; min-height: 40px;"
        )
        agregar_layout.addWidget(self.combo_prod, 3)

        self.spin_cant = QSpinBox()
        self.spin_cant.setRange(1, 99999)
        self.spin_cant.setValue(1)
        self.spin_cant.setPrefix("Cant: ")
        self.spin_cant.setStyleSheet(
            f"background-color: #FFFFFF; color: {c['text_primary']}; "
            f"border: 1px solid #E2E8F0; border-radius: 8px; "
            f"padding: 8px 12px; font-size: 14px; min-height: 40px;"
        )
        agregar_layout.addWidget(self.spin_cant)

        self.spin_precio = QDoubleSpinBox()
        self.spin_precio.setRange(0, 9999999)
        self.spin_precio.setDecimals(2)
        self.spin_precio.setPrefix("$ ")
        self.spin_precio.setStyleSheet(
            f"background-color: #FFFFFF; color: {c['text_primary']}; "
            f"border: 1px solid #E2E8F0; border-radius: 8px; "
            f"padding: 8px 12px; font-size: 14px; min-height: 40px;"
        )
        agregar_layout.addWidget(self.spin_precio)

        self._cargar_productos()

        btn_agregar = QPushButton("+ Agregar")
        btn_agregar.setFixedHeight(44)
        btn_agregar.setStyleSheet(btn_primary())
        btn_agregar.clicked.connect(self.agregar_item)
        agregar_layout.addWidget(btn_agregar)
        card_layout.addLayout(agregar_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: #E2E8F0; border: none; max-height: 1px;")
        card_layout.addWidget(separator)

        # Table
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Precio compra", "Subtotal", ""]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setStyleSheet("font-size: 13px;")
        card_layout.addWidget(self.tabla)

        # Total
        self.lbl_total = QLabel("Total: $0.00")
        self.lbl_total.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {c['success']}; padding: 8px 0;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(self.lbl_total)

        # Notes
        self.notas = QLineEdit()
        self.notas.setPlaceholderText("Notas (opcional)")
        self.notas.setStyleSheet(
            f"background-color: #FFFFFF; color: {c['text_primary']}; "
            f"border: 1px solid #E2E8F0; border-radius: 8px; "
            f"padding: 8px 12px; font-size: 14px; min-height: 40px;"
        )
        card_layout.addWidget(self.notas)

        # Buttons
        btns = QHBoxLayout()
        btns.setSpacing(12)

        btn_crear = QPushButton("CREAR ORDEN")
        btn_crear.setFixedHeight(44)
        btn_crear.setStyleSheet(btn_primary())
        btn_crear.clicked.connect(self.crear_orden)
        btns.addWidget(btn_crear)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFixedHeight(44)
        btn_cancel.setStyleSheet(btn_secondary())
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        card_layout.addLayout(btns)
        main_layout.addWidget(card)

    def _cargar_proveedores(self):
        from tucajero.services.proveedor_service import ProveedorService

        self.proveedores = ProveedorService(self.session).get_all()
        for p in self.proveedores:
            self.combo_prov.addItem(p.nombre, p.id)

    def _cargar_productos(self):
        from tucajero.services.producto_service import ProductoService

        self.productos = ProductoService(self.session).get_all_productos()
        for p in self.productos:
            self.combo_prod.addItem(f"{p.codigo} — {p.nombre}", p.id)
        self.combo_prod.currentIndexChanged.connect(self._actualizar_precio_sugerido)
        self._actualizar_precio_sugerido()

    def _actualizar_precio_sugerido(self):
        idx = self.combo_prod.currentIndex()
        if idx >= 0 and idx < len(self.productos):
            self.spin_precio.setValue(self.productos[idx].costo or 0)

    def agregar_item(self):
        idx = self.combo_prod.currentIndex()
        if idx < 0:
            return
        producto = self.productos[idx]
        cantidad = self.spin_cant.value()
        precio = self.spin_precio.value()

        for item in self.items:
            if item["producto_id"] == producto.id:
                item["cantidad"] += cantidad
                self._actualizar_tabla()
                return

        self.items.append(
            {
                "producto_id": producto.id,
                "nombre": producto.nombre,
                "cantidad": cantidad,
                "precio_compra": precio,
            }
        )
        self._actualizar_tabla()

    def _actualizar_tabla(self):
        self.tabla.setRowCount(len(self.items))
        total = 0
        for i, item in enumerate(self.items):
            subtotal = item["cantidad"] * item["precio_compra"]
            total += subtotal
            self.tabla.setItem(i, 0, QTableWidgetItem(item["nombre"]))
            self.tabla.setItem(i, 1, QTableWidgetItem(str(item["cantidad"])))
            self.tabla.setItem(
                i, 2, QTableWidgetItem(fmt_moneda(item["precio_compra"]))
            )
            self.tabla.setItem(i, 3, QTableWidgetItem(fmt_moneda(subtotal)))

            btn_del = QPushButton("✕")
            btn_del.setStyleSheet(btn_danger())
            btn_del.clicked.connect(lambda checked, idx=i: self._eliminar_item(idx))
            self.tabla.setCellWidget(i, 4, btn_del)

        self.lbl_total.setText(f"Total: {fmt_moneda(total)}")

    def _eliminar_item(self, idx):
        if 0 <= idx < len(self.items):
            self.items.pop(idx)
            self._actualizar_tabla()

    def crear_orden(self):
        if not self.items:
            QMessageBox.warning(self, "Error", "Agrega al menos un producto")
            return
        if self.combo_prov.count() == 0:
            QMessageBox.warning(self, "Error", "No hay proveedores registrados")
            return

        proveedor_id = self.combo_prov.currentData()
        from tucajero.services.proveedor_service import OrdenCompraService

        try:
            orden = OrdenCompraService(self.session).crear(
                proveedor_id, self.items, notas=self.notas.text().strip()
            )
            QMessageBox.information(
                self,
                "Orden creada",
                f"✅ Orden de compra #{orden.id} creada.\n\n"
                f"Total: {fmt_moneda(orden.total)}\n\n"
                f"Cuando recibas la mercancía, marca la orden "
                f"como 'Recibida' para actualizar el inventario.",
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class DetalleOrdenDialog(QDialog):
    def __init__(self, orden, parent=None):
        super().__init__(parent)
        self.orden = orden
        self.setWindowTitle(f"Detalle - Orden #{orden.id}")
        self.setMinimumSize(600, 450)
        c = get_colors()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

        # Card wrapper
        card = QFrame()
        card.setStyleSheet(
            f"background-color: #FFFFFF; border-radius: 12px; "
            f"border: 1px solid #E2E8F0;"
        )
        card_layout = QVBoxLayout()
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card.setLayout(card_layout)

        # Title
        titulo = QLabel(f"Orden #{orden.id}")
        titulo.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {c['text_primary']}; "
            f"padding-bottom: 8px;"
        )
        card_layout.addWidget(titulo)

        # Info section
        info = QLabel(
            f"<b>Proveedor:</b> {orden.proveedor.nombre}<br>"
            f"<b>Fecha:</b> {orden.fecha.strftime('%d/%m/%Y %I:%M %p')}<br>"
            f"<b>Estado:</b> {orden.estado.capitalize()}<br>"
            f"<b>Total:</b> {fmt_moneda(orden.total)}"
        )
        info.setStyleSheet(
            f"font-size: 13px; color: {c['text_primary']}; padding: 12px; "
            f"background-color: #F8FAFC; border-radius: 8px; "
            f"border: 1px solid #E2E8F0;"
        )
        info.setWordWrap(True)
        card_layout.addWidget(info)

        # Table
        tabla = QTableWidget(len(orden.items), 4)
        tabla.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Precio compra", "Subtotal"]
        )
        tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        card_layout.addWidget(tabla)

        from tucajero.models.producto import Producto

        session = None
        if parent and hasattr(parent, "session"):
            session = parent.session

        for i, item in enumerate(orden.items):
            prod = None
            if session:
                prod = session.query(Producto).get(item.producto_id)
            nombre = prod.nombre if prod else f"Producto #{item.producto_id}"
            tabla.setItem(i, 0, QTableWidgetItem(nombre))
            tabla.setItem(i, 1, QTableWidgetItem(str(item.cantidad)))
            tabla.setItem(i, 2, QTableWidgetItem(fmt_moneda(item.precio_compra)))
            tabla.setItem(i, 3, QTableWidgetItem(fmt_moneda(item.subtotal)))

        # Notes
        if orden.notas:
            nota = QLabel(f"Notas: {orden.notas}")
            nota.setStyleSheet(
                f"color: {c['text_secondary']}; font-size: 12px; padding: 4px 0;"
            )
            nota.setWordWrap(True)
            card_layout.addWidget(nota)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: #E2E8F0; border: none; max-height: 1px;")
        card_layout.addWidget(separator)

        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedHeight(44)
        btn_cerrar.setStyleSheet(btn_secondary())
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)
        card_layout.addLayout(btn_layout)

        main_layout.addWidget(card)
