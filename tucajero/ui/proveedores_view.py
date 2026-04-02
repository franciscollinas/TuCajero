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
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Proveedores y Compras")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.tabs = QTabWidget()
        self.tab_proveedores = self._crear_tab_proveedores()
        self.tab_ordenes = self._crear_tab_ordenes()
        self.tabs.addTab(self.tab_proveedores, "🏭 Proveedores")
        self.tabs.addTab(self.tab_ordenes, "📦 Órdenes de Compra")
        layout.addWidget(self.tabs)

    def _crear_tab_proveedores(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_nuevo = QPushButton("+ Nuevo Proveedor")
        btn_nuevo.setStyleSheet(btn_primary())
        btn_nuevo.clicked.connect(self.nuevo_proveedor)
        btn_layout.addWidget(btn_nuevo)

        btn_editar = QPushButton("Editar")
        btn_editar.setStyleSheet(btn_primary())
        btn_editar.clicked.connect(self.editar_proveedor)
        btn_layout.addWidget(btn_editar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(btn_danger())
        btn_eliminar.clicked.connect(self.eliminar_proveedor)
        btn_layout.addWidget(btn_eliminar)

        layout.addLayout(btn_layout)

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
        layout.addWidget(self.tabla_prov)

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
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.addStretch()

        btn_nueva = QPushButton("+ Nueva Orden de Compra")
        btn_nueva.setFixedHeight(36)
        btn_nueva.setMaximumWidth(200)
        btn_nueva.setStyleSheet(btn_primary())
        btn_nueva.clicked.connect(self.nueva_orden)
        btn_layout.addWidget(btn_nueva)

        btn_recibir = QPushButton("✅ Recibir mercancía")
        btn_recibir.setFixedHeight(36)
        btn_recibir.setMaximumWidth(200)
        btn_recibir.setStyleSheet(btn_primary())
        btn_recibir.clicked.connect(self.recibir_orden)
        btn_layout.addWidget(btn_recibir)

        btn_cancelar = QPushButton("✕ Cancelar orden")
        btn_cancelar.setFixedHeight(36)
        btn_cancelar.setMaximumWidth(200)
        btn_cancelar.setStyleSheet(btn_danger())
        btn_cancelar.clicked.connect(self.cancelar_orden)
        btn_layout.addWidget(btn_cancelar)

        layout.addLayout(btn_layout)
        layout.setContentsMargins(8, 8, 8, 8)

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
        layout.addWidget(self.tabla_ord)

        info = QLabel("💡 Doble clic en una orden para ver el detalle de productos")
        from tucajero.utils.theme import get_colors

        c = get_colors()
        info.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 12px; padding: 4px;"
        )
        layout.addWidget(info)

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
        self.setMinimumWidth(420)
        layout = QFormLayout()
        self.setLayout(layout)

        self.nombre = QLineEdit()
        self.nit = QLineEdit()
        self.telefono = QLineEdit()
        self.email = QLineEdit()
        self.direccion = QLineEdit()

        for w in [self.nombre, self.nit, self.telefono, self.email, self.direccion]:
            w.setStyleSheet("padding: 8px; font-size: 14px;")

        layout.addRow("Nombre *:", self.nombre)
        layout.addRow("NIT:", self.nit)
        layout.addRow("Teléfono:", self.telefono)
        layout.addRow("Email:", self.email)
        layout.addRow("Dirección:", self.direccion)

        if proveedor_id:
            from tucajero.services.proveedor_service import ProveedorService

            p = ProveedorService(session).get_by_id(proveedor_id)
            if p:
                self.nombre.setText(p.nombre)
                self.nit.setText(p.nit or "")
                self.telefono.setText(p.telefono or "")
                self.email.setText(p.email or "")
                self.direccion.setText(p.direccion or "")

        btns = QHBoxLayout()
        btn_g = QPushButton("Guardar")
        btn_g.setStyleSheet(btn_primary())
        btn_g.clicked.connect(self.guardar)
        btns.addWidget(btn_g)
        btn_c = QPushButton("Cancelar")
        btn_c.setStyleSheet(btn_secondary())
        btn_c.clicked.connect(self.reject)
        btns.addWidget(btn_c)
        layout.addRow("", btns)

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
        self.setMinimumSize(700, 550)
        self.init_ui()

    def init_ui(self):
        from tucajero.utils.theme import get_colors

        c = get_colors()

        layout = QVBoxLayout()
        self.setLayout(layout)

        prov_layout = QHBoxLayout()
        prov_layout.addWidget(QLabel("Proveedor:"))
        self.combo_prov = QComboBox()
        self.combo_prov.setStyleSheet("padding: 8px; font-size: 14px;")
        self._cargar_proveedores()
        prov_layout.addWidget(self.combo_prov, 1)
        layout.addLayout(prov_layout)

        agregar_layout = QHBoxLayout()

        self.spin_precio = QDoubleSpinBox()
        self.spin_precio.setRange(0, 9999999)
        self.spin_precio.setDecimals(2)
        self.spin_precio.setPrefix("$")

        self.combo_prod = QComboBox()
        self.combo_prod.setStyleSheet("padding: 8px;")
        agregar_layout.addWidget(self.combo_prod, 3)

        self.spin_cant = QSpinBox()
        self.spin_cant.setRange(1, 99999)
        self.spin_cant.setValue(1)
        self.spin_cant.setPrefix("Cant: ")
        agregar_layout.addWidget(self.spin_cant)

        agregar_layout.addWidget(self.spin_precio)

        self._cargar_productos()

        btn_agregar = QPushButton("+ Agregar")
        btn_agregar.setStyleSheet(btn_primary())
        btn_agregar.clicked.connect(self.agregar_item)
        agregar_layout.addWidget(btn_agregar)
        layout.addLayout(agregar_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Precio compra", "Subtotal", ""]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.tabla)

        self.lbl_total = QLabel("Total: $0.00")
        self.lbl_total.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {c['success']}; padding: 8px;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_total)

        self.notas = QLineEdit()
        self.notas.setPlaceholderText("Notas (opcional)")
        self.notas.setStyleSheet("padding: 8px;")
        layout.addWidget(self.notas)

        btns = QHBoxLayout()
        btn_crear = QPushButton("📦 CREAR ORDEN")
        btn_crear.setStyleSheet(btn_primary())
        btn_crear.clicked.connect(self.crear_orden)
        btns.addWidget(btn_crear)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(btn_secondary())
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

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
        self.setWindowTitle(f"Detalle — Orden #{orden.id}")
        self.setMinimumSize(550, 400)
        from tucajero.utils.theme import get_colors

        c = get_colors()
        layout = QVBoxLayout()
        self.setLayout(layout)

        info = QLabel(
            f"<b>Proveedor:</b> {orden.proveedor.nombre}  |  "
            f"<b>Fecha:</b> {orden.fecha.strftime('%d/%m/%Y %I:%M %p')}  |  "
            f"<b>Estado:</b> {orden.estado.capitalize()}  |  "
            f"<b>Total:</b> {fmt_moneda(orden.total)}"
        )
        info.setStyleSheet(
            f"font-size:13px; padding:8px; background: {c['bg_card']}; border-radius:4px;"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        tabla = QTableWidget(len(orden.items), 4)
        tabla.setHorizontalHeaderLabels(
            ["Producto", "Cantidad", "Precio compra", "Subtotal"]
        )
        tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

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
        layout.addWidget(tabla)

        if orden.notas:
            nota = QLabel(f"📝 Notas: {orden.notas}")
            nota.setStyleSheet(
                f"color: {c['text_secondary']}; font-size: 12px; padding: 4px;"
            )
            layout.addWidget(nota)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(btn_secondary())
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
