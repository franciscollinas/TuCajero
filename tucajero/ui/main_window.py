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

        header = self._build_header()
        content_layout.addWidget(header)

        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack, 1)

        main_layout.addWidget(content_area, 1)

        self._views = {}
        self._nav_buttons = {}

    def _build_header(self):
        from utils.theme import get_colors

        c = get_colors()
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet(
            f"background-color: {c['bg_card']}; border-bottom: 1px solid {c['border']};"
        )
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)

        logo_label = QLabel("🏪")
        logo_label.setFixedSize(44, 44)
        logo_label.setStyleSheet(
            f"border-radius: 22px; background: {c['accent']}; color: white; font-size: 20px;"
        )
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        self.lbl_store_name = QLabel(get_store_name())
        self.lbl_store_name.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 16px; font-weight: bold;"
        )
        info_layout.addWidget(self.lbl_store_name)

        parts = []
        if get_nit():
            parts.append(f"NIT: {get_nit()}")
        if get_phone():
            parts.append(f"Tel: {get_phone()}")
        if get_address():
            parts.append(get_address())
        if parts:
            sub = QLabel("  |  ".join(parts))
            sub.setStyleSheet(f"color: {c['text_secondary']}; font-size: 11px;")
            info_layout.addWidget(sub)

        layout.addLayout(info_layout)
        layout.addStretch()
        return header

    def _build_sidebar(self):
        from utils.theme import get_colors

        c = get_colors()

        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {c["bg_sidebar"]};
                border-right: 1px solid {c["border"]};
            }}
        """)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet(f"background-color: {c['bg_sidebar']};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)
        logo_label = QLabel("🏪")
        logo_label.setStyleSheet("font-size: 24px;")
        app_name = QLabel("TuCajero")
        app_name.setStyleSheet(
            f"color: {c['text_primary']}; font-size: 18px; font-weight: bold;"
        )
        h_layout.addWidget(logo_label)
        h_layout.addWidget(app_name)
        h_layout.addStretch()
        layout.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {c['border']}; background: {c['border']};")
        layout.addWidget(sep)

        menu_label = QLabel("  MENÚ")
        menu_label.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 10px; font-weight: bold; padding: 16px 16px 4px 16px;"
        )
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
            btn = QPushButton(f"  {icon}  {label}")
            btn.setFixedHeight(44)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {c["text_secondary"]};
                    border: none;
                    border-radius: 0;
                    text-align: left;
                    padding-left: 16px;
                    font-size: 13px;
                    font-weight: normal;
                }}
                QPushButton:hover {{
                    background-color: {c["bg_card"]};
                    color: {c["text_primary"]};
                }}
                QPushButton:checked {{
                    background-color: {c["accent"]};
                    color: white;
                    font-weight: bold;
                    border-left: 3px solid white;
                }}
            """)
            btn.clicked.connect(lambda checked, k=key: self.switch_view_by_name(k))
            self._nav_buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {c['border']}; background: {c['border']};")
        layout.addWidget(sep2)

        self.lbl_cajero = QLabel("👑 Administrador")
        self.lbl_cajero.setStyleSheet(
            f"color: {c['success']}; font-size: 12px; padding: 8px 16px;"
        )
        layout.addWidget(self.lbl_cajero)

        btn_acerca = QPushButton("  ℹ️  Acerca de")
        btn_acerca.setFixedHeight(36)
        btn_acerca.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {c["text_muted"]};
                border: none;
                text-align: left;
                padding-left: 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                color: {c["text_secondary"]};
            }}
        """)
        btn_acerca.clicked.connect(self.mostrar_acerca)
        layout.addWidget(btn_acerca)

        copyright_label = QLabel("© Ing. Francisco Llinas P.")
        copyright_label.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 10px; padding: 4px 16px 12px 16px;"
        )
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
            btn.setChecked(key == name)

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
