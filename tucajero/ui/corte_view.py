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
    QDialog,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt
from datetime import datetime


class CorteView(QWidget):
    """Vista de corte de caja"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_estadisticas()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Corte de Caja")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.info_widget = QWidget()
        self.info_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout()
        self.info_widget.setLayout(info_layout)

        self.lbl_fecha = QLabel(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        self.lbl_fecha.setStyleSheet("font-size: 18px;")
        info_layout.addWidget(self.lbl_fecha)

        self.lbl_estado = QLabel("Caja: ABIERTA")
        self.lbl_estado.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #27ae60;"
        )
        info_layout.addWidget(self.lbl_estado)

        self.lbl_total = QLabel("Total vendido: $0.00")
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #27ae60;"
        )
        info_layout.addWidget(self.lbl_total)

        self.lbl_num_ventas = QLabel("Número de ventas: 0")
        self.lbl_num_ventas.setStyleSheet("font-size: 18px;")
        info_layout.addWidget(self.lbl_num_ventas)

        layout.addWidget(self.info_widget)

        botones_layout = QHBoxLayout()

        self.btn_abrir = QPushButton("ABRIR CAJA")
        self.btn_abrir.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_abrir.clicked.connect(self.abrir_caja)
        botones_layout.addWidget(self.btn_abrir)

        self.btn_cerrar = QPushButton("CERRAR CAJA")
        self.btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_cerrar.clicked.connect(self.cerrar_caja)
        botones_layout.addWidget(self.btn_cerrar)

        layout.addLayout(botones_layout)

        self.btn_gasto = QPushButton("Registrar Gasto de Caja")
        self.btn_gasto.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_gasto.clicked.connect(self.registrar_gasto)
        layout.addWidget(self.btn_gasto)

        self.btn_anular = QPushButton("Anular Venta")
        self.btn_anular.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_anular.clicked.connect(self.anular_venta)
        layout.addWidget(self.btn_anular)

        self.btn_facturas = QPushButton("Ver Facturas del Día")
        self.btn_facturas.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.btn_facturas.clicked.connect(self.ver_facturas_dia)
        layout.addWidget(self.btn_facturas)

        self.lbl_ganancia = QLabel("Ganancia neta: $0.00")
        self.lbl_ganancia.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #8e44ad; padding: 8px;"
        )
        layout.addWidget(self.lbl_ganancia)

        historial_label = QLabel("Ventas del día")
        historial_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 20px;"
        )
        layout.addWidget(historial_label)

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(3)
        self.tabla_ventas.setHorizontalHeaderLabels(["ID", "Hora", "Total"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_ventas.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.tabla_ventas)

        gastos_label = QLabel("Gastos del día")
        gastos_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-top: 15px;"
        )
        layout.addWidget(gastos_label)

        self.tabla_gastos = QTableWidget()
        self.tabla_gastos.setColumnCount(3)
        self.tabla_gastos.setHorizontalHeaderLabels(["Hora", "Concepto", "Monto"])
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_gastos.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.tabla_gastos)

    def cargar_estadisticas(self):
        """Carga las estadísticas del día"""
        from services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        caja_abierta = service.esta_caja_abierta()

        if caja_abierta:
            self.lbl_estado.setText("Caja: ABIERTA")
            self.lbl_estado.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #27ae60;"
            )
            self.btn_abrir.setEnabled(False)
            self.btn_cerrar.setEnabled(True)
            self.btn_gasto.setEnabled(True)
            self.btn_anular.setEnabled(True)
        else:
            self.lbl_estado.setText("Caja: CERRADA")
            self.lbl_estado.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #e74c3c;"
            )
            self.btn_abrir.setEnabled(True)
            self.btn_cerrar.setEnabled(False)
            self.btn_gasto.setEnabled(False)
            self.btn_anular.setEnabled(False)

        self.lbl_total.setText(f"Total vendido: ${stats['total']:.2f}")
        self.lbl_num_ventas.setText(f"Número de ventas: {stats['num_ventas']}")
        self.lbl_ganancia.setText(
            f"Ganancia neta: ${stats['ganancia_neta']:.2f} "
            f"(Gastos: ${stats['total_gastos']:.2f})"
        )

        ventas = stats["ventas"]
        self.tabla_ventas.setRowCount(len(ventas))

        for i, venta in enumerate(ventas):
            self.tabla_ventas.setItem(i, 0, QTableWidgetItem(str(venta.id)))
            self.tabla_ventas.setItem(
                i, 1, QTableWidgetItem(venta.fecha.strftime("%H:%M:%S"))
            )
            self.tabla_ventas.setItem(i, 2, QTableWidgetItem(f"${venta.total:.2f}"))

        gastos = stats["gastos"]
        self.tabla_gastos.setRowCount(len(gastos))

        for i, gasto in enumerate(gastos):
            self.tabla_gastos.setItem(
                i, 0, QTableWidgetItem(gasto.fecha.strftime("%H:%M"))
            )
            self.tabla_gastos.setItem(i, 1, QTableWidgetItem(gasto.concepto))
            self.tabla_gastos.setItem(i, 2, QTableWidgetItem(f"${gasto.monto:.2f}"))

    def abrir_caja(self):
        """Abre la caja"""
        from services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        service.abrir_caja()

        QMessageBox.information(
            self,
            "Caja Abierta",
            "La caja ha sido abierta correctamente.\n\nYa puedes comenzar a registrar ventas.",
        )

        self.cargar_estadisticas()

    def registrar_gasto(self):
        """Abre diálogo para registrar gasto"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Gasto de Caja")
        dialog.setMinimumWidth(380)
        layout = QFormLayout()
        dialog.setLayout(layout)

        info = QLabel("El monto será descontado de la ganancia del día.")
        info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addRow("", info)

        concepto_input = QLineEdit()
        concepto_input.setPlaceholderText("Ej: Compra de bolsas, Pasaje, Luz...")
        concepto_input.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addRow("Concepto:", concepto_input)

        monto_input = QDoubleSpinBox()
        monto_input.setRange(0.01, 999999)
        monto_input.setDecimals(2)
        monto_input.setStyleSheet("padding: 8px; font-size: 16px;")
        layout.addRow("Monto:", monto_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("REGISTRAR")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(
            "background-color: #e67e22; color: white; padding: 8px 16px;"
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow("", buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            concepto = concepto_input.text().strip()
            monto = monto_input.value()
            if not concepto:
                QMessageBox.warning(self, "Error", "El concepto es obligatorio")
                return
            if monto <= 0:
                QMessageBox.warning(self, "Error", "El monto debe ser mayor a cero")
                return
            try:
                from services.corte_service import CorteCajaService

                service = CorteCajaService(self.session)
                service.registrar_gasto(concepto, monto)
                self.cargar_estadisticas()
                QMessageBox.information(
                    self,
                    "Gasto Registrado",
                    f"Gasto registrado:\n{concepto}: ${monto:.2f}",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def cerrar_caja(self):
        """Cierra la caja"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de cerrar la caja?\nSe registrará el corte del día.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            from services.corte_service import CorteCajaService

            service = CorteCajaService(self.session)
            stats = service.get_estadisticas_hoy()

            corte = service.cerrar_caja()

            if corte:
                QMessageBox.information(
                    self,
                    "Corte de Caja",
                    f"Corte de caja cerrado!\n\n"
                    f"Total vendido: ${corte.total_ventas:.2f}\n"
                    f"Gastos: ${stats['total_gastos']:.2f}\n"
                    f"Ganancia neta: ${stats['ganancia_neta']:.2f}\n\n"
                    f"Ventas: {stats['num_ventas']}",
                )
            else:
                QMessageBox.warning(self, "Error", "No hay caja abierta")

            self.cargar_estadisticas()

    def anular_venta(self):
        """Anula una venta del día"""
        from services.corte_service import CorteCajaService
        from services.producto_service import VentaService
        from ui.ventas_view import VentasView

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        ventas = stats["ventas"]

        if not ventas:
            QMessageBox.warning(self, "Sin ventas", "No hay ventas registradas hoy")
            return

        from PySide6.QtWidgets import QInputDialog

        venta_ids = [str(v.id) for v in ventas]
        venta_id_str, ok = QInputDialog.getItem(
            self,
            "Anular Venta",
            "Seleccione la venta a anular:",
            venta_ids,
            0,
            False,
        )

        if not ok or not venta_id_str:
            return

        venta_id = int(venta_id_str)

        respuesta = QMessageBox.question(
            self,
            "Confirmar Anulación",
            f"¿Está seguro de anular la venta #{venta_id}?\n"
            "El stock de los productos será restaurado.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            venta_service = VentaService(self.session)
            venta_service.anular_venta(venta_id)
            QMessageBox.information(
                self,
                "Venta Anulada",
                f"Venta #{venta_id} ha sido anulada.\nEl stock ha sido restaurado.",
            )
            self.cargar_estadisticas()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al anular venta: {str(e)}")

    def ver_facturas_dia(self):
        """Abre o genera el PDF de facturas del día"""
        from utils.factura_diaria import get_factura_diaria_path
        import subprocess
        import os

        pdf_path = get_factura_diaria_path()
        if not os.path.exists(pdf_path):
            QMessageBox.information(
                self,
                "Sin facturas",
                "No hay facturas registradas para el día de hoy.",
            )
            return

        try:
            if os.name == "nt":
                os.startfile(pdf_path)
            else:
                subprocess.run(["xdg-open", pdf_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir el archivo: {str(e)}")
