# TuCajero - Código Completo del Proyecto

## Tabla de Contenidos
1. [main.py - Punto de Entrada](#1-mainpy---punto-de-entrada)
2. [ui/main_window.py - Ventana Principal](#2-uimain_windowpy---ventana-principal)
3. [ui/ventas_view.py - Vista de Ventas](#3-uiventas_viewpy---vista-de-ventas)
4. [ui/productos_view.py - Gestión de Productos](#4-uiproductos_viewpy---gestión-de-productos)
5. [ui/inventario_view.py - Gestión de Inventario](#5-uiinventario_viewpy---gestión-de-inventario)
6. [ui/corte_view.py - Corte de Caja](#6-uicorte_viewpy---corte-de-caja)
7. [models/producto.py - Modelos de Datos](#7-modelsproductopy---modelos-de-datos)
8. [services/producto_service.py - Servicios](#8-servicesproducto_servicepy---servicios)
9. [services/corte_service.py - Servicio de Corte](#9-servicescorte_servicepy---servicio-de-corte)
10. [repositories/producto_repo.py - Repositorio Productos](#10-repositoriesproducto_repopy---repositorio-productos)
11. [repositories/venta_repo.py - Repositorio Ventas](#11-repositoriesventa_repopy---repositorio-ventas)
12. [config/database.py - Configuración de Base de Datos](#12-configdatabasepy---configuración-de-base-de-datos)
13. [security/license_manager.py - Gestión de Licencias](#13-securitylicense_managerpy---gestión-de-licencias)

---

## 1. main.py - Punto de Entrada

```python
"""
TuCajero
Sistema simple de caja registradora para pequeños negocios.
"""

import sys
import logging
import os
from logging.handlers import RotatingFileHandler
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from config.database import init_db, get_session, crear_carpetas
from services.corte_service import CorteCajaService
from ui.main_window import MainWindow
from ui.ventas_view import VentasView
from ui.productos_view import ProductosView
from ui.inventario_view import InventarioView
from ui.corte_view import CorteView
from ui.activate_view import ActivationDialog
from security.license_manager import validar_licencia, crear_license_default
from utils.store_config import load_store_config


def configurar_logging():
    """Configura el logging global con rotación"""
    from config.database import get_log_file, crear_carpetas

    crear_carpetas()
    log_file = get_log_file()

    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)

    logging.basicConfig(
        handlers=[handler],
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )


def mostrar_activacion():
    """Muestra la ventana de activación"""
    dialog = ActivationDialog()
    return dialog.exec() == QDialog.DialogCode.Accepted and dialog.activation_success


def main():
    """Función principal de la aplicación"""
    crear_carpetas()
    configurar_logging()
    load_store_config()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "cruzmedic.ico")

    print(f"[INFO] Icono cargado desde: {ICON_PATH}")
    print(f"[INFO] Archivo existe: {os.path.exists(ICON_PATH)}")

    try:
        crear_license_default()
    except Exception as e:
        logging.error(f"Error al crear licencia: {e}")

    if not validar_licencia():
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setWindowIcon(QIcon(ICON_PATH))

        while True:
            result = mostrar_activacion()
            if not result:
                QMessageBox.critical(
                    None,
                    "Sistema Bloqueado",
                    "El sistema requiere activación para funcionar.\n\nEl programa se cerrará.",
                )
                sys.exit(1)
            elif validar_licencia():
                break
    else:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setWindowIcon(QIcon(ICON_PATH))

    try:
        init_db()
    except Exception as e:
        logging.error(f"Error al inicializar base de datos: {e}")
        QMessageBox.critical(
            None, "Error", f"Error al inicializar la base de datos:\n{str(e)}"
        )
        sys.exit(1)

    session = get_session()

    try:
        service = CorteCajaService(session)
        service.abrir_caja()
    except Exception as e:
        logging.error(f"Error al abrir caja: {e}")

    window = MainWindow()
    window.setWindowIcon(QIcon(ICON_PATH))

    try:
        ventas_view = VentasView(session)
        productos_view = ProductosView(session)
        inventario_view = InventarioView(session)
        corte_view = CorteView(session)

        ventas_view.sale_completed.connect(productos_view.recargar_productos)
        ventas_view.sale_completed.connect(inventario_view.recargar_inventario)
        ventas_view.sale_completed.connect(corte_view.cargar_estadisticas)

        window.add_view(ventas_view, "ventas")
        window.add_view(productos_view, "productos")
        window.add_view(inventario_view, "inventario")
        window.add_view(corte_view, "corte")
    except Exception as e:
        logging.error(f"Error al crear vistas: {e}")
        QMessageBox.critical(None, "Error", f"Error al cargar las vistas:\n{str(e)}")
        sys.exit(1)

    window.switch_to_ventas()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error crítico no manejado: {e}")
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox

            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Error crítico",
                f"Ha ocurrido un error inesperado:\n\n{str(e)}\n\nRevise logs/app.log",
            )
        except:
            print(f"Error crítico: {e}")
        sys.exit(1)
```

---

## 2. ui/main_window.py - Ventana Principal

```python
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from utils.store_config import get_store_name, get_logo_path
import os


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self):
        super().__init__()
        store_name = get_store_name()
        self.setWindowTitle(f"TuCajero POS - {store_name}")
        self.setMinimumSize(1024, 768)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.sidebar = self.crear_sidebar()
        main_layout.addWidget(self.sidebar)

        content_area = QWidget()
        content_layout = QVBoxLayout()
        content_area.setLayout(content_layout)

        header = self.crear_header()
        content_layout.addWidget(header)

        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack, 1)

        main_layout.addWidget(content_area, 1)

    def crear_header(self):
        """Crea el encabezado con logo y nombre de tienda"""
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50;")
        header.setFixedHeight(80)

        layout = QHBoxLayout()
        header.setLayout(layout)

        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    60,
                    60,
                    Qt.AspectRatioFlag.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label, 0)

        store_name = get_store_name()
        title_label = QLabel(f"TuCajero POS")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label, 1)

        if store_name:
            store_label = QLabel(store_name)
            store_label.setStyleSheet("color: #3498db; font-size: 16px;")
            layout.addWidget(store_label, 0)

        return header

    def crear_sidebar(self):
        """Crea el menú lateral"""
        sidebar = QWidget()
        layout = QVBoxLayout()
        sidebar.setLayout(layout)
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #34495e;")

        title = QLabel("TuCajero")
        title.setStyleSheet(
            "color: white; font-size: 20px; font-weight: bold; padding: 15px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.btn_ventas = self.crear_boton("Ventas", self.switch_to_ventas)
        self.btn_productos = self.crear_boton("Productos", self.switch_to_productos)
        self.btn_inventario = self.crear_boton("Inventario", self.switch_to_inventario)
        self.btn_corte = self.crear_boton("Corte de Caja", self.switch_to_corte)

        layout.addWidget(self.btn_ventas)
        layout.addWidget(self.btn_productos)
        layout.addWidget(self.btn_inventario)
        layout.addWidget(self.btn_corte)

        layout.addStretch()

        btn_acerca = QPushButton("Acerca de")
        btn_acerca.setFixedHeight(40)
        btn_acerca.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #95a5a6;
                border: none;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        btn_acerca.clicked.connect(self.mostrar_acerca)
        layout.addWidget(btn_acerca)

        copyright_label = QLabel("© Ing. Francisco Llinas P.")
        copyright_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 10px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)

        return sidebar

    def mostrar_acerca(self):
        """Muestra la ventana Acerca de"""
        from ui.about_view import AboutView

        dialog = AboutView(self)
        dialog.exec()

    def crear_boton(self, texto, callback):
        """Crea un botón del menú"""
        btn = QPushButton(texto)
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        btn.clicked.connect(callback)
        return btn

    def add_view(self, widget, name):
        """Agrega una vista al stack"""
        self.content_stack.addWidget(widget)
        return self.content_stack.count() - 1

    def switch_view(self, index):
        """Cambia a una vista específica"""
        self.content_stack.setCurrentIndex(index)

    def switch_to_ventas(self):
        self.switch_view(0)

    def switch_to_productos(self):
        self.switch_view(1)

    def switch_to_inventario(self):
        self.switch_view(2)

    def switch_to_corte(self):
        self.switch_view(3)
```

---

## 3. ui/ventas_view.py - Vista de Ventas

```python
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
)
from PySide6.QtCore import Qt, Signal


class PaymentDialog(QDialog):
    """Dialog for cash payment with change calculation"""

    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.total = total
        self.payment_amount = 0
        self.init_ui()

    def init_ui(self):
        """Initialize the payment dialog UI"""
        self.setWindowTitle("Cobro - Pago en Efectivo")
        self.setFixedSize(400, 280)

        layout = QVBoxLayout()
        self.setLayout(layout)

        store_name_label = QLabel()
        from utils.store_config import get_store_name

        store_name_label.setText(get_store_name())
        store_name_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50;"
        )
        store_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(store_name_label)

        total_label = QLabel(f"TOTAL A PAGAR")
        total_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(total_label)

        self.lbl_total = QLabel(f"${self.total:.2f}")
        self.lbl_total.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: #27ae60;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_total)

        layout.addWidget(QLabel(""))

        pago_label = QLabel("Monto recibido:")
        pago_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(pago_label)

        self.pago_input = QDoubleSpinBox()
        self.pago_input.setRange(0, 999999999)
        self.pago_input.setDecimals(2)
        self.pago_input.setStyleSheet("font-size: 24px; padding: 10px;")
        self.pago_input.setFocus()
        self.pago_input.valueChanged.connect(self.calcular_cambio)
        layout.addWidget(self.pago_input)

        self.lbl_cambio = QLabel("Cambio: $0.00")
        self.lbl_cambio.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #3498db;"
        )
        self.lbl_cambio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_cambio)

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

    def calcular_cambio(self):
        """Calculate change from payment"""
        pago = self.pago_input.value()
        cambio = pago - self.total
        if cambio >= 0:
            self.lbl_cambio.setText(f"Cambio: ${cambio:.2f}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #27ae60;"
            )
            self.payment_amount = pago
        else:
            self.lbl_cambio.setText(f"Faltan: ${abs(cambio):.2f}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #e74c3c;"
            )
            self.payment_amount = 0

    def accept(self):
        """Handle dialog acceptance"""
        if self.pago_input.value() < self.total:
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
        self.codigo_input.setPlaceholderText("Código de producto o ESCANEAR")
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
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Código", "Producto", "Cantidad", "Precio", "Subtotal"]
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

        total_layout = QHBoxLayout()
        total_layout.addStretch()

        self.lbl_total = QLabel("TOTAL: $0.00")
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; padding: 15px; color: #2c3e50;"
        )
        total_layout.addWidget(self.lbl_total)

        layout.addLayout(total_layout)

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
        """Search product by code"""
        from services.producto_service import ProductoService

        codigo = self.codigo_input.text().strip()
        if not codigo:
            return

        service = ProductoService(self.session)
        producto = service.get_producto_by_codigo(codigo)

        if not producto:
            QMessageBox.warning(self, "Error", "Producto no encontrado")
            self.codigo_input.clear()
            self.codigo_input.setFocus()
            return

        if producto.stock <= 0:
            QMessageBox.warning(self, "Error", "Producto sin stock")
            self.codigo_input.clear()
            self.codigo_input.setFocus()
            return

        self.agregar_al_carrito(producto)
        self.codigo_input.clear()
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
            }
        )
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Update cart table"""
        self.tabla.setRowCount(len(self.carrito))

        total = 0
        for i, item in enumerate(self.carrito):
            subtotal = item["cantidad"] * item["precio"]
            total += subtotal

            self.tabla.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self.tabla.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(item["cantidad"])))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"${item['precio']:.2f}"))
            self.tabla.setItem(i, 4, QTableWidgetItem(f"${subtotal:.2f}"))

        self.lbl_total.setText(f"TOTAL: ${total:.2f}")

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

        total = sum(item["cantidad"] * item["precio"] for item in self.carrito)

        dialog = PaymentDialog(total, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            service = VentaService(self.session)
            venta = service.registrar_venta(self.carrito)

            generador = GeneradorTicket()
            generador.imprimir(venta, venta.items)

            cambio = dialog.payment_amount - total
            QMessageBox.information(
                self,
                "Venta Registrada",
                f"Venta #{venta.id}\nTotal: ${total:.2f}\nPago: ${dialog.payment_amount:.2f}\nCambio: ${cambio:.2f}\n\n¡Gracias por su compra!",
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
```

---

## 4. ui/productos_view.py - Gestión de Productos

```python
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

        layout.addLayout(btn_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Código", "Nombre", "Precio", "Stock"]
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


class ProductoDialog(QDialog):
    """Diálogo para agregar/editar productos"""

    def __init__(self, session, parent=None, producto_id=None):
        super().__init__(parent)
        self.session = session
        self.producto_id = producto_id
        self.setWindowTitle(
            "Agregar Producto" if not producto_id else "Editar Producto"
        )
        self.setMinimumWidth(400)
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
            if self.producto_id:
                service.update_producto(
                    self.producto_id,
                    codigo=codigo,
                    nombre=nombre,
                    precio=precio,
                    costo=costo,
                    stock=stock,
                )
            else:
                service.create_producto(codigo, nombre, precio, costo, stock)

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")
```

---

## 5. ui/inventario_view.py - Gestión de Inventario

```python
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
```

---

## 6. ui/corte_view.py - Corte de Caja

```python
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
)
from PySide6.QtCore import Qt
from datetime import datetime


class CorteView(QWidget):
    """Vista de corte de caja"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_estadisticas()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Corte de Caja")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.info_widget = QWidget()
        self.info_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout()
        self.info_widget.setLayout(info_layout)

        self.lbl_fecha = QLabel(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        self.lbl_fecha.setStyleSheet("font-size: 18px;")
        info_layout.addWidget(self.lbl_fecha)

        self.lbl_estado = QLabel("Caja: ABIERTA")
        self.lbl_estado.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #27ae60;"
        )
        info_layout.addWidget(self.lbl_estado)

        self.lbl_total = QLabel("Total vendido: $0.00")
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #27ae60;"
        )
        info_layout.addWidget(self.lbl_total)

        self.lbl_num_ventas = QLabel("Número de ventas: 0")
        self.lbl_num_ventas.setStyleSheet("font-size: 18px;")
        info_layout.addWidget(self.lbl_num_ventas)

        layout.addWidget(self.info_widget)

        botones_layout = QHBoxLayout()

        self.btn_abrir = QPushButton("ABRIR CAJA")
        self.btn_abrir.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_abrir.clicked.connect(self.abrir_caja)
        botones_layout.addWidget(self.btn_abrir)

        self.btn_cerrar = QPushButton("CERRAR CAJA")
        self.btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_cerrar.clicked.connect(self.cerrar_caja)
        botones_layout.addWidget(self.btn_cerrar)

        layout.addLayout(botones_layout)

        historial_label = QLabel("Ventas del día")
        historial_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 20px;"
        )
        layout.addWidget(historial_label)

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(3)
        self.tabla_ventas.setHorizontalHeaderLabels(["ID", "Hora", "Total"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_ventas.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.tabla_ventas)

    def cargar_estadisticas(self):
        """Carga las estadísticas del día"""
        from services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        caja_abierta = service.esta_caja_abierta()

        if caja_abierta:
            self.lbl_estado.setText("Caja: ABIERTA")
            self.lbl_estado.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #27ae60;"
            )
            self.btn_abrir.setEnabled(False)
            self.btn_cerrar.setEnabled(True)
        else:
            self.lbl_estado.setText("Caja: CERRADA")
            self.lbl_estado.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #e74c3c;"
            )
            self.btn_abrir.setEnabled(True)
            self.btn_cerrar.setEnabled(False)

        self.lbl_total.setText(f"Total vendido: ${stats['total']:.2f}")
        self.lbl_num_ventas.setText(f"Número de ventas: {stats['num_ventas']}")

        ventas = stats["ventas"]
        self.tabla_ventas.setRowCount(len(ventas))

        for i, venta in enumerate(ventas):
            self.tabla_ventas.setItem(i, 0, QTableWidgetItem(str(venta.id)))
            self.tabla_ventas.setItem(
                i, 1, QTableWidgetItem(venta.fecha.strftime("%H:%M:%S"))
            )
            self.tabla_ventas.setItem(i, 2, QTableWidgetItem(f"${venta.total:.2f}"))

    def abrir_caja(self):
        """Abre la caja"""
        from services.corte_service import CorteCajaService

        service = CorteCajaService(session)
        service.abrir_caja()

        QMessageBox.information(
            self,
            "Caja Abierta",
            "La caja ha sido abierta correctamente.\n\nYa puedes comenzar a registrar ventas.",
        )

        self.cargar_estadisticas()

    def cerrar_caja(self):
        """Cierra la caja"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de cerrar la caja?\nSe registrará el corte del día.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            from services.corte_service import CorteCajaService

            service = CorteCajaService(self.session)
            stats = service.get_estadisticas_hoy()

            corte = service.cerrar_caja()

            if corte:
                QMessageBox.information(
                    self,
                    "Corte de Caja",
                    f"Corte de caja cerrado!\n\n"
                    f"Total vendido: ${corte.total_ventas:.2f}\n"
                    f"Ventas: {stats['num_ventas']}",
                )
            else:
                QMessageBox.warning(self, "Error", "No hay caja abierta")

            self.cargar_estadisticas()
```

---

## 7. models/producto.py - Modelos de Datos

```python
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class Producto(Base):
    """Modelo de Producto"""

    __tablename__ = "productos"
    __table_args__ = (
        Index("idx_producto_codigo", "codigo"),
        Index("idx_producto_nombre", "nombre"),
    )

    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    costo = Column(Float, default=0)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)

    venta_items = relationship("VentaItem", back_populates="producto")
    movimientos = relationship("MovimientoInventario", back_populates="producto")

    def __repr__(self):
        return f"<Producto {self.nombre}>"


class Venta(Base):
    """Modelo de Venta"""

    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)

    items = relationship(
        "VentaItem", back_populates="venta", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Venta {self.id} - {self.total}>"


class VentaItem(Base):
    """Modelo de Item de Venta"""

    __tablename__ = "venta_items"

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="items")
    producto = relationship("Producto", back_populates="venta_items")

    @property
    def subtotal(self):
        return self.cantidad * self.precio

    def __repr__(self):
        return f"<VentaItem {self.producto_id} x {self.cantidad}>"


class MovimientoInventario(Base):
    """Modelo de Movimiento de Inventario"""

    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String(10), nullable=False)  # 'entrada' o 'salida'
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    producto = relationship("Producto", back_populates="movimientos")

    def __repr__(self):
        return f"<Movimiento {self.tipo} - {self.cantidad}>"


class CorteCaja(Base):
    """Modelo de Corte de Caja"""

    __tablename__ = "cortes_caja"

    id = Column(Integer, primary_key=True)
    fecha_apertura = Column(DateTime, default=datetime.now)
    fecha_cierre = Column(DateTime, nullable=True)
    total_ventas = Column(Float, default=0)
    numero_ventas = Column(Integer, default=0)

    def __repr__(self):
        return f"<CorteCaja {self.id}>"
```

---

## 8. services/producto_service.py - Servicios

```python
from repositories.producto_repo import ProductoRepository
from repositories.venta_repo import VentaRepository, InventarioRepository


class ProductoService:
    """Servicio para lógica de negocio de productos"""

    def __init__(self, session):
        self.session = session
        self.repo = ProductoRepository(session)

    def validar_codigo(self, codigo, exclude_id=None):
        """Valida que el código no esté repetido"""
        if self.repo.existe_codigo(codigo, exclude_id):
            raise ValueError(f"El código '{codigo}' ya está en uso")

    def get_all_productos(self):
        """Retorna todos los productos"""
        return self.repo.get_all()

    def get_producto_by_id(self, producto_id):
        """Retorna un producto por ID"""
        return self.repo.get_by_id(producto_id)

    def get_producto_by_codigo(self, codigo):
        """Retorna un producto por código"""
        return self.repo.get_by_codigo(codigo)

    def create_producto(self, codigo, nombre, precio, costo=0, stock=0):
        """Crea un nuevo producto"""
        self.validar_codigo(codigo)
        return self.repo.create(codigo, nombre, precio, costo, stock)

    def update_producto(self, producto_id, **kwargs):
        """Actualiza un producto"""
        if "codigo" in kwargs:
            self.validar_codigo(kwargs["codigo"], exclude_id=producto_id)
        return self.repo.update(producto_id, **kwargs)

    def delete_producto(self, producto_id):
        """Elimina un producto"""
        return self.repo.delete(producto_id)

    def search_productos(self, query):
        """Busca productos"""
        return self.repo.search(query)


class VentaService:
    """Servicio para lógica de negocio de ventas"""

    def __init__(self, session):
        self.session = session
        self.venta_repo = VentaRepository(session)
        self.producto_repo = ProductoRepository(session)
        self.inventario_repo = InventarioRepository(session)
        from services.corte_service import CorteCajaService

        self.corte_service = CorteCajaService(session)

    def registrar_venta(self, items):
        """Registra una venta y descuenta inventario"""
        if not self.corte_service.esta_caja_abierta():
            raise Exception(
                "No se puede registrar la venta porque la caja está cerrada."
            )

        for item in items:
            producto = self.producto_repo.get_by_id(item["producto_id"])
            if producto.stock < item["cantidad"]:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

        venta = self.venta_repo.create_venta(items)

        for item in items:
            self.producto_repo.update_stock(item["producto_id"], -item["cantidad"])
            self.inventario_repo.create_movimiento(
                item["producto_id"], "salida", item["cantidad"]
            )

        return venta

    def get_ventas_hoy(self):
        """Retorna las ventas de hoy"""
        return self.venta_repo.get_ventas_hoy()

    def get_total_hoy(self):
        """Retorna el total de ventas de hoy"""
        return self.venta_repo.get_total_hoy()

    def get_count_hoy(self):
        """Retorna el número de ventas de hoy"""
        return self.venta_repo.get_count_hoy()


class InventarioService:
    """Servicio para lógica de negocio de inventario"""

    def __init__(self, session):
        self.session = session
        self.producto_repo = ProductoRepository(session)
        self.inventario_repo = InventarioRepository(session)

    def entrada_inventario(self, producto_id, cantidad):
        """Registra entrada de inventario"""
        self.producto_repo.update_stock(producto_id, cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "entrada", cantidad)

    def salida_inventario(self, producto_id, cantidad):
        """Registra salida manual de inventario"""
        producto = self.producto_repo.get_by_id(producto_id)
        if producto.stock < cantidad:
            raise ValueError("Stock insuficiente")
        self.producto_repo.update_stock(producto_id, -cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "salida", cantidad)

    def descontar_por_venta(self, producto_id, cantidad):
        """Descuenta inventario por venta (usado desde ventas)"""
        producto = self.producto_repo.get_by_id(producto_id)
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para {producto.nombre}")
        self.producto_repo.update_stock(producto_id, -cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "salida", cantidad)

    def obtener_stock(self, producto_id):
        """Obtiene el stock actual de un producto"""
        producto = self.producto_repo.get_by_id(producto_id)
        return producto.stock if producto else 0

    def get_movimientos_producto(self, producto_id):
        """Retorna los movimientos de un producto"""
        return self.inventario_repo.get_movimientos_producto(producto_id)

    def get_all_productos(self):
        """Retorna todos los productos con su stock"""
        return self.producto_repo.get_all()
```

---

## 9. services/corte_service.py - Servicio de Corte

```python
from models.producto import CorteCaja
from repositories.venta_repo import VentaRepository
from datetime import datetime


class CorteCajaService:
    """Servicio para lógica de negocio de corte de caja"""

    def __init__(self, session):
        self.session = session
        self.venta_repo = VentaRepository(session)

    def get_corte_actual(self):
        """Retorna el corte de caja del día"""
        return (
            self.session.query(CorteCaja)
            .filter(CorteCaja.fecha_cierre.is_(None))
            .first()
        )

    def abrir_caja(self):
        """Abre la caja creando un nuevo corte"""
        corte_existente = self.get_corte_actual()
        if corte_existente:
            return corte_existente

        corte = CorteCaja(fecha_apertura=datetime.now(), total_ventas=0)
        self.session.add(corte)
        self.session.commit()
        return corte

    def cerrar_caja(self):
        """Cierra la caja actual"""
        corte = self.get_corte_actual()
        if not corte:
            return None

        total = self.venta_repo.get_total_hoy()
        num_ventas = self.venta_repo.get_count_hoy()
        corte.fecha_cierre = datetime.now()
        corte.total_ventas = total
        corte.numero_ventas = num_ventas
        self.session.commit()

        try:
            from utils.backup import backup_database

            backup_database()
        except Exception as e:
            print(f"Error al crear backup: {e}")

        return corte

    def obtener_total_vendido(self):
        """Retorna el total vendido hoy"""
        return self.venta_repo.get_total_hoy()

    def obtener_numero_ventas(self):
        """Retorna el número de ventas hoy"""
        return self.venta_repo.get_count_hoy()

    def esta_caja_abierta(self):
        """Retorna True si la caja está abierta"""
        return self.get_corte_actual() is not None

    def get_estadisticas_hoy(self):
        """Retorna las estadísticas de ventas de hoy"""
        return {
            "total": self.venta_repo.get_total_hoy(),
            "num_ventas": self.venta_repo.get_count_hoy(),
            "ventas": self.venta_repo.get_ventas_hoy(),
        }

    def get_historial_cortes(self):
        """Retorna el historial de cortes de caja"""
        return (
            self.session.query(CorteCaja)
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )
```

---

## 10. repositories/producto_repo.py - Repositorio Productos

```python
from models.producto import Producto
from sqlalchemy import and_


class ProductoRepository:
    """Repositorio para acceso a datos de productos"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todos los productos activos"""
        return self.session.query(Producto).filter(Producto.activo == True).all()

    def get_by_id(self, producto_id):
        """Retorna un producto por su ID"""
        return self.session.query(Producto).filter(Producto.id == producto_id).first()

    def get_by_codigo(self, codigo):
        """Retorna un producto por su código de barras"""
        return (
            self.session.query(Producto)
            .filter(and_(Producto.codigo == codigo, Producto.activo == True))
            .first()
        )

    def existe_codigo(self, codigo, exclude_id=None):
        """Verifica si existe un código (excluyendo un ID opcional)"""
        query = self.session.query(Producto).filter(Producto.codigo == codigo)
        if exclude_id:
            query = query.filter(Producto.id != exclude_id)
        return query.filter(Producto.activo == True).first() is not None

    def create(self, codigo, nombre, precio, costo=0, stock=0):
        """Crea un nuevo producto"""
        producto = Producto(
            codigo=codigo, nombre=nombre, precio=precio, costo=costo, stock=stock
        )
        self.session.add(producto)
        self.session.commit()
        return producto

    def update(self, producto_id, **kwargs):
        """Actualiza un producto"""
        producto = self.get_by_id(producto_id)
        if producto:
            for key, value in kwargs.items():
                setattr(producto, key, value)
            self.session.commit()
        return producto

    def delete(self, producto_id):
        """Elimina (desactiva) un producto"""
        producto = self.get_by_id(producto_id)
        if producto:
            producto.activo = False
            self.session.commit()
        return producto

    def update_stock(self, producto_id, cantidad):
        """Actualiza el stock de un producto"""
        producto = self.get_by_id(producto_id)
        if producto:
            producto.stock += cantidad
            self.session.commit()
        return producto

    def search(self, query):
        """Busca productos por código, nombre o parte del nombre"""
        search_term = f"%{query}%"
        return (
            self.session.query(Producto)
            .filter(
                and_(
                    Producto.activo == True,
                    (
                        Producto.codigo.ilike(search_term)
                        | Producto.nombre.ilike(search_term)
                    ),
                )
            )
            .all()
        )
```

---

## 11. repositories/venta_repo.py - Repositorio Ventas

```python
from models.producto import Venta, VentaItem, MovimientoInventario
from sqlalchemy import and_
from datetime import datetime, timedelta


class VentaRepository:
    """Repositorio para acceso a datos de ventas"""

    def __init__(self, session):
        self.session = session

    def create_venta(self, items):
        """Crea una venta con sus items"""
        total = sum(item["cantidad"] * item["precio"] for item in items)

        venta = Venta(total=total, fecha=datetime.now())
        self.session.add(venta)
        self.session.flush()

        for item in items:
            venta_item = VentaItem(
                venta_id=venta.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio=item["precio"],
            )
            self.session.add(venta_item)

        self.session.commit()
        return venta

    def get_ventas_hoy(self):
        """Retorna las ventas de hoy"""
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        fin_dia = datetime.combine(hoy, datetime.max.time())

        return (
            self.session.query(Venta)
            .filter(and_(Venta.fecha >= inicio_dia, Venta.fecha <= fin_dia))
            .all()
        )

    def get_total_hoy(self):
        """Retorna el total de ventas de hoy"""
        ventas = self.get_ventas_hoy()
        return sum(v.total for v in ventas)

    def get_count_hoy(self):
        """Retorna el número de ventas de hoy"""
        return len(self.get_ventas_hoy())

    def get_all(self):
        """Retorna todas las ventas"""
        return self.session.query(Venta).order_by(Venta.fecha.desc()).all()


class InventarioRepository:
    """Repositorio para acceso a datos de inventario"""

    def __init__(self, session):
        self.session = session

    def create_movimiento(self, producto_id, tipo, cantidad):
        """Crea un movimiento de inventario"""
        movimiento = MovimientoInventario(
            producto_id=producto_id, tipo=tipo, cantidad=cantidad, fecha=datetime.now()
        )
        self.session.add(movimiento)
        self.session.commit()
        return movimiento

    def get_movimientos_producto(self, producto_id):
        """Retorna los movimientos de un producto"""
        return (
            self.session.query(MovimientoInventario)
            .filter(MovimientoInventario.producto_id == producto_id)
            .order_by(MovimientoInventario.fecha.desc())
            .all()
        )

    def get_movimientos_hoy(self):
        """Retorna los movimientos de hoy"""
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        fin_dia = datetime.combine(hoy, datetime.max.time())

        return (
            self.session.query(MovimientoInventario)
            .filter(
                and_(
                    MovimientoInventario.fecha >= inicio_dia,
                    MovimientoInventario.fecha <= fin_dia,
                )
            )
            .all()
        )
```

---

## 12. config/database.py - Configuración de Base de Datos

```python
import os
import sys


def get_data_dir():
    """Returns the data directory for the application.

    Uses %LOCALAPPDATA%/TuCajero for Windows.
    Falls back to user home directory for other platforms.
    """
    if sys.platform == "win32":
        return os.path.join(
            os.environ.get("LOCALAPPDATA", os.environ["APPDATA"]), "TuCajero"
        )
    else:
        return os.path.join(os.path.expanduser("~"), ".tucajero")


def get_base_dir():
    """Returns the base directory of the application"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def crear_carpetas():
    """Creates necessary folders if they don't exist"""
    data_dir = get_data_dir()

    db_dir = os.path.join(data_dir, "database")
    os.makedirs(db_dir, exist_ok=True)

    backups_dir = os.path.join(db_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)

    logs_dir = os.path.join(data_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    config_dir = os.path.join(get_base_dir(), "config")
    os.makedirs(config_dir, exist_ok=True)


def get_db_path():
    """Returns the database path - always uses %LOCALAPPDATA%"""
    data_dir = get_data_dir()
    db_dir = os.path.join(data_dir, "database")
    return os.path.join(db_dir, "pos.db")


def get_logs_dir():
    """Returns the logs directory"""
    data_dir = get_data_dir()
    return os.path.join(data_dir, "logs")


def get_log_file():
    """Returns the full path to the log file"""
    return os.path.join(get_logs_dir(), "app.log")


def get_engine():
    """Creates and returns the database engine with production config"""
    db_path = get_db_path()

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker, declarative_base

    engine = create_engine(
        f"sqlite:///{db_path}", echo=False, connect_args={"check_same_thread": False}
    )

    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.execute(text("PRAGMA foreign_keys=ON"))

    return engine


def get_session():
    """Creates and returns a database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initializes the database creating all tables"""
    crear_carpetas()
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()

    from models.producto import Producto

    engine = get_engine()
    Base.metadata.create_all(engine)
```

---

## 13. security/license_manager.py - Gestión de Licencias

```python
import uuid
import hashlib
import json
import os
import sys
import platform

SECRET = "tito_castilla_pos_secret"


def get_base_dir():
    """Retorna el directorio base de la aplicación"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_machine_id():
    """Obtiene un identificador único robusto de la computadora"""
    components = [
        str(uuid.getnode()),
        platform.node(),
        platform.processor() or "unknown",
        platform.machine() or "unknown",
    ]
    combined = "|".join(components)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def generar_licencia(machine_id):
    """Genera una licencia basada en el machine_id"""
    licencia = hashlib.sha256((machine_id + SECRET).encode()).hexdigest()[:16]
    return licencia.upper()


def get_license_path():
    """Retorna la ruta del archivo de licencia"""
    base_dir = get_base_dir()
    config_dir = os.path.join(base_dir, "config")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "license.json")


def cargar_licencia():
    """Carga la configuración de licencia"""
    license_path = get_license_path()
    if not os.path.exists(license_path):
        return {"activated": False, "license_key": ""}

    try:
        with open(license_path, "r") as f:
            return json.load(f)
    except:
        return {"activated": False, "license_key": ""}


def guardar_licencia(license_key):
    """Guarda la licencia en el archivo"""
    license_path = get_license_path()
    data = {"activated": True, "license_key": license_key.upper()}
    with open(license_path, "w") as f:
        json.dump(data, f, indent=4)
    return True


def validar_licencia():
    """Valida si la licencia es correcta"""
    licencia_data = cargar_licencia()

    if not licencia_data.get("activated", False):
        return False

    machine_id = get_machine_id()
    licencia_correcta = generar_licencia(machine_id)

    return licencia_data.get("license_key", "").upper() == licencia_correcta


def crear_license_default():
    """Crea el archivo de licencia por defecto"""
    license_path = get_license_path()
    if not os.path.exists(license_path):
        data = {"activated": False, "license_key": ""}
        with open(license_path, "w") as f:
            json.dump(data, f, indent=4)
```

---

## Fin del Documento
