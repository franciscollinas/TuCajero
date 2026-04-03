"""Login Screen - TuCajero POS
Premium PIN-based authentication with enhanced contrast and depth
High-end SaaS aesthetic with clear visual hierarchy
Fixed rendering using QDialog with proper attributes
"""

import os
import sys
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QGraphicsDropShadowEffect,
    QMessageBox,
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QPixmap


def get_logo_path():
    """Get logo path that works in both dev and compiled EXE"""
    if getattr(sys, "frozen", False):
        # Running as compiled EXE
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        logo = os.path.join(base, "tucajero", "assets", "icons", "logo.png")
    else:
        # Running as script
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo = os.path.join(base, "assets", "icons", "logo.png")
    return logo if os.path.exists(logo) else ""


class PINBox(QPushButton):
    """Tactile PIN digit input box with enhanced contrast states"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.setCheckable(True)
        self._value = ""
        self._focused = False
        self._hovered = False
        
        self.update_style()
        self.clicked.connect(self._on_click)

    def _on_click(self):
        self._focused = True
        self.update_style()

    def update_style(self):
        if self._focused:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 2px solid #2563EB;
                    border-radius: 10px;
                    font-size: 24px;
                    font-weight: 700;
                    color: #0F172A;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #F1F5F9;
                }
            """)
        elif self._hovered:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #94A3B8;
                    border-radius: 10px;
                    font-size: 24px;
                    font-weight: 700;
                    color: #0F172A;
                    padding: 0px;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #CBD5E1;
                    border-radius: 10px;
                    font-size: 24px;
                    font-weight: 700;
                    color: #0F172A;
                    padding: 0px;
                }
                QPushButton:hover {
                    border: 1px solid #94A3B8;
                }
            """)

    def enterEvent(self, event):
        self._hovered = True
        self.update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update_style()
        super().leaveEvent(event)

    def set_value(self, value):
        self._value = str(value) if value else ""
        self.setText("•" if self._value else "")

    def clear(self):
        self._value = ""
        self.setText("")

    def get_value(self):
        return self._value


class LoginView(QDialog):
    """Premium PIN-based login screen with modern SaaS layout"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_seleccionado = None
        self.pin_boxes = []
        self.current_box = 0

        # Window configuration for modern SaaS layout
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowSystemMenuHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setModal(True)

        self.init_ui()

    def init_ui(self):
        # 1. WINDOW SIZE - Responsive, not fullscreen
        self.resize(1280, 800)
        self.setMinimumSize(1024, 720)

        # 2. ROOT BACKGROUND - Transparent (only card visible)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("""
            QDialog {
                background: transparent;
                border: none;
            }
        """)

        # 3. MAIN LAYOUT - Centering system
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 4. CONTENT CONTAINER - Compact width for focus
        container = QWidget()
        container.setFixedWidth(360)
        container.setStyleSheet("background: transparent;")

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 5. LOGIN CARD - Professional design
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 16)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(0)

        # ═══════════════════════════════════════
        # SPACING SYSTEM - Refined SaaS pattern
        # ═══════════════════════════════════════

        # BRAND BLOCK - Logo at top (includes brand name + tagline)
        card_layout.addSpacing(24)
        logo_path = get_logo_path()
        if logo_path:
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(
                240, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_logo)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("background: transparent; border: none;")
            card_layout.addWidget(logo_label)
            card_layout.addSpacing(28)

        # USER BADGE - Refined
        user_container = QWidget()
        user_container.setStyleSheet("background: transparent;")
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_label = QLabel("👤 Admin")
        user_label.setStyleSheet(
            "QLabel { "
            "color: #0F172A; "
            "font-size: 13px; "
            "font-weight: 500; "
            "background-color: #F1F5F9; "
            "border: 1px solid #E2E8F0; "
            "padding: 6px 12px; "
            "border-radius: 8px; "
            "}"
        )
        user_layout.addWidget(user_label)
        card_layout.addWidget(user_container)
        card_layout.addSpacing(32)

        # PIN LABEL - Hero section
        pin_label = QLabel("Enter your PIN")
        pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pin_label.setStyleSheet(
            "QLabel { "
            "color: #64748B; "
            "font-size: 13px; "
            "font-weight: 400; "
            "background: transparent; "
            "}"
        )
        card_layout.addWidget(pin_label)
        card_layout.addSpacing(20)

        # PIN BOXES (4 digits) - Main interaction
        pin_layout = QHBoxLayout()
        pin_layout.setSpacing(16)
        pin_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for i in range(4):
            pin_box = PINBox()
            pin_box.setObjectName(f"pin_box_{i}")
            self.pin_boxes.append(pin_box)
            pin_layout.addWidget(pin_box)
        card_layout.addLayout(pin_layout)
        card_layout.addSpacing(32)

        # ACCESS BUTTON - Premium feel
        self.login_btn = QPushButton("Acceder")
        self.login_btn.setFixedHeight(52)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2563EB, stop:1 #1D4ED8);
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1D4ED8, stop:1 #1E40AF);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1E40AF, stop:1 #1E3A8A);
            }
        """)
        self.login_btn.clicked.connect(self.login)
        card_layout.addWidget(self.login_btn)

        # FOOTER
        card_layout.addSpacing(24)
        footer = QLabel("Secure access to your sales system")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "QLabel { "
            "color: #94A3B8; "
            "font-size: 12px; "
            "background: transparent; "
            "}"
        )
        card_layout.addWidget(footer)

        # Add card to container
        container_layout.addWidget(card)

        # Add container to main layout
        main_layout.addWidget(container)

        # Focus first PIN box
        self.pin_boxes[0].setFocus()
        self.pin_boxes[0]._focused = True
        self.pin_boxes[0].update_style()

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                self._enter_digit(str(key - Qt.Key.Key_0))
                return True
            elif key == Qt.Key.Key_Backspace:
                self._delete_digit()
                return True
            elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.login()
                return True
        return super().eventFilter(obj, event)

    def _enter_digit(self, digit):
        if self.current_box < 4:
            self.pin_boxes[self.current_box].set_value(digit)
            self.pin_boxes[self.current_box]._focused = False
            self.pin_boxes[self.current_box].update_style()
            self.current_box += 1
            if self.current_box < 4:
                self.pin_boxes[self.current_box]._focused = True
                self.pin_boxes[self.current_box].update_style()

    def _delete_digit(self):
        if self.current_box > 0:
            self.current_box -= 1
            self.pin_boxes[self.current_box].clear()
            self.pin_boxes[self.current_box]._focused = True
            self.pin_boxes[self.current_box].update_style()

    def get_pin(self):
        return "".join(box.get_value() for box in self.pin_boxes)

    def login(self):
        pin = self.get_pin()
        if len(pin) != 4:
            QMessageBox.warning(self, "Error", "Ingresa un PIN de 4 dígitos")
            return

        # Authenticate PIN against database
        from tucajero.services.cajero_service import CajeroService
        from tucajero.models.cajero import Cajero

        cajero_service = CajeroService(self.session)

        # Ensure default admin exists
        cajero_service.crear_admin_default()

        # Try to find a cajero with matching PIN
        cajeros = cajero_service.get_all()
        cajero_encontrado = None

        for cajero in cajeros:
            if cajero.verificar_pin(pin):
                cajero_encontrado = cajero
                break

        if not cajero_encontrado:
            QMessageBox.warning(self, "Error", "PIN incorrecto. Intenta de nuevo.")
            # Clear PIN boxes
            for box in self.pin_boxes:
                box.clear()
            self.current_box = 0
            self.pin_boxes[0]._focused = True
            self.pin_boxes[0].update_style()
            return

        # Login successful
        self.cajero_seleccionado = cajero_encontrado
        self.accept()
