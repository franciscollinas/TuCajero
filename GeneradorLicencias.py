import sys
import hashlib
import base64
import threading
import time
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor

_S = b"dGl0b19jYXN0aWxsYV9wb3Nfc2VjcmV0"
SECRET = base64.b64decode(_S).decode()


def generar_licencia(machine_id):
    return hashlib.sha256((machine_id + SECRET).encode()).hexdigest()[:16].upper()


class GeneradorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Licencias — TuCajero")
        self.setFixedSize(460, 360)
        self._licencia_actual = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        self.setLayout(layout)

        titulo = QLabel("Generador de Licencias — TuCajero")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2c3e50; padding: 8px;"
        )
        layout.addWidget(titulo)

        subtitulo = QLabel("Solo para uso del administrador")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        layout.addWidget(subtitulo)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #ecf0f1;")
        layout.addWidget(sep)

        lbl_input = QLabel("Machine ID del cliente:")
        lbl_input.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #2c3e50; margin-top: 8px;"
        )
        layout.addWidget(lbl_input)

        self.input_machine = QLineEdit()
        self.input_machine.setPlaceholderText("Pega aquí el Machine ID del cliente...")
        self.input_machine.setMinimumHeight(38)
        self.input_machine.setStyleSheet(
            "font-size: 13px; font-family: Consolas, monospace;"
            "padding: 6px 10px; border: 1px solid #bdc3c7; border-radius: 6px;"
        )
        self.input_machine.returnPressed.connect(self.generar)
        layout.addWidget(self.input_machine)

        self.btn_generar = QPushButton("Generar Licencia")
        self.btn_generar.setMinimumHeight(42)
        self.btn_generar.setStyleSheet(
            "QPushButton {"
            "background-color: #2c3e50; color: white;"
            "font-size: 14px; font-weight: bold;"
            "border-radius: 6px; border: none; padding: 8px;"
            "}"
            "QPushButton:hover { background-color: #34495e; }"
            "QPushButton:pressed { background-color: #1a252f; }"
        )
        self.btn_generar.clicked.connect(self.generar)
        layout.addWidget(self.btn_generar)

        lbl_resultado_titulo = QLabel("Licencia generada:")
        lbl_resultado_titulo.setStyleSheet(
            "font-size: 12px; color: #7f8c8d; margin-top: 8px;"
        )
        layout.addWidget(lbl_resultado_titulo)

        self.lbl_resultado = QLabel("—")
        self.lbl_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_resultado.setMinimumHeight(52)
        self.lbl_resultado.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
            "font-family: Consolas, monospace;"
            "color: #2c3e50; letter-spacing: 2px;"
            "background-color: #f8f9fa;"
            "border: 1px solid #dee2e6; border-radius: 6px;"
            "padding: 8px;"
        )
        layout.addWidget(self.lbl_resultado)

        self.btn_copiar = QPushButton("Copiar licencia")
        self.btn_copiar.setMinimumHeight(36)
        self.btn_copiar.setEnabled(False)
        self.btn_copiar.setStyleSheet(
            "QPushButton {"
            "background-color: #27ae60; color: white;"
            "font-size: 13px; font-weight: bold;"
            "border-radius: 6px; border: none; padding: 6px;"
            "}"
            "QPushButton:hover { background-color: #2ecc71; }"
            "QPushButton:disabled { background-color: #bdc3c7; color: #ecf0f1; }"
        )
        self.btn_copiar.clicked.connect(self.copiar)
        layout.addWidget(self.btn_copiar)

        self.input_machine.setFocus()

    def generar(self):
        machine_id = self.input_machine.text().strip()
        if not machine_id:
            QMessageBox.warning(
                self, "Campo vacío", "Ingresa el Machine ID del cliente."
            )
            return
        if len(machine_id) < 4:
            QMessageBox.warning(
                self,
                "Machine ID inválido",
                "El código parece muy corto. Verifica que sea el completo.",
            )
            return
        licencia = generar_licencia(machine_id)
        self._licencia_actual = licencia
        self.lbl_resultado.setText(licencia)
        self.lbl_resultado.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
            "font-family: Consolas, monospace;"
            "color: #27ae60; letter-spacing: 2px;"
            "background-color: #f0fff4;"
            "border: 1px solid #27ae60; border-radius: 6px;"
            "padding: 8px;"
        )
        self.btn_copiar.setEnabled(True)

    def copiar(self):
        if not self._licencia_actual:
            return
        QApplication.clipboard().setText(self._licencia_actual)
        self.btn_copiar.setText("Copiado ✓")
        QTimer.singleShot(1500, lambda: self.btn_copiar.setText("Copiar licencia"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = GeneradorWindow()
    window.show()
    sys.exit(app.exec())
