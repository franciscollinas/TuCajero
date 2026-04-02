from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QHeaderView,
)
from PySide6.QtCore import Qt
from tucajero.utils.formato import fmt_moneda
from tucajero.utils.theme import btn_primary, btn_secondary, get_colors
c = get_colors()


class SelectorClienteDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.cliente = None
        self.setWindowTitle("Seleccionar Cliente")
        self.setMinimumSize(500, 400)
        from tucajero.utils.theme import get_colors
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['bg_app']}; }}")
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText(
            "Buscar por nombre, documento o teléfono..."
        )
        self.input_buscar.setStyleSheet(f"padding: 10px; font-size: 14px; background: {c['bg_input']}; color: {c['text_primary']}; border: 1.5px solid {c['border']}; border-radius: 8px;")
        self.input_buscar.textChanged.connect(self.buscar)
        layout.addWidget(self.input_buscar)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(
            ["Nombre", "Documento", "Teléfono", "Saldo"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.doubleClicked.connect(self.seleccionar)
        self.tabla.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.tabla)

        btns = QHBoxLayout()
        btn_sel = QPushButton("✓ Seleccionar")
        btn_sel.setStyleSheet(btn_primary())
        btn_sel.clicked.connect(self.seleccionar)
        btns.addWidget(btn_sel)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet(btn_secondary())
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        self.clientes = []
        self.cargar()

    def cargar(self, clientes=None):
        from tucajero.services.cliente_service import ClienteService

        if clientes is None:
            clientes = ClienteService(self.session).get_all()
        self.clientes = clientes
        self.tabla.setRowCount(len(clientes))
        for i, c in enumerate(clientes):
            self.tabla.setItem(i, 0, QTableWidgetItem(c.nombre))
            self.tabla.setItem(i, 1, QTableWidgetItem(c.documento or ""))
            self.tabla.setItem(i, 2, QTableWidgetItem(c.telefono or ""))
            self.tabla.setItem(i, 3, QTableWidgetItem(fmt_moneda(c.saldo_credito)))

    def buscar(self, texto):
        from tucajero.services.cliente_service import ClienteService

        service = ClienteService(self.session)
        clientes = service.search(texto) if texto.strip() else service.get_all()
        self.cargar(clientes)

    def seleccionar(self):
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.clientes):
            self.cliente = self.clientes[row]
            self.accept()
