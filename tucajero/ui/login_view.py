"""Login Screen - TuCajero POS
Premium PIN-based authentication with refined visual depth
High-end SaaS aesthetic with subtle tactile interactions
"""

import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QColor, QPixmap, QPalette, QLinearGradient, QRadialGradient, QBrush


class PINBox(QPushButton):
    """Tactile PIN digit input box with hover/focus states"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(56, 56)
        self.setCheckable(True)
        self._value = ""
        self._focused = False
        self._hovered = False
        
        self.update_style()
        self.clicked.connect(self._on_click)

    def _on_click(self):
        """Handle box click - focus this box"""
        self._focused = True
        self.update_style()

    def update_style(self):
        """Update visual style based on state"""
        if self._focused:
            # Focus state - blue border with subtle inner glow
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 2px solid #2563EB;
                    border-radius: 10px;
                    font-size: 22px;
                    font-weight: 600;
                    color: #0F172A;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #F8FAFC;
                }
            """)
        elif self._hovered:
            # Hover state - slight border darkening
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #CBD5E1;
                    border-radius: 10px;
                    font-size: 22px;
                    font-weight: 600;
                    color: #0F172A;
                    padding: 0px;
                }
            """)
        else:
            # Default state
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                    font-size: 22px;
                    font-weight: 600;
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
        """Set the digit value"""
        self._value = str(value) if value else ""
        self.setText("•" if self._value else "")

    def clear(self):
        """Clear the box"""
        self._value = ""
        self.setText("")

    def get_value(self):
        """Get the digit value"""
        return self._value


class LoginView(QDialog):
    """Premium PIN-based login screen for TuCajero POS"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_seleccionado = None
        self.pin_boxes = []
        self.current_box = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("TuCajero POS - Login")
        self.setFixedSize(1200, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Premium background with subtle radial gradient
        self.setStyleSheet("""
            QDialog {
                background: qradialgradient(cx:0.5, cy:0.45, radius:0.6,
                    fx:0.5, fy:0.45,
                    stop:0 #F1F5F9, stop:0.5 #F8FAFC, stop:1 #EEF2FF);
            }
        """)

        # Main layout - centered
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login card with premium depth
        card = QWidget()
        card.setFixedSize(380, 500)
        card.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }
        """)

        # Layered shadow for floating effect
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(40)
        shadow1.setOffset(0, 12)
        shadow1.setColor(QColor(0, 0, 0, 15))
        
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(20)
        shadow2.setOffset(0, 4)
        shadow2.setColor(QColor(0, 0, 0, 10))
        
        card.setGraphicsEffect(shadow1)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(0)

        # 1. Logo with increased top spacing
        card_layout.addSpacing(8)
        
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(
                44, 44,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(scaled_logo)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("background: transparent;")
            card_layout.addWidget(logo_label)
            
            # More separation between logo and app name
            card_layout.addSpacing(20)

        # 2. App name
        app_name = QLabel("TuCajero POS")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 19px;
                font-weight: 600;
                letter-spacing: 0.3px;
                background: transparent;
            }
        """)
        card_layout.addWidget(app_name)
        card_layout.addSpacing(28)

        # 3. Active user with refined badge
        user_container = QWidget()
        user_container.setStyleSheet("background: transparent;")
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        user_label = QLabel("Admin")
        user_label.setStyleSheet("""
            QLabel {
                color: #0F172A;
                font-size: 14px;
                font-weight: 600;
                background-color: #F1F5F9;
                padding: 6px 18px;
                border-radius: 6px;
                letter-spacing: 0.2px;
            }
        """)
        user_layout.addWidget(user_label)
        card_layout.addWidget(user_container)
        card_layout.addSpacing(32)

        # PIN label
        pin_label = QLabel("Ingresa tu PIN")
        pin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pin_label.setStyleSheet("""
            QLabel {
                color: #64748B;
                font-size: 14px;
                font-weight: 500;
                background: transparent;
                letter-spacing: 0.2px;
            }
        """)
        card_layout.addWidget(pin_label)
        card_layout.addSpacing(16)

        # 4. PIN input - 4 tactile boxes with increased spacing
        pin_layout = QHBoxLayout()
        pin_layout.setSpacing(14)
        pin_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i in range(4):
            pin_box = PINBox()
            pin_box.setObjectName(f"pin_box_{i}")
            self.pin_boxes.append(pin_box)
            pin_layout.addWidget(pin_box)

        card_layout.addLayout(pin_layout)
        card_layout.addSpacing(32)

        # 5. Primary button with smooth transitions
        self.login_btn = QPushButton("Acceder")
        self.login_btn.setFixedHeight(48)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 500;
                letter-spacing: 0.3px;
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
        card_layout.addSpacing(20)
        footer = QLabel("Acceso seguro al sistema de ventas")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                color: #94A3B8;
                font-size: 12px;
                background: transparent;
                letter-spacing: 0.2px;
            }
        """)
        card_layout.addWidget(footer)

        main_layout.addWidget(card)

        # Focus on first PIN box
        self.pin_boxes[0].setFocus()
        self.pin_boxes[0]._focused = True
        self.pin_boxes[0].update_style()

        # Install event filter for keyboard navigation
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Handle keyboard input for PIN boxes"""
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QKeyEvent
        
        if event.type() == QEvent.Type.KeyPress:
            key_event = event
            key = key_event.key()
            
            # Handle digit input
            if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
                digit = str(key - Qt.Key.Key_0)
                self._enter_digit(digit)
                return True
            
            # Handle backspace
            elif key == Qt.Key.Key_Backspace:
                self._delete_digit()
                return True
            
            # Handle Enter
            elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                self.login()
                return True
        
        return super().eventFilter(obj, event)

    def _enter_digit(self, digit):
        """Enter a digit into the current PIN box"""
        if self.current_box < 4:
            self.pin_boxes[self.current_box].set_value(digit)
            self.pin_boxes[self.current_box]._focused = False
            self.pin_boxes[self.current_box].update_style()
            
            self.current_box += 1
            
            if self.current_box < 4:
                self.pin_boxes[self.current_box]._focused = True
                self.pin_boxes[self.current_box].update_style()

    def _delete_digit(self):
        """Delete the last entered digit"""
        if self.current_box > 0:
            self.current_box -= 1
            self.pin_boxes[self.current_box].clear()
            self.pin_boxes[self.current_box]._focused = True
            self.pin_boxes[self.current_box].update_style()

    def get_pin(self):
        """Get complete PIN from all boxes"""
        return "".join(box.get_value() for box in self.pin_boxes)

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
