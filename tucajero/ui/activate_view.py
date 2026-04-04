from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QDialog,
    QApplication,
)
from PySide6.QtCore import Qt, QTimer
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium
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
        self.setStyleSheet(f"background: {Colors.BG_APP};")

        titulo = QLabel(f"Activación de {store_name}")
        titulo.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()
        machine_label = QLabel("Machine ID:")
        machine_label.setStyleSheet(f"font-weight: bold; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(machine_label)

        self.machine_id_display = QLabel(machine_id)
        self.machine_id_display.setObjectName("machine_id_display")
        self.machine_id_display.setStyleSheet(f"color: {Colors.PRIMARY}; font-family: monospace; font-weight: bold; background: transparent;")
        self.machine_id_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.machine_id_display)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setObjectName("info_label")
        info_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; background: transparent;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Ingrese su licencia")
        self.licencia_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                padding: 10px 14px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.BORDER_FOCUS};
            }}
        """)
        self.licencia_input.setMaxLength(16)
        layout.addWidget(self.licencia_input)

        btn_layout = QHBoxLayout()
        self.btn_activar = ButtonPremium("ACTIVAR", style="primary")
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
    """Diálogo de activación con tema claro"""

    def __init__(self, parent=None):
        super().__init__(parent)
        store_name = get_store_name()
        self.setWindowTitle(f"Activación - {store_name}")
        self.setModal(True)
        self.activation_success = False
        self.setStyleSheet(f"background: {Colors.BG_APP};")

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(450, 380)

        titulo = QLabel(f"Activación de {store_name}")
        titulo.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: bold; background: transparent;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()

        machine_label = QLabel("Machine ID de esta computadora:")
        machine_label.setObjectName("machine_label")
        machine_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; background: transparent;")
        layout.addWidget(machine_label)

        machine_layout = QHBoxLayout()

        self.txt_machine_id = QLineEdit(machine_id)
        self.txt_machine_id.setReadOnly(True)
        self.txt_machine_id.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_ELEVATED};
                color: {Colors.PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.SM}px;
                padding: 8px;
                font-family: monospace;
                font-size: 13px;
                font-weight: bold;
            }}
        """)
        machine_layout.addWidget(self.txt_machine_id)

        self.btn_copiar = ButtonPremium("📋 Copiar", style="secondary")
        self.btn_copiar.clicked.connect(self.copiar_machine_id)
        machine_layout.addWidget(self.btn_copiar)

        layout.addLayout(machine_layout)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setObjectName("info_label")
        info_label.setStyleSheet(f"color: {Colors.TEXT_MUTED}; background: transparent;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Licencia de 16 caracteres")
        self.licencia_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.SM}px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.BORDER_FOCUS};
            }}
        """)
        self.licencia_input.setMaxLength(16)
        layout.addWidget(self.licencia_input)

        btn_activar = ButtonPremium("ACTIVAR SISTEMA", style="primary")
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
