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
    QLineEdit,
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QPixmap


def get_logo_path():
    """Get logo path that works in both dev and compiled EXE"""
    if getattr(sys, "frozen", False):
        # Running as compiled EXE - assets are at _MEIPASS/assets/
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        logo = os.path.join(base, "assets", "icons", "logo.png")
    else:
        # Running as script
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo = os.path.join(base, "assets", "icons", "logo.png")
    return logo if os.path.exists(logo) else ""


class PINBox(QPushButton):
    """Tactile PIN digit input box with smooth transitions"""

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

    def set_focus_state(self, focused):
        """Smoothly transition focus state"""
        self._focused = focused
        self.update_style()

    def update_style(self):
        if self._focused:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #DBEAFE;
                    border: 2px solid #2563EB;
                    border-radius: 10px;
                    font-size: 24px;
                    font-weight: 700;
                    color: #0F172A;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #DBEAFE;
                }
            """)
        elif self._hovered:
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
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                    font-size: 24px;
                    font-weight: 700;
                    color: #0F172A;
                    padding: 0px;
                }
                QPushButton:hover {
                    border: 1px solid #CBD5E1;
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

        # 5. LOGIN CARD - Professional design with shadow
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
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(15, 23, 42, 20))  # rgba(15, 23, 42, 0.08)
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

        # USERNAME INPUT
        username_input = QLineEdit()
        username_input.setPlaceholderText("👤 Usuario")
        username_input.setFixedHeight(44)
        username_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                color: #0F172A;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
            }
        """)
        self.username_input = username_input
        card_layout.addWidget(username_input)
        card_layout.addSpacing(20)

        # PIN LABEL - Hero section
        pin_label = QLabel("Ingresa tu PIN")
        pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pin_label.setStyleSheet(
            "QLabel { "
            "color: #64748B; "
            "font-size: 14px; "
            "font-weight: 400; "
            "background: transparent; "
            "border: none; "
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

        # ACCESS BUTTON - Premium feel with micro-interactions
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
        footer = QLabel("Acceso seguro al sistema de ventas")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(
            "QLabel { "
            "color: #64748B; "
            "font-size: 12px; "
            "font-weight: 600; "
            "background: transparent; "
            "padding: 8px 12px; "
            "border: 1px solid #E2E8F0; "
            "border-radius: 6px; "
            "}"
        )
        card_layout.addWidget(footer)

        # Add card to container
        container_layout.addWidget(card)

        # Add container to main layout
        main_layout.addWidget(container)

        # Focus first PIN box with smooth animation
        self.pin_boxes[0].setFocus()
        self.pin_boxes[0].set_focus_state(True)

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
            # Blur current box smoothly
            if self.current_box > 0:
                self.pin_boxes[self.current_box - 1].set_focus_state(False)
            
            self.pin_boxes[self.current_box].set_value(digit)
            self.pin_boxes[self.current_box].set_focus_state(False)
            self.current_box += 1
            
            # Focus next box smoothly
            if self.current_box < 4:
                self.pin_boxes[self.current_box].set_focus_state(True)

    def _delete_digit(self):
        if self.current_box > 0:
            # Blur current box
            self.pin_boxes[self.current_box].set_focus_state(False)
            self.current_box -= 1
            
            # Clear and focus previous box smoothly
            self.pin_boxes[self.current_box].clear()
            self.pin_boxes[self.current_box].set_focus_state(True)

    def get_pin(self):
        return "".join(box.get_value() for box in self.pin_boxes)

    def login(self):
        pin = self.get_pin()
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Error", "Ingresa tu nombre de usuario")
            self.username_input.setFocus()
            return
            
        if len(pin) != 4:
            QMessageBox.warning(self, "Error", "Ingresa un PIN de 4 dígitos")
            return

        # Authenticate user by username and PIN
        from tucajero.services.cajero_service import CajeroService

        cajero_service = CajeroService(self.session)
        cajero_service.crear_admin_default()

        # Find user by name (case-insensitive)
        cajeros = cajero_service.get_all()
        cajero_encontrado = None
        
        for cajero in cajeros:
            if cajero.nombre.lower() == username.lower():
                if cajero.verificar_pin(pin):
                    cajero_encontrado = cajero
                break

        if not cajero_encontrado:
            QMessageBox.warning(self, "Error", "PIN incorrecto. Intenta de nuevo.")
            # Clear PIN boxes with smooth transitions
            for box in self.pin_boxes:
                box.clear()
                box.set_focus_state(False)
            self.current_box = 0
            self.pin_boxes[0].set_focus_state(True)
            return

        # Login successful
        self.cajero_seleccionado = cajero_encontrado
        self.accept()
