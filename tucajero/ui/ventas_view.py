from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import CardPremium, ButtonPremium, TABLE_STYLE_PREMIUM
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDoubleSpinBox,
    QHeaderView,
    QDialog,
    QDialogButtonBox,
    QButtonGroup,
    QRadioButton,
    QSizePolicy,
    QInputDialog,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, QTimer
from tucajero.utils.formato import fmt_moneda

IVA_RATE = 0.19


class PaymentDialog(QDialog):
    """Dialog for payment with multiple payment methods"""

    def __init__(self, subtotal, iva, total, parent=None, cliente=None, descuento=0):
        super().__init__(parent)
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.payment_amount = 0
        self.metodo_pago = "Efectivo"
        self.cliente = cliente
        self.descuento = descuento
        self.init_ui()

    def init_ui(self):
        """Initialize the payment dialog UI - Premium Design"""
        self.setWindowTitle("Cobro")
        self.setMinimumSize(450, 550)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        from tucajero.utils.store_config import get_store_name

        # Header con nombre del negocio
        store_name_label = QLabel(get_store_name())
        store_name_label.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Colors.TEXT_PRIMARY};"
        )
        store_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(store_name_label)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(
            f"background-color: {Colors.BORDER_DEFAULT}; max-height: 1px; border: none;"
        )
        layout.addWidget(sep)

        # Total a pagar - Display premium
        total_container = QWidget()
        total_container.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_ELEVATED};
                border-radius: 16px;
                border: 1px solid {Colors.BORDER_DEFAULT};
                padding: 16px;
            }}
        """)
        total_layout = QVBoxLayout(total_container)
        total_layout.setSpacing(8)

        total_label = QLabel("TOTAL A PAGAR")
        total_label.setObjectName("total_label")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_label.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;"
        )
        total_layout.addWidget(total_label)

        self.lbl_total = QLabel(fmt_moneda(self.total))
        self.lbl_total.setStyleSheet(
            f"font-size: 36px; font-weight: 700; color: {Colors.SUCCESS};"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(self.lbl_total)

        if self.descuento > 0:
            lbl_desc = QLabel(f"Descuento: -{fmt_moneda(self.descuento)}")
            lbl_desc.setStyleSheet(
                f"font-size:14px; color:{Colors.DANGER}; font-weight: 600;"
            )
            lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            total_layout.addWidget(lbl_desc)

        layout.addWidget(total_container)

        # Métodos de pago
        metodo_label = QLabel("MÉTODO DE PAGO")
        metodo_label.setStyleSheet(
            f"font-size: 11px; font-weight: 700; color: {Colors.TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        layout.addWidget(metodo_label)

        # Container para botones de método
        metodos_container = QWidget()
        metodos_layout = QGridLayout(metodos_container)
        metodos_layout.setSpacing(8)
        metodos_layout.setContentsMargins(0, 0, 0, 0)

        self.metodo_group = QButtonGroup()
        self.metodo_buttons = []

        metodos = [
            ("💵 Efectivo", "Efectivo", Colors.PRIMARY),
            ("📱 Nequi", "Nequi", Colors.PRIMARY),
            ("📲 Daviplata", "Daviplata", Colors.WARNING),
            ("🏦 Transferencia", "Transferencia", Colors.INFO),
        ]
        if self.cliente:
            metodos.append(("🟡 Fiado (crédito)", "Fiado", Colors.WARNING))

        for idx, (texto, valor, color) in enumerate(metodos):
            radio = QRadioButton(texto)
            radio.setStyleSheet(f"""
                QRadioButton {{
                    background-color: {Colors.BG_INPUT};
                    color: {Colors.TEXT_PRIMARY};
                    border: 2px solid {Colors.BORDER_DEFAULT};
                    border-radius: 12px;
                    padding: 14px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    spacing: 10px;
                }}
                QRadioButton:hover {{
                    border-color: {color};
                    background-color: {Colors.BG_HOVER};
                }}
                QRadioButton:checked {{
                    border-color: {color};
                    background-color: {color}20;
                    font-weight: 600;
                }}
                QRadioButton::indicator {{
                    width: 20px;
                    height: 20px;
                    border-radius: 10px;
                    border: 2px solid {Colors.BORDER_DEFAULT};
                    background: {Colors.BG_INPUT};
                }}
                QRadioButton::indicator:hover {{
                    border-color: {color};
                }}
                QRadioButton::indicator:checked {{
                    border-color: {color};
                    background: {color};
                }}
            """)
            self.metodo_group.addButton(radio)
            self.metodo_group.setId(radio, idx)
            radio.metodo_valor = valor
            radio.toggled.connect(self.on_metodo_changed)
            self.metodo_buttons.append(radio)
            metodos_layout.addWidget(radio, idx // 2, idx % 2)

        layout.addWidget(metodos_container)

        self.metodo_group.buttons()[0].setChecked(True)

        # Container para pago en efectivo
        self.efectivo_container = QWidget()
        efectivo_layout = QVBoxLayout(self.efectivo_container)
        efectivo_layout.setSpacing(8)
        efectivo_layout.setContentsMargins(0, 0, 0, 0)
        self.efectivo_container.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_ELEVATED};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        pago_label = QLabel("Monto recibido:")
        pago_label.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; font-weight: 500;"
        )
        efectivo_layout.addWidget(pago_label)

        self.pago_input = QDoubleSpinBox()
        self.pago_input.setRange(0, 999999999)
        self.pago_input.setDecimals(2)
        self.pago_input.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1.5px solid {Colors.BORDER_DEFAULT};
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 20px;
                font-weight: 600;
            }}
            QDoubleSpinBox:focus {{
                border-color: {Colors.PRIMARY};
            }}
        """)
        self.pago_input.setMinimumWidth(200)
        self.pago_input.setFocus()
        self.pago_input.valueChanged.connect(self.calcular_cambio)
        efectivo_layout.addWidget(self.pago_input)

        self.lbl_cambio = QLabel(f"Cambio: {fmt_moneda(0)}")
        self.lbl_cambio.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {Colors.SUCCESS};"
        )
        self.lbl_cambio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        efectivo_layout.addWidget(self.lbl_cambio)

        layout.addWidget(self.efectivo_container)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        # Botón Cancelar
        btn_cancel = ButtonPremium("CANCELAR", style="secondary")
        btn_cancel.setFixedHeight(48)
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)

        # Botón Confirmar
        btn_confirm = ButtonPremium("CONFIRMAR PAGO", style="success")
        btn_confirm.setFixedHeight(48)
        btn_confirm.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_confirm)

        layout.addLayout(buttons_layout)

    def on_metodo_changed(self):
        """Handle payment method change"""
        for radio in self.metodo_group.buttons():
            if radio.isChecked():
                self.metodo_pago = radio.metodo_valor
                break
        if self.metodo_pago == "Efectivo":
            self.efectivo_container.setVisible(True)
        else:
            self.efectivo_container.setVisible(False)

    def calcular_cambio(self):
        """Calculate change from payment"""
        pago = self.pago_input.value()
        cambio = pago - self.total
        if cambio >= 0:
            self.lbl_cambio.setText(f"Cambio: {fmt_moneda(cambio)}")
            self.lbl_cambio.setStyleSheet(
                f"font-size: 20px; font-weight: 700; color: {Colors.SUCCESS};"
            )
            self.payment_amount = pago
        else:
            self.lbl_cambio.setText(f"Faltan: {fmt_moneda(abs(cambio))}")
            self.lbl_cambio.setStyleSheet(
                f"font-size: 20px; font-weight: 700; color: {Colors.DANGER};"
            )
            self.payment_amount = 0

    def accept(self):
        """Handle dialog acceptance"""
        if self.metodo_pago == "Efectivo" and self.pago_input.value() < self.total:
            QMessageBox.warning(
                self, "Pago insuficiente", "El monto recibido es menor al total"
            )
            return
        super().accept()


class VentasView(QWidget):
    """Sales view with auto-refresh support"""

    sale_completed = Signal()
    cotizacion_creada = Signal()

    def __init__(self, session, parent=None, cajero_activo=None):
        super().__init__(parent)
        self.session = session
        self.cajero_activo = cajero_activo
        self.carrito = []
        self.productos = []
        self.descuento = {"tipo": None, "valor": 0, "total": 0}
        self._initialized = False
        self._loading = False
        self._procesando_pago = False
        self.init_ui()
        self._initialized = True
        self.cargar_productos()
        self.txt_codigo.setFocus()

    def init_ui(self):
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QVBoxLayout,
            QWidget,
            QLabel,
            QLineEdit,
            QTableWidget,
            QHeaderView,
            QFrame,
            QButtonGroup,
            QGridLayout,
            QGraphicsDropShadowEffect,
        )
        from PySide6.QtGui import QColor

        # Fondo oscuro premium
        self.setStyleSheet(f"background: {Colors.BG_APP};")

        # Layout principal 2 columnas
        main = QHBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(20)

        # ════════════════════════════════════════
        # COLUMNA IZQUIERDA (70%)
        # ════════════════════════════════════════
        left = QWidget()
        left.setStyleSheet("background: transparent;")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(0, 0, 0, 0)
        left_l.setSpacing(12)

        # ── Card: Header de venta ──────────────
        hdr_card = QWidget()
        hdr_card.setObjectName("hdrCard")
        hdr_card.setStyleSheet(f"""
            QWidget#hdrCard {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: none;
            }}
            QWidget#hdrCard * {{ background: transparent; border: none; }}
        """)
        self._apply_shadow(hdr_card)
        hdr_l = QHBoxLayout(hdr_card)
        hdr_l.setContentsMargins(20, 14, 20, 14)

        title_lbl = QLabel("Nueva Venta")
        title_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 18px; font-weight: bold;"
        )
        hdr_l.addWidget(title_lbl)
        hdr_l.addStretch()

        self.lbl_cliente = QLabel("👤  Sin cliente")
        self.lbl_cliente.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 12px;"
        )
        hdr_l.addWidget(self.lbl_cliente)

        self.btn_cliente = ButtonPremium("Seleccionar cliente", style="primary")
        self.btn_cliente.setMinimumHeight(44)
        self.btn_cliente.clicked.connect(self.seleccionar_cliente)
        hdr_l.addWidget(self.btn_cliente)
        self.btn_quitar_cliente = QPushButton("✕")
        self.btn_quitar_cliente.setFixedSize(28, 28)
        self.btn_quitar_cliente.setVisible(False)
        self.btn_quitar_cliente.setStyleSheet(
            f"background: {Colors.DANGER}22; color: {Colors.DANGER}; border-radius: 14px; border: none; font-weight: bold;"
        )
        self.btn_quitar_cliente.clicked.connect(self.quitar_cliente)
        hdr_l.addWidget(self.btn_quitar_cliente)
        left_l.addWidget(hdr_card)

        # ── Card: Búsqueda ──────────────────────
        search_card = QWidget()
        search_card.setObjectName("searchCard")
        search_card.setStyleSheet(f"""
            QWidget#searchCard {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: none;
            }}
            QWidget#searchCard * {{ background: transparent; border: none; }}
        """)
        self._apply_shadow(search_card)
        search_l = QHBoxLayout(search_card)
        search_l.setContentsMargins(16, 12, 16, 12)
        search_l.setSpacing(10)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16px; background: transparent;")
        search_l.addWidget(search_icon)

        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText(
            "Buscar productos por nombre, código o categoría..."
        )
        self.txt_codigo.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.LG}px;
                padding: {Spacing.LG}px {Spacing.XL}px;
                font-size: {Typography.H4}px;
                min-height: 30px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.PRIMARY};
                background: {Colors.BG_ELEVATED};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_MUTED};
            }}
        """)
        self.txt_codigo.returnPressed.connect(self.buscar_producto)
        self.txt_codigo.setFocus()
        search_l.addWidget(self.txt_codigo)

        self.btn_buscar = ButtonPremium("Buscar  →", style="primary")
        self.btn_buscar.setFixedSize(110, 36)
        self.btn_buscar.clicked.connect(self.mostrar_buscador)
        search_l.addWidget(self.btn_buscar)
        left_l.addWidget(search_card)

        # ── Card: Tabla del carrito ─────────────
        cart_card = QWidget()
        cart_card.setObjectName("cartCard")
        cart_card.setStyleSheet(f"""
            QWidget#cartCard {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: none;
            }}
        """)
        self._apply_shadow(cart_card)
        cart_l = QVBoxLayout(cart_card)
        cart_l.setContentsMargins(0, 0, 0, 0)
        cart_l.setSpacing(0)

        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(7)
        self.tabla_carrito.setHorizontalHeaderLabels(
            ["Código", "Stock", "Producto", "Cant.", "Precio", "IVA", "Subtotal"]
        )
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch  # Producto
        )
        self.tabla_carrito.setColumnWidth(0, 120)  # Código
        self.tabla_carrito.setColumnWidth(1, 80)   # Stock
        self.tabla_carrito.setColumnWidth(3, 140)  # Cant. (más ancho para botones)
        self.tabla_carrito.setColumnWidth(4, 120)  # Precio
        self.tabla_carrito.setColumnWidth(5, 100)  # IVA
        self.tabla_carrito.setColumnWidth(6, 130)  # Subtotal
        self.tabla_carrito.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_carrito.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_carrito.setMinimumHeight(280)
        self.tabla_carrito.setStyleSheet(TABLE_STYLE_PREMIUM)
        cart_l.addWidget(self.tabla_carrito)

        # Barra de acciones (Descuento + Eliminar — sin botones ± redundantes)
        actions_bar = QWidget()
        actions_bar.setMinimumHeight(60)
        actions_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        actions_bar.setStyleSheet(
            f"background: {Colors.BG_INPUT}; border-radius: 0 0 12px 12px; "
            f"border-top: 1px solid {Colors.BORDER_DEFAULT};"
        )
        actions_l = QHBoxLayout(actions_bar)
        actions_l.setContentsMargins(12, 8, 12, 8)
        actions_l.setSpacing(8)

        self.btn_descuento = ButtonPremium("% Descuento", style="secondary")
        self.btn_descuento.setMinimumHeight(44)
        self.btn_descuento.clicked.connect(self.aplicar_descuento)

        self.btn_eliminar = ButtonPremium("🗑  Eliminar", style="danger")
        self.btn_eliminar.setMinimumHeight(44)
        self.btn_eliminar.clicked.connect(self.eliminar_item)

        actions_l.addWidget(self.btn_descuento)
        actions_l.addStretch()
        actions_l.addWidget(self.btn_eliminar)
        cart_l.addWidget(actions_bar)
        left_l.addWidget(cart_card)

        main.addWidget(left, 7)

        # ════════════════════════════════════════
        # COLUMNA DERECHA — Panel de pago
        # ════════════════════════════════════════
        right = QWidget()
        right.setFixedWidth(300)
        right.setStyleSheet("background: transparent;")
        self.right_layout = QVBoxLayout(right)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(12)

        # ── Card: Resumen de pago ───────────────
        resumen_card = QWidget()
        resumen_card.setObjectName("resumenCard")
        resumen_card.setStyleSheet(f"""
            QWidget#resumenCard {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: none;
            }}
            QWidget#resumenCard * {{ background: transparent; border: none; }}
        """)
        self._apply_shadow(resumen_card)
        res_l = QVBoxLayout(resumen_card)
        res_l.setContentsMargins(20, 18, 20, 18)
        res_l.setSpacing(10)

        res_title = QLabel("Resumen de Pago")
        res_title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: 15px; font-weight: bold;"
        )
        res_l.addWidget(res_title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {Colors.BORDER_DEFAULT}; border: none; max-height: 1px;")
        res_l.addWidget(sep)

        def make_row(label_text, value_text, color=None):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;"
            )
            val = QLabel(value_text)
            val.setStyleSheet(
                f"color: {color or Colors.TEXT_PRIMARY}; font-size: 13px; font-weight: bold;"
            )
            val.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(lbl)
            row.addWidget(val)
            return row, val

        sub_row, self.lbl_subtotal = make_row("Subtotal", fmt_moneda(0))
        res_l.addLayout(sub_row)

        iva_row, self.lbl_iva = make_row("IVA (19%)", fmt_moneda(0))
        res_l.addLayout(iva_row)

        desc_row, self.lbl_descuento_val = make_row("Descuento", "-$0.00", Colors.SUCCESS)
        res_l.addLayout(desc_row)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"background: {Colors.BORDER_DEFAULT}; border: none; max-height: 1px;")
        res_l.addWidget(sep2)

        # TOTAL A PAGAR
        total_row = QHBoxLayout()
        total_lbl = QLabel("TOTAL A PAGAR")
        total_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: bold; letter-spacing: 0.5px;"
        )
        self.lbl_total = QLabel(fmt_moneda(0))
        self.lbl_total.setStyleSheet(
            f"color: {Colors.PRIMARY}; font-size: 24px; font-weight: bold;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_row.addWidget(total_lbl)
        total_row.addWidget(self.lbl_total)
        res_l.addLayout(total_row)
        self.right_layout.addWidget(resumen_card)

        # ── Card: Método de pago ────────────────
        metodo_card = QWidget()
        metodo_card.setObjectName("metodoCard")
        metodo_card.setStyleSheet(f"""
            QWidget#metodoCard {{
                background-color: {Colors.BG_CARD};
                border-radius: 12px;
                border: none;
            }}
            QWidget#metodoCard * {{ background: transparent; }}
        """)
        self._apply_shadow(metodo_card)
        met_l = QVBoxLayout(metodo_card)
        met_l.setContentsMargins(20, 16, 20, 16)
        met_l.setSpacing(10)

        met_title = QLabel("MÉTODO DE PAGO")
        met_title.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 10px; font-weight: bold; letter-spacing: 1px;"
        )
        met_l.addWidget(met_title)

        self.metodo_grupo = QButtonGroup(self)
        metodos = [
            ("💵", "EFECTIVO"),
            ("📱", "NEQUI"),
            ("📱", "DAVIPLATA"),
            ("🏦", "TRANSF."),
            ("💳", "MIXTO"),
        ]
        grid = QGridLayout()
        grid.setSpacing(8)

        for i, (icon, nombre) in enumerate(metodos):
            btn = QPushButton(f"{icon}\n{nombre}")
            btn.setFixedHeight(64)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {Colors.BG_INPUT};
                    color: {Colors.TEXT_SECONDARY};
                    border: 1.5px solid {Colors.BORDER_DEFAULT};
                    border-radius: {BorderRadius.MD}px;
                    font-size: {Typography.CAPTION}px;
                    font-weight: {Typography.BOLD};
                }}
                QPushButton:checked {{
                    background: {Colors.BG_ELEVATED};
                    color: {Colors.PRIMARY};
                    border: 1.5px solid {Colors.PRIMARY};
                }}
                QPushButton:hover {{
                    background: {Colors.BG_HOVER};
                    border-color: {Colors.PRIMARY};
                }}
            """)
            if i == 0:
                btn.setChecked(True)
            self.metodo_grupo.addButton(btn, i)
            if i == 4:
                grid.addWidget(btn, i // 2, 0, 1, 2)
            else:
                grid.addWidget(btn, i // 2, i % 2)

        met_l.addLayout(grid)
        self.right_layout.addWidget(metodo_card)

        self.right_layout.addStretch()

        # ── Botón CONFIRMAR VENTA ───────────────
        self.btn_cobrar = ButtonPremium("✦  CONFIRMAR VENTA", style="success")
        self.btn_cobrar.setMinimumHeight(70)
        self.btn_cobrar.clicked.connect(self.cobrar)
        self.right_layout.addWidget(self.btn_cobrar)

        # Botones secundarios
        sec_l = QHBoxLayout()
        sec_l.setSpacing(8)

        self.btn_cancelar = ButtonPremium("✕  Cancelar", style="secondary")
        self.btn_cancelar.setMinimumHeight(44)
        self.btn_cancelar.clicked.connect(self.cancelar_venta)

        self.btn_cotizacion = ButtonPremium("📋  Cotizar", style="secondary")
        self.btn_cotizacion.setMinimumHeight(44)
        self.btn_cotizacion.clicked.connect(self.guardar_cotizacion)

        sec_l.addWidget(self.btn_cancelar)
        sec_l.addWidget(self.btn_cotizacion)
        self.right_layout.addLayout(sec_l)

        main.addWidget(right, 3)

        # Inicializar estado
        self.carrito = []
        self.descuento = {"tipo": None, "valor": 0, "total": 0}
        self.cliente_seleccionado = None
        self._highlight_nueva_fila = False

    def _apply_shadow(self, widget, blur=16, offset_y=4, opacity=35):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, offset_y)
        shadow.setColor(QColor(0, 0, 0, opacity))
        widget.setGraphicsEffect(shadow)

    def cargar_productos(self):
        """Load all products for the search"""
        from tucajero.services.producto_service import ProductoService

        service = ProductoService(self.session)
        self.productos = service.get_all_productos()

    def recargar_productos(self):
        """Reload products (called after sale)"""
        self.session.commit()
        self.cargar_productos()

    def buscar_producto(self):
        """Search product by code or name"""
        if not self._initialized:
            return

        from tucajero.services.producto_service import ProductoService

        texto = self.txt_codigo.text().strip()
        if not texto:
            return

        service = ProductoService(self.session)

        producto = service.get_producto_by_codigo(texto)
        if producto and producto.stock > 0:
            self.agregar_al_carrito(producto)
            self.txt_codigo.clear()
            self.txt_codigo.setFocus()
            return

        productos = service.get_producto_by_nombre(texto)
        if len(productos) == 1:
            producto = productos[0]
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.txt_codigo.clear()
                self.txt_codigo.setFocus()
                return
        elif len(productos) > 1:
            self.txt_codigo.clear()
            self.mostrar_buscador_productos(productos)
            return

        QMessageBox.warning(None, "No encontrado", f"No se encontró '{texto}'")
        self.txt_codigo.selectAll()
        self.txt_codigo.setFocus()

    def mostrar_buscador(self):
        """Show product search dialog"""
        import logging
        from tucajero.ui.buscador_productos import BuscadorProductosDialog

        dialog = BuscadorProductosDialog(
            self.productos, session=self.session, parent=self
        )
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.producto_seleccionado
        ):
            producto = dialog.producto_seleccionado
            try:
                stock = getattr(producto, "stock", 0)
                if stock is None:
                    stock = 0
                if stock > 0:
                    self.agregar_al_carrito(producto)
                    self.txt_codigo.setFocus()
                else:
                    QMessageBox.warning(
                        None,
                        "Sin stock",
                        f"El producto '{producto.nombre}' no tiene stock disponible.",
                    )
            except Exception as e:
                logging.error(
                    f"Error al procesar producto del buscador: {e}", exc_info=True
                )
                QMessageBox.critical(
                    None,
                    "Error",
                    f"No se pudo procesar el producto seleccionado:\n{str(e)}",
                )

    def seleccionar_cliente(self):
        from tucajero.ui.selector_cliente import SelectorClienteDialog

        dialog = SelectorClienteDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.cliente:
            self.cliente_seleccionado = dialog.cliente
            self.lbl_cliente.setText(
                f"👤 {dialog.cliente.nombre}"
                + (
                    f" — 🔴 Debe {fmt_moneda(dialog.cliente.saldo_credito)}"
                    if dialog.cliente.saldo_credito > 0
                    else ""
                )
            )
            self.lbl_cliente.setStyleSheet(
                f"color: {Colors.PRIMARY}; font-size: 12px; font-weight: bold;"
            )
            self.btn_quitar_cliente.setVisible(True)

    def quitar_cliente(self):
        self.cliente_seleccionado = None
        self.lbl_cliente.setText("👤 Sin cliente")
        self.lbl_cliente.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
        )
        self.btn_quitar_cliente.setVisible(False)

    def mostrar_buscador_productos(self, productos):
        """Show custom product list when multiple matches"""
        import logging
        from tucajero.ui.buscador_productos import BuscadorProductosDialog

        dialog = BuscadorProductosDialog(productos, session=self.session, parent=self)
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.producto_seleccionado
        ):
            producto = dialog.producto_seleccionado
            try:
                stock = getattr(producto, "stock", 0)
                if stock is None:
                    stock = 0
                if stock > 0:
                    self.agregar_al_carrito(producto)
                    self.txt_codigo.setFocus()
                else:
                    QMessageBox.warning(
                        None,
                        "Sin stock",
                        f"El producto '{producto.nombre}' no tiene stock disponible.",
                    )
            except Exception as e:
                logging.error(f"Error al procesar producto: {e}", exc_info=True)
                QMessageBox.critical(
                    None, "Error", f"No se pudo procesar el producto:\n{str(e)}"
                )

    def agregar_al_carrito(self, producto):
        """Add product to cart"""
        import logging

        try:
            logging.info(f"Intentando agregar producto: {producto}")

            producto_id = getattr(producto, "id", None)
            if producto_id is None:
                raise AttributeError(f"Producto sin id: {producto}")

            for item in self.carrito:
                if item["producto_id"] == producto_id:
                    item["cantidad"] += 1
                    self.actualizar_tabla()
                    self.mostrar_feedback(f"✓ {producto.nombre} x{item['cantidad']}")
                    logging.info(
                        f"Producto existente actualizado. Carrito: {len(self.carrito)} items"
                    )
                    return

            self.carrito.append(
                {
                    "producto_id": producto_id,
                    "codigo": producto.codigo,
                    "nombre": producto.nombre,
                    "precio": float(producto.precio),
                    "cantidad": 1,
                    "stock": getattr(producto, "stock", 0),
                    "aplica_iva": getattr(producto, "aplica_iva", True),
                }
            )
            self.actualizar_tabla()
            self.tabla_carrito.scrollToBottom()
            self._highlight_ultima_fila()
            self.mostrar_feedback(f"✓ {producto.nombre} agregado")
            logging.info(f"Producto agregado. Carrito: {len(self.carrito)} items")

        except Exception as e:
            logging.error(f"Error al agregar producto al carrito: {e}", exc_info=True)
            # Usar None como padre para evitar problemas de ciclo de vida de widgets
            QMessageBox.critical(
                None, "Error", f"No se pudo agregar el producto:\n{str(e)}"
            )

    def _highlight_ultima_fila(self):
        from PySide6.QtGui import QColor, QBrush
        from PySide6.QtCore import QTimer

        last_row = self.tabla_carrito.rowCount() - 1
        if last_row < 0:
            return

        for col in range(self.tabla_carrito.columnCount()):
            item = self.tabla_carrito.item(last_row, col)
            if item:
                item.setBackground(QBrush(QColor(Colors.SUCCESS + "44")))

        def quitar_highlight():
            if last_row < self.tabla_carrito.rowCount():
                for col in range(self.tabla_carrito.columnCount()):
                    cell = self.tabla_carrito.cellWidget(last_row, col)
                    item = self.tabla_carrito.item(last_row, col)
                    if item:
                        item.setBackground(QBrush(QColor("transparent")))

        QTimer.singleShot(1500, quitar_highlight)

    def mostrar_feedback(self, mensaje, tipo="success"):
        color = Colors.SUCCESS if tipo == "success" else Colors.DANGER

        try:
            from PySide6.QtWidgets import QLabel
            from PySide6.QtCore import QTimer

            # Crear toast sin padre para evitar problemas de ciclo de vida
            toast = QLabel(mensaje)
            toast.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            toast.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            toast.setStyleSheet(f"""
                background-color: {color};
                color: white;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: bold;
            """)
            toast.adjustSize()
            toast.setFixedWidth(280)

            # Posicionar en la esquina superior derecha del widget
            if self.isVisible():
                pos = self.mapToGlobal(self.rect().topRight())
                x = pos.x() - toast.width() - 20
                y = pos.y() + 80
                toast.move(x, y)

            toast.show()
            toast.raise_()

            # Función segura para eliminar el toast
            def eliminar_toast():
                try:
                    if toast and not toast.isHidden():
                        toast.hide()
                        toast.deleteLater()
                except RuntimeError:
                    pass

            QTimer.singleShot(2000, eliminar_toast)
        except RuntimeError:
            pass

    def actualizar_tabla(self):
        """Update cart table"""
        self.tabla_carrito.setRowCount(0)
        self.tabla_carrito.setRowCount(len(self.carrito))

        subtotal_total = 0
        iva_total = 0

        for i, item in enumerate(self.carrito):
            cantidad = item["cantidad"]
            precio = item["precio"]
            aplica_iva = item.get("aplica_iva", True)
            iva = round(precio * cantidad * 0.19, 2) if aplica_iva else 0
            iva_total += iva
            total_item = precio * cantidad + iva
            subtotal_total += precio * cantidad

            from PySide6.QtWidgets import QTableWidgetItem
            from PySide6.QtCore import Qt

            # Código (centrado)
            item_codigo = QTableWidgetItem(item["codigo"])
            item_codigo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_carrito.setItem(i, 0, item_codigo)
            
            # Stock (centrado)
            item_stock = QTableWidgetItem(str(item["stock"]))
            item_stock.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_carrito.setItem(i, 1, item_stock)
            
            # Producto (centrado)
            item_nombre = QTableWidgetItem(item["nombre"])
            item_nombre.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_carrito.setItem(i, 2, item_nombre)
            
            self.tabla_carrito.setCellWidget(
                i, 3, self._crear_widget_cantidad(i, cantidad)
            )

            # Precio (centrado)
            lbl_precio = QTableWidgetItem(fmt_moneda(precio))
            lbl_precio.setFlags(lbl_precio.flags() & ~Qt.ItemFlag.ItemIsEditable)
            lbl_precio.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_carrito.setItem(i, 4, lbl_precio)

            # IVA (centrado)
            lbl_iva = QTableWidgetItem(fmt_moneda(iva) if aplica_iva else "—")
            lbl_iva.setFlags(lbl_iva.flags() & ~Qt.ItemFlag.ItemIsEditable)
            lbl_iva.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_carrito.setItem(i, 5, lbl_iva)

            # Subtotal (centrado)
            lbl_subtotal = QTableWidgetItem(fmt_moneda(total_item))
            lbl_subtotal.setFlags(lbl_subtotal.flags() & ~Qt.ItemFlag.ItemIsEditable)
            lbl_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla_carrito.setItem(i, 6, lbl_subtotal)

            # Aumentado para que los botones se vean completos
            self.tabla_carrito.setRowHeight(i, 70)

        self._actualizar_resumen(subtotal_total, iva_total)
        self.tabla_carrito.scrollToBottom()

    def _crear_widget_cantidad(self, row, cantidad):
        from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit
        from PySide6.QtGui import QIntValidator

        qty_widget = QWidget()
        qty_widget.setFixedSize(130, 55)  # Ancho fijo para centrar en la celda
        qty_widget.setStyleSheet("background: transparent;")
        qty_layout = QHBoxLayout(qty_widget)
        qty_layout.setContentsMargins(4, 4, 4, 4)
        qty_layout.setSpacing(6)
        qty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_m = QPushButton("−")
        btn_m.setFixedSize(32, 32)
        btn_m.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.DANGER};
                color: white; border-radius: {BorderRadius.FULL}px;
                font-size: {Typography.H5}px; font-weight: {Typography.BOLD}; border: none; padding: 0;
            }}
            QPushButton:hover {{ background: #dc2626; }}
        """)

        lbl_qty = QLineEdit(str(cantidad))
        lbl_qty.setValidator(QIntValidator(1, 99999))  # Hasta 5 cifras
        lbl_qty.setFixedWidth(75)
        lbl_qty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_qty.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-weight: bold; font-size: 15px; "
            "background: transparent; border: none; padding: 0px; margin: 0px;"
        )
        lbl_qty.setFixedHeight(35)

        def update_qty():
            text = lbl_qty.text()
            if text.isdigit() and int(text) > 0:
                self.carrito[row]["cantidad"] = int(text)
            self.actualizar_tabla()

        lbl_qty.editingFinished.connect(update_qty)

        btn_p = QPushButton("+")
        btn_p.setFixedSize(32, 32)
        btn_p.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.SUCCESS};
                color: white; border-radius: {BorderRadius.FULL}px;
                font-size: {Typography.H5}px; font-weight: {Typography.BOLD}; border: none; padding: 0;
            }}
            QPushButton:hover {{ background: #059669; }}
        """)

        btn_m.clicked.connect(lambda _, r=row: self._cambiar_cantidad(r, -1))
        btn_p.clicked.connect(lambda _, r=row: self._cambiar_cantidad(r, +1))

        qty_layout.addWidget(btn_m)
        qty_layout.addWidget(lbl_qty)
        qty_layout.addWidget(btn_p)
        return qty_widget

    def _cambiar_cantidad(self, row, delta):
        if 0 <= row < len(self.carrito):
            nueva = self.carrito[row]["cantidad"] + delta
            if nueva <= 0:
                self.carrito.pop(row)
            else:
                self.carrito[row]["cantidad"] = nueva
            self.actualizar_tabla()

    def _actualizar_resumen(self, subtotal, iva):
        from tucajero.utils.formato import fmt_moneda

        descuento_val = (
            self.descuento.get("total", 0)
            if hasattr(self, "descuento") and self.descuento
            else 0
        )
        total = max(0, subtotal + iva - descuento_val)

        self.lbl_subtotal.setText(fmt_moneda(subtotal))
        self.lbl_iva.setText(fmt_moneda(iva))
        self.lbl_total.setText(fmt_moneda(total))
        
        # Actualizar también el label del panel de cobro si está visible
        if hasattr(self, "lbl_total_cobro") and self.lbl_total_cobro:
            self.lbl_total_cobro.setText(fmt_moneda(total))

        if hasattr(self, "lbl_descuento_val"):
            if descuento_val > 0:
                self.lbl_descuento_val.setText(f"- {fmt_moneda(descuento_val)}")
            else:
                self.lbl_descuento_val.setText("")

    def aplicar_descuento(self):
        if not self.carrito:
            QMessageBox.warning(
                self, "Carrito vacío", "Agrega productos antes de aplicar un descuento."
            )
            return
        subtotal = sum(item["cantidad"] * item["precio"] for item in self.carrito)
        iva = sum(
            round(item["cantidad"] * item["precio"] * 0.19, 2)
            for item in self.carrito
            if item.get("aplica_iva", True)
        )
        total_bruto = subtotal + iva

        from tucajero.ui.descuento_dialog import DescuentoDialog

        dialog = DescuentoDialog(total_bruto, self.descuento.copy(), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.descuento = dialog.descuento_resultado
            self.actualizar_tabla()
            if self.descuento["total"] > 0:
                self.btn_descuento.setText(f"🏷 -{fmt_moneda(self.descuento['total'])}")
                self.btn_descuento.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.SUCCESS};
                        color: white; padding: 4px 12px;
                        font-weight: bold; border-radius: 8px; border: none;
                    }}
                """)
            else:
                self.btn_descuento.setText("% Descuento")
                self.btn_descuento.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.BG_HOVER};
                        color: {Colors.WARNING};
                        border: 1px solid {Colors.WARNING};
                        border-radius: 8px; padding: 4px 12px;
                        font-size: 12px; font-weight: bold;
                    }}
                    QPushButton:hover {{ background-color: {Colors.WARNING}; color: white; }}
                """)

    def eliminar_item(self):
        """Remove item from cart"""
        row = self.tabla_carrito.currentRow()
        if row >= 0 and row < len(self.carrito):
            self.carrito.pop(row)
            self.actualizar_tabla()

    def cancelar_venta(self):
        """Cancel current sale"""
        if not self.carrito:
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Cancelar la venta actual?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.carrito = []
            self.descuento = {"tipo": None, "valor": 0, "total": 0}
            self.btn_descuento.setText("% Descuento")
            self.btn_descuento.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.BG_HOVER};
                    color: {Colors.WARNING};
                    border: 1px solid {Colors.WARNING};
                    border-radius: 8px; padding: 4px 12px;
                    font-size: 12px; font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {Colors.WARNING}; color: white; }}
            """)
            self.actualizar_tabla()
            self.txt_codigo.setFocus()

    def cobrar(self):
        """Show inline payment panel"""
        if not self._initialized:
            return

        if getattr(self, "_procesando_pago", False):
            return

        if not self.carrito:
            return

        self._procesando_pago = True
        self.btn_cobrar.setEnabled(False)

        self.btn_cancelar.setVisible(False)
        self.btn_cotizacion.setVisible(False)
        self.btn_cobrar.setVisible(False)

        metodos = ["Efectivo", "Nequi", "Daviplata", "Transferencia", "Mixto"]
        metodo_id = self.metodo_grupo.checkedId()
        self._metodo_seleccionado = metodos[metodo_id] if metodo_id >= 0 else "Efectivo"

        self.cobro_widget = QWidget()
        self.cobro_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_ELEVATED};
                border-radius: 12px;
                border: 1.5px solid {Colors.PRIMARY};
            }}
        """)
        cobro_layout = QVBoxLayout(self.cobro_widget)
        cobro_layout.setContentsMargins(16, 16, 16, 16)
        cobro_layout.setSpacing(10)

        total_lbl = QLabel("💳 Total a cobrar")
        total_lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: bold;"
        )
        cobro_layout.addWidget(total_lbl)

        self.lbl_total_cobro = QLabel(self.lbl_total.text())
        self.lbl_total_cobro.setStyleSheet(
            f"color: {Colors.SUCCESS}; font-size: 28px; font-weight: bold;"
        )
        self.lbl_total_cobro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cobro_layout.addWidget(self.lbl_total_cobro)

        if self._metodo_seleccionado in ["Efectivo", "Mixto"]:
            texto_lbl = (
                "Monto en Efectivo:"
                if self._metodo_seleccionado == "Mixto"
                else "Monto recibido:"
            )
            recibido_lbl = QLabel(texto_lbl)
            recibido_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px;")
            cobro_layout.addWidget(recibido_lbl)

            self.txt_recibido = QLineEdit()
            self.txt_recibido.setPlaceholderText("$0.00")
            self.txt_recibido.setStyleSheet(f"""
                QLineEdit {{
                    background: {Colors.BG_INPUT};
                    color: {Colors.TEXT_PRIMARY};
                    border: 1.5px solid {Colors.PRIMARY};
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 20px;
                    font-weight: bold;
                }}
            """)
            self.txt_recibido.textChanged.connect(self._calcular_cambio_inline)
            cobro_layout.addWidget(self.txt_recibido)

            texto_cambio = (
                "Restante Electrónico: $0.00"
                if self._metodo_seleccionado == "Mixto"
                else "Cambio: $0.00"
            )
            self.lbl_cambio_inline = QLabel(texto_cambio)
            self.lbl_cambio_inline.setStyleSheet(
                f"color: {Colors.INFO}; font-size: 14px; font-weight: bold;"
            )
            self.lbl_cambio_inline.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cobro_layout.addWidget(self.lbl_cambio_inline)
        else:
            self.txt_recibido = None
            self.lbl_cambio_inline = None

        btns = QHBoxLayout()

        btn_back = ButtonPremium("← Volver", style="secondary")
        btn_back.setFixedHeight(42)
        btn_back.clicked.connect(self._cancelar_cobro)

        btn_confirmar = ButtonPremium("✓ Confirmar", style="success")
        btn_confirmar.setFixedHeight(42)
        btn_confirmar.clicked.connect(self._confirmar_cobro)

        btns.addWidget(btn_back)
        btns.addWidget(btn_confirmar)
        cobro_layout.addLayout(btns)

        self.right_layout.insertWidget(2, self.cobro_widget)
        if hasattr(self, "txt_recibido") and self.txt_recibido:
            self.txt_recibido.setFocus()

    def _calcular_cambio_inline(self):
        if hasattr(self, "txt_recibido") and self.txt_recibido is None:
            return
        try:
            if hasattr(self, "txt_recibido") and self.txt_recibido:
                recibido_txt = self.txt_recibido.text()
            else:
                return

            recibido = float(recibido_txt.replace("$", "").replace(",", "") or 0)
            total = self._get_total_float()
            cambio = recibido - total

            if self._metodo_seleccionado == "Mixto":
                restante = total - recibido
                if recibido < 0:
                    self.lbl_cambio_inline.setText("⚠️ El monto no puede ser negativo")
                    self.lbl_cambio_inline.setStyleSheet(
                        f"color: {Colors.DANGER}; font-size: 14px; font-weight: bold;"
                    )
                elif recibido == 0:
                    self.lbl_cambio_inline.setText(
                        f"💳 Pagadero con electrónico: {fmt_moneda(total)}"
                    )
                    self.lbl_cambio_inline.setStyleSheet(
                        f"color: {Colors.INFO}; font-size: 14px; font-weight: bold;"
                    )
                elif recibido >= total:
                    # El efectivo cubre todo - mostrar cambio
                    self.lbl_cambio_inline.setText(
                        f"✓ Pago completo - Cambio: {fmt_moneda(cambio)}"
                    )
                    self.lbl_cambio_inline.setStyleSheet(
                        f"color: {Colors.SUCCESS}; font-size: 14px; font-weight: bold;"
                    )
                else:
                    # Pago mixto válido: muestra cuánto falta por pagar electrónicamente
                    self.lbl_cambio_inline.setText(
                        f"💳 Restante Electrónico: {fmt_moneda(restante)}"
                    )
                    self.lbl_cambio_inline.setStyleSheet(
                        f"color: {Colors.WARNING}; font-size: 14px; font-weight: bold;"
                    )
            else:
                if recibido < 0:
                    self.lbl_cambio_inline.setText("⚠️ El monto no puede ser negativo")
                    self.lbl_cambio_inline.setStyleSheet(
                        f"color: {Colors.DANGER}; font-size: 14px; font-weight: bold;"
                    )
                elif cambio >= 0:
                    self.lbl_cambio_inline.setText(f"✓ Cambio: {fmt_moneda(cambio)}")
                    self.lbl_cambio_inline.setStyleSheet(
                        f"color: {Colors.SUCCESS}; font-size: 14px; font-weight: bold;"
                    )
                else:
                    self.lbl_cambio_inline.setText(f"⚠️ Faltan: {fmt_moneda(abs(cambio))}")
                    self.lbl_cambio_inline.setStyleSheet(
                        f"color: {Colors.DANGER}; font-size: 14px; font-weight: bold;"
                    )
        except:
            pass

    def _get_total_float(self):
        try:
            txt = (
                self.lbl_total.text()
                .replace("$", "")
                .replace(",", "")
                .replace("TOTAL:", "")
                .strip()
            )
            return float(txt)
        except:
            return 0.0

    def _cancelar_cobro(self):
        if hasattr(self, "cobro_widget"):
            self.cobro_widget.deleteLater()
            del self.cobro_widget
        
        # Limpiar referencias a widgets que estaban dentro de cobro_widget
        # para evitar el error "libshiboken: Internal C++ object already deleted"
        if hasattr(self, "lbl_total_cobro"):
            self.lbl_total_cobro = None
        if hasattr(self, "lbl_cambio_inline"):
            self.lbl_cambio_inline = None
        if hasattr(self, "txt_recibido"):
            self.txt_recibido = None
        
        self.btn_cancelar.setVisible(True)
        self.btn_cotizacion.setVisible(True)
        self.btn_cobrar.setVisible(True)
        self.btn_cobrar.setEnabled(True)
        self._procesando_pago = False

    def _confirmar_cobro(self):
        metodo = getattr(self, "_metodo_seleccionado", "Efectivo")
        try:
            if hasattr(self, "txt_recibido") and self.txt_recibido:
                monto_recibido = float(
                    self.txt_recibido.text().replace("$", "").replace(",", "") or 0
                )
            else:
                monto_recibido = self._get_total_float()
        except:
            monto_recibido = self._get_total_float()

        subtotal = sum(item["cantidad"] * item["precio"] for item in self.carrito)
        iva = sum(
            round(item["cantidad"] * item["precio"] * IVA_RATE, 2)
            for item in self.carrito
            if item.get("aplica_iva", True)
        )
        descuento_total = self.descuento.get("total", 0)
        total = max(0, (subtotal + iva) - descuento_total)

        # VALIDACIÓN PARA PAGO MIXTO
        if metodo == "Mixto":
            if monto_recibido < 0:
                QMessageBox.warning(
                    self,
                    "Pago inválido",
                    "El monto en efectivo no puede ser negativo.",
                )
                return
            if monto_recibido >= total:
                # El efectivo cubre todo, no es necesario pago mixto
                QMessageBox.warning(
                    self,
                    "Pago innecesario",
                    f"El efectivo (${monto_recibido:.2f}) cubre el total de la venta.\n"
                    f"Por favor selecciona 'Efectivo' como método de pago.",
                )
                return
            if monto_recibido == 0:
                QMessageBox.warning(
                    self,
                    "Pago incompleto",
                    "Ingresa un monto en efectivo para el pago mixto.\n\n"
                    "El resto se cobrará con método electrónico (Nequi, Daviplata o Transferencia).",
                )
                return
            # En pago mixto, el efectivo + electrónico debe cubrir el total
            # El monto electrónico es (total - monto_recibido)
            monto_electronico = total - monto_recibido
            if monto_electronico < 0:
                QMessageBox.warning(
                    self,
                    "Pago inválido",
                    f"El monto en efectivo (${monto_recibido:.2f}) excede el total (${total:.2f}).\n"
                    f"Por favor selecciona 'Efectivo' como método de pago.",
                )
                return

        # VALIDACIÓN PARA EFECTIVO (solo si es método puro Efectivo)
        if metodo == "Efectivo" and monto_recibido < total:
            QMessageBox.warning(
                self,
                "Pago insuficiente",
                f"El monto recibido (${monto_recibido:.2f}) es menor al total (${total:.2f}).\n"
                f"Faltan: ${total - monto_recibido:.2f}",
            )
            return

        try:
            from tucajero.services.venta_service import VentaService
            from tucajero.utils.ticket import GeneradorTicket

            service = VentaService(self.session)
            cliente_id = (
                self.cliente_seleccionado.id if self.cliente_seleccionado else None
            )
            es_credito = metodo == "Fiado"
            cajero_id = self.cajero_activo.id if self.cajero_activo else None
            venta = service.registrar_venta(
                self.carrito,
                metodo_pago=metodo,
                cliente_id=cliente_id,
                es_credito=es_credito,
                descuento_tipo=self.descuento.get("tipo"),
                descuento_valor=self.descuento.get("valor", 0),
                descuento_total=descuento_total,
                cajero_id=cajero_id,
            )

            generador = GeneradorTicket()
            generador.imprimir(venta, venta.items)

            try:
                from tucajero.utils.store_config import get_printer_enabled
                from tucajero.utils.impresora import get_impresora

                if get_printer_enabled():
                    imp = get_impresora()
                    imp.imprimir_ticket(venta, venta.items)
                    imp.desconectar()
            except Exception as e:
                import logging

                logging.warning(f"No se pudo imprimir en termica: {e}")

            # Registrar venta en auditoría
            try:
                from tucajero.services.audit_service import AuditService
                audit = AuditService(self.session)
                cajero_id_audit = self.cajero_activo.id if self.cajero_activo else None
                cliente_nombre = self.cliente_seleccionado.nombre if self.cliente_seleccionado else "Mostrador"
                audit.registrar(
                    AuditService.VENTA_REGISTRADA,
                    f"Venta #{venta.id} - {fmt_moneda(venta.total)} - {metodo} - Cliente: {cliente_nombre}",
                    usuario_id=cajero_id_audit,
                    entidad_tipo="Venta",
                    entidad_id=venta.id,
                    valor_nuevo=fmt_moneda(venta.total),
                )
            except Exception:
                pass

            self.mostrar_feedback(f"Venta #{venta.id} exitosa!", "success")

        except ValueError as e:
            QMessageBox.warning(None, "Error", str(e))
            return
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error al registrar venta: {str(e)}")
            return

        self._cancelar_cobro()
        self.carrito = []
        self.descuento = {"tipo": None, "valor": 0, "total": 0}
        self.btn_cobrar.setEnabled(True)
        self._procesando_pago = False
        self.btn_descuento.setText("% Descuento")
        self.btn_descuento.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_HOVER};
                color: {Colors.WARNING};
                border: 1px solid {Colors.WARNING};
                border-radius: 8px; padding: 4px 12px;
                font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {Colors.WARNING}; color: white; }}
        """)
        self.actualizar_tabla()
        self.recargar_productos()
        self.sale_completed.emit()
        self.txt_codigo.setFocus()

    def guardar_cotizacion(self):
        """Save current cart as a quotation"""
        if not self.carrito:
            QMessageBox.warning(
                self, "Cotización vacía", "Agrega productos al carrito primero"
            )
            return

        from tucajero.services.cotizacion_service import CotizacionService

        notas = ""
        if self.cliente_seleccionado:
            texto, ok = QInputDialog.getText(
                self,
                "Notas de cotización",
                f"Cliente: {self.cliente_seleccionado.nombre}\n\nNotas opcionales:",
            )
            if ok:
                notas = texto
        else:
            texto, ok = QInputDialog.getText(
                self, "Notas de cotización", "Notas opcionales:"
            )
            if ok:
                notas = texto

        try:
            service = CotizacionService(self.session)
            cliente_id = (
                self.cliente_seleccionado.id if self.cliente_seleccionado else None
            )
            subtotal = sum(item["cantidad"] * item["precio"] for item in self.carrito)

            cotizacion = service.crear(self.carrito, cliente_id=cliente_id, notas=notas)

            QMessageBox.information(
                self,
                "Cotización guardada",
                f"Cotización #{cotizacion.id} guardada exitosamente.\n"
                f"Cliente: {self.cliente_seleccionado.nombre if self.cliente_seleccionado else 'Sin cliente'}\n"
                f"Total: {fmt_moneda(cotizacion.total)}",
            )

            self.cotizacion_creada.emit()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"No se pudo guardar la cotización: {str(e)}"
            )

    def cargar_carrito_desde_cotizacion(self, carrito, cliente):
        """Load items from a quotation into the cart"""
        self.carrito = []
        for item in carrito:
            self.carrito.append(
                {
                    "producto_id": item["producto_id"],
                    "codigo": item["codigo"],
                    "nombre": item["nombre"],
                    "precio": item["precio"],
                    "cantidad": item["cantidad"],
                    "aplica_iva": item.get("aplica_iva", True),
                }
            )

        if cliente:
            self.cliente_seleccionado = cliente
            self.lbl_cliente.setText(f"👤 {cliente.nombre}")
            self.lbl_cliente.setStyleSheet(
                f"color: {Colors.PRIMARY}; font-size: 12px; font-weight: bold;"
            )
        else:
            self.cliente_seleccionado = None
            self.lbl_cliente.setText("👤 Sin cliente")
            self.lbl_cliente.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;"
            )

        self.descuento = {"tipo": None, "valor": 0, "total": 0}
        self.btn_descuento.setText("% Descuento")
        self.btn_descuento.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_HOVER};
                color: {Colors.WARNING};
                border: 1px solid {Colors.WARNING};
                border-radius: 8px; padding: 4px 12px;
                font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {Colors.WARNING}; color: white; }}
        """)
        self.actualizar_tabla()
        self.txt_codigo.setFocus()

        QMessageBox.information(
            self,
            "Cotización cargada",
            f"Se cargaron {len(self.carrito)} productos desde la cotización.\n"
            "Puedes modificar cantidades o proceder al cobro.",
        )
