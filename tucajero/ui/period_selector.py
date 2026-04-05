"""
Botones para seleccionar período: Semana, Mes, Semestre, Año
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt


class PeriodSelector(QFrame):
    """
    Botones para seleccionar período: Semana, Mes, Semestre, Año
    """

    period_changed = Signal(str)  # Emite: "week", "month", "semester", "year"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        periods = [
            ("Semana", "week"),
            ("Mes", "month"),
            ("Semestre", "semester"),
            ("Año", "year"),
        ]

        self.buttons = {}

        for label, period_id in periods:
            btn = QPushButton(label)
            btn.setMinimumWidth(80)
            btn.setMinimumHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            # Estilo: primero activo, resto inactivo
            if period_id == "week":
                btn.setStyleSheet(self._get_active_style())
                self.active_period = period_id
            else:
                btn.setStyleSheet(self._get_inactive_style())

            btn.clicked.connect(lambda checked, p=period_id: self._on_period_clicked(p))
            self.buttons[period_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

    def _get_active_style(self):
        return """
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """

    def _get_inactive_style(self):
        return """
            QPushButton {
                background-color: transparent;
                color: #666666;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """

    def _on_period_clicked(self, period_id):
        # Resetear todos los botones
        for pid, btn in self.buttons.items():
            if pid == period_id:
                btn.setStyleSheet(self._get_active_style())
            else:
                btn.setStyleSheet(self._get_inactive_style())

        self.active_period = period_id
        self.period_changed.emit(period_id)
