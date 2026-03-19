from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from utils.store_config import (
    save_store_config,
    load_store_config,
    get_store_name,
    get_address,
    get_phone,
    get_email,
    get_nit,
    get_logo_path,
)


class SetupDialog(QDialog):
    """Pantalla de configuración inicial — aparece solo la primera vez"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path = ""
        self.setWindowTitle("Bienvenido")
        self.setFixedSize(600, 550)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50;")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)
        header_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Bienvenido a TuCajero")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Configura tu negocio para comenzar")
        subtitle.setStyleSheet("color: #bdc3c7; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_widget.setLayout(form_layout)
        form_layout.setContentsMargins(40, 30, 40, 20)
        form_layout.setSpacing(15)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Droguería CruzMedic")
        self.nombre_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        form_layout.addWidget(QLabel("Nombre del negocio *"))
        form_layout.addWidget(self.nombre_input)

        nit_layout = QHBoxLayout()
        nit_layout.setSpacing(15)
        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("123456789-0")
        self.nit_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        nit_layout.addWidget(QLabel("NIT"))
        nit_layout.addWidget(self.nit_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("300 123 4567")
        self.telefono_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        nit_layout.addWidget(QLabel("Teléfono"))
        nit_layout.addWidget(self.telefono_input)

        form_layout.addLayout(nit_layout)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("info@ejemplo.com")
        self.email_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        form_layout.addWidget(QLabel("Correo electrónico"))
        form_layout.addWidget(self.email_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Calle 123 #45-67, Ciudad")
        self.direccion_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        form_layout.addWidget(QLabel("Dirección"))
        form_layout.addWidget(self.direccion_input)

        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(15)

        self.btn_logo = QPushButton("Seleccionar imagen...")
        self.btn_logo.setStyleSheet("padding: 12px; font-size: 14px;")
        self.btn_logo.clicked.connect(self.seleccionar_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setStyleSheet(
            "border: 1px solid #bdc3c7; border-radius: 4px; background-color: #f8f9fa;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(QLabel("Logo:"))
        logo_layout.addWidget(self.btn_logo)
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addStretch()

        form_layout.addLayout(logo_layout)

        main_layout.addWidget(form_widget)

        footer = QWidget()
        footer_layout = QVBoxLayout()
        footer.setLayout(footer_layout)
        footer_layout.setContentsMargins(40, 0, 40, 20)
        footer_layout.setSpacing(10)

        nota = QLabel("* Campo requerido")
        nota.setStyleSheet("color: #95a5a6; font-size: 12px;")
        footer_layout.addWidget(nota)

        self.btn_comenzar = QPushButton("COMENZAR")
        self.btn_comenzar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_comenzar.clicked.connect(self.guardar)
        footer_layout.addWidget(self.btn_comenzar)

        main_layout.addWidget(footer)

        self.nombre_input.setFocus()

    def seleccionar_logo(self):
        """Abre dialogo para seleccionar logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.ico *.bmp);;Todos los archivos (*)",
        )
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
            self.btn_logo.setText("Cambiar imagen...")

    def guardar(self):
        """Guarda la configuracion"""
        nombre = self.nombre_input.text().strip()
        if not nombre:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Campo requerido", "El nombre del negocio es requerido"
            )
            self.nombre_input.setFocus()
            return

        config_data = {
            "store_name": nombre,
            "nit": self.nit_input.text().strip(),
            "phone": self.telefono_input.text().strip(),
            "email": self.email_input.text().strip(),
            "address": self.direccion_input.text().strip(),
            "logo_path": self.logo_path,
            "setup_complete": True,
        }

        if save_store_config(config_data):
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")


class SetupView(QWidget):
    """Panel de configuración — accesible desde el menú lateral"""

    config_saved = Signal()

    def __init__(self, session=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.logo_path = get_logo_path()
        self.init_ui()
        self.cargar_config()

    def init_ui(self):
        """Inicializa la interfaz del panel de configuración"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Configuración del Negocio")
        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold; padding-bottom: 10px;"
        )
        layout.addWidget(titulo)

        info_group = QGroupBox("Información del Negocio")
        info_layout = QFormLayout()
        info_group.setLayout(info_layout)
        info_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del negocio")
        self.nombre_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("Nombre:", self.nombre_input)

        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("NIT")
        self.nit_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("NIT:", self.nit_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        self.telefono_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("Teléfono:", self.telefono_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("Email:", self.email_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Dirección")
        self.direccion_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("Dirección:", self.direccion_input)

        layout.addWidget(info_group)

        logo_group = QGroupBox("Logo")
        logo_layout = QHBoxLayout()
        logo_group.setLayout(logo_layout)

        self.btn_logo = QPushButton("Seleccionar imagen...")
        self.btn_logo.setStyleSheet("padding: 10px; font-size: 14px;")
        self.btn_logo.clicked.connect(self.seleccionar_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setStyleSheet(
            "border: 1px solid #bdc3c7; border-radius: 4px; background-color: #f8f9fa;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.logo_path and __import__("os").path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
                self.btn_logo.setText("Cambiar imagen...")

        logo_layout.addWidget(QLabel("Logo:"))
        logo_layout.addWidget(self.btn_logo)
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addStretch()

        layout.addWidget(logo_group)

        layout.addStretch()

        self.btn_guardar = QPushButton("GUARDAR CONFIGURACIÓN")
        self.btn_guardar.setStyleSheet("""
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
        self.btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(self.btn_guardar)

    def cargar_config(self):
        """Carga la configuración actual"""
        self.nombre_input.setText(get_store_name())
        self.nit_input.setText(get_nit())
        self.telefono_input.setText(get_phone())
        self.email_input.setText(get_email())
        self.direccion_input.setText(get_address())

    def seleccionar_logo(self):
        """Abre diálogo para seleccionar logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.ico *.bmp);;Todos los archivos (*)",
        )
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
            self.btn_logo.setText("Cambiar imagen...")

    def guardar(self):
        """Guarda la configuración"""
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(
                self, "Campo requerido", "El nombre del negocio es requerido"
            )
            self.nombre_input.setFocus()
            return

        config_data = {
            "store_name": nombre,
            "nit": self.nit_input.text().strip(),
            "phone": self.telefono_input.text().strip(),
            "email": self.email_input.text().strip(),
            "address": self.direccion_input.text().strip(),
            "logo_path": self.logo_path,
            "setup_complete": True,
        }

        if save_store_config(config_data):
            load_store_config()
            QMessageBox.information(
                self, "Éxito", "Configuración guardada correctamente"
            )
            self.config_saved.emit()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")
