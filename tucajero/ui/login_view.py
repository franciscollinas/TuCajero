"""Login Screen - TuCajero POS
PIN-based authentication for cashiers
Minimalist SaaS + POS hybrid design
Light mode with subtle gradient
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
from PySide6.QtGui import QColor


class LoginView(QDialog):
    """PIN-based login screen for TuCajero POS"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_seleccionado = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("TuCajero POS - Login")
        self.setFixedSize(1200, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Background with subtle gradient
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8FAFC, stop:1 #EEF2FF);
            }
        """)

        # Main layout - centered
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login card
        card = QWidget()
        card.setFixedSize(360, 420)
        card.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        # Soft shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 15))
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
                font-size: 18px;
                font-weight: 600;
                background: transparent;
            }
        """)
        card_layout.addWidget(app_name)

        # 2. Active user
        user_label = QLabel("Admin")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_label.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 14px;
                background: transparent;
            }
        """)
        card_layout.addWidget(user_label)

        # 3. PIN input
        pin_label = QLabel("Ingresa tu PIN")
        pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pin_label.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }
        """)
        card_layout.addWidget(pin_label)

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("••••")
        self.pin_input.setMaxLength(4)
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pin_input.setFixedHeight(56)
        self.pin_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                font-size: 20px;
                font-weight: 600;
                color: #0F172A;
                letter-spacing: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #2563EB;
            }
        """)
        self.pin_input.returnPressed.connect(self.login)
        card_layout.addWidget(self.pin_input)

        # 4. Primary button
        self.login_btn = QPushButton("Acceder")
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

        # 5. Footer
        footer = QLabel("Acceso seguro al sistema de ventas")
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

        # Focus on PIN input
        self.pin_input.setFocus()

    def login(self):
        """Handle PIN login"""
        pin = self.pin_input.text().strip()

        if not pin or len(pin) != 4:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Ingresa un PIN de 4 dígitos")
            return

        # TODO: Implement PIN authentication logic
        # For now, accept any 4-digit PIN
        self.accept()
