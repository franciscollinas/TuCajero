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
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from utils.store_config import get_store_name, get_logo_path
import os


class WatermarkWidget(QWidget):
    """Widget con marca de agua del logo en el fondo"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._watermark = None
        self._cargar_logo()

    def _cargar_logo(self):
        try:
            from utils.store_config import get_logo_path
            import os

            logo_path = get_logo_path()
            if logo_path and os.path.exists(logo_path):
                pixmap = QPixmap(logo_path)
                if not pixmap.isNull():
                    self._watermark = pixmap
        except Exception:
            self._watermark = None

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._watermark is None:
            return
        painter = QPainter(self)
        painter.setOpacity(0.06)
        size = min(self.width(), self.height()) * 0.65
        scaled = self._watermark.scaled(
            int(size),
            int(size),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        painter.end()


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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        self.sidebar = self.crear_sidebar()
        main_layout.addWidget(self.sidebar)

        # Área de contenido con marca de agua
        content_area = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_area.setLayout(content_layout)

        header = self.crear_header()
        content_layout.addWidget(header)

        # Contenedor con marca de agua
        self.watermark_container = WatermarkWidget(self)
        wm_layout = QVBoxLayout()
        wm_layout.setContentsMargins(0, 0, 0, 0)
        self.watermark_container.setLayout(wm_layout)

        self.content_stack = QStackedWidget()
        wm_layout.addWidget(self.content_stack)

        content_layout.addWidget(self.watermark_container, 1)
        main_layout.addWidget(content_area, 1)

    def crear_header(self):
        """Crea el encabezado con información de la tienda"""
        from utils.icon_helper import get_app_icon

        self.setWindowIcon(get_app_icon())
        from utils.store_config import (
            get_store_name,
            get_logo_path,
            get_address,
            get_phone,
            get_email,
            get_nit,
        )
        import os

        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: #1a252f;
            }
        """)
        header.setFixedHeight(100)
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 10, 16, 10)
        header.setLayout(layout)

        # Logo en el header
        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    70,
                    70,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                logo_label.setPixmap(scaled)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                logo_label.setStyleSheet("padding-right: 12px;")
                layout.addWidget(logo_label)

        # Bloque de texto
        text_widget = QWidget()
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_widget.setLayout(text_layout)

        store_name = get_store_name()
        name_label = QLabel(store_name.upper())
        name_label.setStyleSheet("""
            color: #ffffff;
            font-size: 26px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        text_layout.addWidget(name_label)

        address = get_address()
        phone = get_phone()
        email = get_email()
        nit = get_nit()

        info_parts = []
        if address:
            info_parts.append(f"📍 {address}")
        if phone:
            info_parts.append(f"📞 {phone}")
        if email:
            info_parts.append(f"✉ {email}")
        if nit:
            info_parts.append(f"NIT: {nit}")

        if info_parts:
            info_label = QLabel("   |   ".join(info_parts))
            info_label.setStyleSheet("""
                color: #a0b0c0;
                font-size: 12px;
            """)
            text_layout.addWidget(info_label)

        layout.addWidget(text_widget, 1)
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
        self.btn_config = self.crear_boton("Configuración", self.abrir_configuracion)

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

    def abrir_configuracion(self):
        from ui.config_view import ConfigNegocioDialog

        dialog = ConfigNegocioDialog(self)
        dialog.exec()

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

    def closeEvent(self, event):
        """Maneja el cierre de la aplicación."""
        import logging

        try:
            from config.database import close_db

            close_db()
        except Exception as e:
            logging.warning(f"Error en closeEvent: {e}")
        event.accept()
