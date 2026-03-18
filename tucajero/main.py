"""
TuCajero - Punto de Venta
Entry point principal de la aplicación.
"""

import sys
import logging
import os
import socket
import traceback
from logging.handlers import RotatingFileHandler

from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from PySide6.QtCore import QLocale

from config.database import (
    init_db,
    get_session,
    crear_carpetas,
    close_db,
    is_db_locked,
    cleanup_wal_files,
)
from utils.icon_helper import get_app_icon
from services.corte_service import CorteCajaService
from ui.main_window import MainWindow
from ui.ventas_view import VentasView
from ui.productos_view import ProductosView
from ui.inventario_view import InventarioView
from ui.corte_view import CorteView
from ui.activate_view import ActivationDialog
from security.license_manager import validar_licencia, crear_license_default
from utils.store_config import load_store_config, config_exists

_logger_initialized = False
_single_instance_socket = None


class SingleInstanceGuard:
    """Gestiona que solo haya una instancia de la app."""

    PORT = 19427

    @classmethod
    def check(cls):
        """Verifica si ya existe una instancia. Retorna mensaje de error o None."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", cls.PORT))
            sock.listen(1)
            sock.settimeout(0.5)
            global _single_instance_socket
            _single_instance_socket = sock
            return None
        except OSError:
            return "Ya hay una instancia de TuCajero en ejecución.\nCierre la aplicación antes de abrirla de nuevo."
        except Exception as e:
            return f"Error al verificar instancia: {e}"

    @classmethod
    def release(cls):
        """Libera el socket de instancia única."""
        global _single_instance_socket
        if _single_instance_socket:
            try:
                _single_instance_socket.close()
            except:
                pass
            _single_instance_socket = None


def setup_logging():
    """Configura el sistema de logging."""
    global _logger_initialized

    crear_carpetas()
    from config.database import get_log_file

    log_file = get_log_file()

    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )

    logging.basicConfig(
        handlers=[handler],
        level=logging.DEBUG,
        force=True,
    )

    _logger_initialized = True

    logging.info("=" * 60)
    logging.info("TuCajero - Inicio")
    logging.info(f"Python: {sys.version.split()[0]}")
    logging.info(f"Platform: {sys.platform}")
    logging.info("=" * 60)


def safe_exit(exit_code=0):
    """
    Salida segura de la aplicación.
    SIEMPRE ejecuta cleanup, incluso si hay errores.
    """
    logging.info("Iniciando salida segura...")

    try:
        SingleInstanceGuard.release()
    except Exception as e:
        logging.warning(f"Error al liberar socket: {e}")

    try:
        close_db()
    except Exception as e:
        logging.warning(f"Error al cerrar BD: {e}")

    if is_db_locked():
        logging.warning("BD aún bloqueada después de cierre")
        try:
            cleanup_wal_files()
        except:
            pass

    try:
        from utils.post_close_validator import validate_post_close

        success, issues = validate_post_close()
        if issues:
            logging.warning(f"Problemas post-cierre: {issues}")
    except Exception as e:
        logging.warning(f"Error en validación post-cierre: {e}")

    logging.info(f"Salida con código: {exit_code}")

    try:
        logging.shutdown()
    except:
        pass

    sys.exit(exit_code)


def show_error(title, message):
    """Muestra un mensaje de error al usuario."""
    try:
        QMessageBox.critical(None, title, message)
    except:
        print(f"ERROR: {title}\n{message}")


def main():
    """Función principal."""

    instance_error = SingleInstanceGuard.check()
    if instance_error:
        app = QApplication(sys.argv)
        QMessageBox.warning(None, "TuCajero", instance_error)
        sys.exit(1)

    try:
        setup_logging()
    except Exception as e:
        print(f"Error al configurar logging: {e}")
        traceback.print_exc()
        sys.exit(1)

    _app_icon = get_app_icon()

    QLocale.setDefault(QLocale(QLocale.Language.Spanish, QLocale.Country.Colombia))

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(_app_icon)
    app.setQuitOnLastWindowClosed(True)

    app.aboutToQuit.connect(lambda: logging.info("Qt aboutToQuit recibido"))

    try:
        crear_license_default()
    except Exception as e:
        logging.error(f"Error al crear licencia por defecto: {e}")

    if not validar_licencia():
        while True:
            dialog = ActivationDialog()
            if (
                dialog.exec() != QDialog.DialogCode.Accepted
                or not dialog.activation_success
            ):
                show_error(
                    "Sistema Bloqueado",
                    "El sistema requiere activación para funcionar.\n\nEl programa se cerrará.",
                )
                safe_exit(1)
            if validar_licencia():
                break

    if not config_exists():
        from ui.config_view import ConfigNegocioDialog

        dialog = ConfigNegocioDialog(primera_vez=True)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            show_error(
                "Configuración requerida",
                "Debe configurar los datos del negocio para continuar.",
            )
            safe_exit(1)

    load_store_config()

    try:
        init_db()
    except Exception as e:
        logging.error(f"Error al inicializar BD: {e}")
        show_error("Error", f"Error al inicializar la base de datos:\n{str(e)}")
        safe_exit(1)

    session = get_session()

    try:
        corte_service = CorteCajaService(session)
        corte_service.abrir_caja()
    except Exception as e:
        logging.error(f"Error al abrir caja: {e}")
        QMessageBox.warning(
            None,
            "Aviso",
            "No se pudo abrir la caja automáticamente.\n"
            "Ve a 'Corte de Caja' y ábrela manualmente.",
        )

    window = MainWindow()
    window.setWindowIcon(_app_icon)

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
        logging.error(traceback.format_exc())
        show_error("Error", f"Error al cargar las vistas:\n{str(e)}")
        safe_exit(1)

    window.switch_to_ventas()
    window.show()

    logging.info("MainWindow mostrada, iniciando event loop")

    exit_code = app.exec()

    logging.info(f"Event loop terminado con código: {exit_code}")
    safe_exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Error crítico no manejado: {e}")
        logging.critical(traceback.format_exc())
        show_error(
            "Error crítico",
            f"Ha ocurrido un error inesperado:\n\n{str(e)}\n\nRevise %LOCALAPPDATA%\\TuCajero\\logs\\app.log",
        )
        safe_exit(1)
