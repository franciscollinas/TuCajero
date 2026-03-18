from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QDialog,
)
from PySide6.QtCore import Qt
from security.license_manager import (
    get_machine_id,
    generar_licencia,
    guardar_licencia,
    validar_licencia,
)
from utils.store_config import get_store_name


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
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setStyleSheet("color: #7f8c8d; padding-bottom: 20px;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()
        machine_label = QLabel(f"Machine ID:")
        machine_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(machine_label)

        self.machine_id_display = QLabel(machine_id)
        self.machine_id_display.setStyleSheet(
            "background-color: #ecf0f1; padding: 10px; font-family: monospace; font-size: 14px;"
        )
        self.machine_id_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.machine_id_display)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 8px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Ingrese su licencia")
        self.licencia_input.setStyleSheet("padding: 10px; font-size: 16px;")
        self.licencia_input.setMaxLength(16)
        layout.addWidget(self.licencia_input)

        btn_layout = QHBoxLayout()

        self.btn_activar = QPushButton("ACTIVAR")
        self.btn_activar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_activar.clicked.connect(self.activar)
        btn_layout.addWidget(self.btn_activar)

        layout.addLayout(btn_layout)

    def activar(self):
        """Activa el sistema con la licencia"""
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


class ActivationDialog(QDialog):
    """Diálogo de activación"""

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
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setStyleSheet("color: #7f8c8d; padding-bottom: 10px;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()

        machine_label = QLabel("Machine ID de esta computadora:")
        machine_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(machine_label)

        self.machine_id_display = QLabel(machine_id)
        self.machine_id_display.setStyleSheet(
            "background-color: #ecf0f1; padding: 10px; font-family: monospace; font-size: 12px;"
        )
        self.machine_id_display.setWordWrap(True)
        layout.addWidget(self.machine_id_display)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 8px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Ingrese su licencia de 16 caracteres")
        self.licencia_input.setStyleSheet("padding: 10px; font-size: 14px;")
        self.licencia_input.setMaxLength(16)
        layout.addWidget(self.licencia_input)

        btn_activar = QPushButton("ACTIVAR SISTEMA")
        btn_activar.setStyleSheet("""
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
        btn_activar.clicked.connect(self.activar)
        layout.addWidget(btn_activar)

    def activar(self):
        """Activa el sistema"""
        licencia = self.licencia_input.text().strip().upper()

        if not licencia:
            QMessageBox.warning(self, "Error", "Ingrese una licencia")
            return

        if len(licencia) != 16:
            QMessageBox.warning(self, "Error", "La licencia debe tener 16 caracteres")
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
