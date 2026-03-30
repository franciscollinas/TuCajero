from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QFrame,
    QWidget,
    QCheckBox,
)
from PySide6.QtCore import Qt

from app.ui.theme.theme import app_style, PRIMARY, ACCENT, CARD_BG, CARD_BORDER


class LoginView(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_seleccionado = None
        self.init_ui()
        self.cargar_cajeros()

    def init_ui(self):
        self.setWindowTitle("TuCajero POS - Login")
        self.setFixedSize(1100, 650)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(app_style())

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        left_panel = self.create_left_panel()
        root_layout.addWidget(left_panel, 1)

        right_panel = self.create_right_panel()
        root_layout.addWidget(right_panel, 1)

    def create_left_panel(self):
        container = QWidget()
        container.setStyleSheet("background: #0F172A;")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        center_wrapper = QWidget()
        center_wrapper.setMaximumWidth(420)
        center_layout = QVBoxLayout(center_wrapper)
        center_layout.setSpacing(16)

        avatar = QLabel("👤")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            QLabel {
                font-size: 56px;
                background: rgba(124, 58, 237, 0.15);
                border: 3px solid #7C3AED;
                border-radius: 50px;
                min-width: 100px;
                max-width: 100px;
                min-height: 100px;
                max-height: 100px;
            }
        """)
        center_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Iniciar sesión")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        center_layout.addWidget(title)

        subtitle = QLabel("Sistema POS profesional")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 14px;
                background: transparent;
            }
        """)
        center_layout.addWidget(subtitle)

        center_layout.addSpacing(16)

        user_label = QLabel("Usuario")
        user_label.setStyleSheet(
            "color: #94A3B8; font-size: 12px; font-weight: 600; background: transparent;"
        )
        center_layout.addWidget(user_label)

        self.combo_usuario = QComboBox()
        self.combo_usuario.setFixedHeight(40)
        self.combo_usuario.setStyleSheet("""
            QComboBox {
                background-color: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 14px;
            }
            QComboBox:hover {
                border-color: #7C3AED;
            }
            QComboBox:focus {
                border-color: #7C3AED;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #94A3B8;
            }
            QComboBox QAbstractItemView {
                background: rgba(15, 23, 42, 0.98);
                color: white;
                border: 1px solid #7C3AED;
                border-radius: 8px;
                padding: 4px;
                selection-background-color: #7C3AED;
            }
        """)
        center_layout.addWidget(self.combo_usuario)

        pass_label = QLabel("Contraseña")
        pass_label.setStyleSheet(
            "color: #94A3B8; font-size: 12px; font-weight: 600; background: transparent; margin-top: 8px;"
        )
        center_layout.addWidget(pass_label)

        self.input_pass = QLineEdit()
        self.input_pass.setFixedHeight(40)
        self.input_pass.setPlaceholderText("••••••••")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:hover {
                border-color: #7C3AED;
            }
            QLineEdit:focus {
                border-color: #7C3AED;
                background-color: rgba(255,255,255,0.08);
            }
            QLineEdit::placeholder {
                color: #64748B;
            }
        """)
        self.input_pass.returnPressed.connect(self.validar_login)
        center_layout.addWidget(self.input_pass)

        center_layout.addSpacing(16)

        btn_login = QPushButton("INICIAR SESIÓN")
        btn_login.setFixedHeight(45)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C3AED, stop:1 #EC4899);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B5CF6, stop:1 #F472B6);
            }
            QPushButton:pressed {
                background: #6D28D9;
            }
        """)
        btn_login.clicked.connect(self.validar_login)
        center_layout.addWidget(btn_login)

        remember_check = QCheckBox("Recordarme")
        remember_check.setStyleSheet("""
            QCheckBox {
                color: #94A3B8;
                font-size: 13px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #64748B;
                background: transparent;
            }
            QCheckBox::indicator:checked {
                background: #7C3AED;
                border-color: #7C3AED;
            }
        """)
        center_layout.addWidget(remember_check)

        forgot_label = QLabel("¿Olvidaste tu contraseña?")
        forgot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        forgot_label.setStyleSheet("""
            QLabel {
                color: #7C3AED;
                font-size: 13px;
                background: transparent;
                margin-top: 8px;
            }
        """)
        center_layout.addWidget(forgot_label)

        center_layout.addStretch()

        layout.addWidget(center_wrapper, 0, Qt.AlignmentFlag.AlignCenter)

        return container

    def create_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7C3AED, stop:1 #06B6D4);
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)

        layout.addStretch()

        title = QLabel("Welcome.")
        title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 52px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel("Sistema de punto de venta profesional")
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.75);
                font-size: 16px;
                background: transparent;
                margin-top: 8px;
            }
        """)
        layout.addWidget(subtitle)

        layout.addStretch()

        return panel

    def cargar_cajeros(self):
        from services.cajero_service import CajeroService

        cajeros = CajeroService(self.session).get_all()
        cajeros_activos = [c for c in cajeros if c.activo]

        self.combo_usuario.clear()
        for cajero in cajeros_activos:
            rol = " (Admin)" if cajero.rol == "admin" else ""
            self.combo_usuario.addItem(f"{cajero.nombre}{rol}", cajero)

        if self.combo_usuario.count() == 0:
            self.combo_usuario.addItem("Administrador", None)

    def validar_login(self):
        from PySide6.QtWidgets import QMessageBox

        password = self.input_pass.text().strip()

        if not password:
            QMessageBox.warning(self, "Error", "Por favor ingresa tu contraseña")
            return

        cajero = self.combo_usuario.currentData()

        if not cajero:
            QMessageBox.warning(
                self, "Error", "No se pudo obtener información del cajero"
            )
            return

        from services.cajero_service import CajeroService

        if CajeroService(self.session).verificar_login(cajero.id, password):
            self.cajero_seleccionado = cajero
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Contraseña incorrecta")
            self.input_pass.clear()
            self.input_pass.setFocus()
