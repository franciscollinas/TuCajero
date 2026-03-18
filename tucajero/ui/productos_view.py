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
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


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

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        tab_productos = QWidget()
        tab_prod_layout = QVBoxLayout()
        tab_productos.setLayout(tab_prod_layout)

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
        tab_prod_layout.addLayout(btn_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Código", "Nombre", "Precio", "Stock", "Categorías"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet("font-size: 14px;")
        tab_prod_layout.addWidget(self.tabla)
        self.tabs.addTab(tab_productos, "📦  Productos")

        tab_categorias = QWidget()
        tab_cat_layout = QVBoxLayout()
        tab_categorias.setLayout(tab_cat_layout)

        cat_btn_layout = QHBoxLayout()
        btn_nueva_cat = QPushButton("+ Nueva Categoría")
        btn_nueva_cat.setStyleSheet(
            "background-color: #8e44ad; color: white; padding: 10px;"
        )
        btn_nueva_cat.clicked.connect(self.crear_categoria)
        cat_btn_layout.addWidget(btn_nueva_cat)
        btn_editar_cat = QPushButton("Renombrar")
        btn_editar_cat.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px;"
        )
        btn_editar_cat.clicked.connect(self.renombrar_categoria)
        cat_btn_layout.addWidget(btn_editar_cat)
        btn_eliminar_cat = QPushButton("Eliminar")
        btn_eliminar_cat.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px;"
        )
        btn_eliminar_cat.clicked.connect(self.eliminar_categoria)
        cat_btn_layout.addWidget(btn_eliminar_cat)
        cat_btn_layout.addStretch()
        tab_cat_layout.addLayout(cat_btn_layout)

        self.tabla_categorias = QTableWidget()
        self.tabla_categorias.setColumnCount(3)
        self.tabla_categorias.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Productos asignados"]
        )
        self.tabla_categorias.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_categorias.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_categorias.setStyleSheet("font-size: 14px;")
        tab_cat_layout.addWidget(self.tabla_categorias)
        self.tabs.addTab(tab_categorias, "🏷️  Categorías")

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
            cats = ", ".join(c.nombre for c in p.categorias) if p.categorias else "—"
            self.tabla.setItem(i, 5, QTableWidgetItem(cats))

        self._cargar_tabla_categorias()

    def _cargar_tabla_categorias(self):
        from services.categoria_service import CategoriaService

        service = CategoriaService(self.session)
        cats = service.get_all()
        self.tabla_categorias.setRowCount(len(cats))
        for i, c in enumerate(cats):
            self.tabla_categorias.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.tabla_categorias.setItem(i, 1, QTableWidgetItem(c.nombre))
            num = len([p for p in c.productos if p.activo])
            self.tabla_categorias.setItem(i, 2, QTableWidgetItem(str(num)))

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

    def crear_categoria(self):
        from PySide6.QtWidgets import QInputDialog

        nombre, ok = QInputDialog.getText(
            self,
            "Nueva Categoría",
            "Nombre de la categoría (ej: Antibióticos, Vitaminas):",
        )
        if ok and nombre.strip():
            try:
                from services.categoria_service import CategoriaService

                CategoriaService(self.session).crear(nombre)
                self.cargar_productos()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def renombrar_categoria(self):
        from PySide6.QtWidgets import QInputDialog

        row = self.tabla_categorias.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una categoría")
            return
        cat_id = int(self.tabla_categorias.item(row, 0).text())
        nombre_actual = self.tabla_categorias.item(row, 1).text()
        nuevo, ok = QInputDialog.getText(
            self, "Renombrar Categoría", "Nuevo nombre:", text=nombre_actual
        )
        if ok and nuevo.strip():
            try:
                from services.categoria_service import CategoriaService

                CategoriaService(self.session).renombrar(cat_id, nuevo)
                self.cargar_productos()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def eliminar_categoria(self):
        row = self.tabla_categorias.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una categoría")
            return
        cat_id = int(self.tabla_categorias.item(row, 0).text())
        nombre = self.tabla_categorias.item(row, 1).text()
        resp = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar la categoría '{nombre}'?\nLos productos no serán eliminados.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            from services.categoria_service import CategoriaService

            CategoriaService(self.session).eliminar(cat_id)
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

        from services.categoria_service import CategoriaService

        self.cat_service = CategoriaService(self.session)
        cats = self.cat_service.get_all()

        cat_label = QLabel("Categorías:")
        layout.addRow(cat_label)

        self.lista_categorias = QListWidget()
        self.lista_categorias.setSelectionMode(
            QAbstractItemView.SelectionMode.MultiSelection
        )
        self.lista_categorias.setMaximumHeight(120)
        self.lista_categorias.setStyleSheet("font-size: 13px;")
        for cat in cats:
            item = QListWidgetItem(f"🏷 {cat.nombre}")
            item.setData(Qt.ItemDataRole.UserRole, cat.id)
            self.lista_categorias.addItem(item)
        layout.addRow("", self.lista_categorias)

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

            if producto.categorias:
                cat_ids = {c.id for c in producto.categorias}
                for i in range(self.lista_categorias.count()):
                    item = self.lista_categorias.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) in cat_ids:
                        item.setSelected(True)

    def guardar(self):
        """Guarda el producto"""
        from services.producto_service import ProductoService

        codigo = self.codigo_input.text().strip()
        nombre = self.nombre_input.text().strip()
        precio = self.precio_input.value()
        costo = self.costo_input.value()
        stock = self.stock_input.value()

        if not codigo or not nombre:
            QMessageBox.warning(self, "Error", "Código y nombre son requeridos")
            return

        service = ProductoService(self.session)

        try:
            producto = None
            if self.producto_id:
                service.update_producto(
                    self.producto_id,
                    codigo=codigo,
                    nombre=nombre,
                    precio=precio,
                    costo=costo,
                    stock=stock,
                )
                producto_id_guardar = self.producto_id
            else:
                producto = service.create_producto(codigo, nombre, precio, costo, stock)
                producto_id_guardar = producto.id

            cat_ids = []
            for i in range(self.lista_categorias.count()):
                item = self.lista_categorias.item(i)
                if item.isSelected():
                    cat_ids.append(item.data(Qt.ItemDataRole.UserRole))
            from services.categoria_service import CategoriaService

            CategoriaService(self.session).asignar_a_producto(
                producto_id_guardar, cat_ids
            )

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
