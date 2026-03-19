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
from utils.formato import fmt_moneda


class DescuentoDialog(QDialog):
    def __init__(self, total_bruto, descuento_actual, parent=None):
        super().__init__(parent)
        self.total_bruto = total_bruto
        self.descuento_resultado = descuento_actual.copy()
        self.setWindowTitle("Aplicar Descuento")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        lbl_total = QLabel(f"Total actual: {fmt_moneda(total_bruto)}")
        lbl_total.setStyleSheet(
            "font-size:16px;font-weight:bold;padding:8px;"
            "background:#ecf0f1;border-radius:4px;"
        )
        lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_total)

        tipo_label = QLabel("Tipo de descuento:")
        tipo_label.setStyleSheet("font-size:13px;font-weight:bold;margin-top:8px;")
        layout.addWidget(tipo_label)

        self.radio_group = QButtonGroup()
        self.radio_pct = QRadioButton("Porcentaje (%)")
        self.radio_fijo = QRadioButton("Valor fijo ($)")
        self.radio_pct.setStyleSheet("font-size:14px;padding:4px;")
        self.radio_fijo.setStyleSheet("font-size:14px;padding:4px;")
        self.radio_group.addButton(self.radio_pct, 1)
        self.radio_group.addButton(self.radio_fijo, 2)
        self.radio_pct.setChecked(True)
        self.radio_pct.toggled.connect(self.on_tipo_changed)
        layout.addWidget(self.radio_pct)
        layout.addWidget(self.radio_fijo)

        self.lbl_input = QLabel("Porcentaje de descuento:")
        self.lbl_input.setStyleSheet("font-size:13px;margin-top:8px;")
        layout.addWidget(self.lbl_input)

        self.valor_input = QDoubleSpinBox()
        self.valor_input.setRange(0, 100)
        self.valor_input.setDecimals(2)
        self.valor_input.setStyleSheet("font-size:18px;padding:8px;")
        self.valor_input.setSuffix(" %")
        self.valor_input.valueChanged.connect(self.actualizar_preview)
        layout.addWidget(self.valor_input)

        self.lbl_preview = QLabel("")
        self.lbl_preview.setStyleSheet(
            "font-size:15px;font-weight:bold;color:#27ae60;"
            "padding:8px;background:#f0fff4;border-radius:4px;"
        )
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_preview)
        self.actualizar_preview()

        btns = QHBoxLayout()
        btn_aplicar = QPushButton("✓ APLICAR DESCUENTO")
        btn_aplicar.setStyleSheet(
            "background:#27ae60;color:white;"
            "padding:12px;font-weight:bold;font-size:14px;"
        )
        btn_aplicar.clicked.connect(self.aplicar)
        btns.addWidget(btn_aplicar)

        btn_quitar = QPushButton("✕ Quitar descuento")
        btn_quitar.setStyleSheet("background:#e74c3c;color:white;padding:12px;")
        btn_quitar.clicked.connect(self.quitar)
        btns.addWidget(btn_quitar)

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("padding:12px;")
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

    def on_tipo_changed(self):
        if self.radio_pct.isChecked():
            self.lbl_input.setText("Porcentaje de descuento:")
            self.valor_input.setRange(0, 100)
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
        self.descuento_resultado = self._descuento_calculado
        self.accept()

    def quitar(self):
        self.descuento_resultado = {"tipo": None, "valor": 0, "total": 0}
        self.accept()
