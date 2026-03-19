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
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from utils.formato import fmt_moneda


class ClientesView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_clientes()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Clientes")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        busq_layout = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText(
            "Buscar por nombre, documento o teléfono..."
        )
        self.input_buscar.setStyleSheet("padding: 10px; font-size: 14px;")
        self.input_buscar.textChanged.connect(self.buscar_cliente)
        busq_layout.addWidget(self.input_buscar)
        layout.addLayout(busq_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_nuevo = QPushButton("+ Nuevo Cliente")
        btn_nuevo.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 10px;"
        )
        btn_nuevo.clicked.connect(self.nuevo_cliente)
        btn_layout.addWidget(btn_nuevo)

        btn_editar = QPushButton("Editar")
        btn_editar.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px;"
        )
        btn_editar.clicked.connect(self.editar_cliente)
        btn_layout.addWidget(btn_editar)

        btn_abonar = QPushButton("💰 Abonar")
        btn_abonar.setStyleSheet(
            "background-color: #e67e22; color: white; padding: 10px; font-weight: bold;"
        )
        btn_abonar.clicked.connect(self.abonar_cliente)
        btn_layout.addWidget(btn_abonar)

        btn_historial = QPushButton("📋 Ver compras")
        btn_historial.setStyleSheet(
            "background-color: #8e44ad; color: white; padding: 10px;"
        )
        btn_historial.clicked.connect(self.ver_historial)
        btn_layout.addWidget(btn_historial)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px;"
        )
        btn_eliminar.clicked.connect(self.eliminar_cliente)
        btn_layout.addWidget(btn_eliminar)

        layout.addLayout(btn_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Nombre", "Documento", "Teléfono", "Email", "Saldo crédito"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setStyleSheet("font-size: 14px;")
        self.tabla.doubleClicked.connect(self.ver_historial)
        layout.addWidget(self.tabla)

        self.lbl_deudas = QLabel("")
        self.lbl_deudas.setStyleSheet("color: #e74c3c; font-size: 13px; padding: 4px;")
        layout.addWidget(self.lbl_deudas)

    def cargar_clientes(self, clientes=None):
        from services.cliente_service import ClienteService

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
                f"⚠ {len(con_deuda)} cliente(s) con deuda pendiente "
                f"— Total: {fmt_moneda(total_deuda)}"
            )
        else:
            self.lbl_deudas.setText("")

    def buscar_cliente(self, texto):
        from services.cliente_service import ClienteService

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
        from services.cliente_service import ClienteService

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
        from services.cliente_service import ClienteService

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
        resp = QMessageBox.question(self, "Confirmar", "¿Eliminar este cliente?")
        if resp == QMessageBox.StandardButton.Yes:
            from services.cliente_service import ClienteService

            ClienteService(self.session).delete(cliente_id)
            self.cargar_clientes()


class ClienteDialog(QDialog):
    def __init__(self, session, parent=None, cliente_id=None):
        super().__init__(parent)
        self.session = session
        self.cliente_id = cliente_id
        self.setWindowTitle("Nuevo Cliente" if not cliente_id else "Editar Cliente")
        self.setMinimumWidth(420)
        layout = QFormLayout()
        self.setLayout(layout)

        self.nombre = QLineEdit()
        self.documento = QLineEdit()
        self.telefono = QLineEdit()
        self.email = QLineEdit()
        self.direccion = QLineEdit()

        self.nombre.setStyleSheet("padding: 8px; font-size: 14px;")
        self.documento.setStyleSheet("padding: 8px; font-size: 14px;")
        self.telefono.setStyleSheet("padding: 8px; font-size: 14px;")
        self.email.setStyleSheet("padding: 8px; font-size: 14px;")
        self.direccion.setStyleSheet("padding: 8px; font-size: 14px;")

        layout.addRow("Nombre *:", self.nombre)
        layout.addRow("Documento:", self.documento)
        layout.addRow("Teléfono:", self.telefono)
        layout.addRow("Email:", self.email)
        layout.addRow("Dirección:", self.direccion)

        if cliente_id:
            from services.cliente_service import ClienteService

            c = ClienteService(session).get_by_id(cliente_id)
            if c:
                self.nombre.setText(c.nombre)
                self.documento.setText(c.documento or "")
                self.telefono.setText(c.telefono or "")
                self.email.setText(c.email or "")
                self.direccion.setText(c.direccion or "")

        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet("background:#27ae60;color:white;padding:10px;")
        btn_guardar.clicked.connect(self.guardar)
        btns.addWidget(btn_guardar)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        layout.addRow("", btns)

    def guardar(self):
        nombre = self.nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es requerido")
            return
        from services.cliente_service import ClienteService

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
        self.setWindowTitle(f"Registrar Abono — {cliente.nombre}")
        self.setMinimumWidth(380)
        layout = QVBoxLayout()
        self.setLayout(layout)

        info = QWidget()
        info.setStyleSheet("background:#ffeaa7;padding:12px;border-radius:6px;")
        info_l = QVBoxLayout()
        info.setLayout(info_l)
        info_l.addWidget(QLabel(f"<b>Cliente:</b> {cliente.nombre}"))
        info_l.addWidget(
            QLabel(f"<b>Deuda actual:</b> {fmt_moneda(cliente.saldo_credito)}")
        )
        layout.addWidget(info)

        form = QFormLayout()
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setRange(0.01, cliente.saldo_credito)
        self.monto_input.setDecimals(2)
        self.monto_input.setValue(cliente.saldo_credito)
        self.monto_input.setStyleSheet("font-size: 16px; padding: 8px;")
        self.monto_input.valueChanged.connect(self.actualizar_preview)
        form.addRow("Monto a abonar:", self.monto_input)
        layout.addLayout(form)

        self.lbl_preview = QLabel("")
        self.lbl_preview.setStyleSheet("font-size: 13px; color: #27ae60; padding: 4px;")
        layout.addWidget(self.lbl_preview)
        self.actualizar_preview()

        btns = QHBoxLayout()
        btn_ok = QPushButton("✓ REGISTRAR ABONO")
        btn_ok.setStyleSheet(
            "background:#27ae60;color:white;padding:12px;font-weight:bold;"
        )
        btn_ok.clicked.connect(self.confirmar)
        btns.addWidget(btn_ok)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def actualizar_preview(self):
        monto = self.monto_input.value()
        nuevo_saldo = max(0, self.cliente.saldo_credito - monto)
        self.lbl_preview.setText(f"Saldo después del abono: {fmt_moneda(nuevo_saldo)}")

    def confirmar(self):
        from services.cliente_service import ClienteService

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
        self.setWindowTitle(f"Historial — {cliente.nombre}")
        self.setMinimumSize(600, 450)
        layout = QVBoxLayout()
        self.setLayout(layout)

        info = QLabel(
            f"<b>{cliente.nombre}</b>  |  "
            f"Doc: {cliente.documento or '—'}  |  "
            f"Tel: {cliente.telefono or '—'}  |  "
            f"Saldo: {fmt_moneda(cliente.saldo_credito)}"
        )
        info.setStyleSheet(
            "font-size:13px;padding:8px;background:#ecf0f1;border-radius:4px;"
        )
        layout.addWidget(info)

        tabla = QTableWidget(len(ventas), 4)
        tabla.setHorizontalHeaderLabels(["ID", "Fecha", "Total", "Método"])
        tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tabla.setStyleSheet("font-size:13px;")

        total = 0
        for i, v in enumerate(ventas):
            tabla.setItem(i, 0, QTableWidgetItem(str(v.id)))
            tabla.setItem(i, 1, QTableWidgetItem(v.fecha.strftime("%d/%m/%Y %H:%M")))
            tabla.setItem(i, 2, QTableWidgetItem(fmt_moneda(v.total)))
            metodo = v.metodo_pago or "Efectivo"
            if v.es_credito:
                metodo = "🔴 Fiado"
            tabla.setItem(i, 3, QTableWidgetItem(metodo))
            total += v.total
        layout.addWidget(tabla)

        resumen = QLabel(
            f"Total compras: {len(ventas)}  |  Valor total: {fmt_moneda(total)}"
        )
        resumen.setStyleSheet("font-size:13px;padding:4px;font-weight:bold;")
        layout.addWidget(resumen)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
