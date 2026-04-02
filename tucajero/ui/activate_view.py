from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QDialog,
    QApplication,
)
from PySide6.QtCore import Qt, QTimer
from tucajero.utils.theme import btn_primary, btn_secondary, get_colors
c = get_colors()
from tucajero.security.license_manager import (
    get_machine_id,
    generar_licencia,
    guardar_licencia,
    validar_licencia,
)
from tucajero.utils.store_config import get_store_name


class ActivateView(QWidget):
    """Vista de activación del sistema"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activation_success = False
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        store_name = get_store_name()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(400, 300)
        self.setWindowTitle(f"Activación - {store_name}")

        titulo = QLabel(f"Activación de {store_name}")
        titulo.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {c['primary']};")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()
        machine_label = QLabel(f"Machine ID:")
        machine_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(machine_label)

        self.machine_id_display = QLabel(machine_id)
        self.machine_id_display.setObjectName("machine_id_display")
        self.machine_id_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.machine_id_display)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setObjectName("info_label")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Ingrese su licencia")
        self.licencia_input.setStyleSheet("padding: 10px; font-size: 16px;")
        self.licencia_input.setMaxLength(16)
        layout.addWidget(self.licencia_input)

        btn_layout = QHBoxLayout()

        self.btn_activar = QPushButton("ACTIVAR")
        self.btn_activar.setStyleSheet(btn_primary())
        self.btn_activar.clicked.connect(self.activar)
        btn_layout.addWidget(self.btn_activar)

        layout.addLayout(btn_layout)

    def activar(self):
        """Activa el sistema con la licencia"""
        import logging

        try:
            licencia = self.licencia_input.text().strip().upper()

            if not licencia:
                QMessageBox.warning(self, "Error", "Ingrese una licencia")
                return

            machine_id = get_machine_id()
            licencia_correcta = generar_licencia(machine_id)

            if licencia == licencia_correcta:
                guardar_licencia(licencia)
                QMessageBox.information(
                    self,
                    "Sistema Activado",
                    f"{get_store_name()} ha sido activado correctamente.\n\nEl sistema se cerrará. Vuelve a abrirlo.",
                )
                self.activation_success = True
                self.close()
            else:
                QMessageBox.critical(
                    self,
                    "Licencia Inválida",
                    "La licencia ingresada no es válida para esta computadora.",
                )
                self.licencia_input.clear()
        except Exception as e:
            logging.error(f"Error al activar licencia: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{str(e)}")


class ActivationDialog(QDialog):
    """Diálogo de activación con tema adaptativo"""

    def __init__(self, parent=None):
        super().__init__(parent)
        store_name = get_store_name()
        self.setWindowTitle(f"Activación - {store_name}")
        self.setModal(True)
        self.activation_success = False

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(450, 380)

        titulo = QLabel(f"Activación de {store_name}")
        titulo.setStyleSheet(f"color: {c['primary']}; font-size: 18px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()

        machine_label = QLabel("Machine ID de esta computadora:")
        machine_label.setObjectName("machine_label")
        layout.addWidget(machine_label)

        machine_layout = QHBoxLayout()

        self.txt_machine_id = QLineEdit(machine_id)
        self.txt_machine_id.setReadOnly(True)
        self.txt_machine_id.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['surface']};
                color: {c['primary']};
                border: 1px solid {c['border']};
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 13px;
                font-weight: bold;
            }}
        """)
        machine_layout.addWidget(self.txt_machine_id)

        self.btn_copiar = QPushButton("📋 Copiar")
        self.btn_copiar.setStyleSheet(btn_secondary())
        self.btn_copiar.clicked.connect(self.copiar_machine_id)
        machine_layout.addWidget(self.btn_copiar)

        layout.addLayout(machine_layout)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setObjectName("info_label")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Licencia de 16 caracteres")
        self.licencia_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['background']};
                color: {c['text']};
                border: 2px solid {c['primary']};
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {c['primary_hover']};
            }}
        """)
        self.licencia_input.setMaxLength(16)
        layout.addWidget(self.licencia_input)

        btn_activar = QPushButton("ACTIVAR SISTEMA")
        btn_activar.setStyleSheet(btn_primary())
        btn_activar.clicked.connect(self.activar)
        layout.addWidget(btn_activar)

    def copiar_machine_id(self):
        """Copia el Machine ID al portapapeles"""
        QApplication.clipboard().setText(self.txt_machine_id.text())
        self.btn_copiar.setText("✅ Copiado")
        QTimer.singleShot(2000, lambda: self.btn_copiar.setText("📋 Copiar"))

    def activar(self):
        """Activa el sistema"""
        import logging

        try:
            licencia = self.licencia_input.text().strip().upper()

            if not licencia:
                QMessageBox.warning(self, "Error", "Ingrese una licencia")
                return

            if len(licencia) != 16:
                QMessageBox.warning(
                    self, "Error", "La licencia debe tener 16 caracteres"
                )
                return

            machine_id = get_machine_id()
            licencia_correcta = generar_licencia(machine_id)

            if licencia == licencia_correcta:
                guardar_licencia(licencia)
                QMessageBox.information(
                    self,
                    "Sistema Activado",
                    f"{get_store_name()} ha sido activado correctamente.\n\nEl sistema se cerrará. Vuélvelo a abrir.",
                )
                self.activation_success = True
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Licencia Inválida",
                    "La licencia ingresada no es válida para esta computadora.",
                )
                self.licencia_input.clear()
        except Exception as e:
            logging.error(f"Error al activar licencia: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{str(e)}")
