"""Login Screen - TuCajero POS
Minimalist SaaS design (Stripe/Linear style)
Light mode only - Clean, calm, professional
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QWidget,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class LoginView(QDialog):
    """Minimalist login screen for TuCajero POS"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_seleccionado = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("TuCajero POS - Login")
        self.setFixedSize(1200, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Background
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
        """)

        # Main layout - centered
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login card
        card = QWidget()
        card.setFixedSize(380, 520)
        card.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        # Subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 12))  # Very subtle black with low alpha
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)

        # 1. App name
        app_name = QLabel("TuCajero POS")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 19px;
                font-weight: 600;
                background: transparent;
            }
        """)
        card_layout.addWidget(app_name)

        # 2. Title
        title = QLabel("Iniciar sesión")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 23px;
                font-weight: 600;
                background: transparent;
            }
        """)
        card_layout.addWidget(title)

        # 3. Subtitle
        subtitle = QLabel("Accede a tu sistema de ventas")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 14px;
                background: transparent;
            }
        """)
        card_layout.addWidget(subtitle)

        # 4. Input fields
        inputs_layout = QVBoxLayout()
        inputs_layout.setSpacing(16)

        # Email input
        email_label = QLabel("Correo electrónico")
        email_label.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }
        """)
        inputs_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("tu@correo.com")
        self.email_input.setFixedHeight(48)
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                color: #0F172A;
            }
            QLineEdit:focus {
                border: 1px solid #2563EB;
            }
        """)
        inputs_layout.addWidget(self.email_input)

        # Password input
        password_label = QLabel("Contraseña")
        password_label.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }
        """)
        inputs_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(48)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                color: #0F172A;
            }
            QLineEdit:focus {
                border: 1px solid #2563EB;
            }
        """)
        self.password_input.returnPressed.connect(self.login)
        inputs_layout.addWidget(self.password_input)

        card_layout.addLayout(inputs_layout)

        # 5. Primary button
        self.login_btn = QPushButton("Ingresar")
        self.login_btn.setFixedHeight(48)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
        """)
        self.login_btn.clicked.connect(self.login)
        card_layout.addWidget(self.login_btn)

        # 6. Secondary link
        forgot_link = QLabel("¿Olvidaste tu contraseña?")
        forgot_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        forgot_link.setStyleSheet("""
            QLabel {
                color: #2563EB;
                font-size: 14px;
                background: transparent;
            }
        """)
        forgot_link.setCursor(Qt.CursorShape.PointingHandCursor)
        card_layout.addWidget(forgot_link)

        # 7. Footer text
        footer = QLabel("Sistema seguro para gestión de ventas")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 12px;
                background: transparent;
            }
        """)
        card_layout.addWidget(footer)

        main_layout.addWidget(card)

    def login(self):
        """Handle login"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Completa todos los campos")
            return

        # TODO: Implement authentication logic
        # For now, accept any login
        self.accept()
