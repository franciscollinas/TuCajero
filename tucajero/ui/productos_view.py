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
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QHeaderView,
    QCheckBox,
    QComboBox,
    QInputDialog,
)
from PySide6.QtCore import Qt


class ProductosView(QWidget):
    """Vista de gestión de productos"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_productos()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Productos")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_agregar = QPushButton("+ Agregar Producto")
        btn_agregar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 10px;"
        )
        btn_agregar.clicked.connect(self.abrir_dialogo_agregar)
        btn_layout.addWidget(btn_agregar)

        btn_editar = QPushButton("Editar")
        btn_editar.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px;"
        )
        btn_editar.clicked.connect(self.editar_producto)
        btn_layout.addWidget(btn_editar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px;"
        )
        btn_eliminar.clicked.connect(self.eliminar_producto)
        btn_layout.addWidget(btn_eliminar)

        btn_categorias = QPushButton("Categorías")
        btn_categorias.setStyleSheet(
            "background-color: #9b59b6; color: white; padding: 10px;"
        )
        btn_categorias.clicked.connect(self.abrir_gestor_categorias)
        btn_layout.addWidget(btn_categorias)

        layout.addLayout(btn_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Código", "Nombre", "Precio", "Stock", "Categoría"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.tabla)

    def cargar_productos(self):
        """Carga los productos desde la base de datos"""
        from services.producto_service import ProductoService

        service = ProductoService(self.session)
        productos = service.get_all_productos()

        self.tabla.setRowCount(len(productos))

        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 2, QTableWidgetItem(p.nombre))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"${p.precio:.2f}"))
            self.tabla.setItem(i, 4, QTableWidgetItem(str(p.stock)))
            cat_nombre = p.categoria.nombre if p.categoria else "—"
            self.tabla.setItem(i, 5, QTableWidgetItem(cat_nombre))

    def recargar_productos(self):
        """Recarga los productos (para auto-actualizacion despues de venta)"""
        self.cargar_productos()

    def obtener_producto_seleccionado(self):
        """Retorna el ID del producto seleccionado"""
        row = self.tabla.currentRow()
        if row >= 0:
            item = self.tabla.item(row, 0)
            if item is not None:
                try:
                    return int(item.text())
                except (ValueError, TypeError):
                    return None
        return None

    def abrir_dialogo_agregar(self):
        """Abre el diálogo para agregar un producto"""
        dialog = ProductoDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_productos()

    def editar_producto(self):
        """Abre el diálogo para editar un producto"""
        producto_id = self.obtener_producto_seleccionado()
        if not producto_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        dialog = ProductoDialog(self.session, self, producto_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_productos()

    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        producto_id = self.obtener_producto_seleccionado()
        if not producto_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de eliminar este producto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            from services.producto_service import ProductoService

            service = ProductoService(self.session)
            service.delete_producto(producto_id)
            self.cargar_productos()

    def abrir_gestor_categorias(self):
        """Abre el diálogo de gestión de categorías"""
        dialog = CategoriaDialog(self.session, self)
        dialog.exec()
        self.cargar_productos()


class ProductoDialog(QDialog):
    """Diálogo para agregar/editar productos"""

    def __init__(self, session, parent=None, producto_id=None):
        super().__init__(parent)
        self.session = session
        self.producto_id = producto_id
        self.setWindowTitle(
            "Agregar Producto" if not producto_id else "Editar Producto"
        )
        self.setMinimumWidth(450)
        self.init_ui()

        if producto_id:
            self.cargar_producto()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QFormLayout()
        self.setLayout(layout)

        self.codigo_input = QLineEdit()
        layout.addRow("Código:", self.codigo_input)

        self.nombre_input = QLineEdit()
        layout.addRow("Nombre:", self.nombre_input)

        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0, 999999)
        self.precio_input.setDecimals(2)
        layout.addRow("Precio:", self.precio_input)

        self.costo_input = QDoubleSpinBox()
        self.costo_input.setRange(0, 999999)
        self.costo_input.setDecimals(2)
        layout.addRow("Costo:", self.costo_input)

        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 999999)
        layout.addRow("Stock:", self.stock_input)

        cat_layout = QHBoxLayout()
        self.cat_combo = QComboBox()
        self.cat_combo.addItem("Sin categoría", None)
        self._cargar_categorias()
        cat_layout.addWidget(self.cat_combo)

        btn_nueva_cat = QPushButton("+")
        btn_nueva_cat.setFixedWidth(40)
        btn_nueva_cat.setToolTip("Crear nueva categoría")
        btn_nueva_cat.clicked.connect(self._crear_categoria_rapida)
        cat_layout.addWidget(btn_nueva_cat)

        layout.addRow("Categoría:", cat_layout)

        self.aplica_iva = QCheckBox("Aplica IVA (19%)")
        self.aplica_iva.setChecked(True)
        layout.addRow("", self.aplica_iva)

        btn_layout = QHBoxLayout()

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 10px;"
        )
        btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_guardar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(
            "background-color: #95a5a6; color: white; padding: 10px;"
        )
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        layout.addRow("", btn_layout)

    def _cargar_categorias(self):
        """Carga las categorías en el combo"""
        self.cat_combo.clear()
        self.cat_combo.addItem("Sin categoría", None)
        from services.producto_service import CategoriaService

        service = CategoriaService(self.session)
        cats = service.get_all()
        for cat in cats:
            self.cat_combo.addItem(cat.nombre, cat.id)

    def _crear_categoria_rapida(self):
        """Crea una categoría rápida"""
        nombre, ok = QInputDialog.getText(
            self, "Nueva Categoría", "Nombre de la categoría:"
        )
        if ok and nombre.strip():
            try:
                from services.producto_service import CategoriaService

                service = CategoriaService(self.session)
                service.create(nombre.strip())
                self._cargar_categorias()
                for i in range(self.cat_combo.count()):
                    if self.cat_combo.itemText(i) == nombre.strip():
                        self.cat_combo.setCurrentIndex(i)
                        break
                QMessageBox.information(self, "Éxito", f"Categoría '{nombre}' creada")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def cargar_producto(self):
        """Carga los datos del producto a editar"""
        from services.producto_service import ProductoService

        service = ProductoService(self.session)
        producto = service.get_producto_by_id(self.producto_id)

        if producto:
            self.codigo_input.setText(producto.codigo)
            self.nombre_input.setText(producto.nombre)
            self.precio_input.setValue(producto.precio)
            self.costo_input.setValue(producto.costo)
            self.stock_input.setValue(producto.stock)
            self.aplica_iva.setChecked(producto.aplica_iva)

            if producto.categoria_id:
                for i in range(self.cat_combo.count()):
                    if self.cat_combo.currentData() == producto.categoria_id:
                        self.cat_combo.setCurrentIndex(i)
                        break

    def guardar(self):
        """Guarda el producto"""
        from services.producto_service import ProductoService

        codigo = self.codigo_input.text().strip()
        nombre = self.nombre_input.text().strip()
        precio = self.precio_input.value()
        costo = self.costo_input.value()
        stock = self.stock_input.value()
        aplica_iva = self.aplica_iva.isChecked()
        categoria_id = self.cat_combo.currentData()

        if not codigo or not nombre:
            QMessageBox.warning(self, "Error", "Código y nombre son requeridos")
            return

        service = ProductoService(self.session)

        try:
            if self.producto_id:
                service.update_producto(
                    self.producto_id,
                    codigo=codigo,
                    nombre=nombre,
                    precio=precio,
                    costo=costo,
                    stock=stock,
                    aplica_iva=aplica_iva,
                    categoria_id=categoria_id,
                )
            else:
                service.create_producto(
                    codigo, nombre, precio, costo, stock, aplica_iva, categoria_id
                )

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")


class CategoriaDialog(QDialog):
    """Diálogo para gestionar categorías"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Gestión de Categorías")
        self.setMinimumWidth(500)
        self.init_ui()
        self.cargar_categorias()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()

        btn_agregar = QPushButton("+ Agregar")
        btn_agregar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px;"
        )
        btn_agregar.clicked.connect(self.agregar_categoria)
        btn_layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 8px;"
        )
        btn_eliminar.clicked.connect(self.eliminar_categoria)
        btn_layout.addWidget(btn_eliminar)

        btn_layout.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

    def cargar_categorias(self):
        """Carga las categorías"""
        from services.producto_service import CategoriaService

        service = CategoriaService(self.session)
        cats = service.get_all()

        self.tabla.setRowCount(len(cats))
        for i, cat in enumerate(cats):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(cat.id)))
            self.tabla.setItem(i, 1, QTableWidgetItem(cat.nombre))
            self.tabla.setItem(i, 2, QTableWidgetItem(cat.descripcion or ""))

    def agregar_categoria(self):
        """Agrega una nueva categoría"""
        nombre, ok1 = QInputDialog.getText(self, "Nueva Categoría", "Nombre:")
        if not ok1 or not nombre.strip():
            return

        desc, ok2 = QInputDialog.getText(
            self, "Nueva Categoría", "Descripción (opcional):"
        )
        desc = desc.strip() if ok2 else ""

        try:
            from services.producto_service import CategoriaService

            service = CategoriaService(self.session)
            service.create(nombre.strip(), desc)
            self.cargar_categorias()
            QMessageBox.information(self, "Éxito", "Categoría creada")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def eliminar_categoria(self):
        """Elimina la categoría seleccionada"""
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una categoría")
            return

        cat_id = int(self.tabla.item(row, 0).text())
        cat_nombre = self.tabla.item(row, 1).text()

        resp = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar la categoría '{cat_nombre}'?"
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        try:
            from services.producto_service import CategoriaService

            service = CategoriaService(self.session)
            service.delete(cat_id)
            self.cargar_categorias()
            QMessageBox.information(self, "Éxito", "Categoría eliminada")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
