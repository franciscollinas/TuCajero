"""
TuCajero
Sistema simple de caja registradora para pequeños negocios.
"""

import sys
import logging
import os
from logging.handlers import RotatingFileHandler
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from PySide6.QtCore import QLocale
from config.database import init_db, get_session, crear_carpetas
from services.corte_service import CorteCajaService
from ui.main_window import MainWindow
from ui.ventas_view import VentasView
from ui.productos_view import ProductosView
from ui.inventario_view import InventarioView
from ui.corte_view import CorteView
from ui.activate_view import ActivationDialog
from security.license_manager import validar_licencia, crear_license_default
from utils.store_config import load_store_config


def configurar_logging():
    """Configura el logging global con rotación"""
    from config.database import get_log_file, crear_carpetas

    crear_carpetas()
    log_file = get_log_file()

    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)

    logging.basicConfig(
        handlers=[handler],
        level=logging.WARNING,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )


def mostrar_activacion():
    """Muestra la ventana de activación"""
    dialog = ActivationDialog()
    return dialog.exec() == QDialog.DialogCode.Accepted and dialog.activation_success


def mostrar_config_inicial():
    """Muestra la pantalla de configuración del negocio (primera vez)"""
    from ui.config_view import ConfigNegocioDialog

    dialog = ConfigNegocioDialog(primera_vez=True)
    return dialog.exec() == QDialog.DialogCode.Accepted


def main():
    """Función principal de la aplicación"""
    crear_carpetas()
    configurar_logging()
    load_store_config()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "cruzmedic.ico")

    print(f"[INFO] Icono cargado desde: {ICON_PATH}")
    print(f"[INFO] Archivo existe: {os.path.exists(ICON_PATH)}")

    QLocale.setDefault(QLocale(QLocale.Language.Spanish, QLocale.Country.Colombia))

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(ICON_PATH))

    try:
        crear_license_default()
    except Exception as e:
        logging.error(f"Error al crear licencia: {e}")

    if not validar_licencia():
        while True:
            result = mostrar_activacion()
            if not result:
                QMessageBox.critical(
                    None,
                    "Sistema Bloqueado",
                    "El sistema requiere activación para funcionar.\n\nEl programa se cerrará.",
                )
                sys.exit(1)
            elif validar_licencia():
                break

    # Detectar primera instalación
    from utils.store_config import config_exists

    if not config_exists():
        result = mostrar_config_inicial()
        if not result:
            QMessageBox.critical(
                None,
                "Configuración requerida",
                "Debe configurar los datos del negocio para continuar.",
            )
            sys.exit(1)

    # Recargar config recién guardada
    load_store_config()

    try:
        init_db()
    except Exception as e:
        logging.error(f"Error al inicializar base de datos: {e}")
        QMessageBox.critical(
            None, "Error", f"Error al inicializar la base de datos:\n{str(e)}"
        )
        sys.exit(1)

    session = get_session()

    try:
        service = CorteCajaService(session)
        service.abrir_caja()
    except Exception as e:
        logging.error(f"Error al abrir caja: {e}")
        QMessageBox.warning(
            None,
            "Aviso",
            "No se pudo abrir la caja automáticamente.\n"
            "Ve a 'Corte de Caja' y ábrela manualmente.",
        )

    window = MainWindow()
    window.setWindowIcon(QIcon(ICON_PATH))

    try:
        ventas_view = VentasView(session)
        productos_view = ProductosView(session)
        inventario_view = InventarioView(session)
        corte_view = CorteView(session)
        from ui.historial_view import HistorialView

        historial_view = HistorialView(session)

        ventas_view.sale_completed.connect(productos_view.recargar_productos)
        ventas_view.sale_completed.connect(inventario_view.recargar_inventario)
        ventas_view.sale_completed.connect(corte_view.cargar_estadisticas)

        window.add_view(ventas_view, "ventas")
        window.add_view(productos_view, "productos")
        window.add_view(inventario_view, "inventario")
        window.add_view(corte_view, "corte")
        window.add_view(historial_view, "historial")
    except Exception as e:
        logging.error(f"Error al crear vistas: {e}")
        QMessageBox.critical(None, "Error", f"Error al cargar las vistas:\n{str(e)}")
        sys.exit(1)

    window.switch_to_ventas()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error crítico no manejado: {e}")
        try:
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Error crítico",
                f"Ha ocurrido un error inesperado:\n\n{str(e)}\n\nRevise logs/app.log",
            )
        except:
            print(f"Error crítico: {e}")
        sys.exit(1)
