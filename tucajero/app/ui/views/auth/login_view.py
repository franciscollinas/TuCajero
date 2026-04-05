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

from tucajero.ui.design_tokens import DarkColors as DC, Typography, Spacing, BorderRadius


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
        self.setStyleSheet(f"""
            QDialog {{
                background: {DC.BG_APP};
                border: none;
            }}
        """)

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        left_panel = self.create_left_panel()
        root_layout.addWidget(left_panel, 1)

        right_panel = self.create_right_panel()
        root_layout.addWidget(right_panel, 1)

    def create_left_panel(self):
        container = QWidget()
        container.setStyleSheet(f"background: {DC.BG_APP};")

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        center_wrapper = QWidget()
        center_wrapper.setMaximumWidth(420)
        center_layout = QVBoxLayout(center_wrapper)
        center_layout.setSpacing(16)

        avatar = QLabel("👤")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            QLabel {{
                font-size: 56px;
                background: rgba(139, 92, 246, 0.15);
                border: 3px solid {DC.PURPLE};
                border-radius: 50px;
                min-width: 100px;
                max-width: 100px;
                min-height: 100px;
                max-height: 100px;
            }}
        """)
        center_layout.addWidget(avatar, 0, Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Iniciar sesión")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {DC.TEXT_PRIMARY};
                font-size: {Typography.H3}px;
                font-weight: {Typography.BOLD};
                background: transparent;
            }}
        """)
        center_layout.addWidget(title)

        subtitle = QLabel("Sistema POS profesional")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {DC.TEXT_TERTIARY};
                font-size: {Typography.BODY}px;
                background: transparent;
            }}
        """)
        center_layout.addWidget(subtitle)

        center_layout.addSpacing(16)

        user_label = QLabel("Usuario")
        user_label.setStyleSheet(
            f"color: {DC.TEXT_TERTIARY}; font-size: {Typography.CAPTION}px; "
            f"font-weight: {Typography.SEMIBOLD}; background: transparent;"
        )
        center_layout.addWidget(user_label)

        self.combo_usuario = QComboBox()
        self.combo_usuario.setFixedHeight(40)
        self.combo_usuario.setStyleSheet(f"""
            QComboBox {{
                background-color: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: {BorderRadius.MD}px;
                padding: 8px 12px;
                color: white;
                font-size: {Typography.BODY}px;
            }}
            QComboBox:hover {{
                border-color: {DC.PURPLE};
            }}
            QComboBox:focus {{
                border-color: {DC.PURPLE};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {DC.TEXT_TERTIARY};
            }}
            QComboBox QAbstractItemView {{
                background: rgba(15, 23, 42, 0.98);
                color: white;
                border: 1px solid {DC.PURPLE};
                border-radius: {BorderRadius.MD}px;
                padding: 4px;
                selection-background-color: {DC.PURPLE};
            }}
        """)
        center_layout.addWidget(self.combo_usuario)

        pass_label = QLabel("Contraseña")
        pass_label.setStyleSheet(
            f"color: {DC.TEXT_TERTIARY}; font-size: {Typography.CAPTION}px; "
            f"font-weight: {Typography.SEMIBOLD}; background: transparent; margin-top: 8px;"
        )
        center_layout.addWidget(pass_label)

        self.input_pass = QLineEdit()
        self.input_pass.setFixedHeight(40)
        self.input_pass.setPlaceholderText("••••••••")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setStyleSheet(f"""
            QLineEdit {{
                background-color: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: {BorderRadius.MD}px;
                padding: 8px 12px;
                color: white;
                font-size: {Typography.BODY}px;
            }}
            QLineEdit:hover {{
                border-color: {DC.PURPLE};
            }}
            QLineEdit:focus {{
                border-color: {DC.PURPLE};
                background-color: rgba(255,255,255,0.08);
            }}
            QLineEdit::placeholder {{
                color: {DC.TEXT_MUTED};
            }}
        """)
        self.input_pass.returnPressed.connect(self.validar_login)
        center_layout.addWidget(self.input_pass)

        center_layout.addSpacing(16)

        btn_login = QPushButton("INICIAR SESIÓN")
        btn_login.setFixedHeight(45)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DC.PURPLE}, stop:1 #EC4899);
                color: white;
                border: none;
                border-radius: {BorderRadius.LG}px;
                padding: 12px 24px;
                font-size: {Typography.BODY}px;
                font-weight: {Typography.BOLD};
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {DC.PURPLE_LIGHT}, stop:1 #F472B6);
                color: white;
            }}
            QPushButton:pressed {{
                background: {DC.PURPLE_DARK};
            }}
        """)
        btn_login.clicked.connect(self.validar_login)
        center_layout.addWidget(btn_login)

        remember_check = QCheckBox("Recordarme")
        remember_check.setStyleSheet(f"""
            QCheckBox {{
                color: {DC.TEXT_TERTIARY};
                font-size: {Typography.BODY_SM}px;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid {DC.TEXT_MUTED};
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background: {DC.PURPLE};
                border-color: {DC.PURPLE};
            }}
        """)
        center_layout.addWidget(remember_check)

        forgot_label = QLabel("¿Olvidaste tu contraseña?")
        forgot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        forgot_label.setStyleSheet(f"""
            QLabel {{
                color: {DC.PURPLE};
                font-size: {Typography.BODY_SM}px;
                background: transparent;
                margin-top: 8px;
            }}
        """)
        center_layout.addWidget(forgot_label)

        center_layout.addStretch()

        layout.addWidget(center_wrapper, 0, Qt.AlignmentFlag.AlignCenter)

        return container

    def create_right_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {DC.PURPLE}, stop:1 {DC.INFO});
            }}
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)

        layout.addStretch()

        title = QLabel("Welcome.")
        title.setStyleSheet(f"""
            QLabel {{
                color: {DC.TEXT_PRIMARY};
                font-size: 52px;
                font-weight: {Typography.BOLD};
                background: transparent;
            }}
        """)
        layout.addWidget(title)

        subtitle = QLabel("Sistema de punto de venta profesional")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.75);
                font-size: {Typography.H5}px;
                background: transparent;
                margin-top: 8px;
            }}
        """)
        layout.addWidget(subtitle)

        layout.addStretch()

        return panel

    def cargar_cajeros(self):
        from tucajero.services.cajero_service import CajeroService

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

        from tucajero.services.cajero_service import CajeroService

        if CajeroService(self.session).verificar_login(cajero.id, password):
            self.cajero_seleccionado = cajero
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Contraseña incorrecta")
            self.input_pass.clear()
            self.input_pass.setFocus()
