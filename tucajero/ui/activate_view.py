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
from security.license_manager import (
    get_machine_id,
    generar_licencia,
    guardar_licencia,
    validar_licencia,
)
from utils.store_config import get_store_name
from utils.theme import texto_secundario, texto_terciario, fondo_widget, fondo_input


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
        subtitulo.setStyleSheet(f"color: {texto_secundario()}; padding-bottom: 20px;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()
        machine_label = QLabel(f"Machine ID:")
        machine_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(machine_label)

        self.machine_id_display = QLabel(machine_id)
        self.machine_id_display.setStyleSheet(
            f"background-color: {fondo_widget()}; padding: 10px; font-family: monospace; font-size: 14px;"
        )
        self.machine_id_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.machine_id_display)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setStyleSheet(
            f"color: {texto_secundario()}; font-size: 12px; padding: 8px;"
        )
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
        titulo.setStyleSheet("color: #4a9eff; font-size: 18px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setStyleSheet(
            f"color: {texto_terciario()}; font-size: 12px; padding-bottom: 10px;"
        )
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()

        machine_label = QLabel("Machine ID de esta computadora:")
        machine_label.setStyleSheet(
            f"font-weight: bold; color: {texto_terciario()}; margin-top: 10px;"
        )
        layout.addWidget(machine_label)

        machine_layout = QHBoxLayout()

        self.txt_machine_id = QLineEdit(machine_id)
        self.txt_machine_id.setReadOnly(True)
        self.txt_machine_id.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                color: #1a1a1a;
                border: 1px solid #999999;
                border-radius: 4px;
                padding: 8px;
                font-family: monospace;
                font-size: 13px;
                font-weight: bold;
            }
        """)
        machine_layout.addWidget(self.txt_machine_id)

        self.btn_copiar = QPushButton("📋 Copiar")
        self.btn_copiar.setFixedHeight(36)
        self.btn_copiar.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
        self.btn_copiar.clicked.connect(self.copiar_machine_id)
        machine_layout.addWidget(self.btn_copiar)

        layout.addLayout(machine_layout)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setStyleSheet(
            f"color: {texto_terciario()}; font-size: 12px; padding: 8px;"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Licencia de 16 caracteres")
        self.licencia_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #1a1a1a;
                border: 2px solid #0078d4;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #005a9e;
            }
        """)
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

    def copiar_machine_id(self):
        """Copia el Machine ID al portapapeles"""
        QApplication.clipboard().setText(self.txt_machine_id.text())
        self.btn_copiar.setText("✅ Copiado")
        QTimer.singleShot(2000, lambda: self.btn_copiar.setText("📋 Copiar"))

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
