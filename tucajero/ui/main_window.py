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
    QButtonGroup,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium
from tucajero.utils.store_config import (
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
        
        # Fondo oscuro premium
        from tucajero.ui.design_tokens import Colors
        self.setStyleSheet(f"background: {Colors.BG_APP};")
        
        store_name = get_store_name()
        self.setWindowTitle(f"TuCajero POS - {store_name}")
        self.setMinimumSize(1024, 768)
        self.session = None
        self.cajero_activo = None
        self._stock_alert_mostrada = False
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
        from tucajero.utils.store_config import (
            get_store_name,
            get_nit,
            get_phone,
            get_address,
            get_logo_path,
        )
        import os

        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_CARD};
                border-bottom: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # Logo del negocio
        logo = QLabel()
        logo.setFixedSize(42, 42)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
            logo.setStyleSheet(f"border-radius: 21px; border: 2px solid {Colors.BORDER_DEFAULT};")
        else:
            logo.setText("🏪")
            logo.setStyleSheet(
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {Colors.PRIMARY}, stop:1 {Colors.INFO}); border-radius: 21px; font-size: 20px; border: none;"
            )
        layout.addWidget(logo)

        # Info del negocio
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        info_col.setContentsMargins(0, 0, 0, 0)

        store_lbl = QLabel(get_store_name())
        store_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700; background: transparent; border: none;"
        )
        info_col.addWidget(store_lbl)

        parts = []
        if get_nit():
            parts.append(f"NIT: {get_nit()}")
        if get_phone():
            parts.append(f"📞 {get_phone()}")
        if get_address():
            parts.append(f"📍 {get_address()}")
        if parts:
            sub = QLabel("  |  ".join(parts))
            sub.setStyleSheet(
                f"color: {Colors.TEXT_MUTED}; font-size: 11px; background: transparent; border: none;"
            )
            info_col.addWidget(sub)

        layout.addLayout(info_col)
        layout.addStretch()

        # Widget de usuario estilo Premium
        user_w = QWidget()
        user_w.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_INPUT};
                border-radius: 22px;
                border: 1px solid {Colors.BORDER_DEFAULT};
                padding: 4px;
            }}
        """)
        ul = QHBoxLayout(user_w)
        ul.setContentsMargins(12, 4, 16, 4)
        ul.setSpacing(10)

        av = QLabel("👑")
        av.setFixedSize(32, 32)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK}); border-radius: 16px; font-size: 14px; border: none;"
        )
        ul.addWidget(av)

        u_info = QVBoxLayout()
        u_info.setSpacing(0)
        u_info.setContentsMargins(0, 0, 0, 0)
        self.lbl_cajero = QLabel("Administrador")
        self.lbl_cajero.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: 600; background: transparent; border: none;"
        )
        lbl_rol = QLabel("EXECUTIVE LEVEL")
        lbl_rol.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 9px; letter-spacing: 0.5px; background: transparent; border: none; text-transform: uppercase;"
        )
        u_info.addWidget(self.lbl_cajero)
        u_info.addWidget(lbl_rol)
        ul.addLayout(u_info)
        layout.addWidget(user_w)

        return header

    def _build_sidebar(self):
        from tucajero.utils.store_config import get_logo_path
        import os

        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background: {Colors.BG_PANEL};
                border-right: 1px solid {Colors.BORDER_SUBTLE};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header del sidebar ──────────────────────────────────
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet(f"""
            QWidget {{
                background: {Colors.BG_PANEL};
                border-bottom: 1px solid {Colors.BORDER_SUBTLE};
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)
        h_layout.setSpacing(12)

        # Logo
        logo = QLabel()
        logo.setFixedSize(38, 38)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_icon = os.path.join(
            os.path.dirname(__file__), "..", "assets", "icons", "tucajero.ico"
        )
        store_logo = get_logo_path()
        if os.path.exists(app_icon):
            from PySide6.QtGui import QPixmap

            pix = QPixmap(app_icon).scaled(
                34,
                34,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
            logo.setStyleSheet(
                "border-radius: 10px; background: transparent; border: none;"
            )
        elif store_logo and os.path.exists(store_logo):
            from PySide6.QtGui import QPixmap

            pix = QPixmap(store_logo).scaled(
                34,
                34,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
            logo.setStyleSheet(
                "border-radius: 10px; background: transparent; border: none;"
            )
        else:
            logo.setText("TC")
            logo.setStyleSheet(
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK}); color: white; border-radius: 10px; font-size: 13px; font-weight: 700; border: none;"
            )

        app_name = QLabel("TuCajero")
        app_name.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H3}px;
                font-weight: {Typography.BOLD};
                background: transparent;
                border: none;
            }}
        """)

        h_layout.addWidget(logo)
        h_layout.addWidget(app_name)
        h_layout.addStretch()
        layout.addWidget(header)

        # ── Label MENÚ ─────────────────────────────────────────
        menu_label = QLabel("MENÚ")
        menu_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_TERTIARY};
                font-size: {Typography.TINY}px;
                font-weight: {Typography.SEMIBOLD};
                letter-spacing: 1px;
                padding: {Spacing.XXL}px {Spacing.XXL}px {Spacing.XS}px {Spacing.XXL}px;
                background: transparent;
                text-transform: uppercase;
            }}
        """)
        layout.addWidget(menu_label)

        # ── Botones de navegación ──────────────────────────────
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("🛒", "Punto de Venta", "ventas"),
            ("📦", "Inventario", "productos"),
            ("👥", "Clientes", "clientes"),
            ("📋", "Cotizaciones", "cotizaciones"),
            ("💰", "Corte de Caja", "corte"),
            ("📉", "Historial", "historial"),
            ("⚙", "Configuración", "setup"),
            ("🏭", "Proveedores", "proveedores"),
        ]

        self._nav_buttons = {}
        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        for icon, label, key in nav_items:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setFixedHeight(44)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.TEXT_SECONDARY};
                    border: none;
                    border-radius: {BorderRadius.MD}px;
                    padding: {Spacing.LG}px {Spacing.XL}px;
                    text-align: left;
                    font-size: {Typography.BODY}px;
                    font-weight: {Typography.MEDIUM};
                }}
                QPushButton:hover {{
                    background: {Colors.BG_HOVER};
                    color: {Colors.TEXT_PRIMARY};
                }}
                QPushButton:checked {{
                    background: {Colors.PRIMARY};
                    color: white;
                    font-weight: {Typography.SEMIBOLD};
                }}
            """)
            btn.clicked.connect(lambda checked, k=key: self.switch_view_by_name(k))
            self._nav_buttons[key] = btn
            self._nav_group.addButton(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # ── Separador ──────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER_DEFAULT}; border: none; max-height: 1px;")
        layout.addWidget(sep)

        # ── Footer ─────────────────────────────────────────────
        footer_widget = QWidget()
        footer_widget.setStyleSheet(f"""
            QWidget {{
                background: {Colors.BG_ELEVATED};
                border-top: 1px solid {Colors.BORDER_SUBTLE};
                padding: {Spacing.LG}px;
            }}
        """)
        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        footer_layout.setSpacing(Spacing.XXS)

        self.lbl_cajero_footer = QLabel("👑  Administrador")
        self.lbl_cajero_footer.setStyleSheet(f"""
            QLabel {{
                color: {Colors.SUCCESS};
                font-size: {Typography.BODY_SM}px;
                font-weight: {Typography.MEDIUM};
                background: transparent;
                border: none;
            }}
        """)
        footer_layout.addWidget(self.lbl_cajero_footer)

        copyright_label = QLabel("© Ing. Francisco Llinas P.")
        copyright_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_TERTIARY};
                font-size: {Typography.TINY}px;
                background: transparent;
                border: none;
            }}
        """)
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        footer_layout.addWidget(copyright_label)

        layout.addWidget(footer_widget)

        return sidebar

    def mostrar_acerca(self):
        """Muestra la ventana Acerca de"""
        from tucajero.ui.about_view import AboutView

        dialog = AboutView(self)
        dialog.exec()

    def add_view(self, widget, name):
        """Agrega una vista al stack"""
        self.content_stack.addWidget(widget)
        self._views[name] = widget
        return self.content_stack.count() - 1

    def switch_view_by_name(self, name):
        """Cambia a una vista por nombre y actualiza navegación"""
        widget = self._get_or_create_view(name)
        self.content_stack.setCurrentWidget(widget)
        for key, btn in self._nav_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(key == name)
            btn.blockSignals(False)

    def _get_or_create_view(self, name):
        """Crea la vista solo cuando se necesita (lazy loading)"""
        if name in self._views:
            return self._views[name]

        view = None
        if name == "ventas":
            from tucajero.ui.ventas_view import VentasView

            view = VentasView(
                self.session, parent=self, cajero_activo=self.cajero_activo
            )
        elif name == "productos":
            from tucajero.ui.productos_view import ProductosView

            view = ProductosView(self.session, parent=self)
        elif name == "corte":
            from tucajero.ui.corte_view import CorteView

            view = CorteView(
                self.session, cajero_activo=self.cajero_activo, parent=self
            )
        elif name == "historial":
            from tucajero.ui.historial_view import HistorialView

            view = HistorialView(self.session, parent=self)
        elif name == "clientes":
            from tucajero.ui.clientes_view import ClientesView

            view = ClientesView(self.session, parent=self)
        elif name == "cotizaciones":
            from tucajero.ui.cotizaciones_view import CotizacionesView

            view = CotizacionesView(self.session, parent=self)
        elif name == "proveedores":
            from tucajero.ui.proveedores_view import ProveedoresView

            view = ProveedoresView(self.session, parent=self)
        elif name == "setup":
            from tucajero.ui.setup_view import SetupView

            view = SetupView(self.session, parent=self)
        elif name == "dashboard":
            from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView

            view = DashboardView(self.session, parent=self)
        elif name == "cajeros":
            from tucajero.ui.cajeros_view import CajerosView

            view = CajerosView(self.session, parent=self)
        elif name == "config":  # Alias for backward compatibility
            from tucajero.ui.setup_view import SetupView

            view = SetupView(self.session, parent=self)

        if view:
            self.content_stack.addWidget(view)
            self._views[name] = view

        return view

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

    def switch_to_cotizaciones(self):
        self.switch_view_by_name("cotizaciones")

    def switch_to_corte(self):
        self.switch_view_by_name("corte")

    def switch_to_historial(self):
        self.switch_view_by_name("historial")

    def switch_to_config(self):
        self.switch_view_by_name("setup")

    def switch_to_proveedores(self):
        self.switch_view_by_name("proveedores")

    def set_cajero_activo(self, cajero):
        self.cajero_activo = cajero
        icono = "👑" if cajero.rol == "admin" else "👤"
        self.lbl_cajero.setText(f"{icono} {cajero.nombre}")
        if hasattr(self, "header_user_label") and self.header_user_label:
            self.header_user_label.setText(cajero.nombre)
        from PySide6.QtCore import QTimer

        QTimer.singleShot(1500, self._mostrar_alerta_stock)

    def _mostrar_alerta_stock(self):
        """Muestra popup de productos con stock bajo al iniciar"""
        if self._stock_alert_mostrada:
            return
        self._stock_alert_mostrada = True

        if not self.session:
            return

        try:
            from tucajero.services.producto_service import ProductoService

            ps = ProductoService(self.session)
            criticos = ps.get_productos_stock_critico()
            bajos = ps.get_productos_bajo_stock_limite(5)
            total_alertas = len(criticos) + len(bajos)

            if total_alertas == 0:
                return

            from PySide6.QtWidgets import QMessageBox

            mensaje = "⚠️ Productos con stock bajo:\n\n"

            if criticos:
                mensaje += f"❌ Sin stock ({len(criticos)}):\n"
                for p in criticos[:5]:
                    mensaje += f"   • {p.nombre}\n"
                if len(criticos) > 5:
                    mensaje += f"   ... y {len(criticos) - 5} más\n"

            if bajos:
                mensaje += f"\n⚠️ Stock bajo ≤5 unidades ({len(bajos)}):\n"
                for p in bajos[:5]:
                    mensaje += f"   • {p.nombre} (Stock: {p.stock})\n"
                if len(bajos) > 5:
                    mensaje += f"   ... y {len(bajos) - 5} más\n"

            mensaje += "\nRevisa el módulo de Inventario para reponer."

            QMessageBox.warning(self, "📦 Stock bajo", mensaje)

        except Exception as e:
            pass

    def actualizar_badge_productos(self, num_alertas):
        """Actualiza el botón de Productos con badge de alertas"""
        btn = self._nav_buttons.get("productos")
        if btn:
            if num_alertas > 0:
                btn.setText(f"  📦  Productos  🔴{num_alertas}")
            else:
                btn.setText(f"  📦  Productos")

    def closeEvent(self, event):
        """Cierra la aplicación correctamente"""
        try:
            from tucajero.config.database import close_db

            close_db()
        except Exception as e:
            import logging

            logging.error(f"closeEvent error: {e}")
        event.accept()
