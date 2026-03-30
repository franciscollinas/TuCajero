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
)
from PySide6.QtCore import Qt
from utils.theme import btn_primary, btn_danger


class CajerosView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_cajeros()

    def init_ui(self):
        from utils.theme import get_colors
        c = get_colors()
        self.setStyleSheet(f"background-color: {c['bg_app']};")
        
        layout = QVBoxLayout()
        self.setLayout(layout)
 
        titulo = QLabel("Gestión de Cajeros")
        titulo.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {c['text_primary']};")
        layout.addWidget(titulo)
 
        info = QLabel(
            "Administra los cajeros que pueden usar el sistema. "
            "Solo el administrador puede ver esta sección."
        )
        info.setStyleSheet(f"color: {c['text_secondary']};")
        info.setWordWrap(True)
        layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_nuevo = QPushButton("+ Nuevo Cajero")
        btn_nuevo.setStyleSheet(btn_primary())
        btn_nuevo.clicked.connect(self.nuevo_cajero)
        btn_layout.addWidget(btn_nuevo)

        btn_cambiar_pin = QPushButton("🔑 Cambiar PIN")
        btn_cambiar_pin.setStyleSheet(btn_primary())
        btn_cambiar_pin.clicked.connect(self.cambiar_pin)
        btn_layout.addWidget(btn_cambiar_pin)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(btn_danger())
        btn_eliminar.clicked.connect(self.eliminar_cajero)
        btn_layout.addWidget(btn_eliminar)

        layout.addLayout(btn_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Rol"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

    def cargar_cajeros(self):
        from services.cajero_service import CajeroService

        cajeros = CajeroService(self.session).get_all()
        self.cajeros = cajeros
        self.tabla.setRowCount(len(cajeros))
        for i, c in enumerate(cajeros):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.tabla.setItem(i, 1, QTableWidgetItem(c.nombre))
            rol_item = QTableWidgetItem(
                "👑 Administrador" if c.rol == "admin" else "Cajero"
            )
            self.tabla.setItem(i, 2, rol_item)

    def obtener_seleccionado(self):
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.cajeros):
            return self.cajeros[row]
        return None

    def nuevo_cajero(self):
        from PySide6.QtWidgets import QInputDialog
        from PySide6.QtWidgets import QLineEdit

        nombre, ok1 = QInputDialog.getText(self, "Nuevo Cajero", "Nombre del cajero:")
        if not ok1 or not nombre.strip():
            return
        pin, ok2 = QInputDialog.getText(
            self, "Nuevo Cajero", "PIN de 4 dígitos:", QLineEdit.EchoMode.Password
        )
        if not ok2:
            return
        from services.cajero_service import CajeroService

        try:
            CajeroService(self.session).crear(nombre.strip(), pin)
            self.cargar_cajeros()
            QMessageBox.information(
                self, "Éxito", f"Cajero '{nombre}' creado correctamente."
            )
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def cambiar_pin(self):
        cajero = self.obtener_seleccionado()
        if not cajero:
            QMessageBox.warning(self, "Error", "Selecciona un cajero")
            return
        from PySide6.QtWidgets import QInputDialog, QLineEdit

        nuevo_pin, ok = QInputDialog.getText(
            self,
            "Cambiar PIN",
            f"Nuevo PIN de 4 dígitos para {cajero.nombre}:",
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return
        from services.cajero_service import CajeroService

        try:
            CajeroService(self.session).cambiar_pin(cajero.id, nuevo_pin)
            QMessageBox.information(self, "Éxito", "PIN actualizado.")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def eliminar_cajero(self):
        cajero = self.obtener_seleccionado()
        if not cajero:
            QMessageBox.warning(self, "Error", "Selecciona un cajero")
            return
        if cajero.rol == "admin":
            QMessageBox.warning(self, "Error", "No se puede eliminar al administrador.")
            return
        resp = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar al cajero '{cajero.nombre}'?"
        )
        if resp == QMessageBox.StandardButton.Yes:
            from services.cajero_service import CajeroService

            CajeroService(self.session).eliminar(cajero.id)
            self.cargar_cajeros()
