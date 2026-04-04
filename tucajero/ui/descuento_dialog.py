from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDoubleSpinBox,
    QButtonGroup,
    QRadioButton,
    QWidget,
)
from PySide6.QtCore import Qt
from tucajero.utils.formato import fmt_moneda
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium


class DescuentoDialog(QDialog):
    """Dialog for applying discounts with limits and validation"""

    MAX_DESCUENTO_PORCENTAJE = 50  # Límite máximo de descuento: 50%

    def __init__(self, total_bruto, descuento_actual, parent=None, es_admin=False):
        super().__init__(parent)
        self.total_bruto = total_bruto
        self.descuento_resultado = descuento_actual.copy()
        self.es_admin = es_admin
        self.max_descuento = self.MAX_DESCUENTO_PORCENTAJE if es_admin else 25
        self.setWindowTitle("Aplicar Descuento")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        lbl_total = QLabel(f"Total actual: {fmt_moneda(total_bruto)}")
        lbl_total.setStyleSheet(
            f"font-size:{Typography.H5}px; font-weight:{Typography.BOLD}; padding:{Spacing.SM}px; "
            f"background: {Colors.BG_CARD}; color: {Colors.TEXT_PRIMARY}; border-radius:{BorderRadius.SM}px; border: 1px solid {Colors.BORDER_DEFAULT};"
        )
        lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_total)

        tipo_label = QLabel("Tipo de descuento:")
        tipo_label.setStyleSheet(f"font-size:{Typography.BODY}px;font-weight:{Typography.BOLD};margin-top:{Spacing.SM}px; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(tipo_label)

        self.radio_group = QButtonGroup()
        self.radio_pct = QRadioButton("Porcentaje (%)")
        self.radio_fijo = QRadioButton("Valor fijo ($)")
        self.radio_pct.setStyleSheet(f"font-size:{Typography.H5}px;padding:{Spacing.XXS}px;")
        self.radio_fijo.setStyleSheet(f"font-size:{Typography.H5}px;padding:{Spacing.XXS}px;")
        self.radio_group.addButton(self.radio_pct, 1)
        self.radio_group.addButton(self.radio_fijo, 2)
        self.radio_pct.setChecked(True)
        self.radio_pct.toggled.connect(self.on_tipo_changed)
        layout.addWidget(self.radio_pct)
        layout.addWidget(self.radio_fijo)

        self.lbl_input = QLabel("Porcentaje de descuento:")
        self.lbl_input.setStyleSheet(f"font-size:{Typography.BODY}px;margin-top:{Spacing.SM}px; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(self.lbl_input)

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(0, 100)
        self.valor_input.setDecimals(2)
        self.valor_input.setStyleSheet(f"font-size:{Typography.H4}px;padding:{Spacing.SM}px; background-color: {Colors.BG_INPUT}; color: {Colors.TEXT_PRIMARY}; border: 1.5px solid {Colors.BORDER_DEFAULT};")
        self.valor_input.setSuffix(" %")
        self.valor_input.valueChanged.connect(self.actualizar_preview)
        layout.addWidget(self.valor_input)

        self.lbl_preview = QLabel("")
        self.lbl_preview.setStyleSheet(
            f"font-size:{Typography.H5}px; font-weight:{Typography.BOLD}; color: {Colors.SUCCESS}; "
            f"padding:{Spacing.SM}px; background: {Colors.SUCCESS_LIGHT}; border-radius:{BorderRadius.SM}px; border: 1px solid {Colors.SUCCESS};"
        )
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_preview)
        self.actualizar_preview()

        btns = QHBoxLayout()
        btn_aplicar = ButtonPremium("✓ APLICAR DESCUENTO", style="primary")
        btn_aplicar.clicked.connect(self.aplicar)
        btns.addWidget(btn_aplicar)

        btn_quitar = ButtonPremium("✕ Quitar descuento", style="danger")
        btn_quitar.clicked.connect(self.quitar)
        btns.addWidget(btn_quitar)

        btn_cancel = ButtonPremium("Cancelar", style="secondary")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        if descuento_actual.get("tipo") == "porcentaje":
            self.radio_pct.setChecked(True)
            self.valor_input.setValue(descuento_actual.get("valor", 0))
        elif descuento_actual.get("tipo") == "valor_fijo":
            self.radio_fijo.setChecked(True)
            self.on_tipo_changed()
            self.valor_input.setValue(descuento_actual.get("valor", 0))

    def validar_descuento(self, valor, tipo):
        """Valida que el descuento esté dentro de los límites permitidos"""
        if tipo == "porcentaje":
            if valor > self.max_descuento:
                return False, f"El descuento máximo permitido es {self.max_descuento}%."
            return True, None
        else:  # valor_fijo
            if valor >= self.total_bruto:
                return False, "El descuento no puede ser igual o mayor al total de la venta."
            return True, None

    def on_tipo_changed(self):
        if self.radio_pct.isChecked():
            self.lbl_input.setText(f"Porcentaje de descuento (máx. {self.max_descuento}%):")
            self.valor_input.setRange(0, self.max_descuento)
            self.valor_input.setSuffix(" %")
            self.valor_input.setValue(0)
        else:
            self.lbl_input.setText("Valor fijo a descontar:")
            self.valor_input.setRange(0, self.total_bruto)
            self.valor_input.setSuffix("")
            self.valor_input.setPrefix("$")
            self.valor_input.setValue(0)
        self.actualizar_preview()

    def actualizar_preview(self):
        val = self.valor_input.value()
        if self.radio_pct.isChecked():
            descuento = round(self.total_bruto * val / 100, 2)
            tipo = "porcentaje"
        else:
            descuento = min(val, self.total_bruto)
            tipo = "valor_fijo"
        nuevo_total = max(0, self.total_bruto - descuento)
        self.lbl_preview.setText(
            f"Descuento: -{fmt_moneda(descuento)}  →  "
            f"Nuevo total: {fmt_moneda(nuevo_total)}"
        )
        self._descuento_calculado = {"tipo": tipo, "valor": val, "total": descuento}

    def aplicar(self):
        """Apply discount with validation"""
        val = self.valor_input.value()

        # Validar límites del descuento usando validar_descuento()
        tipo = "porcentaje" if self.radio_pct.isChecked() else "valor_fijo"
        valido, error = self.validar_descuento(val, tipo)
        
        if not valido:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Descuento no válido", error)
            return

        # Calcular descuento final
        if self.radio_pct.isChecked():
            descuento = round(self.total_bruto * val / 100, 2)
        else:
            descuento = min(val, self.total_bruto)

        # Validar que el descuento no sea mayor al total
        if descuento >= self.total_bruto:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Descuento no válido",
                "El descuento no puede ser igual o mayor al total de la venta."
            )
            return

        self.descuento_resultado = {"tipo": tipo, "valor": val, "total": descuento}
        self.accept()

    def quitar(self):
        self.descuento_resultado = {"tipo": None, "valor": 0, "total": 0}
        self.accept()
