"""
TuCajero
Sistema simple de caja registradora para pequeños negocios.
"""

import sys
import os

# Agregar el directorio base al PYTHONPATH para que funcione el EXE
if getattr(sys, 'frozen', False):
    # Si se ejecuta como EXE compilado
    application_path = os.path.dirname(sys.executable)
    sys.path.insert(0, application_path)
else:
    # Si se ejecuta como script Python
    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, application_path)

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
        # Override global dark styles for this dialog
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QMessageBox QLabel {
                color: #0F172A;
                background: transparent;
            }
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton#qt_msgbox_detailsbutton {
                background-color: #E2E8F0;
                color: #0F172A;
            }
        """)
        msg.exec()
    except:
        pass


sys.excepthook = global_exception_handler
from tucajero.config.database import init_db, get_session, crear_carpetas
from tucajero.services.corte_service import CorteCajaService
from tucajero.ui.main_window import MainWindow
from tucajero.ui.ventas_view import VentasView
from tucajero.models.cliente import Cliente
from tucajero.ui.activate_view import ActivationDialog
from tucajero.security.license_manager import validar_licencia
from tucajero.utils.store_config import load_store_config, is_setup_complete
from tucajero.ui.setup_view import SetupDialog
from tucajero.app.ui.theme.theme import app_style


def configurar_logging():
    """Configura el logging global con rotación"""
    from tucajero.utils.logging_config import setup_logging, get_logs_path

    log_path = setup_logging()
    logging.info(f"Logging inicializado en: {log_path}")


def main():
    """Función principal de la aplicación"""
    # Inicializar BD primero para evitar conflictos de imports de modelos
    try:
        init_db()
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logging.error(f"Error al inicializar BD: {e}\n{error_detail}")
        QMessageBox.critical(None, "Error", f"Error en BD:\n{e}\n\n{error_detail}")
        sys.exit(1)

    crear_carpetas()
    configurar_logging()
    load_store_config()

    from tucajero.utils.backup import backup_semanal

    backup_semanal()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "tucajero.ico")

    # Iniciar aplicación Qt
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(app_style())  # Tema claro global
    app.setWindowIcon(QIcon(ICON_PATH))

    # Validar licencia antes de abrir la app
    while not validar_licencia():
        dialog = ActivationDialog()
        dialog.exec()
        if not dialog.activation_success:
            sys.exit(0)

    if not is_setup_complete():
        setup = SetupDialog()
        if setup.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)
        load_store_config()

    session = get_session()

    from tucajero.services.cajero_service import CajeroService
    from tucajero.models.cajero import Cajero

    cajero_service = CajeroService(session)
    cajero_service.crear_admin_default()

    from tucajero.ui.login_view import LoginView

    login = LoginView(session)
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

    # Nuevo dashboard estilo SaaS
    from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView

    dashboard_view = DashboardView(session)
    window.add_view(dashboard_view, "dashboard")

    ventas_view = VentasView(session, cajero_activo=cajero_activo)
    window.add_view(ventas_view, "ventas")
    ventas_view.sale_completed.connect(dashboard_view.refresh)

    try:
        from tucajero.ui.setup_view import SetupView

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
