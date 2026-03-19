from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from utils.store_config import (
    get_store_name,
    get_logo_path,
    get_nit,
    get_phone,
    get_email,
    get_address,
)
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
        """Crea el encabezado con logo, nombre e info de tienda"""
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50;")
        header.setMinimumHeight(70)
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label, 0)

        store_name = get_store_name()
        nit = get_nit()
        phone = get_phone()
        email = get_email()
        address = get_address()

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        title_label = QLabel(f"TuCajero POS")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        info_layout.addWidget(title_label)

        if store_name:
            store_label = QLabel(store_name)
            store_label.setWordWrap(True)
            store_label.setStyleSheet(
                "color: #3498db; font-size: 13px; font-weight: bold;"
            )
            info_layout.addWidget(store_label)

        contact_parts = []
        if nit:
            contact_parts.append(f"NIT: {nit}")
        if phone:
            contact_parts.append(f"Tel: {phone}")
        if email:
            contact_parts.append(email)
        if contact_parts:
            contact_label = QLabel("  |  ".join(contact_parts))
            contact_label.setStyleSheet("color: #bdc3c7; font-size: 11px;")
            info_layout.addWidget(contact_label)

        if address:
            addr_label = QLabel(address)
            addr_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
            info_layout.addWidget(addr_label)

        layout.addLayout(info_layout, 1)

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
        self.btn_historial = self.crear_boton("Historial", self.switch_to_historial)
        self.btn_config = self.crear_boton("Config", self.switch_to_config)

        layout.addWidget(self.btn_ventas)
        layout.addWidget(self.btn_productos)
        layout.addWidget(self.btn_inventario)
        layout.addWidget(self.btn_corte)
        layout.addWidget(self.btn_historial)
        layout.addWidget(self.btn_config)

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

    def switch_to_historial(self):
        self.switch_view(4)

    def switch_to_config(self):
        self.switch_view(5)

    def closeEvent(self, event):
        """Cierra la aplicación correctamente"""
        try:
            from config.database import close_db

            close_db()
        except Exception as e:
            import logging

            logging.error(f"closeEvent error: {e}")
        event.accept()
