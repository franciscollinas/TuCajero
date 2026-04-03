"""Login Screen - TuCajero POS
PIN-based authentication with 4 separate boxes
Premium branded design with company logo
Minimalist SaaS + POS hybrid
"""

import os
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
from PySide6.QtGui import QColor, QPixmap


class PINBox(QLineEdit):
    """Single PIN digit input box"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxLength(1)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(56, 56)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                font-size: 20px;
                font-weight: 600;
                color: #0F172A;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
            }
        """)


class LoginView(QDialog):
    """PIN-based login screen for TuCajero POS with branding"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_seleccionado = None
        self.pin_boxes = []
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
        card.setFixedSize(380, 480)
        card.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        # Improved soft shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)

        # 1. Company Logo
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(
                40, 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_logo)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("background: transparent;")
            card_layout.addWidget(logo_label)
            card_layout.addSpacing(12)

        # 2. App name
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

        # 3. Active user with badge style
        user_container = QWidget()
        user_container.setStyleSheet("background: transparent;")
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        user_label = QLabel("Admin")
        user_label.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 15px;
                font-weight: 600;
                background-color: #F1F5F9;
                padding: 6px 16px;
                border-radius: 6px;
            }
        """)
        user_layout.addWidget(user_label)
        card_layout.addWidget(user_container)

        # Spacing before PIN section
        card_layout.addSpacing(8)

        # PIN label
        pin_label = QLabel("Ingresa tu PIN")
        pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pin_label.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
            }
        """)
        card_layout.addWidget(pin_label)

        # 4. PIN input - 4 separate boxes
        pin_layout = QHBoxLayout()
        pin_layout.setSpacing(12)
        pin_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i in range(4):
            pin_box = PINBox()
            pin_box.setObjectName(f"pin_box_{i}")
            self.pin_boxes.append(pin_box)
            pin_layout.addWidget(pin_box)

            # Auto-focus next box
            if i < 3:
                pin_box.textChanged.connect(lambda text, idx=i: self._on_pin_changed(text, idx))

        card_layout.addLayout(pin_layout)

        # Spacing after PIN
        card_layout.addSpacing(8)

        # 5. Primary button
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

        # 6. Footer
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

        # Focus on first PIN box
        self.pin_boxes[0].setFocus()

    def _on_pin_changed(self, text, index):
        """Auto-focus next PIN box when digit entered"""
        if text and index < 3:
            self.pin_boxes[index + 1].setFocus()
            self.pin_boxes[index + 1].selectAll()

    def get_pin(self):
        """Get complete PIN from all boxes"""
        return "".join(box.text() for box in self.pin_boxes)

    def login(self):
        """Handle PIN login"""
        pin = self.get_pin()

        if len(pin) != 4:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Ingresa un PIN de 4 dígitos")
            return

        # TODO: Implement PIN authentication logic
        # For now, accept any 4-digit PIN
        self.accept()
