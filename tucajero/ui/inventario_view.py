from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QDialog,
    QFormLayout,
    QSpinBox,
    QHeaderView,
    QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from utils.formato import fmt_moneda


class InventarioView(QWidget):
    """Vista de inventario"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.productos = []
        self.init_ui()
        self.cargar_inventario()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Inventario")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        info_label = QLabel("Seleccione un producto y elija Entrada o Salida")
        info_label.setObjectName("info_label")
        layout.addWidget(info_label)

        self.banner_stock = QWidget()
        self.banner_stock.setVisible(False)
        banner_layout = QHBoxLayout()
        self.banner_stock.setLayout(banner_layout)
        self.banner_stock.setStyleSheet(
            "background-color: #e67e22; border-radius: 6px; padding: 8px;"
        )

        self.lbl_banner = QLabel("")
        self.lbl_banner.setStyleSheet(
            "color: white; font-weight: bold; font-size: 13px;"
        )
        banner_layout.addWidget(self.lbl_banner)

        self.btn_ver_bajos = QPushButton("Ver solo productos críticos")
        self.btn_ver_bajos.setStyleSheet(
            "background: white; color: #e67e22; "
            "font-weight: bold; padding: 4px 10px; border-radius: 4px;"
        )
        self.btn_ver_bajos.clicked.connect(self.filtrar_stock_bajo)
        banner_layout.addWidget(self.btn_ver_bajos)

        self.btn_ver_todos = QPushButton("Ver todos")
        self.btn_ver_todos.setStyleSheet(
            "background: rgba(255,255,255,0.3); color: white; "
            "padding: 4px 10px; border-radius: 4px;"
        )
        self.btn_ver_todos.clicked.connect(self.cargar_inventario)
        banner_layout.addWidget(self.btn_ver_todos)

        layout.addWidget(self.banner_stock)

        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText(
            "🔍 Buscar producto por código o nombre..."
        )
        self.input_busqueda.setStyleSheet("padding: 10px; font-size: 14px;")
        self.input_busqueda.textChanged.connect(self.filtrar_productos)
        layout.addWidget(self.input_busqueda)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Código", "Producto", "Stock", "Precio"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet("font-size: 14px;")
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tabla.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()

        btn_entrada = QPushButton("+ Entrada")
        btn_entrada.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 12px; font-weight: bold;"
        )
        btn_entrada.clicked.connect(lambda: self.movimiento_inventario("entrada"))
        btn_layout.addWidget(btn_entrada)

        btn_salida = QPushButton("- Salida")
        btn_salida.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 12px; font-weight: bold;"
        )
        btn_salida.clicked.connect(lambda: self.movimiento_inventario("salida"))
        btn_layout.addWidget(btn_salida)

        self.btn_desempacar = QPushButton("💊 Desempacar")
        self.btn_desempacar.setStyleSheet(
            "background-color: #2980b9; color: white; padding: 12px; font-weight: bold;"
        )
        self.btn_desempacar.setToolTip(
            "Convierte cajas/empaques en unidades individuales"
        )
        self.btn_desempacar.clicked.connect(self.desempacar_producto)
        btn_layout.addWidget(self.btn_desempacar)

        btn_layout.addStretch()

        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px;"
        )
        btn_actualizar.clicked.connect(self.cargar_inventario)
        btn_layout.addWidget(btn_actualizar)

        layout.addLayout(btn_layout)

    def cargar_inventario(self):
        """Carga el inventario desde la base de datos"""
        from services.producto_service import InventarioService, ProductoService

        service = InventarioService(self.session)
        productos = service.get_all_productos()
        self.productos = productos

        service_check = ProductoService(self.session)
        bajos = service_check.get_productos_stock_bajo()
        criticos = service_check.get_productos_stock_critico()
        total_alertas = len(set([p.id for p in bajos + criticos]))

        if total_alertas > 0:
            self.banner_stock.setVisible(True)
            critico_txt = f" ({len(criticos)} sin stock)" if criticos else ""
            self.lbl_banner.setText(
                f"⚠  {total_alertas} producto(s) con stock bajo{critico_txt}"
            )
            if len(criticos) > 0:
                self.banner_stock.setStyleSheet(
                    "background-color: #e74c3c; border-radius: 6px; padding: 8px;"
                )
                self.lbl_banner.setStyleSheet(
                    "color: white; font-weight: bold; font-size: 13px;"
                )
        else:
            self.banner_stock.setVisible(False)

        self._mostrar_productos(productos)

    def _mostrar_productos(self, productos):
        """Muestra la lista de productos en la tabla"""
        self.tabla.setRowCount(len(productos))

        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.nombre))

            stock_minimo = p.stock_minimo or 0
            stock_item = QTableWidgetItem(str(p.stock))

            if p.stock <= 0:
                stock_item.setBackground(QColor("#e74c3c"))
                stock_item.setForeground(QColor("white"))
            elif stock_minimo > 0 and p.stock <= stock_minimo:
                stock_item.setBackground(QColor("#e67e22"))
                stock_item.setForeground(QColor("white"))
            elif stock_minimo > 0 and p.stock <= stock_minimo * 2:
                stock_item.setBackground(QColor("#f39c12"))
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

    def recargar_inventario(self):
        """Recarga el inventario (para auto-actualizacion despues de venta)"""
        self.cargar_inventario()

    def obtener_producto_seleccionado(self):
        """Retorna el ID del producto seleccionado"""
        row = self.tabla.currentRow()
        if row >= 0:
            item = self.tabla.item(row, 0)
            if item is not None:
                codigo = item.text()
                from services.producto_service import ProductoService

                service = ProductoService(self.session)
                producto = service.get_producto_by_codigo(codigo)
                return producto
        return None

    def movimiento_inventario(self, tipo):
        """Abre el diálogo para registrar movimiento"""
        producto = self.obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        dialog = MovimientoDialog(self.session, producto, tipo, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_inventario()

    def desempacar_producto(self):
        producto = self.obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return
        if not producto.producto_fraccion_id:
            QMessageBox.warning(
                self,
                "No fraccionable",
                "Este producto no tiene un producto unitario vinculado.\n"
                "Para configurarlo, edita el producto en la sección Productos.",
            )
            return
        dialog = DesempaqueDialog(self.session, producto, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_inventario()

    def filtrar_stock_bajo(self):
        """Muestra solo productos con stock bajo o crítico"""
        from services.producto_service import ProductoService

        service = ProductoService(self.session)
        bajos = service.get_productos_stock_bajo()
        criticos = service.get_productos_stock_critico()
        productos = list({p.id: p for p in bajos + criticos}.values())

        self.tabla.setRowCount(len(productos))
        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.nombre))
            stock_item = QTableWidgetItem(str(p.stock))
            if p.stock <= 0:
                stock_item.setBackground(QColor("#e74c3c"))
                stock_item.setForeground(QColor("white"))
            else:
                stock_item.setBackground(QColor("#e67e22"))
                stock_item.setForeground(QColor("white"))
            self.tabla.setItem(i, 2, stock_item)
            self.tabla.setItem(i, 3, QTableWidgetItem(f"${p.precio:,.2f}"))


class MovimientoDialog(QDialog):
    """Diálogo para registrar movimientos de inventario"""

    def __init__(self, session, producto, tipo, parent=None):
        super().__init__(parent)
        self.session = session
        self.producto = producto
        self.tipo = tipo
        color = "#27ae60" if tipo == "entrada" else "#e74c3c"
        self.setWindowTitle(
            f"{'Entrada' if tipo == 'entrada' else 'Salida'} de Inventario"
        )
        self.setMinimumWidth(350)
        self.init_ui(color)

    def init_ui(self, color):
        """Inicializa la interfaz"""
        layout = QFormLayout()
        self.setLayout(layout)

        info_box = QWidget()
        info_box.setStyleSheet(
            f"background-color: #f8f9fa; padding: 10px; border-radius: 5px;"
        )
        info_layout = QVBoxLayout()
        info_box.setLayout(info_layout)

        info_layout.addWidget(QLabel(f"<b>Producto:</b> {self.producto.nombre}"))
        info_layout.addWidget(QLabel(f"<b>Código:</b> {self.producto.codigo}"))
        info_layout.addWidget(QLabel(f"<b>Stock actual:</b> {self.producto.stock}"))

        layout.addRow("", info_box)

        self.cantidad_input = QSpinBox()
        self.cantidad_input.setRange(1, 999999)
        self.cantidad_input.setStyleSheet("padding: 8px; font-size: 16px;")
        self.cantidad_input.setFocus()
        layout.addRow("Cantidad:", self.cantidad_input)

        btn_layout = QHBoxLayout()

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet(
            f"background-color: {color}; color: white; padding: 12px; font-weight: bold;"
        )
        btn_aceptar.clicked.connect(self.aceptar)
        btn_layout.addWidget(btn_aceptar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(
            "background-color: #5a6080; color: white; padding: 8px; border-radius: 6px;"
        )
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        layout.addRow("", btn_layout)

    def aceptar(self):
        """Registra el movimiento"""
        from services.producto_service import InventarioService

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
        self.session = session
        self.producto = producto
        self.setWindowTitle("Desempacar producto")
        self.setMinimumWidth(420)
        layout = QVBoxLayout()
        self.setLayout(layout)

        from models.producto import Producto

        hijo = session.query(Producto).get(producto.producto_fraccion_id)
        und = producto.unidades_por_empaque or 1

        info = QWidget()
        info.setStyleSheet("background:#ecf0f1;padding:12px;border-radius:6px;")
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
        self.spin_cajas.setStyleSheet("font-size:16px;padding:8px;")
        self.spin_cajas.valueChanged.connect(self.actualizar_preview)
        form.addRow("¿Cuántas cajas desempacar?", self.spin_cajas)
        layout.addLayout(form)

        self.lbl_preview = QLabel("")
        self.lbl_preview.setStyleSheet(
            "font-size:14px;color:#27ae60;font-weight:bold;padding:8px;"
        )
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_preview)
        self.actualizar_preview()

        btns = QHBoxLayout()
        btn_ok = QPushButton("✓ CONFIRMAR DESEMPAQUE")
        btn_ok.setStyleSheet(
            "background:#27ae60;color:white;padding:12px;font-weight:bold;"
        )
        btn_ok.clicked.connect(self.confirmar)
        btns.addWidget(btn_ok)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def actualizar_preview(self):
        cajas = self.spin_cajas.value()
        und = self.producto.unidades_por_empaque or 1
        unidades = cajas * und
        self.lbl_preview.setText(f"{cajas} caja(s) → {unidades} unidades")

    def confirmar(self):
        from services.fraccion_service import FraccionService

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
