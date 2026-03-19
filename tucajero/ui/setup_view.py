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
    QScrollArea,
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
    """Pantalla de configuración inicial — aparece solo la primera vez."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path = ""
        self.setWindowTitle("Bienvenido")
        self.setMinimumSize(680, 600)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50;")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)
        header_layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Bienvenido a TuCajero")
        title.setStyleSheet("color: white; font-size: 26px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Configura tu negocio para comenzar")
        subtitle.setStyleSheet("color: #bdc3c7; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        main_layout.addWidget(scroll, 1)

        scroll_content = QWidget()
        form_layout = QVBoxLayout()
        scroll_content.setLayout(form_layout)
        form_layout.setContentsMargins(30, 20, 30, 20)
        form_layout.setSpacing(10)

        def field_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 12px; color: #555; margin-bottom: 2px;")
            return lbl

        def input_style():
            return (
                "padding: 8px; font-size: 13px; "
                "border: 1px solid #bdc3c7; border-radius: 4px;"
            )

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Droguería CruzMedic")
        self.nombre_input.setStyleSheet(input_style())
        form_layout.addWidget(field_label("Nombre del negocio *"))
        form_layout.addWidget(self.nombre_input)

        nit_tel_layout = QHBoxLayout()
        nit_tel_layout.setSpacing(15)

        nit_widget = QWidget()
        nit_vl = QVBoxLayout()
        nit_vl.setSpacing(2)
        nit_vl.setContentsMargins(0, 0, 0, 0)
        nit_widget.setLayout(nit_vl)
        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("123456789-0")
        self.nit_input.setStyleSheet(input_style())
        nit_vl.addWidget(field_label("NIT"))
        nit_vl.addWidget(self.nit_input)

        tel_widget = QWidget()
        tel_vl = QVBoxLayout()
        tel_vl.setSpacing(2)
        tel_vl.setContentsMargins(0, 0, 0, 0)
        tel_widget.setLayout(tel_vl)
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("300 123 4567")
        self.telefono_input.setStyleSheet(input_style())
        tel_vl.addWidget(field_label("Teléfono"))
        tel_vl.addWidget(self.telefono_input)

        nit_tel_layout.addWidget(nit_widget, 1)
        nit_tel_layout.addWidget(tel_widget, 1)
        form_layout.addLayout(nit_tel_layout)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("info@ejemplo.com")
        self.email_input.setStyleSheet(input_style())
        form_layout.addWidget(field_label("Correo electrónico"))
        form_layout.addWidget(self.email_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Calle 123 #45-67, Ciudad")
        self.direccion_input.setStyleSheet(input_style())
        form_layout.addWidget(field_label("Dirección"))
        form_layout.addWidget(self.direccion_input)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(15)

        self.btn_logo = QPushButton("📁  Seleccionar logo...")
        self.btn_logo.setFixedHeight(36)
        self.btn_logo.setStyleSheet(
            "padding: 0 16px; font-size: 13px; "
            "border: 1px solid #bdc3c7; border-radius: 4px; "
            "text-align: left; background-color: white;"
        )
        self.btn_logo.clicked.connect(self.seleccionar_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(70, 70)
        self.logo_preview.setStyleSheet(
            "border: 1px solid #bdc3c7; border-radius: 4px; background-color: #f8f9fa;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_row.addWidget(self.btn_logo, 1)
        logo_row.addWidget(self.logo_preview)

        form_layout.addWidget(field_label("Logo de tu negocio"))
        form_layout.addLayout(logo_row)

        form_layout.addStretch()
        scroll.setWidget(scroll_content)

        footer = QWidget()
        footer_layout = QVBoxLayout()
        footer.setLayout(footer_layout)
        footer_layout.setContentsMargins(30, 10, 30, 20)
        footer_layout.setSpacing(8)

        nota = QLabel("* Campo requerido")
        nota.setStyleSheet("color: #95a5a6; font-size: 11px;")
        footer_layout.addWidget(nota)

        self.btn_comenzar = QPushButton("COMENZAR")
        self.btn_comenzar.setFixedHeight(48)
        self.btn_comenzar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
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
        """Abre diálogo para seleccionar logo."""
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
                    70,
                    70,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
            import os

            self.btn_logo.setText(f"📁  {os.path.basename(file_path)}")
            self.btn_logo.setStyleSheet(
                "padding: 0 16px; font-size: 13px; "
                "border: 1px solid #27ae60; border-radius: 4px; "
                "text-align: left; background-color: white;"
            )

    def guardar(self):
        """Guarda la configuración."""
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
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")


class SetupView(QWidget):
    """Panel de configuración — accesible desde el menú lateral."""

    config_saved = Signal()

    def __init__(self, session=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.logo_path = ""
        self.init_ui()
        self.cargar_config()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        titulo = QLabel("Configuración del Negocio")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; padding-bottom: 10px;"
        )
        layout.addWidget(titulo)

        fields_layout = QVBoxLayout()
        fields_layout.setSpacing(8)

        def field_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 12px; color: #555;")
            return lbl

        def input_style():
            return "padding: 8px; font-size: 13px; border: 1px solid #bdc3c7; border-radius: 4px;"

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del negocio")
        self.nombre_input.setStyleSheet(input_style())
        fields_layout.addWidget(field_label("Nombre *"))
        fields_layout.addWidget(self.nombre_input)

        nit_tel_layout = QHBoxLayout()
        nit_tel_layout.setSpacing(15)

        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("NIT")
        self.nit_input.setStyleSheet(input_style())
        nit_tel_layout.addWidget(field_label("NIT"))
        nit_tel_layout.addWidget(self.nit_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        self.telefono_input.setStyleSheet(input_style())
        nit_tel_layout.addWidget(field_label("Teléfono"))
        nit_tel_layout.addWidget(self.telefono_input)

        fields_layout.addLayout(nit_tel_layout)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setStyleSheet(input_style())
        fields_layout.addWidget(field_label("Correo electrónico"))
        fields_layout.addWidget(self.email_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Dirección")
        self.direccion_input.setStyleSheet(input_style())
        fields_layout.addWidget(field_label("Dirección"))
        fields_layout.addWidget(self.direccion_input)

        logo_row = QHBoxLayout()
        logo_row.setSpacing(15)

        self.btn_logo = QPushButton("📁  Seleccionar logo...")
        self.btn_logo.setFixedHeight(36)
        self.btn_logo.setStyleSheet(
            "padding: 0 16px; font-size: 13px; border: 1px solid #bdc3c7; border-radius: 4px; "
            "text-align: left; background-color: white;"
        )
        self.btn_logo.clicked.connect(self.seleccionar_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(70, 70)
        self.logo_preview.setStyleSheet(
            "border: 1px solid #bdc3c7; border-radius: 4px; background-color: #f8f9fa;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_row.addWidget(self.btn_logo, 1)
        logo_row.addWidget(self.logo_preview)
        fields_layout.addWidget(field_label("Logo"))
        fields_layout.addLayout(logo_row)

        layout.addLayout(fields_layout)
        layout.addStretch()

        self.btn_guardar = QPushButton("GUARDAR CONFIGURACIÓN")
        self.btn_guardar.setFixedHeight(48)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(self.btn_guardar)

    def cargar_config(self):
        self.nombre_input.setText(get_store_name())
        self.nit_input.setText(get_nit())
        self.telefono_input.setText(get_phone())
        self.email_input.setText(get_email())
        self.direccion_input.setText(get_address())
        logo = get_logo_path()
        if logo:
            import os

            if os.path.exists(logo):
                self.logo_path = logo
                pixmap = QPixmap(logo)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        70,
                        70,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.logo_preview.setPixmap(scaled)
                    self.btn_logo.setText(f"📁  {os.path.basename(logo)}")

    def seleccionar_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.ico *.bmp);;Todos (*)",
        )
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    70,
                    70,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
            import os

            self.btn_logo.setText(f"📁  {os.path.basename(file_path)}")

    def guardar(self):
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
            self.config_saved.emit()
            QMessageBox.information(
                self, "Éxito", "Configuración guardada correctamente"
            )
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")
