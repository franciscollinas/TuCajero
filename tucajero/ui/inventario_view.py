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
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class InventarioView(QWidget):
    """Vista de inventario"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
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
        info_label.setStyleSheet("color: #7f8c8d; padding-bottom: 10px;")
        layout.addWidget(info_label)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Código", "Producto", "Stock", "Precio"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet("font-size: 14px;")
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
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
        from services.producto_service import InventarioService

        service = InventarioService(self.session)
        productos = service.get_all_productos()

        self.tabla.setRowCount(len(productos))

        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.nombre))

            stock_item = QTableWidgetItem(str(p.stock))
            if p.stock <= 0:
                stock_item.setBackground(QColor("#ffcccc"))
            elif p.stock < 5:
                stock_item.setBackground(QColor("#fff3cd"))
            self.tabla.setItem(i, 2, stock_item)

            self.tabla.setItem(i, 3, QTableWidgetItem(f"${p.precio:.2f}"))

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
            "background-color: #95a5a6; color: white; padding: 12px;"
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
