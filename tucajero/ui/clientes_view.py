from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QHeaderView,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from tucajero.utils.formato import fmt_moneda
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium


class ClientesView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_clientes()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {Colors.BG_APP};")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(Spacing.XXXL, Spacing.XXL, Spacing.XXXL, Spacing.XXL)
        main_layout.setSpacing(Spacing.XXL)
        self.setLayout(main_layout)

        # Titulo
        titulo = QLabel("Clientes")
        titulo.setStyleSheet(f"font-size: {Typography.H2}px; font-weight: {Typography.EXTRABOLD}; color: {Colors.TEXT_PRIMARY};")
        main_layout.addWidget(titulo)

        # Busqueda
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por nombre, documento o telefono...")
        self.input_buscar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1.5px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.SM}px {Spacing.XS}px;
                font-size: {Typography.H5}px;
                min-height: 42px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {Colors.PRIMARY};
            }}
        """)
        self.input_buscar.textChanged.connect(self.buscar_cliente)
        main_layout.addWidget(self.input_buscar)

        # Botones de accion
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.SM)

        btn_nuevo = ButtonPremium("+ Nuevo Cliente", style="primary")
        btn_nuevo.clicked.connect(self.nuevo_cliente)
        btn_layout.addWidget(btn_nuevo)

        btn_editar = ButtonPremium("Editar", style="primary")
        btn_editar.clicked.connect(self.editar_cliente)
        btn_layout.addWidget(btn_editar)

        btn_abonar = ButtonPremium("Abonar", style="success")
        btn_abonar.clicked.connect(self.abonar_cliente)
        btn_layout.addWidget(btn_abonar)

        btn_historial = ButtonPremium("Ver compras", style="secondary")
        btn_historial.clicked.connect(self.ver_historial)
        btn_layout.addWidget(btn_historial)

        btn_eliminar = ButtonPremium("Eliminar", style="danger")
        btn_eliminar.clicked.connect(self.eliminar_cliente)
        btn_layout.addWidget(btn_eliminar)

        main_layout.addLayout(btn_layout)

        # Tabla dentro de card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.XL}px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(0)
        card.setLayout(card_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Documento", "Telefono", "Email", "Saldo credito"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_PRIMARY};
                border: none;
                gridline-color: {Colors.BORDER_DEFAULT};
                font-size: {Typography.BODY}px;
            }}
            QTableWidget::item {{
                padding: {Spacing.SM}px {Spacing.MD}px;
            }}
            QHeaderView::section {{
                background-color: {Colors.BG_ELEVATED};
                color: {Colors.TEXT_SECONDARY};
                padding: {Spacing.SM}px {Spacing.MD}px;
                border: none;
                border-bottom: 2px solid {Colors.BORDER_DEFAULT};
                font-weight: {Typography.SEMIBOLD};
                font-size: {Typography.CAPTION}px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        self.tabla.doubleClicked.connect(self.ver_historial)
        card_layout.addWidget(self.tabla)

        main_layout.addWidget(card)

        # Deudas
        self.lbl_deudas = QLabel("")
        self.lbl_deudas.setStyleSheet(f"color: {Colors.DANGER}; font-size: {Typography.BODY}px; padding: {Spacing.SM}px {Spacing.XXS}px;")
        self.lbl_deudas.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_deudas)

    def cargar_clientes(self, clientes=None):
        from tucajero.services.cliente_service import ClienteService

        service = ClienteService(self.session)
        if clientes is None:
            clientes = service.get_all()

        self.tabla.setRowCount(len(clientes))
        total_deuda = 0

        for i, c in enumerate(clientes):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.tabla.setItem(i, 1, QTableWidgetItem(c.nombre))
            self.tabla.setItem(i, 2, QTableWidgetItem(c.documento or ""))
            self.tabla.setItem(i, 3, QTableWidgetItem(c.telefono or ""))
            self.tabla.setItem(i, 4, QTableWidgetItem(c.email or ""))

            saldo_item = QTableWidgetItem(fmt_moneda(c.saldo_credito))
            if c.saldo_credito > 0:
                saldo_item.setBackground(QColor("#ffeaa7"))
                saldo_item.setForeground(QColor("#d35400"))
            self.tabla.setItem(i, 5, saldo_item)
            total_deuda += c.saldo_credito

        con_deuda = [c for c in clientes if c.saldo_credito > 0]
        if con_deuda:
            self.lbl_deudas.setText(
                f"\u26a0 {len(con_deuda)} cliente(s) con deuda pendiente "
                f"\u2014 Total: {fmt_moneda(total_deuda)}"
            )
        else:
            self.lbl_deudas.setText("")

    def buscar_cliente(self, texto):
        from tucajero.services.cliente_service import ClienteService

        service = ClienteService(self.session)
        if texto.strip():
            clientes = service.search(texto.strip())
        else:
            clientes = service.get_all()
        self.cargar_clientes(clientes)

    def obtener_cliente_seleccionado(self):
        row = self.tabla.currentRow()
        if row >= 0:
            item = self.tabla.item(row, 0)
            if item:
                return int(item.text())
        return None

    def nuevo_cliente(self):
        dialog = ClienteDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_clientes()

    def editar_cliente(self):
        cliente_id = self.obtener_cliente_seleccionado()
        if not cliente_id:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        dialog = ClienteDialog(self.session, self, cliente_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_clientes()

    def abonar_cliente(self):
        cliente_id = self.obtener_cliente_seleccionado()
        if not cliente_id:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        from tucajero.services.cliente_service import ClienteService

        service = ClienteService(self.session)
        cliente = service.get_by_id(cliente_id)
        if cliente.saldo_credito <= 0:
            QMessageBox.information(
                self, "Sin deuda", f"{cliente.nombre} no tiene saldo pendiente."
            )
            return
        dialog = AbonoDialog(self.session, cliente, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_clientes()

    def ver_historial(self):
        cliente_id = self.obtener_cliente_seleccionado()
        if not cliente_id:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        from tucajero.services.cliente_service import ClienteService

        service = ClienteService(self.session)
        cliente = service.get_by_id(cliente_id)
        ventas = service.get_ventas_cliente(cliente_id)
        dialog = HistorialClienteDialog(cliente, ventas, self)
        dialog.exec()

    def eliminar_cliente(self):
        cliente_id = self.obtener_cliente_seleccionado()
        if not cliente_id:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        resp = QMessageBox.question(self, "Confirmar", "\u00bfEliminar este cliente?")
        if resp == QMessageBox.StandardButton.Yes:
            from tucajero.services.cliente_service import ClienteService

            ClienteService(self.session).delete(cliente_id)
            self.cargar_clientes()


class ClienteDialog(QDialog):
    def __init__(self, session, parent=None, cliente_id=None):
        super().__init__(parent)
        self.session = session
        self.cliente_id = cliente_id
        self.setWindowTitle("Nuevo Cliente" if not cliente_id else "Editar Cliente")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {Colors.BG_APP}; }}
            QLabel {{ color: {Colors.TEXT_PRIMARY}; font-size: {Typography.BODY}px; }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

        # Card contenedor
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.MD}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
                padding: {Spacing.XXL}px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(Spacing.MD)
        card.setLayout(card_layout)

        # Titulo del formulario
        titulo = QLabel("Nuevo Cliente" if not cliente_id else "Editar Cliente")
        titulo.setStyleSheet(f"font-size: {Typography.H4}px; font-weight: {Typography.EXTRABOLD}; color: {Colors.TEXT_PRIMARY};")
        titulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(titulo)

        # Formulario
        form = QFormLayout()
        form.setSpacing(Spacing.MD)
        form.setContentsMargins(0, Spacing.SM, 0, 0)

        input_style = f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1.5px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.SM}px {Spacing.XS}px;
                font-size: {Typography.H5}px;
                min-height: 42px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {Colors.PRIMARY};
            }}
        """

        label_style = f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.BODY}px; font-weight: {Typography.MEDIUM};"

        self.nombre = QLineEdit()
        self.nombre.setStyleSheet(input_style)
        self.documento = QLineEdit()
        self.documento.setStyleSheet(input_style)
        self.telefono = QLineEdit()
        self.telefono.setStyleSheet(input_style)
        self.email = QLineEdit()
        self.email.setStyleSheet(input_style)
        self.direccion = QLineEdit()
        self.direccion.setStyleSheet(input_style)

        self._add_form_row(form, "Nombre *:", self.nombre, label_style)
        self._add_form_row(form, "Documento:", self.documento, label_style)
        self._add_form_row(form, "Telefono:", self.telefono, label_style)
        self._add_form_row(form, "Email:", self.email, label_style)
        self._add_form_row(form, "Direccion:", self.direccion, label_style)

        card_layout.addLayout(form)

        if cliente_id:
            from tucajero.services.cliente_service import ClienteService

            cliente = ClienteService(session).get_by_id(cliente_id)
            if cliente:
                self.nombre.setText(cliente.nombre)
                self.documento.setText(cliente.documento or "")
                self.telefono.setText(cliente.telefono or "")
                self.email.setText(cliente.email or "")
                self.direccion.setText(cliente.direccion or "")

        # Botones
        btns = QHBoxLayout()
        btns.setSpacing(Spacing.SM)
        btns.addStretch()
        btn_guardar = ButtonPremium("Guardar", style="primary")
        btn_guardar.setFixedHeight(44)
        btn_guardar.clicked.connect(self.guardar)
        btns.addWidget(btn_guardar)
        btn_cancel = ButtonPremium("Cancelar", style="secondary")
        btn_cancel.setFixedHeight(44)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        card_layout.addLayout(btns)

        main_layout.addWidget(card)

    def _add_form_row(self, form_layout, label_text, widget, label_style):
        label = QLabel(label_text)
        label.setStyleSheet(label_style)
        form_layout.addRow(label, widget)

    def guardar(self):
        nombre = self.nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es requerido")
            return
        from tucajero.services.cliente_service import ClienteService

        service = ClienteService(self.session)
        try:
            if self.cliente_id:
                service.update(
                    self.cliente_id,
                    nombre=nombre,
                    documento=self.documento.text().strip(),
                    telefono=self.telefono.text().strip(),
                    email=self.email.text().strip(),
                    direccion=self.direccion.text().strip(),
                )
            else:
                service.create(
                    nombre,
                    self.documento.text().strip(),
                    self.telefono.text().strip(),
                    self.email.text().strip(),
                    self.direccion.text().strip(),
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class AbonoDialog(QDialog):
    def __init__(self, session, cliente, parent=None):
        super().__init__(parent)
        self.session = session
        self.cliente = cliente
        self.setWindowTitle(f"Registrar Abono \u2014 {cliente.nombre}")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {Colors.BG_APP}; }}
            QLabel {{ color: {Colors.TEXT_PRIMARY}; }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

        # Card contenedor
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.MD}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
                padding: {Spacing.XXL}px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(Spacing.XL)
        card.setLayout(card_layout)

        # Titulo
        titulo = QLabel("Registrar Abono")
        titulo.setStyleSheet(f"font-size: {Typography.H4}px; font-weight: {Typography.EXTRABOLD}; color: {Colors.TEXT_PRIMARY};")
        titulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(titulo)

        # Info del cliente
        info = QFrame()
        info.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_ELEVATED};
                border-radius: {BorderRadius.SM}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
                padding: {Spacing.MD}px;
            }}
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(Spacing.XS)
        info.setLayout(info_layout)

        lbl_cliente = QLabel(f"<b>Cliente:</b> {cliente.nombre}")
        lbl_cliente.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.H5}px;")
        info_layout.addWidget(lbl_cliente)

        lbl_deuda = QLabel(f"<b>Deuda actual:</b> {fmt_moneda(cliente.saldo_credito)}")
        lbl_deuda.setStyleSheet(f"color: {Colors.DANGER}; font-size: {Typography.H5}px; font-weight: {Typography.SEMIBOLD};")
        info_layout.addWidget(lbl_deuda)

        card_layout.addWidget(info)

        # Formulario monto
        form = QFormLayout()
        form.setSpacing(Spacing.MD)

        self.monto_input = QDoubleSpinBox()
        self.monto_input.setRange(0.01, cliente.saldo_credito)
        self.monto_input.setDecimals(2)
        self.monto_input.setValue(cliente.saldo_credito)
        self.monto_input.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1.5px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                padding: {Spacing.SM}px {Spacing.XS}px;
                font-size: {Typography.H4}px;
                font-weight: {Typography.SEMIBOLD};
                min-height: 44px;
            }}
            QDoubleSpinBox:focus {{
                border: 1.5px solid {Colors.PRIMARY};
            }}
        """)
        self.monto_input.valueChanged.connect(self.actualizar_preview)

        form_label = QLabel("Monto a abonar:")
        form_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Typography.BODY}px; font-weight: {Typography.MEDIUM};")
        form.addRow(form_label, self.monto_input)
        card_layout.addLayout(form)

        # Preview
        self.lbl_preview = QLabel("")
        self.lbl_preview.setStyleSheet(f"font-size: {Typography.H5}px; color: {Colors.SUCCESS}; padding: {Spacing.MD}px; background-color: {Colors.SUCCESS_LIGHT}; border-radius: {BorderRadius.SM}px;")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.lbl_preview)
        self.actualizar_preview()

        # Botones
        btns = QHBoxLayout()
        btns.setSpacing(Spacing.SM)
        btns.addStretch()
        btn_ok = ButtonPremium("Registrar Abono", style="success")
        btn_ok.setFixedHeight(44)
        btn_ok.clicked.connect(self.confirmar)
        btns.addWidget(btn_ok)
        btn_cancel = ButtonPremium("Cancelar", style="secondary")
        btn_cancel.setFixedHeight(44)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        card_layout.addLayout(btns)

        main_layout.addWidget(card)

    def actualizar_preview(self):
        monto = self.monto_input.value()
        nuevo_saldo = max(0, self.cliente.saldo_credito - monto)
        self.lbl_preview.setText(f"Saldo despu\u00e9s del abono: {fmt_moneda(nuevo_saldo)}")

    def confirmar(self):
        from tucajero.services.cliente_service import ClienteService

        try:
            ClienteService(self.session).abonar(
                self.cliente.id, self.monto_input.value()
            )
            QMessageBox.information(
                self,
                "Abono registrado",
                f"Abono de {fmt_moneda(self.monto_input.value())} "
                f"registrado para {self.cliente.nombre}",
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class HistorialClienteDialog(QDialog):
    def __init__(self, cliente, ventas, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Historial \u2014 {cliente.nombre}")
        self.setMinimumSize(640, 480)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {Colors.BG_APP}; }}
            QLabel {{ color: {Colors.TEXT_PRIMARY}; }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

        # Centrar contenido
        content_widget = QWidget()
        content_widget.setMaximumWidth(600)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(Spacing.XL)
        content_widget.setLayout(content_layout)

        # Info del cliente
        info = QFrame()
        info.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border-radius: {BorderRadius.MD}px;
                border: 1px solid {Colors.BORDER_DEFAULT};
                padding: {Spacing.MD}px;
            }}
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(Spacing.XS)
        info.setLayout(info_layout)

        lbl_nombre = QLabel(f"<b>{cliente.nombre}</b>")
        lbl_nombre.setStyleSheet(f"font-size: {Typography.H5}px; color: {Colors.TEXT_PRIMARY};")
        info_layout.addWidget(lbl_nombre)

        lbl_detalle = QLabel(
            f"Doc: {cliente.documento or '\u2014'}  |  "
            f"Tel: {cliente.telefono or '\u2014'}  |  "
            f"Saldo: {fmt_moneda(cliente.saldo_credito)}"
        )
        lbl_detalle.setStyleSheet(f"font-size: {Typography.BODY}px; color: {Colors.TEXT_SECONDARY};")
        info_layout.addWidget(lbl_detalle)

        content_layout.addWidget(info)

        # Tabla
        tabla = QTableWidget(len(ventas), 4)
        tabla.setHorizontalHeaderLabels(["ID", "Fecha", "Total", "Metodo"])
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                gridline-color: {Colors.BORDER_DEFAULT};
                font-size: {Typography.BODY}px;
            }}
            QTableWidget::item {{
                padding: {Spacing.SM}px {Spacing.MD}px;
            }}
            QHeaderView::section {{
                background-color: {Colors.BG_ELEVATED};
                color: {Colors.TEXT_SECONDARY};
                padding: {Spacing.SM}px {Spacing.MD}px;
                border: none;
                border-bottom: 2px solid {Colors.BORDER_DEFAULT};
                font-weight: {Typography.SEMIBOLD};
                font-size: {Typography.CAPTION}px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)

        total = 0
        for i, v in enumerate(ventas):
            tabla.setItem(i, 0, QTableWidgetItem(str(v.id)))
            tabla.setItem(i, 1, QTableWidgetItem(v.fecha.strftime("%d/%m/%Y %I:%M %p")))
            tabla.setItem(i, 2, QTableWidgetItem(fmt_moneda(v.total)))
            metodo = v.metodo_pago or "Efectivo"
            if v.es_credito:
                metodo = "Fiado"
            tabla.setItem(i, 3, QTableWidgetItem(metodo))
            total += v.total
        content_layout.addWidget(tabla)

        # Resumen
        resumen = QLabel(
            f"Total compras: {len(ventas)}  |  Valor total: {fmt_moneda(total)}"
        )
        resumen.setStyleSheet(f"font-size: {Typography.H5}px; padding: {Spacing.MD}px; color: {Colors.TEXT_PRIMARY}; font-weight: {Typography.SEMIBOLD};")
        resumen.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(resumen)

        # Boton cerrar
        btn_cerrar = ButtonPremium("Cerrar", style="secondary")
        btn_cerrar.setFixedHeight(44)
        btn_cerrar.clicked.connect(self.accept)
        content_layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)

        main_layout.addWidget(content_widget)
