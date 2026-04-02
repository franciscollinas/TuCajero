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
    QDateEdit,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
import os
from tucajero.utils.formato import fmt_moneda
from tucajero.utils.theme import btn_primary, btn_success, btn_warning, btn_danger, btn_secondary


class ProductosView(QWidget):
    """Vista de gestión de productos"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_productos()

    def init_ui(self):
        """Inicializa la interfaz"""
        from tucajero.utils.theme import get_colors

        c = get_colors()
        self.setStyleSheet(f"background-color: {c['bg_app']};")

        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Productos")
        titulo.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {c['text_primary']};"
        )
        layout.addWidget(titulo)

        self.banner_stock = QWidget()
        self.banner_stock.setVisible(False)
        banner_layout = QHBoxLayout()
        self.banner_stock.setLayout(banner_layout)
        self.banner_stock.setStyleSheet(
            f"background-color: {c['warning']}; border-radius: 6px; padding: 8px;"
        )

        self.lbl_banner = QLabel("")
        self.lbl_banner.setStyleSheet(
            "color: white; font-weight: bold; font-size: 13px;"
        )
        banner_layout.addWidget(self.lbl_banner)

        btn_ver_bajos = QPushButton("Ver solo críticos")
        btn_ver_bajos.setStyleSheet(btn_secondary())
        btn_ver_bajos.clicked.connect(self.filtrar_stock_bajo)
        banner_layout.addWidget(btn_ver_bajos)

        btn_ver_todos = QPushButton("Ver todos")
        btn_ver_todos.setStyleSheet(btn_secondary())
        btn_ver_todos.clicked.connect(self.cargar_productos)
        banner_layout.addWidget(btn_ver_todos)

        layout.addWidget(self.banner_stock)

        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText(
            "🔍 Buscar producto por código o nombre..."
        )
        self.input_busqueda.setStyleSheet(
            f"padding: 10px; font-size: 14px; background: {c['bg_input']}; color: {c['text_primary']}; border: 1.5px solid {c['border']}; border-radius: 8px;"
        )
        self.input_busqueda.textChanged.connect(self.filtrar_productos)
        layout.addWidget(self.input_busqueda)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_agregar = QPushButton("+ Agregar Producto")
        btn_agregar.setStyleSheet(btn_primary())
        btn_agregar.clicked.connect(self.abrir_dialogo_agregar)
        btn_layout.addWidget(btn_agregar)

        btn_editar = QPushButton("Editar")
        btn_editar.setStyleSheet(btn_primary())
        btn_editar.clicked.connect(self.editar_producto)
        btn_layout.addWidget(btn_editar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(btn_danger())
        btn_eliminar.clicked.connect(self.eliminar_producto)
        btn_layout.addWidget(btn_eliminar)

        btn_categorias = QPushButton("Categorías")
        btn_categorias.setStyleSheet(btn_primary())
        btn_categorias.clicked.connect(self.abrir_gestor_categorias)
        btn_layout.addWidget(btn_categorias)

        btn_importar = QPushButton("⬆ Importar Excel/CSV")
        btn_importar.setStyleSheet(btn_primary())
        btn_importar.clicked.connect(self.importar_productos)
        btn_layout.addWidget(btn_importar)

        layout.addLayout(btn_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Código", "Nombre", "Stock", "Precio"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: {c["bg_card"]};
                border: 1px solid {c["border"]};
                border-radius: 8px;
                gridline-color: {c["border"]};
                font-size: 14px;
                color: {c["text_primary"]};
            }}
            QHeaderView::section {{
                background-color: {c["bg_input"]};
                color: {c["text_muted"]};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {c["border"]};
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {c["border"]};
            }}
        """)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()

        btn_entrada = QPushButton("+ Entrada")
        btn_entrada.setStyleSheet(btn_primary())
        btn_entrada.clicked.connect(lambda: self.movimiento_inventario("entrada"))
        btn_layout.addWidget(btn_entrada)

        btn_salida = QPushButton("- Salida")
        btn_salida.setStyleSheet(btn_danger())
        btn_salida.clicked.connect(lambda: self.movimiento_inventario("salida"))
        btn_layout.addWidget(btn_salida)

        self.btn_desempacar = QPushButton("💊 Desempacar")
        self.btn_desempacar.setStyleSheet(btn_primary())
        self.btn_desempacar.setToolTip(
            "Convierte cajas/empaques en unidades individuales"
        )
        self.btn_desempacar.clicked.connect(self.desempacar_producto)
        btn_layout.addWidget(self.btn_desempacar)

        btn_layout.addStretch()

        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.setStyleSheet(btn_secondary())
        btn_actualizar.clicked.connect(self.cargar_productos)
        btn_layout.addWidget(btn_actualizar)

        layout.addLayout(btn_layout)

    def cargar_productos(self):
        """Carga los productos desde la base de datos"""
        from tucajero.utils.theme import get_colors

        c = get_colors()

        from tucajero.services.producto_service import ProductoService

        service = ProductoService(self.session)
        productos = service.get_all_productos()
        self.productos = productos

        bajos = service.get_productos_stock_bajo()
        criticos = service.get_productos_stock_critico()
        total_alertas = len(set([p.id for p in bajos + criticos]))

        if total_alertas > 0:
            self.banner_stock.setVisible(True)
            critico_txt = f" ({len(criticos)} sin stock)" if criticos else ""
            self.lbl_banner.setText(
                f"⚠  {total_alertas} producto(s) con stock bajo{critico_txt}"
            )
            if len(criticos) > 0:
                self.banner_stock.setStyleSheet(
                    f"background-color: {c['danger']}; border-radius: 6px; padding: 8px;"
                )
                self.lbl_banner.setStyleSheet(
                    f"color: white; font-weight: bold; font-size: 13px;"
                )
        else:
            self.banner_stock.setVisible(False)

        self._mostrar_productos(productos)

    def _mostrar_productos(self, productos):
        """Muestra la lista de productos en la tabla"""
        from tucajero.utils.theme import get_colors
        
        c = get_colors()
        self.tabla.setRowCount(len(productos))

        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.nombre))

            stock_minimo = p.stock_minimo or 0
            stock_item = QTableWidgetItem(str(p.stock))

            if p.stock <= 0:
                stock_item.setBackground(QColor(c["danger"]))
                stock_item.setForeground(QColor("white"))
            elif stock_minimo > 0 and p.stock <= stock_minimo:
                stock_item.setBackground(QColor(c["warning"]))
                stock_item.setForeground(QColor("white"))
            elif stock_minimo > 0 and p.stock <= stock_minimo * 2:
                stock_item.setBackground(QColor(c["info"]))
                stock_item.setForeground(QColor("white"))

            self.tabla.setItem(i, 2, stock_item)
            self.tabla.setItem(i, 3, QTableWidgetItem(fmt_moneda(p.precio)))

    def filtrar_productos(self, texto):
        """Filtra productos por código o nombre"""
        if not texto:
            self._mostrar_productos(self.productos)
            return

        texto_lower = texto.lower()
        filtrados = [
            p
            for p in self.productos
            if texto_lower in p.codigo.lower() or texto_lower in p.nombre.lower()
        ]
        self._mostrar_productos(filtrados)

    def filtrar_stock_bajo(self):
        """Muestra solo productos con stock bajo o crítico"""
        from tucajero.services.producto_service import ProductoService

        service = ProductoService(self.session)
        bajos = service.get_productos_stock_bajo()
        criticos = service.get_productos_stock_critico()
        productos = list({p.id: p for p in bajos + criticos}.values())
        self._mostrar_productos(productos)

    def obtener_producto_seleccionado(self):
        """Retorna el producto seleccionado"""
        row = self.tabla.currentRow()
        if row >= 0:
            item = self.tabla.item(row, 0)
            if item is not None:
                codigo = item.text()
                from tucajero.services.producto_service import ProductoService

                service = ProductoService(self.session)
                return service.get_producto_by_codigo(codigo)
        return None

    def movimiento_inventario(self, tipo):
        """Abre el diálogo para registrar movimiento"""
        producto = self.obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        dialog = MovimientoDialog(self.session, producto, tipo, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_productos()

    def desempacar_producto(self):
        """Desempaca el producto seleccionado"""
        producto = self.obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return
        if not producto.producto_fraccion_id:
            QMessageBox.warning(
                self,
                "No fraccionable",
                "Este producto no tiene un producto unitario vinculado.\n"
                "Para configurarlo, edita el producto.",
            )
            return
        dialog = DesempaqueDialog(self.session, producto, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_productos()

    def recargar_productos(self):
        """Recarga los productos (para auto-actualizacion despues de venta)"""
        self.cargar_productos()

    def abrir_dialogo_agregar(self):
        """Abre el diálogo para agregar un producto"""
        dialog = ProductoDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_productos()

    def editar_producto(self):
        """Abre el diálogo para editar un producto"""
        producto = self.obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        dialog = ProductoDialog(self.session, self, producto.id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_productos()

    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        producto = self.obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de eliminar este producto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            from tucajero.services.producto_service import ProductoService

            service = ProductoService(self.session)
            service.delete_producto(producto.id)
            self.cargar_productos()

    def abrir_gestor_categorias(self):
        """Abre el diálogo de gestión de categorías"""
        dialog = CategoriaDialog(self.session, self)
        dialog.exec()
        self.cargar_productos()

    def importar_productos(self):
        from PySide6.QtWidgets import QFileDialog
        from tucajero.utils.importador import leer_archivo

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo",
            os.path.expanduser("~"),
            "Excel/CSV (*.xlsx *.xls *.csv)",
        )
        if not filepath:
            return
        try:
            filas = leer_archivo(filepath)
            if not filas:
                QMessageBox.warning(self, "Vacío", "El archivo no tiene datos.")
                return
            dialog = ImportPreviewDialog(filas, filepath, self.session, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.cargar_productos()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer:\n{e}")


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
        from tucajero.utils.theme import get_colors

        c = get_colors()
        self.setStyleSheet(f"""
            QDialog {{ background-color: {c["bg_app"]}; }}
            QLabel {{ color: {c["text_primary"]}; }}
            QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {{ 
                background-color: {c["bg_input"]}; 
                color: {c["text_primary"]};
                border: 1px solid {c["border"]};
                padding: 5px;
            }}
            QLabel#separador {{ color: {c["text_muted"]}; font-weight: bold; margin-top: 10px; }}
        """)

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

        self.stock_min_input = QSpinBox()
        self.stock_min_input.setRange(0, 999999)
        self.stock_min_input.setToolTip(
            "El sistema alertará cuando el stock llegue a esta cantidad.\n"
            "Pon 0 para desactivar la alerta."
        )
        layout.addRow("Stock mínimo:", self.stock_min_input)

        separador = QLabel("── Fraccionamiento ──")
        separador.setObjectName("separador")
        layout.addRow("", separador)

        self.chk_fraccionable = QCheckBox("¿Este producto se vende por unidades?")
        self.chk_fraccionable.toggled.connect(self.on_fraccionable_changed)
        layout.addRow("", self.chk_fraccionable)

        self.fraccion_widget = QWidget()
        fraccion_layout = QFormLayout()
        self.fraccion_widget.setLayout(fraccion_layout)
        self.fraccion_widget.setVisible(False)

        self.und_por_empaque = QSpinBox()
        self.und_por_empaque.setRange(2, 10000)
        self.und_por_empaque.setValue(10)
        fraccion_layout.addRow("Unidades por empaque:", self.und_por_empaque)

        self.btn_crear_fraccion = QPushButton(
            "✨ Crear producto unitario automáticamente"
        )
        self.btn_crear_fraccion.setStyleSheet(btn_primary())
        self.btn_crear_fraccion.clicked.connect(self.crear_fraccion_automatica)
        fraccion_layout.addRow("", self.btn_crear_fraccion)

        self.lbl_fraccion_info = QLabel("")
        self.lbl_fraccion_info.setStyleSheet(f"color: {c['success']}; font-size: 12px;")
        fraccion_layout.addRow("", self.lbl_fraccion_info)

        layout.addRow("", self.fraccion_widget)

        cat_layout = QHBoxLayout()
        self.cat_combo = QComboBox()
        self.cat_combo.addItem("Sin categoría", None)
        self._cargar_categorias()
        cat_layout.addWidget(self.cat_combo)

        btn_nueva_cat = QPushButton("+")
        btn_nueva_cat.setFixedWidth(40)
        btn_nueva_cat.setStyleSheet(btn_secondary() + " padding: 0px; min-height: 0px;")
        btn_nueva_cat.setToolTip("Crear nueva categoría")
        btn_nueva_cat.clicked.connect(self._crear_categoria_rapida)
        cat_layout.addWidget(btn_nueva_cat)

        layout.addRow("Categoría:", cat_layout)

        self.aplica_iva = QCheckBox("Aplica IVA (19%)")
        self.aplica_iva.setChecked(True)
        layout.addRow("", self.aplica_iva)

        self.fecha_vencimiento = QDateEdit()
        self.fecha_vencimiento.setCalendarPopup(True)
        self.fecha_vencimiento.setDate(QDate.currentDate())
        self.fecha_vencimiento.setMinimumDate(QDate.currentDate())  # No permitir fechas pasadas
        self.fecha_vencimiento.setDisplayFormat("yyyy-MM-dd")
        self.fecha_vencimiento.setToolTip(
            "Fecha de vencimiento del producto (no se permiten fechas en el pasado)"
        )
        layout.addRow("Vencimiento:", self.fecha_vencimiento)

        btn_layout = QHBoxLayout()

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet(btn_primary())
        btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_guardar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(btn_secondary())
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        layout.addRow("", btn_layout)

    def _cargar_categorias(self):
        """Carga las categorías en el combo"""
        self.cat_combo.clear()
        self.cat_combo.addItem("Sin categoría", None)
        from tucajero.services.producto_service import CategoriaService

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
                from tucajero.services.producto_service import CategoriaService

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

    def on_fraccionable_changed(self, checked):
        self.fraccion_widget.setVisible(checked)

    def crear_fraccion_automatica(self):
        und = self.und_por_empaque.value()
        precio = self.precio_input.value()
        precio_und = round(precio / und, 2)
        nombre = self.nombre_input.text().strip()
        self.lbl_fraccion_info.setText(
            f"✓ Se creará: '{nombre} (und)' a ${precio_und:,.2f} c/u"
        )

    def cargar_producto(self):
        """Carga los datos del producto a editar"""
        from tucajero.services.producto_service import ProductoService

        service = ProductoService(self.session)
        producto = service.get_producto_by_id(self.producto_id)

        if producto:
            self.codigo_input.setText(producto.codigo)
            self.nombre_input.setText(producto.nombre)
            self.precio_input.setValue(producto.precio)
            self.costo_input.setValue(producto.costo)
            self.stock_input.setValue(producto.stock)
            self.stock_min_input.setValue(producto.stock_minimo or 0)
            self.aplica_iva.setChecked(producto.aplica_iva)

            if producto.fecha_vencimiento:
                self.fecha_vencimiento.setDate(
                    QDate(
                        producto.fecha_vencimiento.year,
                        producto.fecha_vencimiento.month,
                        producto.fecha_vencimiento.day,
                    )
                )
            else:
                self.fecha_vencimiento.setDate(QDate(2099, 12, 31))

            if producto.categoria_id:
                for i in range(self.cat_combo.count()):
                    if self.cat_combo.currentData() == producto.categoria_id:
                        self.cat_combo.setCurrentIndex(i)
                        break

            if producto.unidades_por_empaque:
                self.chk_fraccionable.setChecked(True)
                self.und_por_empaque.setValue(producto.unidades_por_empaque)
                if producto.producto_fraccion:
                    precio_und = producto.producto_fraccion.precio
                    self.lbl_fraccion_info.setText(
                        f"✓ Vinculado: '{producto.producto_fraccion.nombre}' a ${precio_und:,.2f} c/u"
                    )

    def guardar(self):
        """Guarda el producto"""
        from tucajero.services.producto_service import ProductoService
        from PySide6.QtCore import QDate

        codigo = self.codigo_input.text().strip()
        nombre = self.nombre_input.text().strip()
        precio = self.precio_input.value()
        costo = self.costo_input.value()
        stock = self.stock_input.value()
        stock_minimo = self.stock_min_input.value()
        aplica_iva = self.aplica_iva.isChecked()
        categoria_id = self.cat_combo.currentData()

        if not codigo or not nombre:
            QMessageBox.warning(self, "Error", "Código y nombre son requeridos")
            return

        # Validar fecha de vencimiento no esté en el pasado
        fecha_seleccionada = self.fecha_vencimiento.date()
        if fecha_seleccionada < QDate.currentDate():
            QMessageBox.warning(
                self,
                "Fecha inválida",
                "La fecha de vencimiento no puede estar en el pasado.\n\n"
                "Por favor seleccione una fecha futura o deje la fecha actual."
            )
            return

        service = ProductoService(self.session)

        fecha_vencimiento = fecha_seleccionada.toPython()
        # Si la fecha es muy lejana (2099), se considera como sin vencimiento
        if fecha_vencimiento.year == 2099:
            fecha_vencimiento = None

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
                    stock_minimo=stock_minimo,
                    fecha_vencimiento=fecha_vencimiento,
                )
                producto_guardado = service.get_producto_by_id(self.producto_id)
            else:
                producto_guardado = service.create_producto(
                    codigo,
                    nombre,
                    precio,
                    costo,
                    stock,
                    aplica_iva,
                    categoria_id,
                    stock_minimo,
                    fecha_vencimiento=fecha_vencimiento,
                )

            if self.chk_fraccionable.isChecked() and producto_guardado:
                from tucajero.services.fraccion_service import FraccionService

                frac_service = FraccionService(self.session)
                if self.producto_id:
                    if producto_guardado.unidades_por_empaque:
                        unidades = self.und_por_empaque.value()
                        if producto_guardado.unidades_por_empaque != unidades:
                            producto_guardado.unidades_por_empaque = unidades
                            self.session.commit()
                    if not producto_guardado.producto_fraccion_id:
                        frac_service.crear_producto_fraccion(
                            producto_guardado.id, self.und_por_empaque.value()
                        )
                        QMessageBox.information(
                            self,
                            "Éxito",
                            "Producto fraccionario creado automáticamente",
                        )
                else:
                    frac_service.crear_producto_fraccion(
                        producto_guardado.id, self.und_por_empaque.value()
                    )
                    QMessageBox.information(
                        self, "Éxito", "Producto fraccionario creado automáticamente"
                    )

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")


class MovimientoDialog(QDialog):
    """Diálogo para registrar movimientos de inventario"""

    def __init__(self, session, producto, tipo, parent=None):
        super().__init__(parent)
        self.session = session
        self.producto = producto
        self.tipo = tipo
        from tucajero.utils.theme import get_colors

        c = get_colors()
        self.setWindowTitle(
            f"{'Entrada' if tipo == 'entrada' else 'Salida'} de Inventario"
        )

    def init_ui(self, color):
        from tucajero.utils.theme import get_colors

        c = get_colors()
        self.setStyleSheet(f"""
            QDialog {{ background-color: {c["bg_app"]}; }}
            QLabel {{ color: {c["text_primary"]}; }}
            QSpinBox {{ 
                background-color: {c["bg_input"]}; 
                color: {c["text_primary"]};
                border: 1px solid {c["border"]};
                padding: 5px;
            }}
        """)
        layout = QFormLayout()
        self.setLayout(layout)

        info_box = QWidget()
        info_box.setStyleSheet(
            f"background-color: {c['bg_card']}; padding: 10px; border-radius: 5px; border: 1px solid {c['border']};"
        )
        info_layout = QVBoxLayout()
        info_box.setLayout(info_layout)

        info_layout.addWidget(QLabel(f"<b>Producto:</b> {self.producto.nombre}"))
        info_layout.addWidget(QLabel(f"<b>Código:</b> {self.producto.codigo}"))
        info_layout.addWidget(QLabel(f"<b>Stock actual:</b> {self.producto.stock}"))

        layout.addRow("", info_box)

        self.cantidad_input = QSpinBox()
        self.cantidad_input.setRange(1, 999999)
        self.cantidad_input.setStyleSheet(
            f"padding: 8px; font-size: 16px; background-color: {c['bg_input']}; color: {c['text_primary']}; border: 1.5px solid {c['border']};"
        )
        self.cantidad_input.setFocus()
        layout.addRow("Cantidad:", self.cantidad_input)

        btn_layout = QHBoxLayout()

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet(btn_primary())
        btn_aceptar.clicked.connect(self.aceptar)
        btn_layout.addWidget(btn_aceptar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(btn_secondary())
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        layout.addRow("", btn_layout)

    def aceptar(self):
        from tucajero.services.producto_service import InventarioService

        cantidad = self.cantidad_input.value()

        if cantidad <= 0:
            QMessageBox.warning(self, "Error", "Cantidad inválida")
            return

        try:
            service = InventarioService(self.session)
            if self.tipo == "entrada":
                service.entrada_inventario(self.producto.id, cantidad)
            else:
                service.salida_inventario(self.producto.id, cantidad)

            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class DesempaqueDialog(QDialog):
    def __init__(self, session, producto, parent=None):
        super().__init__(parent)
        from tucajero.utils.theme import get_colors

        c = get_colors()
        self.session = session
        self.producto = producto
        self.setWindowTitle("Desempacar producto")
        self.setMinimumWidth(420)
        self.setStyleSheet(
            f"QDialog {{ background-color: {c['bg_app']}; }} QLabel {{ color: {c['text_primary']}; }}"
        )
        layout = QVBoxLayout()
        self.setLayout(layout)

        from tucajero.models.producto import Producto

        hijo = session.query(Producto).get(producto.producto_fraccion_id)
        und = producto.unidades_por_empaque or 1

        info = QWidget()
        info.setStyleSheet(
            f"background:{c['bg_card']};padding:12px;border-radius:6px; border: 1px solid {c['border']};"
        )
        info_layout = QVBoxLayout()
        info.setLayout(info_layout)
        info_layout.addWidget(QLabel(f"<b>Empaque:</b> {producto.nombre}"))
        info_layout.addWidget(QLabel(f"<b>Stock actual (cajas):</b> {producto.stock}"))
        info_layout.addWidget(QLabel(f"<b>Unidades por caja:</b> {und}"))
        info_layout.addWidget(
            QLabel(f"<b>Producto unitario:</b> {hijo.nombre if hijo else '?'}")
        )
        info_layout.addWidget(
            QLabel(f"<b>Stock actual (unidades):</b> {hijo.stock if hijo else 0}")
        )
        layout.addWidget(info)

        form = QFormLayout()
        self.spin_cajas = QSpinBox()
        self.spin_cajas.setRange(1, producto.stock or 1)
        self.spin_cajas.setValue(1)
        self.spin_cajas.setStyleSheet(
            f"background-color: {c['bg_input']}; color: {c['text_primary']}; border: 1px solid {c['border']}; font-size:16px;padding:8px;"
        )
        self.spin_cajas.valueChanged.connect(self.actualizar_preview)
        form.addRow("¿Cuántas cajas desempacar?", self.spin_cajas)
        layout.addLayout(form)

        self.lbl_preview = QLabel("")
        self.lbl_preview.setStyleSheet(
            f"font-size:14px;color:{c['success']};font-weight:bold;padding:8px;"
        )
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_preview)
        self.actualizar_preview()

        btns = QHBoxLayout()
        btn_ok = QPushButton("✓ CONFIRMAR DESEMPAQUE")
        btn_ok.setStyleSheet(btn_primary())
        btn_ok.clicked.connect(self.confirmar)
        btns.addWidget(btn_ok)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(btn_secondary())
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def actualizar_preview(self):
        cajas = self.spin_cajas.value()
        und = self.producto.unidades_por_empaque or 1
        unidades = cajas * und
        self.lbl_preview.setText(f"{cajas} caja(s) → {unidades} unidades")

    def confirmar(self):
        from tucajero.services.fraccion_service import FraccionService

        try:
            resultado = FraccionService(self.session).desempacar(
                self.producto.id, self.spin_cajas.value()
            )
            QMessageBox.information(
                self,
                "Desempaque exitoso",
                f"✓ {resultado['cajas_descontadas']} caja(s) desempacada(s)\n"
                f"✓ {resultado['unidades_agregadas']} unidades agregadas\n\n"
                f"Stock empaque: {resultado['stock_padre']} cajas\n"
                f"Stock unidades: {resultado['stock_hijo']} und",
            )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    # --- Se movieron los métodos a ProductoDialog más abajo ---

    def __init__(self, filas, filepath, session, parent=None):
        super().__init__(parent)
        from tucajero.utils.theme import get_colors

        c = get_colors()
        self.filas = filas
        self.filepath = filepath
        self.session = session
        self.setWindowTitle("Vista previa — Importar productos")
        self.setMinimumSize(750, 520)
        self.setStyleSheet(
            f"QDialog {{ background-color: {c['bg_app']}; }} QLabel {{ color: {c['text_primary']}; }}"
        )
        layout = QVBoxLayout()
        self.setLayout(layout)

        info = QLabel(
            f"📄  {len(self.filas)} filas detectadas  |  {os.path.basename(filepath)}"
        )
        info.setStyleSheet(
            f"font-size:13px;padding:8px;background:{c['bg_card']};color:{c['text_primary']};border-radius:4px; border: 1px solid {c['border']};"
        )
        layout.addWidget(info)

        headers = list(self.filas[0].keys()) if self.filas else []
        preview = self.filas[:20]
        tabla = QTableWidget(len(preview), len(headers))
        tabla.setHorizontalHeaderLabels(headers)
        tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for i, fila in enumerate(preview):
            for j, key in enumerate(headers):
                val = fila.get(key, "") or ""
                if key in ("precio", "costo"):
                    val = fmt_moneda(val)
                tabla.setItem(i, j, QTableWidgetItem(str(val)))
        layout.addWidget(tabla)

        if len(self.filas) > 20:
            nota = QLabel(f"⚠ Mostrando 20 de {len(self.filas)} filas")
            nota.setStyleSheet("color:#e67e22;font-size:12px;padding:4px;")
            layout.addWidget(nota)

        btns = QHBoxLayout()
        btn_imp = QPushButton("⬆ IMPORTAR TODO")
        btn_imp.setStyleSheet(btn_primary())
        btn_imp.clicked.connect(self.ejecutar)
        btns.addWidget(btn_imp)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(btn_secondary())
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def ejecutar(self):
        from tucajero.utils.importador import importar_productos

        try:
            r = importar_productos(self.filepath, self.session)
            msg = (
                f"✅ Importación completada:\n\n"
                f"• Productos nuevos: {r['importados']}\n"
                f"• Actualizados: {r['actualizados']}\n"
                f"• Errores: {len(r['errores'])}"
            )
            if r["errores"]:
                msg += "\n\nPrimeros errores:\n"
                for e in r["errores"][:5]:
                    msg += f"  Fila {e['fila']}: {e['msg']}\n"
            QMessageBox.information(self, "Importación completada", msg)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error al importar", str(e))


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
        from tucajero.utils.theme import get_colors

        c = get_colors()
        self.setStyleSheet(
            f"QDialog {{ background-color: {c['bg_app']}; }} QLabel {{ color: {c['text_primary']}; }}"
        )

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
        btn_agregar.setStyleSheet(btn_primary())
        btn_agregar.clicked.connect(self.agregar_categoria)
        btn_layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(btn_danger())
        btn_eliminar.clicked.connect(self.eliminar_categoria)
        btn_layout.addWidget(btn_eliminar)

        btn_layout.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(btn_secondary())
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

    def cargar_categorias(self):
        """Carga las categorías"""
        from tucajero.services.producto_service import CategoriaService

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
            from tucajero.services.producto_service import CategoriaService

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
            from tucajero.services.producto_service import CategoriaService

            service = CategoriaService(self.session)
            service.delete(cat_id)
            self.cargar_categorias()
            QMessageBox.information(self, "Éxito", "Categoría eliminada")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
