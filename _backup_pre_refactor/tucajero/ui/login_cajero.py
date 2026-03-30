import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QComboBox,
    QLineEdit,
    QCheckBox,
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import (
    QFont,
    QPixmap,
    QPainter,
    QLinearGradient,
    QColor,
    QBrush,
    QIcon,
)
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from utils.theme import btn_primary, btn_secondary, btn_danger, get_colors


class GradientWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#1e3a5f"))
        gradient.setColorAt(0.3, QColor("#3b82f6"))
        gradient.setColorAt(0.6, QColor("#8b5cf6"))
        gradient.setColorAt(1.0, QColor("#06b6d4"))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 32, 32)

        painter.setBrush(QColor(255, 255, 255, 30))
        painter.drawEllipse(self.width() * 0.6, self.height() * 0.1, 200, 200)
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.drawEllipse(self.width() * 0.1, self.height() * 0.7, 150, 150)


class LoginCajeroDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cajero_seleccionado = None
        self.setWindowTitle("TuCajero — Iniciar sesión")
        self.setMinimumSize(760, 570)
        self.setModal(True)
        self.pin_ingresado = ""
        self.init_ui()
        self.cargar_cajeros()

    def keyPressEvent(self, event):
        key = event.key()
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            self.on_tecla(str(key - Qt.Key.Key_0))
        elif key == Qt.Key.Key_Backspace:
            self.on_tecla("⌫")
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            self.on_tecla("→")
        else:
            super().keyPressEvent(event)

    def init_ui(self):
        c = get_colors()
        self.setStyleSheet("QDialog { background-color: #ffffff; }")

        main_container = QWidget()
        main_container.setObjectName("mainContainer")
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_container.setLayout(main_layout)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(main_container)

        left_panel = self.crear_panel_izquierdo()
        main_layout.addWidget(left_panel, 1)

        right_panel = self.crear_panel_derecho()
        main_layout.addWidget(right_panel, 1)

    def crear_panel_izquierdo(self):
        c = get_colors()
        panel = QWidget()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet(f"""
            QWidget#leftPanel {{
                background-color: #ffffff;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)
        panel.setLayout(layout)

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(BASE_DIR, "assets", "icons", "logo.png")

        logo_label = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaled(
                156,
                156,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(pixmap)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(30)
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(0, 6)
            logo_label.setGraphicsEffect(shadow)
        else:
            logo_label.setText("TuCajero")
            logo_label.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #1e293b;"
            )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        titulo = QLabel("Bienvenido de nuevo")
        titulo.setStyleSheet("font-size: 23px; font-weight: bold; color: #1e293b;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingresa tus credenciales para continuar")
        subtitulo.setStyleSheet("font-size: 15px; color: #64748b;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        label_usuario = QLabel("Cajero")
        label_usuario.setStyleSheet(
            "font-size: 15px; font-weight: 600; color: #374151;"
        )
        layout.addWidget(label_usuario)

        self.cajero_combo = QComboBox()
        self.cajero_combo.setPlaceholderText("Selecciona tu nombre")
        self.cajero_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 10px 12px;
                font-size: 13px;
                background-color: #ffffff;
                color: #1e293b;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                min-height: 16px;
            }}
            QComboBox:hover {{
                border-color: #3b82f6;
            }}
            QComboBox:focus {{
                border-color: #3b82f6;
                background-color: #ffffff;
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 12px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #94a3b8;
            }}
            QComboBox QAbstractItemView {{
                background-color: #ffffff;
                color: #1e293b;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px;
                selection-background-color: #3b82f6;
            }}
        """)
        self.cajero_combo.currentIndexChanged.connect(self.on_cajero_changed)
        layout.addWidget(self.cajero_combo)

        label_pin = QLabel("PIN de acceso")
        label_pin.setStyleSheet(
            "font-size: 14px; font-weight: 600; color: #374151; margin-top: 12px;"
        )
        layout.addWidget(label_pin)

        pin_container = QWidget()
        pin_layout = QHBoxLayout()
        pin_layout.setSpacing(8)
        pin_layout.setContentsMargins(0, 0, 0, 0)
        pin_container.setLayout(pin_layout)

        self.pin_dots = []
        for i in range(4):
            dot = QLabel("○")
            dot.setStyleSheet("font-size: 30px; color: #cbd5e1; padding: 6px;")
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pin_dots.append(dot)
            pin_layout.addWidget(dot)

        layout.addWidget(pin_container, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(
            "color: #ef4444; font-size: 12px; padding: 6px; background-color: #fef2f2; border-radius: 6px; margin-top: 6px;"
        )
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_error.setVisible(False)
        layout.addWidget(self.lbl_error)

        teclado = QWidget()
        from PySide6.QtWidgets import QGridLayout

        teclado_layout = QGridLayout()
        teclado_layout.setSpacing(6)
        teclado_layout.setColumnStretch(0, 1)
        teclado_layout.setColumnStretch(1, 1)
        teclado_layout.setColumnStretch(2, 1)
        teclado_layout.setRowStretch(0, 1)
        teclado_layout.setRowStretch(1, 1)
        teclado_layout.setRowStretch(2, 1)
        teclado_layout.setRowStretch(3, 1)
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
            ("→", 3, 2),
        ]
        for texto, fila, col in numeros:
            btn = QPushButton(texto)
            btn.setFixedSize(63, 46)
            if texto == "→":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3b82f6;
                        color: white;
                        border: none;
                        border-radius: 12px;
                        font-size: 18px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #2563eb;
                    }
                """)
            elif texto == "⌫":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f1f5f9;
                        color: #64748b;
                        border: 1px solid #e2e8f0;
                        border-radius: 12px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e2e8f0;
                        border-color: #ef4444;
                        color: #ef4444;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        color: #1e293b;
                        border: 1px solid #e2e8f0;
                        border-radius: 12px;
                        font-size: 20px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: #f1f5f9;
                        border-color: #3b82f6;
                    }
                """)
            btn.clicked.connect(lambda checked, t=texto: self.on_tecla(t))
            teclado_layout.addWidget(btn, fila, col)

        layout.addWidget(teclado, alignment=Qt.AlignmentFlag.AlignCenter)

        return panel

    def crear_panel_derecho(self):
        panel = QWidget()
        panel.setObjectName("rightPanel")

        layout = QVBoxLayout()
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel.setLayout(layout)

        gradient_bg = GradientWidget(panel)
        gradient_bg.setGeometry(panel.rect())

        def update_gradient_size():
            gradient_bg.setGeometry(0, 0, panel.width(), panel.height())

        panel.resizeEvent = lambda event: update_gradient_size()

        contenido = QWidget()
        contenido.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        contenido_layout = QVBoxLayout()
        contenido_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contenido_layout.setSpacing(10)
        contenido.setLayout(contenido_layout)

        layout.addWidget(contenido)

        welcome_label = QLabel("Bienvenido")
        welcome_label.setStyleSheet("""
            font-size: 37px;
            font-weight: 800;
            color: white;
            letter-spacing: -1px;
        """)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contenido_layout.addWidget(welcome_label)

        subtitle = QLabel("Tu sistema de gestión\nde ventas moderno")
        subtitle.setStyleSheet("""
            font-size: 15px;
            color: rgba(255, 255, 255, 0.85);
            line-height: 1.5;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contenido_layout.addWidget(subtitle)

        features = QVBoxLayout()
        features.setSpacing(8)

        feature_items = [
            ("✓", "Gestión de inventario"),
            ("📊", "Reportes y estadísticas"),
            ("💳", "Múltiples métodos de pago"),
        ]

        for icon, text in feature_items:
            feature_widget = QWidget()
            feature_layout = QHBoxLayout()
            feature_layout.setContentsMargins(12, 8, 12, 8)
            feature_layout.setSpacing(10)
            feature_widget.setLayout(feature_layout)
            feature_widget.setStyleSheet("""
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
            """)

            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 14px;")

            text_label = QLabel(text)
            text_label.setStyleSheet("color: white; font-size: 13px;")

            feature_layout.addWidget(icon_label)
            feature_layout.addWidget(text_label)
            feature_layout.addStretch()

            features.addWidget(feature_widget)

        contenido_layout.addSpacing(20)
        contenido_layout.addLayout(features)

        return panel

    def cargar_cajeros(self):
        from services.cajero_service import CajeroService

        cajeros = CajeroService(self.session).get_all()

        self.cajero_combo.clear()
        for cajero in cajeros:
            self.cajero_combo.addItem(cajero.nombre, cajero)

    def on_cajero_changed(self, index):
        if index >= 0:
            self.cajero_seleccionado = self.cajero_combo.currentData()
        else:
            self.cajero_seleccionado = None
        self.pin_ingresado = ""
        self.actualizar_pin_display()
        self.lbl_error.setVisible(False)
        self.lbl_error.setText("")

    def on_tecla(self, tecla):
        if tecla == "⌫":
            self.pin_ingresado = self.pin_ingresado[:-1]
            self.actualizar_pin_display()
        elif tecla == "→":
            self.confirmar_login()
        else:
            if len(self.pin_ingresado) < 4:
                self.pin_ingresado += tecla
                self.actualizar_pin_display()
                if len(self.pin_ingresado) == 4:
                    QTimer.singleShot(150, self.confirmar_login)

    def actualizar_pin_display(self):
        c = get_colors()
        for i, dot in enumerate(self.pin_dots):
            if i < len(self.pin_ingresado):
                dot.setText("●")
                dot.setStyleSheet("font-size: 30px; color: #3b82f6; padding: 6px;")
            else:
                dot.setText("○")
                dot.setStyleSheet("font-size: 30px; color: #cbd5e1; padding: 6px;")

    def confirmar_login(self):
        import logging

        if not self.cajero_seleccionado:
            self.lbl_error.setText("Selecciona un cajero primero")
            self.lbl_error.setVisible(True)
            return
        if len(self.pin_ingresado) != 4:
            self.lbl_error.setText("El PIN debe tener 4 dígitos")
            self.lbl_error.setVisible(True)
            return

        try:
            from services.cajero_service import CajeroService
            from PySide6.QtWidgets import QMessageBox

            ok = CajeroService(self.session).verificar_login(
                self.cajero_seleccionado.id, self.pin_ingresado
            )
            if ok:
                self.accept()
            else:
                self.lbl_error.setText("PIN incorrecto. Intenta de nuevo.")
                self.lbl_error.setVisible(True)
                self.pin_ingresado = ""
                self.actualizar_pin_display()
        except Exception as e:
            logging.error(f"Error en login de cajero: {e}", exc_info=True)
            self.lbl_error.setText("Error al iniciar sesión")
            self.lbl_error.setVisible(True)
            QMessageBox.critical(
                self, "Error", f"Ocurrió un error al iniciar sesión:\n{str(e)}"
            )
