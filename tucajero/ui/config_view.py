import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QFormLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from tucajero.ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from tucajero.ui.components_premium import ButtonPremium


class ConfigNegocioDialog(QDialog):
    def __init__(self, parent=None, primera_vez=False):
        super().__init__(parent)
        self.primera_vez = primera_vez
        self.logo_path_seleccionado = ""
        self.setWindowTitle("Configuración del Negocio")
        self.setMinimumWidth(480)
        self.setMinimumHeight(500)
        if primera_vez:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
            )
        self.init_ui()
        self.cargar_datos_existentes()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setStyleSheet(f"QDialog {{ background-color: {Colors.BG_APP}; }}")
        self.setLayout(layout)

        header = QWidget()
        header.setStyleSheet(
            f"background-color: {Colors.PRIMARY_DARK}; border-radius: {BorderRadius.MD}px; padding: {Spacing.MD}px;"
        )
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        if self.primera_vez:
            titulo = QLabel("¡Bienvenido a TuCajero!")
            titulo.setStyleSheet(f"color: {Colors.TEXT_INVERSE}; font-size: {Typography.H4}px; font-weight: {Typography.BOLD};")
            subtitulo = QLabel("Configura los datos de tu negocio antes de comenzar.")
            subtitulo.setStyleSheet(f"color: rgba(255,255,255,0.8); font-size: {Typography.BODY}px;")
            header_layout.addWidget(titulo)
            header_layout.addWidget(subtitulo)
        else:
            titulo = QLabel("Configuración del Negocio")
            titulo.setStyleSheet(f"color: {Colors.TEXT_INVERSE}; font-size: {Typography.H5}px; font-weight: {Typography.BOLD};")
            header_layout.addWidget(titulo)

        layout.addWidget(header)

        form_widget = QWidget()
        form = QFormLayout()
        form.setSpacing(Spacing.SM)
        form_widget.setLayout(form)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Droguería El Carmen")
        self.nombre_input.setStyleSheet(f"padding: {Spacing.SM}px; font-size: {Typography.H5}px;")
        form.addRow("Nombre del negocio *:", self.nombre_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Ej: Calle 10 # 5-20")
        self.direccion_input.setStyleSheet(f"padding: {Spacing.SM}px; font-size: {Typography.H5}px;")
        form.addRow("Dirección:", self.direccion_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Ej: 3001234567")
        self.telefono_input.setStyleSheet(f"padding: {Spacing.SM}px; font-size: {Typography.H5}px;")
        form.addRow("Teléfono:", self.telefono_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ej: minegocio@gmail.com")
        self.email_input.setStyleSheet(f"padding: {Spacing.SM}px; font-size: {Typography.H5}px;")
        form.addRow("Email:", self.email_input)

        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("Ej: 900123456-1")
        self.nit_input.setStyleSheet(f"padding: {Spacing.SM}px; font-size: {Typography.H5}px;")
        form.addRow("NIT:", self.nit_input)

        logo_widget = QWidget()
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_widget.setLayout(logo_layout)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setStyleSheet(
            f"border: 2px dashed {Colors.BORDER_DEFAULT}; border-radius: {BorderRadius.SM}px; background: {Colors.BG_INPUT}; color: {Colors.TEXT_MUTED};"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setText("Sin logo")
        logo_layout.addWidget(self.logo_preview)

        logo_btn_layout = QVBoxLayout()
        btn_seleccionar_logo = ButtonPremium("Seleccionar logo...", style="secondary")
        btn_seleccionar_logo.clicked.connect(self.seleccionar_logo)
        logo_btn_layout.addWidget(btn_seleccionar_logo)

        self.lbl_logo_path = QLabel("Ningún archivo seleccionado")
        self.lbl_logo_path.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.lbl_logo_path.setWordWrap(True)
        logo_btn_layout.addWidget(self.lbl_logo_path)
        logo_btn_layout.addStretch()
        logo_layout.addLayout(logo_btn_layout)

        form.addRow("Logo del negocio:", logo_widget)
        layout.addWidget(form_widget)

        nota = QLabel("* Campo obligatorio")
        nota.setStyleSheet(f"color: {Colors.DANGER}; font-size: {Typography.TINY}px;")
        layout.addWidget(nota)

        layout.addStretch()

        # ── Sección Backup ────────────────────────
        from PySide6.QtWidgets import QGroupBox

        backup_group = QGroupBox("💾  Backup de Datos")
        backup_group.setStyleSheet(f"""
            QGroupBox {{
                color: {Colors.TEXT_SECONDARY};
                font-size: {Typography.CAPTION}px;
                font-weight: {Typography.BOLD};
                border: 1.5px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.MD}px;
                margin-top: {Spacing.SM}px;
                padding: {Spacing.MD}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Spacing.SM}px;
                padding: 0 {Spacing.XXS}px;
            }}
        """)
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setSpacing(Spacing.XS)

        backup_desc = QLabel(
            "Exporta todos tus datos (productos, ventas, clientes, historial) para hacer una copia de seguridad o migrar a una nueva versión."
        )
        backup_desc.setWordWrap(True)
        backup_desc.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: {Typography.TINY}px; background: transparent;"
        )
        backup_layout.addWidget(backup_desc)

        btns_backup = QHBoxLayout()
        btns_backup.setSpacing(Spacing.XS)

        btn_exportar = ButtonPremium("📤  Exportar datos", style="primary")
        btn_exportar.setFixedHeight(36)
        btn_exportar.clicked.connect(self._exportar_datos)

        btn_importar = ButtonPremium("📥  Importar datos", style="secondary")
        btn_importar.setFixedHeight(36)
        btn_importar.clicked.connect(self._importar_datos)

        btns_backup.addWidget(btn_exportar)
        btns_backup.addWidget(btn_importar)
        btns_backup.addStretch()
        backup_layout.addLayout(btns_backup)

        layout.addWidget(backup_group)

        btn_layout = QHBoxLayout()
        btn_guardar = ButtonPremium(
            "GUARDAR Y CONTINUAR" if self.primera_vez else "GUARDAR", style="primary"
        )
        btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_guardar)

        if not self.primera_vez:
            btn_cancelar = ButtonPremium("Cancelar", style="secondary")
            btn_cancelar.clicked.connect(self.reject)
            btn_layout.addWidget(btn_cancelar)

        layout.addLayout(btn_layout)

    def cargar_datos_existentes(self):
        from tucajero.utils.store_config import (
            load_store_config,
            get_store_name,
            get_address,
            get_phone,
            get_email,
            get_nit,
            get_logo_path,
        )

        load_store_config()
        self.nombre_input.setText(get_store_name())
        self.direccion_input.setText(get_address())
        self.telefono_input.setText(get_phone())
        self.email_input.setText(get_email())
        self.nit_input.setText(get_nit())
        logo = get_logo_path()
        if logo and os.path.exists(logo):
            self.logo_path_seleccionado = logo
            self._mostrar_preview_logo(logo)
            self.lbl_logo_path.setText(os.path.basename(logo))

    def seleccionar_logo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar logo del negocio",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.ico)",
        )
        if archivo:
            self.logo_path_seleccionado = archivo
            self._mostrar_preview_logo(archivo)
            self.lbl_logo_path.setText(os.path.basename(archivo))

    def _mostrar_preview_logo(self, path):
        pm = QPixmap(path)
        if not pm.isNull():
            scaled = pm.scaled(
                76,
                76,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.logo_preview.setPixmap(scaled)
            self.logo_preview.setText("")

    def guardar(self):
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(
                self, "Campo requerido", "El nombre del negocio es obligatorio."
            )
            self.nombre_input.setFocus()
            return

        logo_guardado = ""
        if self.logo_path_seleccionado:
            try:
                import shutil
                from tucajero.utils.store_config import get_config_dir

                assets_dir = os.path.join(os.path.dirname(get_config_dir()), "assets")
                os.makedirs(assets_dir, exist_ok=True)
                ext = os.path.splitext(self.logo_path_seleccionado)[1]
                destino = os.path.join(assets_dir, f"logo{ext}")
                shutil.copy2(self.logo_path_seleccionado, destino)
                logo_guardado = destino
            except Exception as e:
                print(f"[WARN] No se pudo copiar el logo: {e}")
                logo_guardado = self.logo_path_seleccionado

        config = {
            "store_name": nombre,
            "logo_path": logo_guardado,
            "address": self.direccion_input.text().strip(),
            "phone": self.telefono_input.text().strip(),
            "email": self.email_input.text().strip(),
            "nit": self.nit_input.text().strip(),
        }

        from tucajero.utils.store_config import save_store_config

        if save_store_config(config):
            if not self.primera_vez:
                QMessageBox.information(
                    self,
                    "Guardado",
                    "Configuración guardada.\n"
                    "Reinicia la aplicación para ver los cambios en el header.",
                )
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración.")

    def _exportar_datos(self):
        from tucajero.utils.data_manager import exportar_datos
        from datetime import datetime

        nombre_sugerido = (
            f"TuCajero_backup_{datetime.now().strftime('%Y%m%d')}.tucajero"
        )
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar backup de datos",
            nombre_sugerido,
            "Backup TuCajero (*.tucajero);;Todos los archivos (*)",
        )

        if not ruta:
            return

        if not ruta.endswith(".tucajero"):
            ruta += ".tucajero"

        resultado = exportar_datos(ruta)

        if resultado["ok"]:
            QMessageBox.information(
                self,
                "✅ Exportación exitosa",
                f"Datos exportados correctamente.\n\nArchivo guardado en:\n{ruta}\n\nGuarda este archivo en un lugar seguro (USB, Google Drive, etc.)",
            )
        else:
            QMessageBox.critical(
                self,
                "❌ Error al exportar",
                f"No se pudieron exportar los datos:\n{resultado['error']}",
            )

    def _importar_datos(self):
        from tucajero.utils.data_manager import importar_datos

        # Advertencia antes de importar
        confirm = QMessageBox.warning(
            self,
            "⚠️ Importar datos",
            "Esta acción reemplazará TODOS los datos actuales con los del backup.\n\n"
            "Se creará un backup automático de los datos actuales antes de continuar.\n\n"
            "¿Deseas continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar backup de TuCajero",
            "",
            "Backup TuCajero (*.tucajero);;Todos los archivos (*)",
        )

        if not ruta:
            return

        resultado = importar_datos(ruta)

        if resultado["ok"]:
            QMessageBox.information(
                self,
                "✅ Importación exitosa",
                f"Datos restaurados correctamente.\n\n"
                f"Backup importado: versión {resultado.get('version', '?')} del {resultado.get('fecha', '?')}\n\n"
                f"Cierra y vuelve a abrir TuCajero para ver los cambios.",
            )
        else:
            QMessageBox.critical(
                self,
                "❌ Error al importar",
                f"No se pudieron importar los datos:\n{resultado['error']}",
            )
