import os
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
    QDateEdit,
    QComboBox,
    QFrame,
)
from PySide6.QtCore import Qt, QDate, QLocale
from datetime import datetime, date


class HistorialView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cierres = []
        self.init_ui()
        self.cargar_historial()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Historial de Cierres")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        filtros_widget = QWidget()
        filtros_widget.setStyleSheet(
            "background-color: #ecf0f1; padding: 10px; border-radius: 8px;"
        )
        filtros_layout = QHBoxLayout()
        filtros_widget.setLayout(filtros_layout)

        locale_es = QLocale(QLocale.Language.Spanish, QLocale.Country.Colombia)

        filtros_layout.addWidget(QLabel("Desde:"))
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setLocale(locale_es)
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setStyleSheet("padding: 6px;")
        filtros_layout.addWidget(self.fecha_desde)

        filtros_layout.addWidget(QLabel("Hasta:"))
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setLocale(locale_es)
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setStyleSheet("padding: 6px;")
        filtros_layout.addWidget(self.fecha_hasta)

        self.combo_mes = QComboBox()
        self.combo_mes.addItem("Filtro rápido por mes...")
        meses_es = [
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]
        for i, nombre_mes in enumerate(meses_es, start=1):
            self.combo_mes.addItem(nombre_mes, i)
        self.combo_mes.currentIndexChanged.connect(self.filtro_rapido_mes)
        filtros_layout.addWidget(self.combo_mes)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px 16px;"
        )
        btn_filtrar.clicked.connect(self.cargar_historial)
        filtros_layout.addWidget(btn_filtrar)

        filtros_layout.addStretch()

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.setStyleSheet(
            "background-color: #27ae60; color: white; "
            "padding: 8px 16px; font-weight: bold;"
        )
        btn_excel.clicked.connect(self.exportar_excel)
        filtros_layout.addWidget(btn_excel)

        layout.addWidget(filtros_widget)

        self.resumen_widget = QWidget()
        self.resumen_widget.setStyleSheet(
            "background-color: #2c3e50; border-radius: 8px; padding: 12px;"
        )
        resumen_layout = QHBoxLayout()
        self.resumen_widget.setLayout(resumen_layout)

        self.lbl_r_ventas = QLabel("Ventas brutas: $0.00")
        self.lbl_r_ventas.setStyleSheet("color: white; font-size: 14px;")
        self.lbl_r_gastos = QLabel("Gastos: $0.00")
        self.lbl_r_gastos.setStyleSheet("color: #e74c3c; font-size: 14px;")
        self.lbl_r_ganancia = QLabel("Ganancia neta: $0.00")
        self.lbl_r_ganancia.setStyleSheet(
            "color: #2ecc71; font-size: 16px; font-weight: bold;"
        )
        self.lbl_r_cierres = QLabel("Cierres: 0")
        self.lbl_r_cierres.setStyleSheet("color: #bdc3c7; font-size: 13px;")

        resumen_layout.addWidget(self.lbl_r_ventas)
        resumen_layout.addWidget(self.lbl_r_gastos)
        resumen_layout.addWidget(self.lbl_r_ganancia)
        resumen_layout.addStretch()
        resumen_layout.addWidget(self.lbl_r_cierres)
        layout.addWidget(self.resumen_widget)

        cierres_label = QLabel("Cierres del período")
        cierres_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-top: 8px;"
        )
        layout.addWidget(cierres_label)

        self.tabla_cierres = QTableWidget()
        self.tabla_cierres.setColumnCount(8)
        self.tabla_cierres.setHorizontalHeaderLabels(
            [
                "ID",
                "Apertura",
                "Cierre",
                "Ventas brutas",
                "Efectivo",
                "Transferencias",
                "Gastos",
                "Ganancia neta",
            ]
        )
        self.tabla_cierres.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_cierres.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_cierres.setStyleSheet("font-size: 13px;")
        self.tabla_cierres.clicked.connect(self.mostrar_detalle_cierre)
        layout.addWidget(self.tabla_cierres)

        ranking_label = QLabel("Ranking de productos")
        ranking_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-top: 8px;"
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
        self.tabla_ranking.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.tabla_ranking)

    def filtro_rapido_mes(self, index):
        if index == 0:
            return
        mes = self.combo_mes.itemData(index)
        anio = QDate.currentDate().year()
        self.fecha_desde.setDate(QDate(anio, mes, 1))
        ultimo_dia = QDate(anio, mes, 1).daysInMonth()
        self.fecha_hasta.setDate(QDate(anio, mes, ultimo_dia))
        self.cargar_historial()

    def cargar_historial(self):
        from services.historial_service import HistorialService

        self.session.expire_all()
        service = HistorialService(self.session)

        desde = self.fecha_desde.date().toPython()
        hasta = self.fecha_hasta.date().toPython()
        desde_dt = datetime.combine(desde, datetime.min.time())
        hasta_dt = datetime.combine(hasta, datetime.max.time())

        self.cierres = service.get_cierres(desde_dt, hasta_dt)
        resumen = service.get_resumen_periodo(desde_dt, hasta_dt)
        ranking = service.get_ranking_productos(desde_dt, hasta_dt)

        self.lbl_r_ventas.setText(f"Ventas brutas: ${resumen['total_ventas']:.2f}")
        self.lbl_r_gastos.setText(f"Gastos: ${resumen['total_gastos']:.2f}")
        self.lbl_r_ganancia.setText(f"Ganancia neta: ${resumen['ganancia_neta']:.2f}")
        self.lbl_r_cierres.setText(
            f"Cierres: {resumen['num_cierres']} | Ventas: {resumen['num_ventas']}"
        )

        self.tabla_cierres.setRowCount(len(self.cierres))
        for i, c in enumerate(self.cierres):
            self.tabla_cierres.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.tabla_cierres.setItem(
                i,
                1,
                QTableWidgetItem(
                    c.fecha_apertura.strftime("%d/%m/%Y %H:%M")
                    if c.fecha_apertura
                    else ""
                ),
            )
            self.tabla_cierres.setItem(
                i,
                2,
                QTableWidgetItem(
                    c.fecha_cierre.strftime("%d/%m/%Y %H:%M")
                    if c.fecha_cierre
                    else "Abierto"
                ),
            )
            self.tabla_cierres.setItem(i, 3, QTableWidgetItem(f"${c.total_ventas:.2f}"))
            self.tabla_cierres.setItem(
                i, 4, QTableWidgetItem(f"${c.total_efectivo or 0:.2f}")
            )
            self.tabla_cierres.setItem(
                i, 5, QTableWidgetItem(f"${c.total_transferencias or 0:.2f}")
            )
            self.tabla_cierres.setItem(
                i, 6, QTableWidgetItem(f"${c.total_gastos or 0:.2f}")
            )
            self.tabla_cierres.setItem(
                i, 7, QTableWidgetItem(f"${c.ganancia_neta or 0:.2f}")
            )

        self.tabla_ranking.setRowCount(len(ranking))
        for i, r in enumerate(ranking):
            self.tabla_ranking.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.tabla_ranking.setItem(i, 1, QTableWidgetItem(r.nombre))
            self.tabla_ranking.setItem(
                i, 2, QTableWidgetItem(str(int(r.total_vendido or 0)))
            )
            self.tabla_ranking.setItem(
                i, 3, QTableWidgetItem(f"${float(r.total_ingresos or 0):.2f}")
            )

    def mostrar_detalle_cierre(self):
        row = self.tabla_cierres.currentRow()
        if row < 0 or row >= len(self.cierres):
            return
        corte = self.cierres[row]
        from services.historial_service import HistorialService

        service = HistorialService(self.session)
        ventas = service.get_ventas_del_cierre(corte.id)
        detalle = f"Cierre #{corte.id} — {corte.fecha_apertura.strftime('%d/%m/%Y')}\n"
        detalle += f"Ventas brutas: ${corte.total_ventas:.2f}\n"
        detalle += f"Gastos: ${corte.total_gastos or 0:.2f}\n"
        detalle += f"Ganancia neta: ${corte.ganancia_neta or 0:.2f}\n"
        detalle += f"Número de ventas: {len(ventas)}\n\n"
        detalle += "Ventas del día:\n"
        for v in ventas[:20]:
            detalle += f"  #{v.id} {v.fecha.strftime('%H:%M')} — ${v.total:.2f}\n"
        if len(ventas) > 20:
            detalle += f"  ... y {len(ventas) - 20} más"
        QMessageBox.information(self, "Detalle del cierre", detalle)

    def exportar_excel(self):
        from services.historial_service import HistorialService
        from utils.excel_exporter import exportar_historial_excel

        service = HistorialService(self.session)

        desde = self.fecha_desde.date().toPython()
        hasta = self.fecha_hasta.date().toPython()
        desde_dt = datetime.combine(desde, datetime.min.time())
        hasta_dt = datetime.combine(hasta, datetime.max.time())

        cierres = service.get_cierres(desde_dt, hasta_dt)
        if not cierres:
            QMessageBox.warning(
                self, "Sin datos", "No hay cierres en el período seleccionado"
            )
            return
        ventas_por_cierre = {c.id: service.get_ventas_del_cierre(c.id) for c in cierres}
        ranking = service.get_ranking_productos(desde_dt, hasta_dt)
        resumen = service.get_resumen_periodo(desde_dt, hasta_dt)

        try:
            ruta = exportar_historial_excel(
                cierres, ventas_por_cierre, ranking, resumen
            )
            QMessageBox.information(
                self, "Excel exportado", f"Archivo guardado en:\n{ruta}"
            )
            os.startfile(os.path.dirname(ruta))
        except ImportError as e:
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error al exportar", str(e))
