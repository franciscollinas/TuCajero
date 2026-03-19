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
from config.database import init_db, get_session, crear_carpetas
from services.corte_service import CorteCajaService
from ui.main_window import MainWindow
from ui.ventas_view import VentasView
from ui.productos_view import ProductosView
from ui.inventario_view import InventarioView
from ui.corte_view import CorteView
from ui.historial_view import HistorialView
from ui.clientes_view import ClientesView
from ui.cotizaciones_view import CotizacionesView
from ui.proveedores_view import ProveedoresView
from models.cliente import Cliente
from ui.activate_view import ActivationDialog
from security.license_manager import validar_licencia, crear_license_default
from utils.store_config import load_store_config, is_setup_complete
from ui.setup_view import SetupDialog


def configurar_logging():
    """Configura el logging global con rotación"""
    from config.database import get_log_file, crear_carpetas

    crear_carpetas()
    log_file = get_log_file()

    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)

    logging.basicConfig(
        handlers=[handler],
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )


def mostrar_activacion():
    """Muestra la ventana de activación"""
    dialog = ActivationDialog()
    return dialog.exec() == QDialog.DialogCode.Accepted and dialog.activation_success


def main():
    """Función principal de la aplicación"""
    crear_carpetas()
    configurar_logging()
    load_store_config()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "tucajero.ico")

    print(f"[INFO] Icono cargado desde: {ICON_PATH}")
    print(f"[INFO] Archivo existe: {os.path.exists(ICON_PATH)}")

    try:
        crear_license_default()
    except Exception as e:
        logging.error(f"Error al crear licencia: {e}")

    if not validar_licencia():
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setWindowIcon(QIcon(ICON_PATH))

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
    else:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setWindowIcon(QIcon(ICON_PATH))

    if not is_setup_complete():
        setup = SetupDialog()
        if setup.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)
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

    from services.cajero_service import CajeroService
    from models.cajero import Cajero

    cajero_service = CajeroService(session)
    cajero_service.crear_admin_default()

    from ui.login_cajero import LoginCajeroDialog

    login = LoginCajeroDialog(session)
    if login.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)
    cajero_activo = login.cajero_seleccionado

    try:
        service = CorteCajaService(session)
        service.abrir_caja()
    except Exception as e:
        logging.error(f"Error al abrir caja: {e}")

    window = MainWindow()
    window.setWindowIcon(QIcon(ICON_PATH))

    try:
        ventas_view = VentasView(session, cajero_activo=cajero_activo)
        productos_view = ProductosView(session)
        inventario_view = InventarioView(session)
        corte_view = CorteView(session, cajero_activo=cajero_activo)
        historial_view = HistorialView(session)

        ventas_view.sale_completed.connect(productos_view.recargar_productos)
        ventas_view.sale_completed.connect(inventario_view.recargar_inventario)
        ventas_view.sale_completed.connect(corte_view.cargar_estadisticas)

        try:
            from services.producto_service import ProductoService

            ps = ProductoService(session)
            alertas = len(ps.get_productos_stock_bajo()) + len(
                ps.get_productos_stock_critico()
            )
            if alertas > 0:
                window.actualizar_badge_inventario(alertas)
        except Exception as e:
            logging.error(f"Error verificando stock bajo: {e}")

        ventas_view.sale_completed.connect(
            lambda: window.actualizar_badge_inventario(
                len(ProductoService(session).get_productos_stock_bajo())
                + len(ProductoService(session).get_productos_stock_critico())
            )
        )

        window.add_view(ventas_view, "ventas")
        window.add_view(productos_view, "productos")
        window.add_view(inventario_view, "inventario")
        window.add_view(corte_view, "corte")
        window.add_view(historial_view, "historial")

        clientes_view = ClientesView(session)
        window.add_view(clientes_view, "clientes")

        cotizaciones_view = CotizacionesView(session)
        window.add_view(cotizaciones_view, "cotizaciones")

        ventas_view.cotizacion_creada.connect(cotizaciones_view.cargar_cotizaciones)
        cotizaciones_view.cargar_en_ventas.connect(
            ventas_view.cargar_carrito_desde_cotizacion
        )

        if cajero_activo.rol == "admin":
            from ui.cajeros_view import CajerosView

            cajeros_view = CajerosView(session)
            window.add_view(cajeros_view, "cajeros")

        proveedores_view = ProveedoresView(session)
        window.add_view(proveedores_view, "proveedores")

        window.set_cajero_activo(cajero_activo)

        ventas_view.sale_completed.connect(clientes_view.cargar_clientes)

        try:
            from ui.setup_view import SetupView

            config_view = SetupView(session, parent=window)
            window.add_view(config_view, "config")
        except Exception as e:
            logging.error(f"Error al crear vista de config: {e}")

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
