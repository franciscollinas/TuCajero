from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QGridLayout,
    QFrame,
    QMessageBox,
    QWidget,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import (
    QLinearGradient,
    QGradient,
    QBrush,
    QPalette,
    QColor,
    QPainter,
    QIcon,
)

from tucajero.models.cajero import Cajero
from tucajero.services.cajero_service import CajeroService
from tucajero.ui.design_tokens import DarkColors as DC, Typography, Spacing, BorderRadius


class GradientWidget(QWidget):
    """Widget con gradiente de fondo"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(138, 43, 226))
        gradient.setColorAt(0.5, QColor(65, 105, 225))
        gradient.setColorAt(1.0, QColor(0, 206, 209))

        painter.fillRect(self.rect(), gradient)


class LoginCajeroDialog(QDialog):
    """Dialogo de login moderno para cajeros"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_service = CajeroService(session)
        self.cajero_seleccionado = None

        self.init_ui()
        self.cargar_cajeros()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("TuCajero POS - Iniciar Sesión")
        self.setFixedSize(1200, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        main_widget = GradientWidget(self)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self.create_header()
        main_layout.addWidget(header)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(60, 40, 60, 60)
        content_layout.setSpacing(40)

        login_panel = self.create_login_panel()
        content_layout.addWidget(login_panel, 40)

        welcome_panel = self.create_welcome_panel()
        content_layout.addWidget(welcome_panel, 60)

        main_layout.addWidget(content, 1)

        main_layout_container = QVBoxLayout(self)
        main_layout_container.setContentsMargins(0, 0, 0, 0)
        main_layout_container.addWidget(main_widget)

    def create_header(self):
        """Crea el header con logo y boton info"""
        header = QWidget()
        header.setStyleSheet("background: rgba(0, 0, 0, 0.3);")
        header.setFixedHeight(70)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)

        logo_label = QLabel("🏪 TuCajero POS")
        logo_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(logo_label)

        layout.addStretch()

        info_btn = QPushButton("ℹ️ Info")
        info_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        info_btn.clicked.connect(self.mostrar_info)
        layout.addWidget(info_btn)

        return header

    def create_login_panel(self):
        """Crea el panel de login"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 50, 0.85);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 60, 50, 60)
        layout.setSpacing(30)

        user_icon_label = QLabel("👤")
        user_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 80px;
                color: {DC.INFO};
                background: rgba(6, 182, 212, 0.15);
                border: 3px solid {DC.INFO};
                border-radius: 75px;
                min-width: 150px;
                max-width: 150px;
                min-height: 150px;
                max-height: 150px;
            }}
        """)
        layout.addWidget(user_icon_label, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(20)

        user_container = QWidget()
        user_container.setStyleSheet("background: transparent;")
        user_layout = QVBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(8)

        user_label = QLabel("USUARIO")
        user_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        user_layout.addWidget(user_label)

        self.combo_cajero = QComboBox()
        self.combo_cajero.setStyleSheet(f"""
            QComboBox {{
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 15px 20px;
                font-size: 15px;
                min-height: 25px;
            }}
            QComboBox:hover {{
                border-color: {DC.INFO};
                background: rgba(255, 255, 255, 0.15);
            }}
            QComboBox:focus {{
                border-color: {DC.INFO};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid white;
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background: rgba(30, 30, 50, 0.95);
                color: white;
                border: 2px solid {DC.INFO};
                border-radius: 10px;
                padding: 5px;
                selection-background-color: {DC.INFO};
                selection-color: white;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 10px;
                border-radius: 5px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: rgba(6, 182, 212, 0.3);
            }}
        """)

        self.combo_cajero.view().window().setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
        )

        user_layout.addWidget(self.combo_cajero)
        layout.addWidget(user_container)

        pin_container = QWidget()
        pin_container.setStyleSheet("background: transparent;")
        pin_layout = QVBoxLayout(pin_container)
        pin_layout.setContentsMargins(0, 0, 0, 0)
        pin_layout.setSpacing(8)

        pin_label = QLabel("PIN (4 DIGITOS)")
        pin_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        pin_layout.addWidget(pin_label)

        self.input_pin = QLineEdit()
        self.input_pin.setPlaceholderText("••••")
        self.input_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pin.setMaxLength(4)
        self.input_pin.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 15px 20px;
                font-size: 20px;
                letter-spacing: 10px;
                min-height: 25px;
            }}
            QLineEdit:hover {{
                border-color: {DC.INFO};
                background: rgba(255, 255, 255, 0.15);
            }}
            QLineEdit:focus {{
                border-color: {DC.INFO};
                background: rgba(255, 255, 255, 0.2);
            }}
        """)
        self.input_pin.returnPressed.connect(self.validar_login)

        pin_layout.addWidget(self.input_pin)
        layout.addWidget(pin_container)

        btn_login = QPushButton("INICIAR SESIÓN")
        btn_login.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {DC.PURPLE_DARK},
                    stop:1 #EC4899
                );
                color: white;
                border: none;
                border-radius: 12px;
                padding: 18px;
                font-size: {Typography.BODY}px;
                font-weight: {Typography.BOLD};
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EC4899,
                    stop:1 {DC.PURPLE_DARK}
                );
            }}
            QPushButton:pressed {{
                background: {DC.PURPLE_DARK};
            }}
        """)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.clicked.connect(self.validar_login)
        layout.addWidget(btn_login)

        layout.addStretch()

        return panel

    def create_welcome_panel(self):
        """Crea el panel de bienvenida"""
        panel = QWidget()
        panel.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 80, 40, 80)
        layout.setSpacing(30)

        title = QLabel("Bienvenido.")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 72px;
                font-weight: bold;
                background: transparent;
            }
        """)
        layout.addWidget(title)

        subtitle = QLabel(
            "Sistema de punto de venta profesional.\n"
            "Gestión completa de ventas, inventario y clientes.\n"
            "Rápido, seguro y confiable."
        )
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                line-height: 28px;
                background: transparent;
            }
        """)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addStretch()

        decoration = QLabel("~~~")
        decoration.setStyleSheet("""
            QLabel {
                color: rgba(0, 206, 209, 0.3);
                font-size: 180px;
                font-weight: bold;
                background: transparent;
            }
        """)
        decoration.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(decoration)

        return panel

    def cargar_cajeros(self):
        """Carga la lista de cajeros activos"""
        cajeros = self.cajero_service.get_all()
        cajeros_activos = [c for c in cajeros if c.activo]

        self.combo_cajero.clear()
        for cajero in cajeros_activos:
            rol = " (Admin)" if cajero.rol == "admin" else ""
            self.combo_cajero.addItem(f"{cajero.nombre}{rol}", cajero)

        if self.combo_cajero.count() == 0:
            self.combo_cajero.addItem("Administrador", None)

    def validar_login(self):
        """Valida el PIN ingresado"""
        pin = self.input_pin.text().strip()

        if not pin:
            self.mostrar_error("Por favor ingresa tu PIN")
            return

        if len(pin) != 4 or not pin.isdigit():
            self.mostrar_error("El PIN debe tener exactamente 4 digitos")
            return

        cajero = self.combo_cajero.currentData()

        if not cajero:
            self.mostrar_error("No se pudo obtener información del cajero")
            return

        cajero, success, error_msg = self.cajero_service.verificar_login(cajero.id, pin)

        if success:
            self.cajero_seleccionado = cajero
            self.accept()
        else:
            self.mostrar_error(error_msg or "PIN incorrecto")
            self.input_pin.clear()
            self.input_pin.setFocus()

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        QMessageBox.warning(self, "Error de autenticación", mensaje)

    def mostrar_info(self):
        """Muestra información del sistema"""
        info_text = (
            f"<h2 style='color: {DC.INFO};'>TuCajero POS</h2>"
            "<p><b>Version:</b> 2.1.0</p>"
            "<p><b>Fecha:</b> Marzo 2026</p>"
            "<p><b>Estado:</b> Produccion ✅</p>"
            "<hr>"
            "<p><b>Creado por:</b><br>"
            "Ingeniero Francisco Llinas Pisciotti</p>"
            "<hr>"
            f"<p style='font-size: 11px; color: {DC.TEXT_MUTED};'>"
            "© 2026 TuCajero POS. Todos los derechos reservados.<br>"
            "Software propietario para gestión de punto de venta."
            "</p>"
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("Información del Sistema")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info_text)
        msg.setIconPixmap(QMessageBox.Icon.Information.pixmap(QSize(64, 64)))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {DC.BG_ELEVATED};
            }}
            QMessageBox QLabel {{
                color: {DC.TEXT_PRIMARY};
                min-width: 400px;
            }}
            QPushButton {{
                background: {DC.INFO};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-weight: {Typography.BOLD};
            }}
            QPushButton:hover {{
                background: {DC.INFO_DARK};
            }}
        """)
        msg.exec()
