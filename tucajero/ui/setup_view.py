from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QGroupBox,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from tucajero.utils.store_config import (
    save_store_config,
    load_store_config,
    get_store_name,
    get_address,
    get_phone,
    get_email,
    get_nit,
    get_logo_path,
)
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium


class SetupDialog(QDialog):
    """Pantalla de configuración inicial — aparece solo la primera vez."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path = ""
        self.setWindowTitle("Bienvenido")
        self.setMinimumSize(680, 600)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background-color: {Colors.BG_PANEL};")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)
        header_layout.setContentsMargins(24, 24, 24, 24)
        header_layout.setSpacing(4)

        title = QLabel("Bienvenido a TuCajero")
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 26px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Configura tu negocio para comenzar")
        subtitle.setObjectName("subtitle")
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        # Scroll area with centered content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        main_layout.addWidget(scroll, 1)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)
        scroll_layout.setContentsMargins(24, 24, 24, 24)
        scroll_layout.setSpacing(0)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Card container
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {Colors.BG_CARD}; border-radius: {BorderRadius.XL}px; "
            f"border: 1px solid {Colors.BORDER_DEFAULT};"
        )
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        def field_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"font-size: {Typography.BODY_SM}px; font-weight: {Typography.MEDIUM}; "
                f"color: {Colors.TEXT_PRIMARY}; margin-bottom: 0px;"
            )
            return lbl

        def input_style():
            return (
                f"padding: {Spacing.SM}px {Spacing.LG}px; font-size: {Typography.BODY}px; "
                f"background: {Colors.BG_INPUT}; color: {Colors.TEXT_PRIMARY}; "
                f"border: 1.5px solid {Colors.BORDER_DEFAULT}; border-radius: {BorderRadius.MD}px; "
                f"min-height: 42px; max-height: 44px;"
            )

        # Nombre
        card_layout.addWidget(field_label("Nombre del negocio *"))
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Droguería CruzMedic")
        self.nombre_input.setStyleSheet(input_style())
        card_layout.addWidget(self.nombre_input)

        # NIT y Teléfono en fila
        nit_tel_layout = QHBoxLayout()
        nit_tel_layout.setSpacing(16)

        nit_widget = QWidget()
        nit_vl = QVBoxLayout()
        nit_vl.setSpacing(8)
        nit_vl.setContentsMargins(0, 0, 0, 0)
        nit_widget.setLayout(nit_vl)
        nit_vl.addWidget(field_label("NIT"))
        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("123456789-0")
        self.nit_input.setStyleSheet(input_style())
        nit_vl.addWidget(self.nit_input)

        tel_widget = QWidget()
        tel_vl = QVBoxLayout()
        tel_vl.setSpacing(8)
        tel_vl.setContentsMargins(0, 0, 0, 0)
        tel_widget.setLayout(tel_vl)
        tel_vl.addWidget(field_label("Teléfono"))
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("300 123 4567")
        self.telefono_input.setStyleSheet(input_style())
        tel_vl.addWidget(self.telefono_input)

        nit_tel_layout.addWidget(nit_widget, 1)
        nit_tel_layout.addWidget(tel_widget, 1)
        card_layout.addLayout(nit_tel_layout)

        # Email
        card_layout.addWidget(field_label("Correo electrónico"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("info@ejemplo.com")
        self.email_input.setStyleSheet(input_style())
        card_layout.addWidget(self.email_input)

        # Dirección
        card_layout.addWidget(field_label("Dirección"))
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Calle 123 #45-67, Ciudad")
        self.direccion_input.setStyleSheet(input_style())
        card_layout.addWidget(self.direccion_input)

        # Logo section
        card_layout.addWidget(field_label("Logo de tu negocio"))
        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)

        self.btn_logo = ButtonPremium("📁  Seleccionar logo...", style="secondary")
        self.btn_logo.setFixedHeight(42)
        self.btn_logo.clicked.connect(self.seleccionar_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(56, 56)
        self.logo_preview.setStyleSheet(
            f"border: 1.5px solid {Colors.BORDER_DEFAULT}; border-radius: {BorderRadius.MD}px; "
            f"background-color: {Colors.BG_ELEVATED};"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_row.addWidget(self.btn_logo, 1)
        logo_row.addWidget(self.logo_preview)
        card_layout.addLayout(logo_row)

        # Add card to scroll layout
        scroll_layout.addWidget(card)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)

        # Footer
        footer = QWidget()
        footer.setStyleSheet("background-color: transparent;")
        footer_layout = QVBoxLayout()
        footer.setLayout(footer_layout)
        footer_layout.setContentsMargins(24, 16, 24, 24)
        footer_layout.setSpacing(12)

        nota = QLabel("* Campo requerido")
        nota.setObjectName("nota")
        nota.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        nota.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(nota)

        self.btn_comenzar = ButtonPremium("COMENZAR", style="primary")
        self.btn_comenzar.setFixedHeight(44)
        self.btn_comenzar.clicked.connect(self.guardar)
        footer_layout.addWidget(self.btn_comenzar, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(footer)

        self.nombre_input.setFocus()

    def seleccionar_logo(self):
        """Abre diálogo para seleccionar logo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.ico *.bmp);;Todos los archivos (*)",
        )
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    56,
                    56,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
            import os

            self.btn_logo.setText(f"📁  {os.path.basename(file_path)}")
            self.btn_logo.setStyleSheet(btn_secondary())

    def guardar(self):
        """Guarda la configuración."""
        import logging

        try:
            nombre = self.nombre_input.text().strip()
            if not nombre:
                QMessageBox.warning(
                    self, "Campo requerido", "El nombre del negocio es requerido"
                )
                self.nombre_input.setFocus()
                return

            config_data = {
                "store_name": nombre,
                "nit": self.nit_input.text().strip(),
                "phone": self.telefono_input.text().strip(),
                "email": self.email_input.text().strip(),
                "address": self.direccion_input.text().strip(),
                "logo_path": self.logo_path,
                "setup_complete": True,
            }

            if save_store_config(config_data):
                self.accept()
            else:
                QMessageBox.critical(
                    self, "Error", "No se pudo guardar la configuración"
                )
        except Exception as e:
            logging.error(f"Error al guardar configuración: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{str(e)}")


class SetupView(QWidget):
    """Panel de configuración — accesible desde el menú lateral."""

    config_saved = Signal()

    def __init__(self, session=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.logo_path = ""
        self.init_ui()
        self.cargar_config()

    def init_ui(self):

        # Main layout with scroll area for centered content
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Header
        header = QWidget()
        header.setStyleSheet(f"background-color: {Colors.BG_PANEL};")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(4)

        titulo = QLabel("Configuración del Negocio")
        titulo.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {Colors.TEXT_PRIMARY};"
        )
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(titulo)

        subtitulo = QLabel("Administra la información de tu negocio")
        subtitulo.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitulo)

        main_layout.addWidget(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        main_layout.addWidget(scroll, 1)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)
        scroll_layout.setContentsMargins(24, 24, 24, 24)
        scroll_layout.setSpacing(0)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Card container (SetupView)
        card = QFrame()
        card.setStyleSheet(
            f"background-color: {Colors.BG_CARD}; border-radius: {BorderRadius.XL}px; "
            f"border: 1px solid {Colors.BORDER_DEFAULT};"
        )
        card_layout = QVBoxLayout()
        card.setLayout(card_layout)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        def field_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"font-size: {Typography.BODY_SM}px; font-weight: {Typography.MEDIUM}; "
                f"color: {Colors.TEXT_PRIMARY};"
            )
            return lbl

        def input_style():
            return (
                f"padding: {Spacing.SM}px {Spacing.LG}px; font-size: {Typography.BODY}px; "
                f"background: {Colors.BG_INPUT}; color: {Colors.TEXT_PRIMARY}; "
                f"border: 1.5px solid {Colors.BORDER_DEFAULT}; border-radius: {BorderRadius.MD}px; "
                f"min-height: 42px; max-height: 44px;"
            )

        # Nombre
        card_layout.addWidget(field_label("Nombre *"))
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del negocio")
        self.nombre_input.setStyleSheet(input_style())
        card_layout.addWidget(self.nombre_input)

        # NIT y Teléfono en fila
        nit_tel_layout = QHBoxLayout()
        nit_tel_layout.setSpacing(16)

        nit_widget = QWidget()
        nit_vl = QVBoxLayout()
        nit_vl.setSpacing(8)
        nit_vl.setContentsMargins(0, 0, 0, 0)
        nit_widget.setLayout(nit_vl)
        nit_vl.addWidget(field_label("NIT"))
        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("NIT")
        self.nit_input.setStyleSheet(input_style())
        nit_vl.addWidget(self.nit_input)

        tel_widget = QWidget()
        tel_vl = QVBoxLayout()
        tel_vl.setSpacing(8)
        tel_vl.setContentsMargins(0, 0, 0, 0)
        tel_widget.setLayout(tel_vl)
        tel_vl.addWidget(field_label("Teléfono"))
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        self.telefono_input.setStyleSheet(input_style())
        tel_vl.addWidget(self.telefono_input)

        nit_tel_layout.addWidget(nit_widget, 1)
        nit_tel_layout.addWidget(tel_widget, 1)
        card_layout.addLayout(nit_tel_layout)

        # Email
        card_layout.addWidget(field_label("Correo electrónico"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setStyleSheet(input_style())
        card_layout.addWidget(self.email_input)

        # Dirección
        card_layout.addWidget(field_label("Dirección"))
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Dirección")
        self.direccion_input.setStyleSheet(input_style())
        card_layout.addWidget(self.direccion_input)

        # Logo
        card_layout.addWidget(field_label("Logo"))
        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)

        self.btn_logo = ButtonPremium("📁  Seleccionar logo...", style="secondary")
        self.btn_logo.setFixedHeight(42)
        self.btn_logo.clicked.connect(self.seleccionar_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(56, 56)
        self.logo_preview.setStyleSheet(
            f"border: 1.5px solid {Colors.BORDER_DEFAULT}; border-radius: {BorderRadius.MD}px; "
            f"background-color: {Colors.BG_ELEVATED};"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_row.addWidget(self.btn_logo, 1)
        logo_row.addWidget(self.logo_preview)
        card_layout.addLayout(logo_row)

        # Printer section
        card_layout.addSpacing(8)

        printer_group = QGroupBox("Impresora Térmica")
        printer_group.setStyleSheet(
            f"QGroupBox {{ background-color: transparent; border: 1.5px solid {Colors.BORDER_DEFAULT}; "
            f"border-radius: {BorderRadius.LG}px; margin-top: 12px; padding-top: 16px; font-weight: {Typography.SEMIBOLD}; "
            f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.BODY}px; }} "
            f"QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; "
            f"left: 14px; padding: 0 10px; color: {Colors.TEXT_MUTED}; font-size: {Typography.CAPTION}px; "
            f"text-transform: uppercase; letter-spacing: 0.5px; }}"
        )
        printer_layout = QFormLayout()
        printer_group.setLayout(printer_layout)
        printer_layout.setSpacing(12)
        printer_layout.setContentsMargins(16, 16, 16, 16)

        self.chk_impresora = QCheckBox("Usar impresora térmica")
        self.chk_impresora.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; font-size: {Typography.BODY_SM}px; spacing: 8px;"
        )
        self.chk_impresora.toggled.connect(self.on_impresora_toggled)
        printer_layout.addRow("", self.chk_impresora)

        self.tipo_impresora = QComboBox()
        self.tipo_impresora.addItems(["USB", "Red (TCP/IP)", "Serial (COM)"])
        self.tipo_impresora.currentTextChanged.connect(self.on_tipo_impresora_changed)
        printer_layout.addRow("Tipo de conexión:", self.tipo_impresora)

        self.usb_widget = QWidget()
        usb_layout = QFormLayout()
        self.usb_widget.setLayout(usb_layout)
        usb_layout.setSpacing(8)
        usb_layout.setContentsMargins(0, 0, 0, 0)
        self.vendor_id = QLineEdit("0x0416")
        self.vendor_id.setStyleSheet(input_style())
        self.product_id = QLineEdit("0x5011")
        self.product_id.setStyleSheet(input_style())
        usb_layout.addRow("Vendor ID:", self.vendor_id)
        usb_layout.addRow("Product ID:", self.product_id)
        printer_layout.addRow("", self.usb_widget)

        self.red_widget = QWidget()
        red_layout = QFormLayout()
        self.red_widget.setLayout(red_layout)
        red_layout.setSpacing(8)
        red_layout.setContentsMargins(0, 0, 0, 0)
        self.ip_impresora = QLineEdit("192.168.1.100")
        self.ip_impresora.setStyleSheet(input_style())
        self.puerto_impresora = QLineEdit("9100")
        self.puerto_impresora.setStyleSheet(input_style())
        red_layout.addRow("IP:", self.ip_impresora)
        red_layout.addRow("Puerto:", self.puerto_impresora)
        printer_layout.addRow("", self.red_widget)
        self.red_widget.setVisible(False)

        self.serial_widget = QWidget()
        serial_layout = QFormLayout()
        self.serial_widget.setLayout(serial_layout)
        serial_layout.setSpacing(8)
        serial_layout.setContentsMargins(0, 0, 0, 0)
        self.com_port = QLineEdit("COM1")
        self.com_port.setStyleSheet(input_style())
        serial_layout.addRow("Puerto COM:", self.com_port)
        printer_layout.addRow("", self.serial_widget)
        self.serial_widget.setVisible(False)

        self.ancho_papel = QComboBox()
        self.ancho_papel.addItems(["58mm (32 chars)", "80mm (48 chars)"])
        self.ancho_papel.setCurrentIndex(1)
        printer_layout.addRow("Ancho de papel:", self.ancho_papel)

        btn_prueba = ButtonPremium("Imprimir página de prueba", style="secondary")
        btn_prueba.setFixedHeight(42)
        btn_prueba.clicked.connect(self.prueba_impresion)
        printer_layout.addRow("", btn_prueba)

        self.printer_group = printer_group
        card_layout.addWidget(printer_group)
        self.on_impresora_toggled(False)

        # Add card to scroll layout
        scroll_layout.addWidget(card)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)

        # Footer with save button
        footer = QWidget()
        footer.setStyleSheet("background-color: transparent;")
        footer_layout = QVBoxLayout()
        footer.setLayout(footer_layout)
        footer_layout.setContentsMargins(24, 16, 24, 24)
        footer_layout.setSpacing(12)

        self.btn_guardar = ButtonPremium("GUARDAR CONFIGURACIÓN", style="primary")
        self.btn_guardar.setFixedHeight(44)
        self.btn_guardar.clicked.connect(self.guardar)
        footer_layout.addWidget(self.btn_guardar, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(footer)

    def cargar_config(self):
        from tucajero.utils.store_config import get_printer_config

        self.nombre_input.setText(get_store_name())
        self.nit_input.setText(get_nit())
        self.telefono_input.setText(get_phone())
        self.email_input.setText(get_email())
        self.direccion_input.setText(get_address())
        logo = get_logo_path()
        if logo:
            import os

            if os.path.exists(logo):
                self.logo_path = logo
                pixmap = QPixmap(logo)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        56,
                        56,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.logo_preview.setPixmap(scaled)
                    self.btn_logo.setText(f"📁  {os.path.basename(logo)}")

        printer_cfg = get_printer_config()
        if printer_cfg.get("tipo"):
            self.chk_impresora.setChecked(True)
            tipo = printer_cfg.get("tipo", "usb")
            if tipo == "usb":
                self.tipo_impresora.setCurrentText("USB")
                self.vendor_id.setText(printer_cfg.get("vendor_id", "0x0416"))
                self.product_id.setText(printer_cfg.get("product_id", "0x5011"))
            elif tipo == "red":
                self.tipo_impresora.setCurrentText("Red (TCP/IP)")
                self.ip_impresora.setText(printer_cfg.get("ip", "192.168.1.100"))
                self.puerto_impresora.setText(str(printer_cfg.get("puerto", 9100)))
            elif tipo == "serial":
                self.tipo_impresora.setCurrentText("Serial (COM)")
                self.com_port.setText(printer_cfg.get("puerto", "COM1"))
            ancho = printer_cfg.get("ancho", 48)
            self.ancho_papel.setCurrentIndex(0 if ancho == 32 else 1)
        self.on_impresora_toggled(self.chk_impresora.isChecked())

    def seleccionar_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.ico *.bmp);;Todos (*)",
        )
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    56,
                    56,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
            import os

            self.btn_logo.setText(f"📁  {os.path.basename(file_path)}")

    def guardar(self):
        import logging

        try:
            nombre = self.nombre_input.text().strip()
            if not nombre:
                QMessageBox.warning(
                    self, "Campo requerido", "El nombre del negocio es requerido"
                )
                self.nombre_input.setFocus()
                return

            config_data = {
                "store_name": nombre,
                "nit": self.nit_input.text().strip(),
                "phone": self.telefono_input.text().strip(),
                "email": self.email_input.text().strip(),
                "address": self.direccion_input.text().strip(),
                "logo_path": self.logo_path,
                "setup_complete": True,
                "impresora": self._build_printer_config(),
            }

            if save_store_config(config_data):
                self.config_saved.emit()
                QMessageBox.information(
                    self, "Éxito", "Configuración guardada correctamente"
                )
            else:
                QMessageBox.critical(
                    self, "Error", "No se pudo guardar la configuración"
                )
        except Exception as e:
            logging.error(f"Error al guardar configuración: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Ocurrió un error:\n{str(e)}")

    def on_impresora_toggled(self, checked):
        self.tipo_impresora.setEnabled(checked)
        self.usb_widget.setEnabled(checked)
        self.red_widget.setEnabled(checked)
        self.serial_widget.setEnabled(checked)
        self.ancho_papel.setEnabled(checked)

    def on_tipo_impresora_changed(self, tipo):
        self.usb_widget.setVisible("USB" in tipo)
        self.red_widget.setVisible("Red" in tipo)
        self.serial_widget.setVisible("Serial" in tipo)

    def prueba_impresion(self):
        from tucajero.utils.impresora import ImpresoraTermica

        config = self._build_printer_config()
        if not config:
            QMessageBox.warning(
                self, "Sin impresora", "Activa y configura la impresora primero."
            )
            return
        try:
            imp = ImpresoraTermica(config)
            imp.prueba_impresion()
            QMessageBox.information(
                self,
                "Prueba enviada",
                "Pagina de prueba enviada a la impresora.\n"
                "Si no imprimio, verifica la conexion.",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error de impresora",
                f"No se pudo imprimir:\n{str(e)}\n\n"
                "Verifica que la impresora este conectada y encendida.",
            )

    def _build_printer_config(self):
        if not self.chk_impresora.isChecked():
            return {}
        tipo_txt = self.tipo_impresora.currentText()
        ancho = 32 if "58mm" in self.ancho_papel.currentText() else 48
        if "USB" in tipo_txt:
            return {
                "tipo": "usb",
                "vendor_id": self.vendor_id.text().strip(),
                "product_id": self.product_id.text().strip(),
                "ancho": ancho,
            }
        elif "Red" in tipo_txt:
            return {
                "tipo": "red",
                "ip": self.ip_impresora.text().strip(),
                "puerto": self.puerto_impresora.text().strip(),
                "ancho": ancho,
            }
        elif "Serial" in tipo_txt:
            return {
                "tipo": "serial",
                "puerto": self.com_port.text().strip(),
                "ancho": ancho,
            }
        return {}
