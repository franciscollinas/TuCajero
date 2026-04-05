"""
PIN Setup Dialog — Forces admin to create a secure 4-digit PIN.
Validates against sequential, repetitive, and common PINs.
SEC-008 FIX
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt


# PINs that are NOT allowed
PIN_BLACKLIST = {
    "0000", "1111", "2222", "3333", "4444",
    "5555", "6666", "7777", "8888", "9999",
    "1234", "2345", "3456", "4567", "5678",
    "6789", "0123", "9876", "8765", "7654",
    "6543", "5432", "4321", "3210",
    "1212", "1313", "1414", "1515",
    "1000", "2000", "3000", "4000",
    "5000", "6000", "7000", "8000",
}


def es_pin_seguro(pin: str):
    """
    Validates a 4-digit PIN.
    Returns (is_valid, reason_if_invalid)
    """
    if len(pin) != 4 or not pin.isdigit():
        return False, "El PIN debe tener exactamente 4 digitos numericos."

    if pin in PIN_BLACKLIST:
        return False, "Este PIN es demasiado comun. Elija uno menos predecible."

    # Check all same digit
    if len(set(pin)) == 1:
        return False, "El PIN no puede tener todos los digitos iguales."

    # Check repeating pattern (ABAB)
    if len(pin) == 4 and pin[0] == pin[2] and pin[1] == pin[3]:
        return False, "El PIN no puede tener un patron repetitivo."

    # Check sequential ascending
    if all(int(pin[i+1]) == int(pin[i]) + 1 for i in range(3)):
        return False, "El PIN no puede ser una secuencia numerica."

    # Check sequential descending
    if all(int(pin[i+1]) == int(pin[i]) - 1 for i in range(3)):
        return False, "El PIN no puede ser una secuencia numerica invertida."

    return True, ""


class PinSetupDialog(QDialog):
    def __init__(self, session, cajero, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero = cajero
        self.pin_validado = False
        self._pin_creado = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Configuracion inicial - PIN de Administrador")
        self.setFixedSize(500, 450)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background: #0F172A;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(16)

        # Title
        title = QLabel("Crear PIN de Administrador")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #F8FAFC;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel(
            "Este PIN protegera el acceso administrativo.\n"
            "Elija uno que sea facil de recordar pero dificil de adivinar."
        )
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 14px;
                background: transparent;
            }
        """)
        layout.addWidget(subtitle)

        layout.addSpacing(12)

        # PIN Input 1
        lbl_pin1 = QLabel("Ingrese el nuevo PIN (4 digitos)")
        lbl_pin1.setStyleSheet(
            "color: #94A3B8; font-size: 12px; font-weight: 600; background: transparent;"
        )
        layout.addWidget(lbl_pin1)

        self.input_pin = QLineEdit()
        self.input_pin.setFixedHeight(45)
        self.input_pin.setMaxLength(4)
        self.input_pin.setPlaceholderText("....")
        self.input_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_pin.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.05);
                border: 2px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 28px;
                letter-spacing: 12px;
            }
            QLineEdit:focus {
                border-color: #8B5CF6;
            }
        """)
        layout.addWidget(self.input_pin)

        # PIN Input 2 (confirmation)
        lbl_pin2 = QLabel("Confirme el PIN (repitalo)")
        lbl_pin2.setStyleSheet(
            "color: #94A3B8; font-size: 12px; font-weight: 600; background: transparent; margin-top: 8px;"
        )
        layout.addWidget(lbl_pin2)

        self.input_pin_confirm = QLineEdit()
        self.input_pin_confirm.setFixedHeight(45)
        self.input_pin_confirm.setMaxLength(4)
        self.input_pin_confirm.setPlaceholderText("....")
        self.input_pin_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pin_confirm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_pin_confirm.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.05);
                border: 2px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 28px;
                letter-spacing: 12px;
            }
            QLineEdit:focus {
                border-color: #8B5CF6;
            }
        """)
        layout.addWidget(self.input_pin_confirm)

        # Status label
        self.lbl_estado = QLabel("")
        self.lbl_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_estado.setWordWrap(True)
        self.lbl_estado.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 12px;
                background: transparent;
                min-height: 40px;
            }
        """)
        layout.addWidget(self.lbl_estado)

        # Security tips
        tips = QLabel(
            "Reglas de seguridad:\n"
            "  No use secuencias (1234, 9876)\n"
            "  No use digitos repetidos (0000, 1111)\n"
            "  No use patrones (1212, 1313)"
        )
        tips.setAlignment(Qt.AlignmentFlag.AlignLeft)
        tips.setWordWrap(True)
        tips.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 11px;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px;
                padding: 10px 14px;
            }
        """)
        layout.addWidget(tips)

        layout.addSpacing(8)

        # Buttons
        btn_layout = QHBoxLayout()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(42)
        btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.05);
                color: #94A3B8;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        btn_confirmar = QPushButton("Confirmar PIN")
        btn_confirmar.setFixedHeight(42)
        btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirmar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #EC4899);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #A78BFA, stop:1 #F472B6);
            }
        """)
        btn_confirmar.clicked.connect(self.validar_pin)
        btn_layout.addWidget(btn_confirmar)

        layout.addLayout(btn_layout)

    def validar_pin(self):
        pin = self.input_pin.text().strip()
        pin_confirm = self.input_pin_confirm.text().strip()

        # Check length and numeric
        if len(pin) != 4 or not pin.isdigit():
            self.lbl_estado.setText("El PIN debe tener exactamente 4 digitos numericos.")
            self.lbl_estado.setStyleSheet(
                "QLabel { color: #EF4444; font-size: 12px; background: transparent; min-height: 40px; }"
            )
            self.input_pin.setFocus()
            return

        # Check security rules
        es_seguro, razon = es_pin_seguro(pin)
        if not es_seguro:
            self.lbl_estado.setText(razon)
            self.lbl_estado.setStyleSheet(
                "QLabel { color: #EF4444; font-size: 12px; background: transparent; min-height: 40px; }"
            )
            self.input_pin.clear()
            self.input_pin_confirm.clear()
            self.input_pin.setFocus()
            return

        # Check confirmation match
        if pin != pin_confirm:
            self.lbl_estado.setText("Los PIN no coinciden. Intente nuevamente.")
            self.lbl_estado.setStyleSheet(
                "QLabel { color: #EF4444; font-size: 12px; background: transparent; min-height: 40px; }"
            )
            self.input_pin_confirm.clear()
            self.input_pin_confirm.setFocus()
            return

        # PIN is valid - accept dialog
        self.pin_validado = True
        self._pin_creado = pin
        self.lbl_estado.setText("PIN configurado correctamente.")
        self.lbl_estado.setStyleSheet(
            "QLabel { color: #22C55E; font-size: 12px; background: transparent; min-height: 40px; }"
        )
        self.accept()

    def get_pin(self):
        """Returns the validated PIN after dialog acceptance."""
        return self._pin_creado
