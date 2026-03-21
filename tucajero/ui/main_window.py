from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QSizePolicy,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from utils.store_config import (
    get_store_name,
    get_logo_path,
    get_nit,
    get_phone,
    get_email,
    get_address,
)
import os


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self):
        super().__init__()
        store_name = get_store_name()
        self.setWindowTitle(f"TuCajero POS - {store_name}")
        self.setMinimumSize(1024, 768)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.sidebar = self._build_sidebar()
        main_layout.addWidget(self.sidebar)

        content_area = QWidget()
        content_layout = QVBoxLayout()
        content_area.setLayout(content_layout)

        self.header = self._build_header()
        content_layout.addWidget(self.header)

        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack, 1)

        main_layout.addWidget(content_area, 1)

        self._views = {}
        self._nav_buttons = {}

    def _build_header(self):
        from utils.theme import get_colors
        from utils.store_config import (
            get_store_name,
            get_nit,
            get_phone,
            get_address,
            get_logo_path,
        )
        import os

        c = get_colors()

        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {c["bg_sidebar"]};
                border-bottom: 1px solid {c["border"]};
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        logo = QLabel()
        logo.setFixedSize(40, 40)
        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            from PySide6.QtGui import QPixmap

            pix = QPixmap(logo_path).scaled(
                40,
                40,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
            logo.setStyleSheet(f"border-radius: 20px; border: 2px solid {c['accent']};")
        else:
            logo.setText("🏪")
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo.setStyleSheet(f"""
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {c["accent"]}, stop:1 {c["info"]});
                border-radius: 20px;
                font-size: 20px;
                border: none;
            """)
        layout.addWidget(logo)

        info = QVBoxLayout()
        info.setSpacing(1)
        info.setContentsMargins(0, 0, 0, 0)

        nombre = QLabel(get_store_name())
        nombre.setStyleSheet(f"""
            color: {c["text_primary"]};
            font-size: 15px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        info.addWidget(nombre)

        partes = []
        if get_nit():
            partes.append(f"NIT: {get_nit()}")
        if get_phone():
            partes.append(f"📞 {get_phone()}")
        if get_address():
            partes.append(f"📍 {get_address()}")
        if partes:
            sub = QLabel("  |  ".join(partes))
            sub.setStyleSheet(f"""
                color: {c["text_secondary"]};
                font-size: 11px;
                background: transparent;
                border: none;
            """)
            info.addWidget(sub)

        layout.addLayout(info)
        layout.addStretch()

        user_widget = QWidget()
        user_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {c["bg_input"]};
                border-radius: 22px;
                border: 1px solid {c["border"]};
            }}
        """)
        ul = QHBoxLayout(user_widget)
        ul.setContentsMargins(10, 6, 14, 6)
        ul.setSpacing(8)

        avatar = QLabel("👑")
        avatar.setFixedSize(30, 30)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background-color: {c["accent"]};
            border-radius: 15px;
            font-size: 14px;
            border: none;
        """)
        ul.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(0)
        user_info.setContentsMargins(0, 0, 0, 0)

        self.lbl_cajero = QLabel("Administrador")
        self.lbl_cajero.setStyleSheet(f"""
            color: {c["text_primary"]};
            font-size: 12px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        lbl_rol = QLabel("Administrador")
        lbl_rol.setStyleSheet(f"""
            color: {c["text_muted"]};
            font-size: 10px;
            background: transparent;
            border: none;
        """)
        user_info.addWidget(self.lbl_cajero)
        user_info.addWidget(lbl_rol)
        ul.addLayout(user_info)

        layout.addWidget(user_widget)
        return header

    def _build_sidebar(self):
        from utils.theme import get_colors
        from utils.store_config import get_logo_path
        import os

        c = get_colors()

        sidebar = QWidget()
        sidebar.setFixedWidth(185)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {c["bg_sidebar"]};
                border-right: 1px solid rgba(255,255,255,0.05);
            }}
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(f"background-color: {c['bg_sidebar']};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 0, 12, 0)

        logo_container = QLabel()
        logo_container.setFixedSize(32, 32)
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_icon_path = os.path.join(
            os.path.dirname(__file__), "..", "assets", "icons", "tucajero.ico"
        )
        store_logo = get_logo_path()

        if os.path.exists(app_icon_path):
            from PySide6.QtGui import QPixmap

            pix = QPixmap(app_icon_path).scaled(
                28,
                28,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_container.setPixmap(pix)
            logo_container.setStyleSheet(
                "border-radius: 6px; border: none; background: transparent;"
            )
        elif store_logo and os.path.exists(store_logo):
            from PySide6.QtGui import QPixmap

            pix = QPixmap(store_logo).scaled(
                28,
                28,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_container.setPixmap(pix)
            logo_container.setStyleSheet(
                "border-radius: 6px; border: none; background: transparent;"
            )
        else:
            logo_container.setText("TC")
            logo_container.setStyleSheet(f"""
                background-color: {c["accent"]};
                color: white;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            """)

        app_name = QLabel("TuCajero")
        app_name.setStyleSheet(f"""
            color: white;
            font-size: 15px;
            font-weight: bold;
            background: transparent;
        """)
        h_layout.addWidget(logo_container)
        h_layout.addWidget(app_name)
        h_layout.addStretch()
        layout.addWidget(header)

        menu_label = QLabel("MENÚ")
        menu_label.setStyleSheet(f"""
            color: rgba(255,255,255,0.25);
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 1.5px;
            padding: 16px 14px 6px 14px;
            background: transparent;
        """)
        layout.addWidget(menu_label)

        nav_items = [
            ("🖥️", "Escritorio", "dashboard"),
            ("🛒", "Ventas", "ventas"),
            ("📦", "Productos", "productos"),
            ("👥", "Clientes", "clientes"),
            ("📊", "Inventario", "inventario"),
            ("📋", "Cotizaciones", "cotizaciones"),
            ("💰", "Corte de Caja", "corte"),
            ("📈", "Historial", "historial"),
            ("⚙️", "Config", "config"),
            ("🏭", "Proveedores", "proveedores"),
        ]

        self._nav_buttons = {}
        for icon, label, key in nav_items:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setFixedHeight(42)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("navButton", True)
            btn.setStyleSheet(f"""
                QPushButton[navButton="true"] {{
                    background: transparent;
                    color: {c["text_muted"]};
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding: 0px 14px;
                    font-size: 13px;
                    font-weight: normal;
                    margin: 0px 6px;
                }}
                QPushButton[navButton="true"]:hover {{
                    background-color: rgba(255,255,255,0.06);
                    color: {c["text_primary"]};
                }}
                QPushButton[navButton="true"]:checked {{
                    background-color: rgba(108,99,255,0.15);
                    color: {c["accent"]};
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(lambda checked, k=key: self.switch_view_by_name(k))
            self._nav_buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(
            f"color: rgba(255,255,255,0.05); background: rgba(255,255,255,0.05);"
        )
        layout.addWidget(sep2)

        self.lbl_cajero = QLabel("👑 Administrador")
        self.lbl_cajero.setStyleSheet(f"""
            color: {c["success"]};
            font-size: 11px;
            padding: 6px 14px;
            background: transparent;
        """)
        layout.addWidget(self.lbl_cajero)

        btn_acerca = QPushButton("  ℹ️  Acerca de")
        btn_acerca.setFixedHeight(30)
        btn_acerca.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: rgba(255,255,255,0.3);
                border: none;
                text-align: left;
                padding: 0px 14px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                color: rgba(255,255,255,0.5);
            }}
        """)
        btn_acerca.clicked.connect(self.mostrar_acerca)
        layout.addWidget(btn_acerca)

        copyright_label = QLabel("© Ing. Francisco Llinas P.")
        copyright_label.setStyleSheet(f"""
            color: rgba(255,255,255,0.2);
            font-size: 9px;
            padding: 2px 14px 10px 14px;
            background: transparent;
        """)
        layout.addWidget(copyright_label)

        return sidebar

    def mostrar_acerca(self):
        """Muestra la ventana Acerca de"""
        from ui.about_view import AboutView

        dialog = AboutView(self)
        dialog.exec()

    def add_view(self, widget, name):
        """Agrega una vista al stack"""
        self.content_stack.addWidget(widget)
        self._views[name] = widget
        return self.content_stack.count() - 1

    def switch_view_by_name(self, name):
        """Cambia a una vista por nombre y actualiza navegación"""
        if name in self._views:
            self.content_stack.setCurrentWidget(self._views[name])
        for key, btn in self._nav_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(key == name)
            btn.blockSignals(False)

    def switch_view(self, index):
        """Cambia a una vista específica"""
        self.content_stack.setCurrentIndex(index)

    def switch_to_ventas(self):
        self.switch_view_by_name("ventas")

    def switch_to_productos(self):
        self.switch_view_by_name("productos")

    def switch_to_clientes(self):
        self.switch_view_by_name("clientes")

    def switch_to_cajeros(self):
        self.switch_view_by_name("cajeros")

    def switch_to_inventario(self):
        self.switch_view_by_name("inventario")

    def switch_to_cotizaciones(self):
        self.switch_view_by_name("cotizaciones")

    def switch_to_corte(self):
        self.switch_view_by_name("corte")

    def switch_to_historial(self):
        self.switch_view_by_name("historial")

    def switch_to_config(self):
        self.switch_view_by_name("config")

    def switch_to_proveedores(self):
        self.switch_view_by_name("proveedores")

    def set_cajero_activo(self, cajero):
        icono = "👑" if cajero.rol == "admin" else "👤"
        self.lbl_cajero.setText(f"{icono} {cajero.nombre}")
        if hasattr(self, "header_user_label") and self.header_user_label:
            self.header_user_label.setText(cajero.nombre)

    def actualizar_badge_inventario(self, num_alertas):
        """Actualiza el botón de Inventario con badge de alertas"""
        from utils.theme import get_colors

        c = get_colors()
        btn = self._nav_buttons.get("inventario")
        if btn:
            if num_alertas > 0:
                btn.setText(f"  📊  Inventario  🔴{num_alertas}")
            else:
                btn.setText(f"  📊  Inventario")

    def closeEvent(self, event):
        """Cierra la aplicación correctamente"""
        try:
            from config.database import close_db

            close_db()
        except Exception as e:
            import logging

            logging.error(f"closeEvent error: {e}")
        event.accept()
