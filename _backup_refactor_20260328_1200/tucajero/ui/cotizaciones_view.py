from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from utils.formato import fmt_moneda
from utils.theme import btn_danger, btn_primary, get_colors


class CotizacionesView(QWidget):
    cargar_en_ventas = Signal(list, object, int)

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cotizaciones = []
        self.init_ui()
        self.cargar_cotizaciones()

    def init_ui(self):
        from utils.theme import get_colors

        c = get_colors()

        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Cotizaciones")
        titulo.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {c['accent']};"
        )
        layout.addWidget(titulo)

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Mostrar:"))
        self.filtro_combo = QComboBox()
        self.filtro_combo.addItems(["Todas", "Pendientes", "Facturadas", "Canceladas"])
        self.filtro_combo.currentTextChanged.connect(self.cargar_cotizaciones)
        filtro_layout.addWidget(self.filtro_combo)
        filtro_layout.addStretch()
        layout.addLayout(filtro_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_facturar = QPushButton("⚡ Convertir en venta")
        self.btn_facturar.setStyleSheet(btn_primary())
        self.btn_facturar.clicked.connect(self.convertir_en_venta)
        btn_layout.addWidget(self.btn_facturar)

        self.btn_cancelar = QPushButton("✕ Cancelar cotización")
        self.btn_cancelar.setStyleSheet(btn_danger())
        self.btn_cancelar.clicked.connect(self.cancelar_cotizacion)
        btn_layout.addWidget(self.btn_cancelar)

        layout.addLayout(btn_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Fecha", "Cliente", "Total", "Estado", "Notas"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setStyleSheet("font-size: 14px;")
        self.tabla.doubleClicked.connect(self.convertir_en_venta)
        layout.addWidget(self.tabla)

        info = QLabel(
            "Doble clic o 'Convertir en venta' para facturar una cotización pendiente"
        )
        info.setStyleSheet(
            f"color: {c['text_secondary']}; font-size: 13px; font-style: italic;"
        )
        info.setObjectName("info_label")
        layout.addWidget(info)

    def cargar_cotizaciones(self):
        from services.cotizacion_service import CotizacionService

        service = CotizacionService(self.session)

        filtro_texto = self.filtro_combo.currentText()
        estado_map = {
            "Pendientes": "pendiente",
            "Facturadas": "facturada",
            "Canceladas": "cancelada",
            "Todas": None,
        }
        estado = estado_map.get(filtro_texto)
        self.cotizaciones = service.get_all(estado=estado)

        self.tabla.setRowCount(len(self.cotizaciones))
        from utils.theme import get_colors

        c = get_colors()
        for i, cot in enumerate(self.cotizaciones):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(cot.id)))
            self.tabla.setItem(
                i, 1, QTableWidgetItem(cot.fecha.strftime("%d/%m/%Y %I:%M %p"))
            )

            cliente_nombre = "Sin cliente"
            if cot.cliente_id:
                from services.cliente_service import ClienteService

                cliente = ClienteService(self.session).get_by_id(cot.cliente_id)
                if cliente:
                    cliente_nombre = cliente.nombre
            self.tabla.setItem(i, 2, QTableWidgetItem(cliente_nombre))
            self.tabla.setItem(i, 3, QTableWidgetItem(fmt_moneda(cot.total)))

            estado_item = QTableWidgetItem(cot.estado.capitalize())
            if cot.estado == "pendiente":
                estado_item.setBackground(QColor(c["warning"] + "33"))
                estado_item.setForeground(QColor(c["warning"]))
            elif cot.estado == "facturada":
                estado_item.setBackground(QColor(c["success"] + "33"))
                estado_item.setForeground(QColor(c["success"]))
            elif cot.estado == "cancelada":
                estado_item.setBackground(QColor(c["danger"] + "33"))
                estado_item.setForeground(QColor(c["danger"]))
            self.tabla.setItem(i, 4, estado_item)
            self.tabla.setItem(i, 5, QTableWidgetItem(cot.notas or ""))

    def obtener_seleccionada(self):
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.cotizaciones):
            return self.cotizaciones[row]
        return None

    def convertir_en_venta(self):
        cotizacion = self.obtener_seleccionada()
        if not cotizacion:
            QMessageBox.warning(self, "Error", "Selecciona una cotización")
            return
        if cotizacion.estado != "pendiente":
            QMessageBox.warning(
                self,
                "No disponible",
                f"Solo se pueden facturar cotizaciones pendientes.\n"
                f"Esta está: {cotizacion.estado}",
            )
            return

        resp = QMessageBox.question(
            self,
            "Convertir en venta",
            f"¿Convertir la cotización #{cotizacion.id} en venta?\n"
            f"Se abrirá en la pantalla de Ventas lista para cobrar.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        from services.cotizacion_service import CotizacionService
        from services.producto_service import ProductoService

        service = CotizacionService(self.session)
        prod_service = ProductoService(self.session)

        carrito = []
        for item in cotizacion.items:
            producto = prod_service.get_producto_by_id(item.producto_id)
            if producto:
                carrito.append(
                    {
                        "producto_id": item.producto_id,
                        "codigo": producto.codigo,
                        "nombre": producto.nombre,
                        "precio": item.precio,
                        "cantidad": item.cantidad,
                        "aplica_iva": item.aplica_iva,
                    }
                )

        cliente = None
        if cotizacion.cliente_id:
            from services.cliente_service import ClienteService

            cliente = ClienteService(self.session).get_by_id(cotizacion.cliente_id)

        self.cargar_cotizaciones()

        self.cargar_en_ventas.emit(carrito, cliente, cotizacion.id)

        QMessageBox.information(
            self,
            "Listo",
            f"Cotización #{cotizacion.id} cargada en Ventas.\n"
            "Ve a la sección Ventas para completar el cobro.",
        )

    def cancelar_cotizacion(self):
        cotizacion = self.obtener_seleccionada()
        if not cotizacion:
            QMessageBox.warning(self, "Error", "Selecciona una cotización")
            return

        resp = QMessageBox.question(
            self, "Cancelar cotización", f"¿Cancelar la cotización #{cotizacion.id}?"
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        from services.cotizacion_service import CotizacionService

        try:
            CotizacionService(self.session).cancelar(cotizacion.id)
            self.cargar_cotizaciones()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
