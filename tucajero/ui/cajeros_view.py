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
    QFrame,
)
from PySide6.QtCore import Qt
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium, TABLE_STYLE_PREMIUM


class CajerosView(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_cajeros()

    def init_ui(self):
        self.setStyleSheet(f"background-color: {Colors.BG_APP};")

        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Gestión de Cajeros")
        titulo.setStyleSheet(f"font-size: {Typography.H2}px; font-weight: {Typography.BOLD}; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(titulo)

        info = QLabel(
            "Administra los cajeros que pueden usar el sistema. "
            "Solo el administrador puede ver esta sección."
        )
        info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        info.setWordWrap(True)
        layout.addWidget(info)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_nuevo = ButtonPremium("+ Nuevo Cajero", style="primary")
        btn_nuevo.clicked.connect(self.nuevo_cajero)
        btn_layout.addWidget(btn_nuevo)

        btn_cambiar_pin = ButtonPremium("🔑 Cambiar PIN", style="primary")
        btn_cambiar_pin.clicked.connect(self.cambiar_pin)
        btn_layout.addWidget(btn_cambiar_pin)

        btn_eliminar = ButtonPremium("Eliminar", style="danger")
        btn_eliminar.clicked.connect(self.eliminar_cajero)
        btn_layout.addWidget(btn_eliminar)

        layout.addLayout(btn_layout)

        # Card wrapper for table
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.XL}px;
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(1, 1, 1, 1)
        card_layout.setSpacing(0)
        card.setLayout(card_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Rol"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setStyleSheet(TABLE_STYLE_PREMIUM)
        card_layout.addWidget(self.tabla)

        layout.addWidget(card)

    def cargar_cajeros(self):
        from tucajero.services.cajero_service import CajeroService

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
        from tucajero.services.cajero_service import CajeroService

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
        from tucajero.services.cajero_service import CajeroService

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
            from tucajero.services.cajero_service import CajeroService

            CajeroService(self.session).eliminar(cajero.id)
            self.cargar_cajeros()
