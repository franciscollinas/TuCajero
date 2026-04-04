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
from tucajero.utils.theme import btn_primary, btn_success, btn_warning, btn_danger, btn_secondary


class ClientesView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_clientes()

    def init_ui(self):
        from tucajero.utils.theme import get_colors
        c = get_colors()
        self.setStyleSheet(f"background-color: {c['bg_app']};")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

        # Centrar contenido con max-width
        content_widget = QWidget()
        content_widget.setMaximumWidth(600)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(24)
        content_widget.setLayout(content_layout)

        # Titulo
        titulo = QLabel("Clientes")
        titulo.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {c['text_primary']}; padding: 0px 4px;")
        titulo.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(titulo)

        # Busqueda
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por nombre, documento o telefono...")
        self.input_buscar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_input']};
                color: {c['text_primary']};
                border: 1.5px solid {c['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                min-height: 42px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {c['primary']};
            }}
        """)
        self.input_buscar.textChanged.connect(self.buscar_cliente)
        content_layout.addWidget(self.input_buscar)

        # Botones de accion
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_nuevo = QPushButton("+ Nuevo Cliente")
        btn_nuevo.setStyleSheet(btn_primary())
        btn_nuevo.clicked.connect(self.nuevo_cliente)
        btn_layout.addWidget(btn_nuevo)

        btn_editar = QPushButton("Editar")
        btn_editar.setStyleSheet(btn_primary())
        btn_editar.clicked.connect(self.editar_cliente)
        btn_layout.addWidget(btn_editar)

        btn_abonar = QPushButton("Abonar")
        btn_abonar.setStyleSheet(btn_success())
        btn_abonar.clicked.connect(self.abonar_cliente)
        btn_layout.addWidget(btn_abonar)

        btn_historial = QPushButton("Ver compras")
        btn_historial.setStyleSheet(btn_secondary())
        btn_historial.clicked.connect(self.ver_historial)
        btn_layout.addWidget(btn_historial)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(btn_danger())
        btn_eliminar.clicked.connect(self.eliminar_cliente)
        btn_layout.addWidget(btn_eliminar)

        content_layout.addLayout(btn_layout)

        # Tabla dentro de card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                padding: 0px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(16, 16, 16, 16)
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
                background-color: #FFFFFF;
                color: {c['text_primary']};
                border: none;
                gridline-color: #E2E8F0;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
            }}
            QHeaderView::section {{
                background-color: #F8FAFC;
                color: {c['text_secondary']};
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """)
        self.tabla.doubleClicked.connect(self.ver_historial)
        card_layout.addWidget(self.tabla)

        content_layout.addWidget(card)

        # Deudas
        self.lbl_deudas = QLabel("")
        self.lbl_deudas.setStyleSheet(f"color: {c['danger']}; font-size: 13px; padding: 8px 4px;")
        self.lbl_deudas.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.lbl_deudas)

        main_layout.addWidget(content_widget)

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
        from tucajero.utils.theme import get_colors
        c = get_colors()
        self.session = session
        self.cliente_id = cliente_id
        self.setWindowTitle("Nuevo Cliente" if not cliente_id else "Editar Cliente")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {c['bg_app']}; }}
            QLabel {{ color: {c['text_primary']}; font-size: 13px; }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

        # Card contenedor
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                padding: 24px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(16)
        card.setLayout(card_layout)

        # Titulo del formulario
        titulo = QLabel("Nuevo Cliente" if not cliente_id else "Editar Cliente")
        titulo.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {c['text_primary']};")
        titulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(titulo)

        # Formulario
        form = QFormLayout()
        form.setSpacing(16)
        form.setContentsMargins(0, 8, 0, 0)

        input_style = f"""
            QLineEdit {{
                background-color: {c['bg_input']};
                color: {c['text_primary']};
                border: 1.5px solid {c['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                min-height: 42px;
            }}
            QLineEdit:focus {{
                border: 1.5px solid {c['primary']};
            }}
        """

        label_style = f"color: {c['text_secondary']}; font-size: 13px; font-weight: 500;"

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
        btns.setSpacing(12)
        btns.addStretch()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet(btn_primary())
        btn_guardar.setFixedHeight(44)
        btn_guardar.clicked.connect(self.guardar)
        btns.addWidget(btn_guardar)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(btn_secondary())
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
        from tucajero.utils.theme import get_colors
        c = get_colors()
        self.session = session
        self.cliente = cliente
        self.setWindowTitle(f"Registrar Abono \u2014 {cliente.nombre}")
        self.setMinimumWidth(480)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {c['bg_app']}; }}
            QLabel {{ color: {c['text_primary']}; }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

        # Card contenedor
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                padding: 24px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(24)
        card.setLayout(card_layout)

        # Titulo
        titulo = QLabel("Registrar Abono")
        titulo.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {c['text_primary']};")
        titulo.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(titulo)

        # Info del cliente
        info = QFrame()
        info.setStyleSheet(f"""
            QFrame {{
                background-color: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #E2E8F0;
                padding: 16px;
            }}
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        info.setLayout(info_layout)

        lbl_cliente = QLabel(f"<b>Cliente:</b> {cliente.nombre}")
        lbl_cliente.setStyleSheet(f"color: {c['text_primary']}; font-size: 14px;")
        info_layout.addWidget(lbl_cliente)

        lbl_deuda = QLabel(f"<b>Deuda actual:</b> {fmt_moneda(cliente.saldo_credito)}")
        lbl_deuda.setStyleSheet(f"color: {c['danger']}; font-size: 14px; font-weight: 600;")
        info_layout.addWidget(lbl_deuda)

        card_layout.addWidget(info)

        # Formulario monto
        form = QFormLayout()
        form.setSpacing(16)

        self.monto_input = QDoubleSpinBox()
        self.monto_input.setRange(0.01, cliente.saldo_credito)
        self.monto_input.setDecimals(2)
        self.monto_input.setValue(cliente.saldo_credito)
        self.monto_input.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {c['bg_input']};
                color: {c['text_primary']};
                border: 1.5px solid {c['border']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 18px;
                font-weight: 600;
                min-height: 44px;
            }}
            QDoubleSpinBox:focus {{
                border: 1.5px solid {c['primary']};
            }}
        """)
        self.monto_input.valueChanged.connect(self.actualizar_preview)

        form_label = QLabel("Monto a abonar:")
        form_label.setStyleSheet(f"color: {c['text_secondary']}; font-size: 13px; font-weight: 500;")
        form.addRow(form_label, self.monto_input)
        card_layout.addLayout(form)

        # Preview
        self.lbl_preview = QLabel("")
        self.lbl_preview.setStyleSheet(f"font-size: 14px; color: {c['success']}; padding: 12px; background-color: #F0FDF4; border-radius: 8px;")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.lbl_preview)
        self.actualizar_preview()

        # Botones
        btns = QHBoxLayout()
        btns.setSpacing(12)
        btns.addStretch()
        btn_ok = QPushButton("Registrar Abono")
        btn_ok.setStyleSheet(btn_success())
        btn_ok.setFixedHeight(44)
        btn_ok.clicked.connect(self.confirmar)
        btns.addWidget(btn_ok)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(btn_secondary())
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
        from tucajero.utils.theme import get_colors
        c = get_colors()
        self.setWindowTitle(f"Historial \u2014 {cliente.nombre}")
        self.setMinimumSize(640, 480)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {c['bg_app']}; }}
            QLabel {{ color: {c['text_primary']}; }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.setLayout(main_layout)

        # Centrar contenido
        content_widget = QWidget()
        content_widget.setMaximumWidth(600)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(24)
        content_widget.setLayout(content_layout)

        # Info del cliente
        info = QFrame()
        info.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                padding: 16px;
            }}
        """)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        info.setLayout(info_layout)

        lbl_nombre = QLabel(f"<b>{cliente.nombre}</b>")
        lbl_nombre.setStyleSheet(f"font-size: 16px; color: {c['text_primary']};")
        info_layout.addWidget(lbl_nombre)

        lbl_detalle = QLabel(
            f"Doc: {cliente.documento or '\u2014'}  |  "
            f"Tel: {cliente.telefono or '\u2014'}  |  "
            f"Saldo: {fmt_moneda(cliente.saldo_credito)}"
        )
        lbl_detalle.setStyleSheet(f"font-size: 13px; color: {c['text_secondary']};")
        info_layout.addWidget(lbl_detalle)

        content_layout.addWidget(info)

        # Tabla
        tabla = QTableWidget(len(ventas), 4)
        tabla.setHorizontalHeaderLabels(["ID", "Fecha", "Total", "Metodo"])
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setStyleSheet(f"""
            QTableWidget {{
                background-color: #FFFFFF;
                color: {c['text_primary']};
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                gridline-color: #E2E8F0;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
            }}
            QHeaderView::section {{
                background-color: #F8FAFC;
                color: {c['text_secondary']};
                padding: 10px 12px;
                border: none;
                border-bottom: 2px solid #E2E8F0;
                font-weight: 600;
                font-size: 12px;
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
        resumen.setStyleSheet(f"font-size: 14px; padding: 12px; color: {c['text_primary']}; font-weight: 600;")
        resumen.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(resumen)

        # Boton cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet(btn_secondary())
        btn_cerrar.setFixedHeight(44)
        btn_cerrar.clicked.connect(self.accept)
        content_layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)

        main_layout.addWidget(content_widget)
