from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
    QFrame,
    QButtonGroup,
    QMessageBox,
    QDialog,
    QApplication,
)
from PySide6.QtCore import Qt
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium
from tucajero.utils.store_config import (
    get_store_name,
    get_nit,
    get_phone,
    get_email,
    get_address,
)
import os

# Module-level reference to the active window (used during logout cycle)
_current_window = None


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
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

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
            get_logo_path,
            get_nit,
            get_phone,
            get_address,
        )
        import os

        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_CARD};
                border-bottom: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 8, 24, 8)
        layout.setSpacing(20)

        # ── LOGO: Negocio del cliente (imagen) ──────────────────
        logo = QLabel()
        logo.setFixedSize(56, 56)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            from PySide6.QtGui import QPixmap

            pix = QPixmap(logo_path).scaled(
                52,
                52,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo.setPixmap(pix)
            logo.setStyleSheet(f"border-radius: 12px; border: 2px solid {Colors.BORDER_DEFAULT}; background: transparent;")
        else:
            logo.setText("🏪")
            logo.setStyleSheet(
                f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {Colors.PRIMARY}, stop:1 {Colors.INFO}); border-radius: 12px; font-size: 28px; border: none;"
            )
        layout.addWidget(logo)

        # ── INFO: Negocio del cliente ───────────────────────────
        info_col = QVBoxLayout()
        info_col.setSpacing(3)
        info_col.setContentsMargins(0, 0, 0, 0)

        store_lbl = QLabel(get_store_name())
        store_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: 700; background: transparent; border: none;"
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
                f"color: {Colors.TEXT_MUTED}; font-size: 12px; background: transparent; border: none;"
            )
            info_col.addWidget(sub)

        layout.addLayout(info_col)
        layout.addStretch()

        # Widget de usuario estilo Premium
        user_w = QWidget()
        user_w.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_ELEVATED};
                border-radius: 28px;
                border: 1px solid {Colors.BORDER_DEFAULT};
                padding: 6px;
            }}
        """)
        ul = QHBoxLayout(user_w)
        ul.setContentsMargins(14, 6, 18, 6)
        ul.setSpacing(12)

        av = QLabel("👑")
        av.setFixedSize(40, 40)
        av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        av.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK}); border-radius: 20px; font-size: 18px; border: none;"
        )
        ul.addWidget(av)

        u_info = QVBoxLayout()
        u_info.setSpacing(1)
        u_info.setContentsMargins(0, 0, 0, 0)
        self.lbl_cajero = QLabel("Administrador")
        self.lbl_cajero.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 14px; font-weight: 600; background: transparent; border: none;"
        )
        lbl_rol = QLabel("EXECUTIVE LEVEL")
        lbl_rol.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 10px; letter-spacing: 0.5px; background: transparent; border: none; text-transform: uppercase;"
        )
        u_info.addWidget(self.lbl_cajero)
        u_info.addWidget(lbl_rol)
        ul.addLayout(u_info)
        layout.addWidget(user_w)

        return header

    def _build_sidebar(self):
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
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QWidget {{
                background: {Colors.BG_PANEL};
                border-bottom: 1px solid {Colors.BORDER_SUBTLE};
            }}
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 8, 16, 8)
        h_layout.setSpacing(14)

        # Logo texto limpio (sin imagen pixelada)
        logo_text = QLabel("📊 TuCajero")
        logo_text.setStyleSheet(
            f"font-size: 20px; font-weight: {Typography.BOLD}; "
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"border: none;"
        )
        h_layout.addWidget(logo_text)
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
            ("👤", "Cajeros", "cajeros"),
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

        # ── Botones de acción (Acerca de / Cerrar sesión) ─────
        footer_buttons = QHBoxLayout()
        footer_buttons.setSpacing(Spacing.XS)
        footer_buttons.setContentsMargins(0, Spacing.XS, 0, 0)

        self.btn_about_footer = QPushButton("ℹ️")
        self.btn_about_footer.setFixedSize(32, 32)
        self.btn_about_footer.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_about_footer.setToolTip("Acerca de")
        self.btn_about_footer.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.BG_HOVER};
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.SM}px;
                font-size: {Typography.BODY}px;
            }}
            QPushButton:hover {{
                background: {Colors.BG_ACTIVE};
                border-color: {Colors.BORDER_STRONG};
                color: {Colors.TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background: {Colors.BORDER_DEFAULT};
            }}
        """)
        self.btn_about_footer.clicked.connect(self.mostrar_acerca)
        footer_buttons.addWidget(self.btn_about_footer)

        self.btn_logout = QPushButton("🚪")
        self.btn_logout.setFixedSize(32, 32)
        self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_logout.setToolTip("Cerrar sesión")
        self.btn_logout.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.BG_HOVER};
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.SM}px;
                font-size: {Typography.BODY}px;
            }}
            QPushButton:hover {{
                background: {Colors.DANGER_LIGHT};
                border-color: {Colors.DANGER};
                color: {Colors.DANGER};
            }}
            QPushButton:pressed {{
                background: {Colors.DANGER};
                color: white;
            }}
        """)
        self.btn_logout.clicked.connect(self.do_logout)
        footer_buttons.addWidget(self.btn_logout)

        footer_buttons.addStretch()

        footer_layout.addLayout(footer_buttons)

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

    def do_logout(self):
        """Cierra sesión y regresa a la pantalla de login"""
        reply = QMessageBox.question(
            self,
            "Cerrar sesión",
            "¿Está seguro que desea cerrar sesión?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        # Registrar logout en auditoría
        if self.session and self.cajero_activo:
            try:
                from tucajero.services.audit_service import AuditService

                audit = AuditService(self.session)
                audit.registrar(
                    AuditService.LOGOUT,
                    f"Cierre de sesión: {self.cajero_activo.nombre}",
                    usuario_id=self.cajero_activo.id,
                )
                self.session.commit()
            except Exception as e:
                import logging

                logging.warning(f"No se pudo registrar auditoría de logout: {e}")

        # Schedule logout flow after this event returns to avoid
        # destroying `self` before the rest of the code runs.
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, self._do_logout_flow)

    def _do_logout_flow(self):
        """Executes the logout sequence after the current event loop returns."""
        import sys
        import logging

        # Keep a reference to the app so it doesn't get garbage collected
        app_instance = QApplication.instance()

        # Close current window (triggers closeEvent which closes DB)
        self.close()

        try:
            from tucajero.ui.login_view import LoginView
            from tucajero.config.database import get_session

            session = get_session()
            login = LoginView(session)
            result = login.exec()
            if result != QDialog.DialogCode.Accepted:
                sys.exit(0)

            cajero_activo = login.cajero_seleccionado

            # Open cash register
            try:
                from tucajero.services.corte_service import CorteCajaService

                service = CorteCajaService(session)
                service.abrir_caja()
            except Exception as e:
                logging.error(f"Error al abrir caja en logout: {e}")

            # Create new main window
            new_window = MainWindow()
            new_window.session = session
            new_window.set_cajero_activo(cajero_activo)

            # Build core views (lazy loading for the rest)
            from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
            from tucajero.ui.ventas_view import VentasView

            dashboard_view = DashboardView(session)
            new_window.add_view(dashboard_view, "dashboard")
            ventas_view = VentasView(session, cajero_activo=cajero_activo)
            new_window.add_view(ventas_view, "ventas")
            ventas_view.sale_completed.connect(dashboard_view.refresh)
            new_window.switch_view_by_name("dashboard")

            # Store reference globally so it's not GC'd
            global _current_window
            _current_window = new_window

            new_window.show()

            # Run event loop (this blocks until the new window is closed)
            app_instance.exec()

        except Exception as e:
            import traceback

            logging.critical(f"Error durante logout: {e}\n{traceback.format_exc()}")
            sys.exit(1)

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
            self._wire_cotizacion_venta_signal()

        return view

    def _wire_cotizacion_venta_signal(self):
        """Connect cotizaciones signal to ventas view so quotation items load into cart."""
        cotizaciones = self._views.get("cotizaciones")
        ventas = self._views.get("ventas")
        if cotizaciones and ventas and hasattr(cotizaciones, "cargar_en_ventas"):
            try:
                cotizaciones.cargar_en_ventas.disconnect()
            except Exception:
                pass
            cotizaciones.cargar_en_ventas.connect(
                ventas.cargar_carrito_desde_cotizacion
            )
            cotizaciones.cargar_en_ventas.connect(
                lambda carrito, cliente: self.switch_view_by_name("ventas")
            )

    def set_cajero_activo(self, cajero):
        self.cajero_activo = cajero
        icono = "👑" if cajero.rol == "admin" else "👤"
        self.lbl_cajero.setText(f"{icono} {cajero.nombre}")
        if hasattr(self, "lbl_cajero_footer"):
            self.lbl_cajero_footer.setText(f"{icono}  {cajero.nombre}")
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
