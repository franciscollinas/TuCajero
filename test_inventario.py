import sys
import os
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("TEST DE INVENTARIO - TuCajeroPOS")
print("=" * 70)

try:
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    print("\n✅ QApplication creado")
    
    from tucajero.config.database import get_session, init_db
    init_db()
    session = get_session()
    print("✅ Sesión de BD obtenida")
    
    from tucajero.services.producto_service import InventarioService, ProductoService
    print("✅ InventarioService importado")
    
    inv_service = InventarioService(session)
    print(f"✅ InventarioService creado: {type(inv_service)}")
    
    from tucajero.ui.productos_view import ProductosView
    print("✅ ProductosView importado")
    
    view = ProductosView(session)
    print(f"✅ ProductosView creada: {type(view)}")
    
    view.show()
    print("✅ Vista mostrada")
    
    print("\n" + "=" * 70)
    print("EJECUTANDO... (cierra la ventana para terminar)")
    print("=" * 70)
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
    
    with open('error_inventario.log', 'w', encoding='utf-8') as f:
        f.write(traceback.format_exc())
    print(f"\n📄 Error guardado en: error_inventario.log")
