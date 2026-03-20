from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDateEdit,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime, timedelta
import os
from utils.formato import fmt_moneda
from utils.theme import texto_terciario


class HistorialView(QWidget):
    """Vista de historial de cierres y ranking de productos"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_historial()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Historial de Cierres")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        filtros_layout = QHBoxLayout()

        filtros_layout.addWidget(QLabel("Desde:"))
        self.desde_edit = QDateEdit()
        self.desde_edit.setCalendarPopup(True)
        self.desde_edit.setDate(QDate.currentDate().addDays(-30))
        filtros_layout.addWidget(self.desde_edit)

        filtros_layout.addWidget(QLabel("Hasta:"))
        self.hasta_edit = QDateEdit()
        self.hasta_edit.setCalendarPopup(True)
        self.hasta_edit.setDate(QDate.currentDate())
        filtros_layout.addWidget(self.hasta_edit)

        self.filtro_rapido = QComboBox()
        self.filtro_rapido.addItems(
            [
                "Filtro rápido...",
                "Este mes",
                "Mes anterior",
                "Últimos 3 meses",
                "Este año",
            ]
        )
        self.filtro_rapido.currentTextChanged.connect(self.on_filtro_rapido_changed)
        filtros_layout.addWidget(self.filtro_rapido)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px 16px;"
        )
        btn_filtrar.clicked.connect(self.cargar_historial)
        filtros_layout.addWidget(btn_filtrar)

        btn_exportar = QPushButton("Exportar Excel")
        btn_exportar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px 16px;"
        )
        btn_exportar.clicked.connect(self.exportar_excel)
        filtros_layout.addWidget(btn_exportar)

        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)

        self.resumen_widget = QWidget()
        self.resumen_widget.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        resumen_layout = QHBoxLayout()
        self.resumen_widget.setLayout(resumen_layout)

        self.lbl_ventas = QLabel(f"Ventas brutas: {fmt_moneda(0)}")
        self.lbl_ventas.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold;"
        )
        resumen_layout.addWidget(self.lbl_ventas)

        self.lbl_gastos = QLabel(f"Gastos: {fmt_moneda(0)}")
        self.lbl_gastos.setStyleSheet(
            "color: #e74c3c; font-size: 16px; font-weight: bold;"
        )
        resumen_layout.addWidget(self.lbl_gastos)

        self.lbl_ganancia = QLabel(f"Ganancia neta: {fmt_moneda(0)}")
        self.lbl_ganancia.setStyleSheet(
            "color: #2ecc71; font-size: 16px; font-weight: bold;"
        )
        resumen_layout.addWidget(self.lbl_ganancia)

        resumen_layout.addStretch()

        self.lbl_resumen_datos = QLabel("Cierres: 0 | Ventas: 0")
        self.lbl_resumen_datos.setStyleSheet(
            f"color: {texto_terciario()}; font-size: 14px;"
        )
        resumen_layout.addWidget(self.lbl_resumen_datos)

        layout.addWidget(self.resumen_widget)

        cierres_label = QLabel("Cierres del período")
        cierres_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 15px;"
        )
        layout.addWidget(cierres_label)

        self.tabla_cierres = QTableWidget()
        self.tabla_cierres.setColumnCount(5)
        self.tabla_cierres.setHorizontalHeaderLabels(
            ["ID", "Apertura", "Cierre", "Ventas brutas", "Ganancia neta"]
        )
        self.tabla_cierres.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_cierres.setStyleSheet("font-size: 14px;")
        self.tabla_cierres.setMinimumHeight(200)
        layout.addWidget(self.tabla_cierres)

        ranking_label = QLabel("Ranking de productos")
        ranking_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 15px;"
        )
        layout.addWidget(ranking_label)

        self.tabla_ranking = QTableWidget()
        self.tabla_ranking.setColumnCount(4)
        self.tabla_ranking.setHorizontalHeaderLabels(
            ["#", "Producto", "Unidades vendidas", "Ingresos"]
        )
        self.tabla_ranking.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_ranking.setStyleSheet("font-size: 14px;")
        self.tabla_ranking.setMaximumHeight(250)
        layout.addWidget(self.tabla_ranking)

    def on_filtro_rapido_changed(self, text):
        """Aplica filtro rápido"""
        today = QDate.currentDate()
        if text == "Este mes":
            self.desde_edit.setDate(QDate(today.year(), today.month(), 1))
            self.hasta_edit.setDate(today)
        elif text == "Mes anterior":
            first_this_month = QDate(today.year(), today.month(), 1)
            last_prev_month = first_this_month.addDays(-1)
            first_prev_month = QDate(last_prev_month.year(), last_prev_month.month(), 1)
            self.desde_edit.setDate(first_prev_month)
            self.hasta_edit.setDate(last_prev_month)
        elif text == "Últimos 3 meses":
            self.desde_edit.setDate(today.addDays(-90))
            self.hasta_edit.setDate(today)
        elif text == "Este año":
            self.desde_edit.setDate(QDate(today.year(), 1, 1))
            self.hasta_edit.setDate(today)

    def cargar_historial(self):
        """Carga el historial de cierres"""
        desde = self.desde_edit.date().toPython()
        hasta = self.hasta_edit.date().toPython()
        hasta = datetime.combine(hasta, datetime.max.time())

        from models.producto import CorteCaja, VentaItem, Venta, Producto
        from sqlalchemy import and_

        cierres = (
            self.session.query(CorteCaja)
            .filter(
                CorteCaja.fecha_cierre.isnot(None),
                CorteCaja.fecha_apertura
                >= datetime.combine(desde, datetime.min.time()),
                CorteCaja.fecha_apertura <= hasta,
            )
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )

        self.tabla_cierres.setRowCount(len(cierres))

        total_ventas = 0
        total_gastos = 0
        total_cierres = len(cierres)
        total_num_ventas = 0

        for i, corte in enumerate(cierres):
            self.tabla_cierres.setItem(i, 0, QTableWidgetItem(str(corte.id)))
            self.tabla_cierres.setItem(
                i, 1, QTableWidgetItem(corte.fecha_apertura.strftime("%d/%m/%Y %H:%M"))
            )
            self.tabla_cierres.setItem(
                i,
                2,
                QTableWidgetItem(corte.fecha_cierre.strftime("%d/%m/%Y %H:%M"))
                if corte.fecha_cierre
                else QTableWidgetItem("—"),
            )
            self.tabla_cierres.setItem(
                i, 3, QTableWidgetItem(fmt_moneda(corte.total_ventas))
            )
            ganancia = getattr(corte, "ganancia_neta", corte.total_ventas)
            self.tabla_cierres.setItem(i, 4, QTableWidgetItem(fmt_moneda(ganancia)))

            total_ventas += corte.total_ventas
            total_gastos += getattr(corte, "total_gastos", 0)
            total_num_ventas += corte.numero_ventas

        self.lbl_ventas.setText(f"Ventas brutas: {fmt_moneda(total_ventas)}")
        self.lbl_gastos.setText(f"Gastos: {fmt_moneda(total_gastos)}")
        self.lbl_ganancia.setText(
            f"Ganancia neta: {fmt_moneda(total_ventas - total_gastos)}"
        )
        self.lbl_resumen_datos.setText(
            f"Cierres: {total_cierres} | Ventas: {total_num_ventas}"
        )

        self.cargar_ranking(desde, hasta)

    def cargar_ranking(self, desde, hasta):
        """Carga el ranking de productos"""
        desde_dt = datetime.combine(desde, datetime.min.time())
        hasta_dt = datetime.combine(hasta, datetime.max.time())

        from models.producto import VentaItem, Venta, Producto
        from sqlalchemy import func

        ranking = (
            self.session.query(
                Producto.nombre,
                func.sum(VentaItem.cantidad).label("unidades"),
                func.sum(VentaItem.cantidad * VentaItem.precio).label("ingresos"),
            )
            .join(VentaItem, VentaItem.producto_id == Producto.id)
            .join(Venta, Venta.id == VentaItem.venta_id)
            .filter(
                Venta.fecha >= desde_dt,
                Venta.fecha <= hasta_dt,
                Venta.anulada == False,
            )
            .group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(VentaItem.cantidad * VentaItem.precio).desc())
            .limit(50)
            .all()
        )

        self.tabla_ranking.setRowCount(len(ranking))

        for i, item in enumerate(ranking):
            self.tabla_ranking.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.tabla_ranking.setItem(i, 1, QTableWidgetItem(item.nombre))
            self.tabla_ranking.setItem(i, 2, QTableWidgetItem(str(int(item.unidades))))
            self.tabla_ranking.setItem(
                i, 3, QTableWidgetItem(fmt_moneda(item.ingresos))
            )

    def exportar_excel(self):
        """Exporta el historial a Excel"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill

            wb = Workbook()

            desde = self.desde_edit.date().toPython()
            hasta = self.hasta_edit.date().toPython()
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")

            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            filename = os.path.join(downloads, f"TuCajero_Historial_{fecha_str}.xlsx")

            ws_cierres = wb.active
            ws_cierres.title = "Cierres"

            headers = [
                "ID",
                "Apertura",
                "Cierre",
                "Ventas brutas",
                "Gastos",
                "Ganancia neta",
                "N° Ventas",
            ]
            ws_cierres.append(headers)

            for cell in ws_cierres[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    start_color="3498db", end_color="3498db", fill_type="solid"
                )
                cell.alignment = Alignment(horizontal="center")

            for row in range(self.tabla_cierres.rowCount()):
                row_data = []
                for col in range(self.tabla_cierres.columnCount()):
                    item = self.tabla_cierres.item(row, col)
                    row_data.append(item.text() if item else "")
                total = (
                    self.tabla_cierres.item(row, 3).text()
                    if self.tabla_cierres.item(row, 3)
                    else "$0.00"
                )
                row_data.extend(["$0.00", "$0.00", "0"])
                ws_cierres.append(row_data)

            ws_ranking = wb.create_sheet("Ranking")
            ranking_headers = ["#", "Producto", "Unidades vendidas", "Ingresos"]
            ws_ranking.append(ranking_headers)

            for cell in ws_ranking[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    start_color="27ae60", end_color="27ae60", fill_type="solid"
                )

            for row in range(self.tabla_ranking.rowCount()):
                row_data = []
                for col in range(self.tabla_ranking.columnCount()):
                    item = self.tabla_ranking.item(row, col)
                    row_data.append(item.text() if item else "")
                ws_ranking.append(row_data)

            for ws in [ws_cierres, ws_ranking]:
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

            wb.save(filename)
            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"Archivo exportado a:\n{filename}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al exportar",
                f"No se pudo exportar el archivo:\n{str(e)}",
            )
