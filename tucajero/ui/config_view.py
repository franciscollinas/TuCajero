import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QFormLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ConfigNegocioDialog(QDialog):
    def __init__(self, parent=None, primera_vez=False):
        super().__init__(parent)
        self.primera_vez = primera_vez
        self.logo_path_seleccionado = ""
        self.setWindowTitle("Configuración del Negocio")
        self.setMinimumWidth(480)
        self.setMinimumHeight(500)
        if primera_vez:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
            )
        self.init_ui()
        self.cargar_datos_existentes()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        header = QWidget()
        header.setStyleSheet(
            "background-color: #1a252f; border-radius: 8px; padding: 16px;"
        )
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        if self.primera_vez:
            titulo = QLabel("¡Bienvenido a TuCajero!")
            titulo.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
            subtitulo = QLabel("Configura los datos de tu negocio antes de comenzar.")
            subtitulo.setStyleSheet("color: #a0b0c0; font-size: 13px;")
            header_layout.addWidget(titulo)
            header_layout.addWidget(subtitulo)
        else:
            titulo = QLabel("Configuración del Negocio")
            titulo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            header_layout.addWidget(titulo)

        layout.addWidget(header)

        form_widget = QWidget()
        form = QFormLayout()
        form.setSpacing(12)
        form_widget.setLayout(form)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Droguería El Carmen")
        self.nombre_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Nombre del negocio *:", self.nombre_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Ej: Calle 10 # 5-20")
        self.direccion_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Dirección:", self.direccion_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Ej: 3001234567")
        self.telefono_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Teléfono:", self.telefono_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ej: minegocio@gmail.com")
        self.email_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Email:", self.email_input)

        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("Ej: 900123456-1")
        self.nit_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("NIT:", self.nit_input)

        logo_widget = QWidget()
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_widget.setLayout(logo_layout)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setStyleSheet(
            "border: 2px dashed #bdc3c7; border-radius: 8px;background: #f8f9fa;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setText("Sin logo")
        logo_layout.addWidget(self.logo_preview)

        logo_btn_layout = QVBoxLayout()
        btn_seleccionar_logo = QPushButton("Seleccionar logo...")
        btn_seleccionar_logo.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px 16px;"
        )
        btn_seleccionar_logo.clicked.connect(self.seleccionar_logo)
        logo_btn_layout.addWidget(btn_seleccionar_logo)

        self.lbl_logo_path = QLabel("Ningún archivo seleccionado")
        self.lbl_logo_path.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        self.lbl_logo_path.setWordWrap(True)
        logo_btn_layout.addWidget(self.lbl_logo_path)
        logo_btn_layout.addStretch()
        logo_layout.addLayout(logo_btn_layout)

        form.addRow("Logo del negocio:", logo_widget)
        layout.addWidget(form_widget)

        nota = QLabel("* Campo obligatorio")
        nota.setStyleSheet("color: #e74c3c; font-size: 11px;")
        layout.addWidget(nota)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton(
            "GUARDAR Y CONTINUAR" if self.primera_vez else "GUARDAR"
        )
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_guardar)

        if not self.primera_vez:
            btn_cancelar = QPushButton("Cancelar")
            btn_cancelar.setStyleSheet(
                "background-color: #95a5a6; color: white; padding: 12px 24px;"
            )
            btn_cancelar.clicked.connect(self.reject)
            btn_layout.addWidget(btn_cancelar)

        layout.addLayout(btn_layout)

    def cargar_datos_existentes(self):
        from utils.store_config import (
            load_store_config,
            get_store_name,
            get_address,
            get_phone,
            get_email,
            get_nit,
            get_logo_path,
        )

        load_store_config()
        self.nombre_input.setText(get_store_name())
        self.direccion_input.setText(get_address())
        self.telefono_input.setText(get_phone())
        self.email_input.setText(get_email())
        self.nit_input.setText(get_nit())
        logo = get_logo_path()
        if logo and os.path.exists(logo):
            self.logo_path_seleccionado = logo
            self._mostrar_preview_logo(logo)
            self.lbl_logo_path.setText(os.path.basename(logo))

    def seleccionar_logo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar logo del negocio",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.ico)",
        )
        if archivo:
            self.logo_path_seleccionado = archivo
            self._mostrar_preview_logo(archivo)
            self.lbl_logo_path.setText(os.path.basename(archivo))

    def _mostrar_preview_logo(self, path):
        pm = QPixmap(path)
        if not pm.isNull():
            scaled = pm.scaled(
                76,
                76,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.logo_preview.setPixmap(scaled)
            self.logo_preview.setText("")

    def guardar(self):
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(
                self, "Campo requerido", "El nombre del negocio es obligatorio."
            )
            self.nombre_input.setFocus()
            return

        logo_guardado = ""
        if self.logo_path_seleccionado:
            try:
                import shutil
                from utils.store_config import get_config_dir

                assets_dir = os.path.join(os.path.dirname(get_config_dir()), "assets")
                os.makedirs(assets_dir, exist_ok=True)
                ext = os.path.splitext(self.logo_path_seleccionado)[1]
                destino = os.path.join(assets_dir, f"logo{ext}")
                shutil.copy2(self.logo_path_seleccionado, destino)
                logo_guardado = destino
            except Exception as e:
                print(f"[WARN] No se pudo copiar el logo: {e}")
                logo_guardado = self.logo_path_seleccionado

        config = {
            "store_name": nombre,
            "logo_path": logo_guardado,
            "address": self.direccion_input.text().strip(),
            "phone": self.telefono_input.text().strip(),
            "email": self.email_input.text().strip(),
            "nit": self.nit_input.text().strip(),
        }

        from utils.store_config import save_store_config

        if save_store_config(config):
            if not self.primera_vez:
                QMessageBox.information(
                    self,
                    "Guardado",
                    "Configuración guardada.\n"
                    "Reinicia la aplicación para ver los cambios en el header.",
                )
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración.")
