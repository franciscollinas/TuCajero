import sys
import os
import traceback

# Agregar tucajero al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tucajero'))

print("=" * 70)
print("TUCAJERO - DEBUG DE INICIO")
print("=" * 70)

try:
    print("\n[1/7] Creando carpetas...")
    from config.database import crear_carpetas
    crear_carpetas()
    print("      OK")
    
    print("\n[2/7] Configurando logging...")
    from utils.logging_config import setup_logging
    log_path = setup_logging()
    print(f"      OK - Logs en: {log_path}")
    
    print("\n[3/7] Cargando configuración...")
    from utils.store_config import load_store_config
    load_store_config()
    print("      OK")
    
    print("\n[4/7] Inicializando BD...")
    from config.database import init_db
    init_db()
    print("      OK")
    
    print("\n[5/7] Obteniendo sesión...")
    from config.database import get_session
    session = get_session()
    print("      OK")
    
    print("\n[6/7] Creando cajero admin...")
    from services.cajero_service import CajeroService
    cajero_service = CajeroService(session)
    cajero_service.crear_admin_default()
    print("      OK")
    
    print("\n[7/7] Abriendo caja...")
    from services.corte_service import CorteCajaService
    service = CorteCajaService(session)
    service.abrir_caja()
    print("      OK")
    
    print("\n" + "=" * 70)
    print("¡TODO EXITOSO! La aplicación está lista para iniciar.")
    print("=" * 70)
    print("\nEjecutando GUI...")
    
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    from utils.theme import get_stylesheet
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())
    
    window = MainWindow()
    window.session = session
    window.show()
    
    sys.exit(app.exec())
    
except Exception as e:
    print("\n" + "=" * 70)
    print("ERROR CRÍTICO")
    print("=" * 70)
    print(f"\nError: {e}")
    print(f"\nTraceback completo:\n")
    traceback.print_exc()
    print("\n" + "=" * 70)
    input("\nPresiona Enter para salir...")
    sys.exit(1)
