"""
TuCajero
Sistema simple de caja registradora para pequeños negocios.
"""

import sys
import os
import logging
import traceback
from logging.handlers import RotatingFileHandler
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Manejador global de excepciones no controladas"""
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    logging.critical("UNHANDLED EXCEPTION:\n" + error_msg)

    try:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error inesperado")
        msg.setText("Ocurrió un error inesperado.\nLa aplicación seguirá funcionando.")
        msg.setDetailedText(str(exc_value))
        msg.exec()
    except:
        pass


sys.excepthook = global_exception_handler
from config.database import init_db, get_session, crear_carpetas
from services.corte_service import CorteCajaService
from ui.main_window import MainWindow
from ui.dashboard_view import DashboardView
from ui.ventas_view import VentasView
from models.cliente import Cliente
from ui.activate_view import ActivationDialog
from security.license_manager import validar_licencia
from utils.store_config import load_store_config, is_setup_complete
from ui.setup_view import SetupDialog
from utils.theme import get_stylesheet


def configurar_logging():
    """Configura el logging global con rotación"""
    from utils.logging_config import setup_logging, get_logs_path

    log_path = setup_logging()
    logging.info(f"Logging inicializado en: {log_path}")


def main():
    """Función principal de la aplicación"""
    crear_carpetas()
    configurar_logging()
    load_store_config()

    from utils.backup import backup_semanal

    backup_semanal()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "tucajero.ico")

    # Iniciar aplicación Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())
    app.setWindowIcon(QIcon(ICON_PATH))

    # Validar licencia antes de abrir la app
    while not validar_licencia():
        dialog = ActivationDialog()
        dialog.exec()
        if not dialog.activation_success:
            sys.exit(0)
        # Si se activó con éxito, el bucle terminará en la siguiente iteración
        # ya que validar_licencia() ahora retornará True

    if not is_setup_complete():
        setup = SetupDialog()
        if setup.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)
        load_store_config()

    try:
        init_db()
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logging.error(f"Error al inicializar base de datos: {e}\n{error_detail}")
        QMessageBox.critical(
            None, "Error", f"Error al inicializar la base de datos:\n{str(e)}\n\n{error_detail}"
        )
        sys.exit(1)

    session = get_session()

    from services.cajero_service import CajeroService
    from models.cajero import Cajero

    cajero_service = CajeroService(session)
    cajero_service.crear_admin_default()

    from ui.login_cajero import LoginCajeroDialog

    login = LoginCajeroDialog(session)
    result = login.exec()
    if result != QDialog.DialogCode.Accepted:
        sys.exit(0)
    cajero_activo = login.cajero_seleccionado

    try:
        service = CorteCajaService(session)
        service.abrir_caja()
    except Exception as e:
        logging.error(f"Error al abrir caja: {e}")

    logging.info("Creando MainWindow...")
    window = MainWindow()
    window.session = session
    logging.info("MainWindow creado, configurando iconos...")
    window.setWindowIcon(QIcon(ICON_PATH))
    logging.info("Iconos configurados")

    dashboard_view = DashboardView(session)
    window.add_view(dashboard_view, "dashboard")

    ventas_view = VentasView(session, cajero_activo=cajero_activo)
    window.add_view(ventas_view, "ventas")
    ventas_view.sale_completed.connect(dashboard_view.refresh)

    try:
        from ui.setup_view import SetupView

        config_view = SetupView(session, parent=window)
        window.add_view(config_view, "setup")
    except Exception as e:
        logging.error(f"Error al crear vista de config: {e}")

    window.set_cajero_activo(cajero_activo)
    window.switch_view_by_name("dashboard")

    window.switch_to_ventas()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        err_msg = f"Error crítico: {e}\n{traceback.format_exc()}"
        # Write to both log file and debug file
        try:
            logging.error(err_msg)
        except:
            pass
        try:
            debug_file = os.path.join(
                os.environ.get("LOCALAPPDATA", "."), "TuCajero", "debug_error.txt"
            )
            os.makedirs(os.path.dirname(debug_file), exist_ok=True)
            with open(debug_file, "w") as f:
                f.write(err_msg)
        except:
            pass
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox

            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Error crítico",
                f"Ha ocurrido un error inesperado:\n\n{str(e)}\n\nRevise logs/app.log",
            )
        except:
            print(f"Error crítico: {e}")
        sys.exit(1)
