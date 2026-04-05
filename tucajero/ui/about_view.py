from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QDialog
from PySide6.QtCore import Qt
from tucajero.config.app_config import APP_NAME, VERSION as APP_VERSION
from tucajero.utils.store_config import get_store_name
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium


class AboutView(QDialog):
    """Ventana Acerca de - TuCajero POS"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Acerca de {APP_NAME}")
        self.setFixedSize(420, 440)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.LG)
        self.setLayout(layout)

        # ── PRODUCTO: TuCajero POS (nuestra empresa) ──────────────
        titulo = QLabel(APP_NAME)
        titulo.setStyleSheet(
            f"font-size: {Typography.H1}px; font-weight: {Typography.EXTRABOLD}; "
            f"color: {Colors.PRIMARY};"
        )
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        descripcion = QLabel("Sistema de Punto de Venta Profesional")
        descripcion.setStyleSheet(
            f"font-size: {Typography.BODY}px; color: {Colors.TEXT_SECONDARY};"
        )
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(descripcion)

        version = QLabel(f"Versión {APP_VERSION}")
        version.setStyleSheet(
            f"font-size: {Typography.H5}px; color: {Colors.SUCCESS}; "
            f"font-weight: {Typography.BOLD}; margin-top: {Spacing.MD}px;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        # Separador
        sep = QLabel("")
        sep.setFixedHeight(Spacing.MD)
        layout.addWidget(sep)

        # ── NEGOCIO DEL CLIENTE (datos configurados) ──────────────
        store_name = get_store_name()
        if store_name:
            store_label = QLabel(f"Negocio configurado:")
            store_label.setStyleSheet(
                f"font-size: {Typography.CAPTION}px; color: {Colors.TEXT_MUTED}; "
                f"text-transform: uppercase; letter-spacing: 0.5px;"
            )
            store_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(store_label)

            negocio = QLabel(store_name)
            negocio.setStyleSheet(
                f"font-size: {Typography.BODY}px; color: {Colors.TEXT_PRIMARY}; "
                f"font-weight: {Typography.SEMIBOLD};"
            )
            negocio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(negocio)

        layout.addStretch()

        # ── DESARROLLADOR ─────────────────────────────────────────
        desarrollado = QLabel("Desarrollado por:")
        desarrollado.setStyleSheet(
            f"font-size: {Typography.CAPTION}px; color: {Colors.TEXT_TERTIARY};"
        )
        desarrollado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desarrollado)

        autor = QLabel("Ingeniero Francisco Llinas P.")
        autor.setStyleSheet(
            f"font-size: {Typography.BODY}px; font-weight: {Typography.BOLD}; "
            f"color: {Colors.PRIMARY};"
        )
        autor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(autor)

        copyright = QLabel("© 2026 TuCajero POS. Todos los derechos reservados.")
        copyright.setStyleSheet(
            f"font-size: {Typography.CAPTION}px; color: {Colors.TEXT_MUTED};"
        )
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright)

        # Botón
        btn_cerrar = ButtonPremium("Cerrar", style="primary")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
