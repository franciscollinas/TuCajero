from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QGridLayout,
    QLineEdit,
)
from PySide6.QtCore import Qt


class LoginCajeroDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_seleccionado = None
        self.setWindowTitle("TuCajero — Iniciar turno")
        self.setMinimumSize(500, 550)
        self.setModal(True)
        self.pin_ingresado = ""
        self.init_ui()
        self.cargar_cajeros()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50; padding: 20px;")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        titulo = QLabel("TuCajero POS")
        titulo.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(titulo)

        subtitulo = QLabel("Selecciona tu nombre e ingresa tu PIN")
        subtitulo.setObjectName("subtitulo")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitulo)
        layout.addWidget(header)

        cajeros_label = QLabel("¿Quién eres?")
        cajeros_label.setStyleSheet(
            "font-size: 15px; font-weight: bold; padding: 10px 20px 5px;"
        )
        layout.addWidget(cajeros_label)

        self.cajeros_widget = QWidget()
        self.cajeros_layout = QGridLayout()
        self.cajeros_widget.setLayout(self.cajeros_layout)
        layout.addWidget(self.cajeros_widget)

        self.lbl_cajero_sel = QLabel("Selecciona un cajero")
        self.lbl_cajero_sel.setObjectName("lbl_cajero_sel")
        self.lbl_cajero_sel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_cajero_sel)

        self.pin_display = QLineEdit()
        self.pin_display.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_display.setMaxLength(4)
        self.pin_display.setReadOnly(True)
        self.pin_display.setPlaceholderText("PIN")
        self.pin_display.setStyleSheet(
            "font-size: 32px; padding: 10px; text-align: center; "
            "border: 2px solid #bdc3c7; border-radius: 6px; "
            "letter-spacing: 8px;"
        )
        self.pin_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.pin_display)

        teclado = QWidget()
        teclado_layout = QGridLayout()
        teclado.setLayout(teclado_layout)

        numeros = [
            ("1", 0, 0),
            ("2", 0, 1),
            ("3", 0, 2),
            ("4", 1, 0),
            ("5", 1, 1),
            ("6", 1, 2),
            ("7", 2, 0),
            ("8", 2, 1),
            ("9", 2, 2),
            ("⌫", 3, 0),
            ("0", 3, 1),
            ("✓", 3, 2),
        ]
        for texto, fila, col in numeros:
            btn = QPushButton(texto)
            btn.setFixedSize(90, 60)
            if texto == "✓":
                btn.setStyleSheet(
                    "background:#27ae60;color:white;"
                    "font-size:22px;font-weight:bold;border-radius:6px;"
                )
            elif texto == "⌫":
                btn.setStyleSheet(
                    "background:#e74c3c;color:white;font-size:22px;border-radius:6px;"
                )
            else:
                btn.setStyleSheet(
                    "background:#ecf0f1;color:#2c3e50;"
                    "font-size:22px;font-weight:bold;border-radius:6px;"
                )
            btn.clicked.connect(lambda checked, t=texto: self.on_tecla(t))
            teclado_layout.addWidget(btn, fila, col)

        layout.addWidget(teclado, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #e74c3c; font-size: 13px; padding: 4px;")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_error)

    def cargar_cajeros(self):
        from services.cajero_service import CajeroService

        cajeros = CajeroService(self.session).get_all()

        for i in reversed(range(self.cajeros_layout.count())):
            self.cajeros_layout.itemAt(i).widget().setParent(None)

        col = 0
        fila = 0
        for cajero in cajeros:
            btn = QPushButton(cajero.nombre)
            btn.setFixedSize(140, 50)
            if cajero.rol == "admin":
                btn.setStyleSheet("""
                    QPushButton {
                        background:#2c3e50;color:white;
                        font-size:14px;font-weight:bold;
                        border-radius:6px;
                    }
                    QPushButton:checked {
                        background:#3498db;border:2px solid white;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background:#ecf0f1;color:#2c3e50;
                        font-size:14px;border-radius:6px;
                    }
                    QPushButton:checked {
                        background:#3498db;color:white;
                        border:2px solid #2980b9;
                    }
                """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=cajero: self.seleccionar_cajero(c))
            self.cajeros_layout.addWidget(btn, fila, col)
            col += 1
            if col >= 3:
                col = 0
                fila += 1

    def seleccionar_cajero(self, cajero):
        self.cajero_seleccionado = cajero
        self.pin_ingresado = ""
        self.pin_display.clear()
        self.lbl_cajero_sel.setText(f"Hola, {cajero.nombre} 👋  —  Ingresa tu PIN")
        self.lbl_error.setText("")

    def on_tecla(self, tecla):
        if tecla == "⌫":
            self.pin_ingresado = self.pin_ingresado[:-1]
            self.pin_display.setText(self.pin_ingresado)
        elif tecla == "✓":
            self.confirmar_login()
        else:
            if len(self.pin_ingresado) < 4:
                self.pin_ingresado += tecla
                self.pin_display.setText(self.pin_ingresado)
                if len(self.pin_ingresado) == 4:
                    self.confirmar_login()

    def confirmar_login(self):
        if not self.cajero_seleccionado:
            self.lbl_error.setText("⚠ Selecciona un cajero primero")
            return
        if len(self.pin_ingresado) != 4:
            self.lbl_error.setText("⚠ El PIN debe tener 4 dígitos")
            return
        from services.cajero_service import CajeroService

        ok = CajeroService(self.session).verificar_login(
            self.cajero_seleccionado.id, self.pin_ingresado
        )
        if ok:
            self.accept()
        else:
            self.lbl_error.setText("❌ PIN incorrecto. Intenta de nuevo.")
            self.pin_ingresado = ""
            self.pin_display.clear()
