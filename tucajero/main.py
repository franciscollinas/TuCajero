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
        # SEC-012 FIX: Generate a short reference ID for the error
        import uuid
        error_ref = uuid.uuid4().hex[:8]
        logging.critical(f"[{error_ref}] Full error context logged above")

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error inesperado")
        msg.setText(
            "Ocurrio un error inesperado.\n"
            "La aplicacion seguira funcionando.\n\n"
            f"Referencia: {error_ref}\n"
            "Contacte a soporte tecnico con este codigo."
        )
        # SEC-012 FIX: Do NOT show stack traces to users — log only
        # msg.setDetailedText(str(exc_value))  # REMOVED for security
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
    except Exception as e:
        # SEC-004 FIX: Log the error instead of silently swallowing it
        logging.error(f"Error in global_exception_handler QMessageBox display: {e}", exc_info=True)


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

    # SEC-008: Force PIN setup if this is the first login with default admin
    if cajero_activo and getattr(cajero_activo, 'pin_must_be_set', False):
        try:
            from tucajero.app.ui.views.auth.pin_setup_dialog import PinSetupDialog

            pin_dialog = PinSetupDialog(session, cajero_activo)
            if pin_dialog.exec():
                nuevo_pin = pin_dialog.get_pin()
                if nuevo_pin:
                    CajeroService(session).cambiar_pin(cajero_activo.id, nuevo_pin)
                    cajero_activo.pin_must_be_set = False
                    session.commit()
            else:
                sys.exit(0)
        except Exception as e:
            logging.error(f"SEC-008: PIN setup dialog error: {e}")
            # Continue with app — user can change PIN manually in settings

    # Registrar login en auditoría
    try:
        from tucajero.services.audit_service import AuditService
        audit = AuditService(session)
        audit.registrar(
            AuditService.LOGIN,
            f"Inicio de sesión: {cajero_activo.nombre}",
            usuario_id=cajero_activo.id,
        )
    except Exception as e:
        logging.warning(f"No se pudo registrar auditoría de login: {e}")

    try:
        service = CorteCajaService(session)
        service.abrir_caja()
    except Exception as e:
        logging.error(f"Error al abrir caja: {e}")

    logging.info("Creando MainWindow...")
    try:
        window = MainWindow()
        window.session = session
        logging.info("MainWindow creado, configurando iconos...")
        window.setWindowIcon(QIcon(ICON_PATH))
        logging.info("Iconos configurados")

        # Dashboard
        logging.info("Creando Dashboard...")
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        dashboard_view = DashboardView(session)
        window.add_view(dashboard_view, "dashboard")
        logging.info("Dashboard creado OK")

        # Ventas
        logging.info("Creando Ventas...")
        ventas_view = VentasView(session, cajero_activo=cajero_activo)
        window.add_view(ventas_view, "ventas")
        ventas_view.sale_completed.connect(dashboard_view.refresh)
        logging.info("Ventas creado OK")

        # Config
        logging.info("Creando Config...")
        try:
            from tucajero.ui.setup_view import SetupView
            config_view = SetupView(session, parent=window)
            window.add_view(config_view, "setup")
            logging.info("Config creado OK")
        except Exception as e:
            logging.error(f"Error al crear vista de config: {e}", exc_info=True)

        # Productos
        logging.info("Creando Productos...")
        try:
            from tucajero.ui.productos_view import ProductosView
            prod_view = ProductosView(session, parent=window)
            window.add_view(prod_view, "productos")
            logging.info("Productos creado OK")
        except Exception as e:
            logging.error(f"Error al crear vista de productos: {e}", exc_info=True)

        # Clientes
        logging.info("Creando Clientes...")
        try:
            from tucajero.ui.clientes_view import ClientesView
            cli_view = ClientesView(session, parent=window)
            window.add_view(cli_view, "clientes")
            logging.info("Clientes creado OK")
        except Exception as e:
            logging.error(f"Error al crear vista de clientes: {e}", exc_info=True)

        # Cotizaciones
        logging.info("Creando Cotizaciones...")
        try:
            from tucajero.ui.cotizaciones_view import CotizacionesView
            cot_view = CotizacionesView(session, parent=window)
            window.add_view(cot_view, "cotizaciones")
            logging.info("Cotizaciones creado OK")
        except Exception as e:
            logging.error(f"Error al crear vista de cotizaciones: {e}", exc_info=True)

        # Corte
        logging.info("Creando Corte...")
        try:
            from tucajero.ui.corte_view import CorteView
            corte_view = CorteView(session, cajero_activo=cajero_activo, parent=window)
            window.add_view(corte_view, "corte")
            logging.info("Corte creado OK")
        except Exception as e:
            logging.error(f"Error al crear vista de corte: {e}", exc_info=True)

        # Historial
        logging.info("Creando Historial...")
        try:
            from tucajero.ui.historial_view import HistorialView
            hist_view = HistorialView(session, parent=window)
            window.add_view(hist_view, "historial")
            logging.info("Historial creado OK")
        except Exception as e:
            logging.error(f"Error al crear vista de historial: {e}", exc_info=True)

        # Proveedores
        logging.info("Creando Proveedores...")
        try:
            from tucajero.ui.proveedores_view import ProveedoresView
            prov_view = ProveedoresView(session, parent=window)
            window.add_view(prov_view, "proveedores")
            logging.info("Proveedores creado OK")
        except Exception as e:
            logging.error(f"Error al crear vista de proveedores: {e}", exc_info=True)

        # Cajeros
        logging.info("Creando Cajeros...")
        try:
            from tucajero.ui.cajeros_view import CajerosView
            caj_view = CajerosView(session, parent=window)
            window.add_view(caj_view, "cajeros")
            logging.info("Cajeros creado OK")
        except Exception as e:
            logging.error(f"Error al crear vista de cajeros: {e}", exc_info=True)

        window.set_cajero_activo(cajero_activo)
        logging.info("Cajero activo configurado")
        window.switch_view_by_name("dashboard")
        logging.info("Vista dashboard activada")
        window.show()
        logging.info("MainWindow shown!")
        sys.exit(app.exec())
    except Exception as e:
        logging.critical(f"FATAL ERROR en main: {e}", exc_info=True)
        import traceback
        error_msg = traceback.format_exc()
        
        # SEC-012 FIX: Generate error reference ID for support tracking
        import uuid
        error_ref = uuid.uuid4().hex[:8]
        logging.critical(f"[{error_ref}] Full error details logged above")
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error fatal")
        msg.setText(
            f"Error al iniciar la aplicacion.\n\n"
            f"Referencia: {error_ref}\n"
            f"Contacte a soporte tecnico con este codigo."
        )
        # SEC-012 FIX: Do NOT expose stack trace to users
        # msg.setDetailedText(error_msg)  # REMOVED - stack traces logged only
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; }
            QMessageBox QLabel { color: #0F172A; background: transparent; }
            QPushButton { background-color: #2563EB; color: #FFFFFF; border: none; border-radius: 6px; padding: 8px 16px; font-weight: 600; }
        """)
        msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback

        err_msg = f"Error critico: {e}\n{traceback.format_exc()}"
        # Write to both log file and debug file
        try:
            logging.error(err_msg)
        except (OSError, IOError, ValueError) as log_err:
            # SEC-004 FIX: If logging fails, at least we tried — no silent failures
            print(f"FALLBACK: Could not log error: {log_err}")
        try:
            debug_file = os.path.join(
                os.environ.get("LOCALAPPDATA", "."), "TuCajero", "debug_error.txt"
            )
            os.makedirs(os.path.dirname(debug_file), exist_ok=True)
            with open(debug_file, "w") as f:
                f.write(err_msg)
        except (OSError, IOError, PermissionError) as file_err:
            # SEC-004 FIX: Log file write failures
            print(f"FALLBACK: Could not write debug file: {file_err}")
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox

            # SEC-012 FIX: Show generic error message, no stack traces to users
            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Error critico",
                "Ha ocurrido un error inesperado.\n\n"
                "Contacte a soporte tecnico con la informacion en el archivo de logs.",
            )
        except Exception as ui_err:
            print(f"Error critico (fallback): {e}")
            print(f"UI error: {ui_err}")
        sys.exit(1)
