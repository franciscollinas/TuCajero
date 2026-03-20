from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDialog
from PySide6.QtCore import Qt
from utils.store_config import get_store_name, get_address, get_phone, get_nit
from utils.theme import texto_secundario, texto_terciario


class AboutView(QDialog):
    """Ventana Acerca de"""

    def __init__(self, parent=None):
        super().__init__(parent)
        store_name = get_store_name()
        self.setWindowTitle(f"Acerca de {store_name}")
        self.setFixedSize(400, 350)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel(get_store_name())
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        descripcion = QLabel("Sistema de ventas para pequeños negocios")
        descripcion.setStyleSheet(f"font-size: 14px; color: {texto_secundario()};")
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(descripcion)

        version = QLabel("Versión 1.0")
        version.setStyleSheet(
            "font-size: 16px; color: #27ae60; font-weight: bold; margin-top: 20px;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        address = get_address()
        if address:
            addr_label = QLabel(address)
            addr_label.setStyleSheet(f"font-size: 12px; color: {texto_terciario()};")
            addr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(addr_label)

        phone = get_phone()
        if phone:
            phone_label = QLabel(f"Tel: {phone}")
            phone_label.setStyleSheet(f"font-size: 12px; color: {texto_terciario()};")
            phone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(phone_label)

        nit = get_nit()
        if nit:
            nit_label = QLabel(f"NIT: {nit}")
            nit_label.setStyleSheet(f"font-size: 12px; color: {texto_terciario()};")
            nit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(nit_label)

        separator = QLabel("")
        separator.setFixedHeight(20)
        layout.addWidget(separator)

        desarrollado = QLabel("Desarrollado por:")
        desarrollado.setStyleSheet(f"font-size: 12px; color: {texto_terciario()};")
        desarrollado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desarrollado)

        autor = QLabel("Ingeniero Francisco Llinas P.")
        autor.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        autor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(autor)

        layout.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 30px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
