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
        from utils.store_config import get_store_name, get_nit, get_phone, get_address, get_logo_path
        import os
        c = get_colors()

        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_card']};
                border-bottom: 1px solid {c['border']};
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(12)

        # Logo del negocio
        logo = QLabel()
        logo.setFixedSize(38, 38)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            from PySide6.QtGui import QPixmap
            pix = QPixmap(logo_path).scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pix)
            logo.setStyleSheet(f"border-radius: 19px; border: 2px solid {c['border']};")
        else:
            logo.setText("🏪")
            logo.setStyleSheet(f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {c['accent']}, stop:1 {c['info']}); border-radius: 19px; font-size: 18px; border: none;")
        layout.addWidget(logo)

        # Info del negocio
        info_col = QVBoxLayout()
        info_col.setSpacing(1)
        info_col.setContentsMargins(0, 0, 0, 0)

        store_lbl = QLabel(get_store_name())
        store_lbl.setStyleSheet(f"color: {c['text_primary']}; font-size: 15px; font-weight: bold; background: transparent; border: none;")
        info_col.addWidget(store_lbl)

        parts = []
        if get_nit(): parts.append(f"NIT: {get_nit()}")
        if get_phone(): parts.append(f"📞 {get_phone()}")
        if get_address(): parts.append(f"📍 {get_address()}")
        if parts:
            sub = QLabel("  |  ".join(parts))
            sub.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px; background: transparent; border: none;")
            info_col.addWidget(sub)

        layout.addLayout(info_col)
        layout.addStretch()

        # Widget de usuario estilo Sovereign
        user_w = QWidget()
        user_w.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg_input']};
                border-radius: 20px;
                border: 1px solid {c['border']};
            }}
        """)
        ul = QHBoxLayout(user_w)
        ul.setContentsMargins(10, 5, 14, 5)
        ul.setSpacing(8)

        av = QLabel("👑")
        av.setFixedSize(28, 28)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(f"background: {c['accent']}; border-radius: 14px; font-size: 13px; border: none;")
        ul.addWidget(av)

        u_info = QVBoxLayout()
        u_info.setSpacing(0)
        u_info.setContentsMargins(0, 0, 0, 0)
        self.lbl_cajero = QLabel("Administrador")
        self.lbl_cajero.setStyleSheet(f"color: {c['text_primary']}; font-size: 12px; font-weight: bold; background: transparent; border: none;")
        lbl_rol = QLabel("EXECUTIVE LEVEL")
        lbl_rol.setStyleSheet(f"color: {c['text_muted']}; font-size: 9px; letter-spacing: 0.5px; background: transparent; border: none;")
        u_info.addWidget(self.lbl_cajero)
        u_info.addWidget(lbl_rol)
        ul.addLayout(u_info)
        layout.addWidget(user_w)

        return header

    def _build_sidebar(self):
        from utils.theme import get_colors
        from utils.store_config import get_logo_path
        import os
        c = get_colors()

        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"QWidget {{ background-color: #1e293b; border: none; }}")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header del sidebar ──────────────────────────────────
        header = QWidget()
        header.setFixedHeight(64)
        header.setStyleSheet("background-color: #1e293b; border-bottom: 1px solid #334155;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)
        h_layout.setSpacing(10)

        # Logo
        logo = QLabel()
        logo.setFixedSize(34, 34)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_icon = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons', 'tucajero.ico')
        store_logo = get_logo_path()
        if os.path.exists(app_icon):
            from PySide6.QtGui import QPixmap
            pix = QPixmap(app_icon).scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pix)
            logo.setStyleSheet("border-radius: 6px; background: transparent; border: none;")
        elif store_logo and os.path.exists(store_logo):
            from PySide6.QtGui import QPixmap
            pix = QPixmap(store_logo).scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pix)
            logo.setStyleSheet("border-radius: 6px; background: transparent; border: none;")
        else:
            logo.setText("TC")
            logo.setStyleSheet("background-color: #3b82f6; color: white; border-radius: 8px; font-size: 12px; font-weight: bold; border: none;")

        app_name = QLabel("TuCajero")
        app_name.setStyleSheet("color: #f1f5f9; font-size: 16px; font-weight: bold; background: transparent; border: none;")

        h_layout.addWidget(logo)
        h_layout.addWidget(app_name)
        h_layout.addStretch()
        layout.addWidget(header)

        # ── Label MENÚ ─────────────────────────────────────────
        menu_label = QLabel("MENÚ")
        menu_label.setStyleSheet("color: #475569; font-size: 10px; font-weight: bold; letter-spacing: 1px; padding: 20px 20px 6px 20px; background: transparent;")
        layout.addWidget(menu_label)

        # ── Botones de navegación ──────────────────────────────
        nav_items = [
            ("🖥", "Escritorio",    "dashboard"),
            ("🛒", "Ventas",        "ventas"),
            ("📦", "Productos",     "productos"),
            ("👥", "Clientes",      "clientes"),
            ("📊", "Inventario",    "inventario"),
            ("📋", "Cotizaciones",  "cotizaciones"),
            ("💰", "Corte de Caja", "corte"),
            ("📈", "Historial",     "historial"),
            ("⚙", "Config",        "config"),
            ("🏭", "Proveedores",   "proveedores"),
        ]

        self._nav_buttons = {}
        for icon, label, key in nav_items:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setFixedHeight(40)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #94a3b8;
                    border: none;
                    border-radius: 8px;
                    text-align: left;
                    padding: 0px 12px;
                    font-size: 13px;
                    font-weight: normal;
                    margin: 1px 10px;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,0.06);
                    color: #e2e8f0;
                }
                QPushButton:checked {
                    background-color: #3b82f6;
                    color: #ffffff;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked, k=key: self.switch_view_by_name(k))
            self._nav_buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # ── Separador ──────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #334155; border: none; max-height: 1px;")
        layout.addWidget(sep)

        # ── Footer ─────────────────────────────────────────────
        self.lbl_cajero = QLabel("👑  Administrador")
        self.lbl_cajero.setStyleSheet("color: #10b981; font-size: 12px; padding: 10px 16px 4px 16px; background: transparent;")
        layout.addWidget(self.lbl_cajero)

        copyright_label = QLabel("© Ing. Francisco Llinas P.")
        copyright_label.setStyleSheet("color: #334155; font-size: 10px; padding: 2px 16px 14px 16px; background: transparent;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
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
