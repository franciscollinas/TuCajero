# TuCajero - Código Completo

## Estructura de Archivos

Total: **58 archivos Python**

---

## tucajero/main.py
Punto de entrada de la aplicación.

---

## tucajero/config/app_config.py
Constantes de la aplicación (nombre, versión).

---

## tucajero/config/database.py
Configuración de SQLite, engine, sesión, WAL mode, retry, close_db.

---

## tucajero/models/producto.py
Producto, Categoria (modelos SQLAlchemy).

---

## tucajero/models/cliente.py
Cliente (modelo SQLAlchemy).

---

## tucajero/models/cajero.py
Cajero (modelo SQLAlchemy).

---

## tucajero/models/cotizacion.py
Cotizacion, CotizacionItem (modelos SQLAlchemy).

---

## tucajero/models/proveedor.py
Proveedor, OrdenCompra, OrdenCompraItem (modelos SQLAlchemy).

---

## tucajero/repositories/cliente_repo.py
ClienteRepository - acceso a datos de clientes.

---

## tucajero/repositories/producto_repo.py
ProductoRepository - acceso a datos de productos con rollback seguro.

---

## tucajero/repositories/venta_repo.py
VentaRepository, InventarioRepository - acceso a datos de ventas e inventario.

---

## tucajero/security/license_manager.py
Sistema de licencias y activación por Machine ID.

---

## tucajero/services/cajero_service.py
CajeroService - lógica de cajeros con verificación de PIN.

---

## tucajero/services/categoria_service.py
CategoriaService - lógica de categorías.

---

## tucajero/services/cliente_service.py
ClienteService - lógica de clientes.

---

## tucajero/services/corte_service.py
CorteCajaService - lógica de corte de caja.

---

## tucajero/services/cotizacion_service.py
CotizacionService - lógica de cotizaciones.

---

## tucajero/services/fraccion_service.py
FraccionService - lógica de productos fraccionados.

---

## tucajero/services/historial_service.py
HistorialService - lógica del historial de ventas.

---

## tucajero/services/producto_service.py
ProductoService - lógica de productos, stock bajo, crítico.

---

## tucajero/services/proveedor_service.py
ProveedorService - lógica de proveedores.

---

## tucajero/ui/about_view.py
Vista "Acerca de".

---

## tucajero/ui/activate_view.py
Vista de activación de licencia con manejo de errores.

---

## tucajero/ui/buscador_productos.py
Diálogo para buscar productos.

---

## tucajero/ui/cajeros_view.py
Vista de gestión de cajeros.

---

## tucajero/ui/clientes_view.py
Vista de gestión de clientes.

---

## tucajero/ui/config_view.py
Vista de configuración de tienda.

---

## tucajero/ui/corte_view.py
Vista de corte de caja con formato 12h.

---

## tucajero/ui/cotizaciones_view.py
Vista de cotizaciones.

---

## tucajero/ui/dashboard_view.py
Panel de control/dashboard con gráficos y acciones rápidas.

---

## tucajero/ui/descuento_dialog.py
Diálogo para aplicar descuentos.

---

## tucajero/ui/historial_view.py
Vista de historial de ventas.

---

## tucajero/ui/inventario_view.py
Vista de inventario con búsqueda y alertas.

---

## tucajero/ui/login_cajero.py
Diálogo de login de cajeros con try/except.

---

## tucajero/ui/main_window.py
Ventana principal con navegación lazy loading.

---

## tucajero/ui/productos_view.py
Vista de gestión de productos.

---

## tucajero/ui/proveedores_view.py
Vista de gestión de proveedores.

---

## tucajero/ui/selector_cliente.py
Diálogo para seleccionar cliente.

---

## tucajero/ui/setup_view.py
Vista de configuración inicial y del sistema.

---

## tucajero/ui/ventas_view.py
Vista de ventas (POS principal) con клиент/carrito.

---

## tucajero/ui/chart_widget.py (NUEVO)
Widget de gráficos matplotlib con fallback.

---

## tucajero/utils/backup.py
Funciones de backup: manual, semanal, restaurar, exportar, limpiar.

---

## tucajero/utils/data_manager.py
Gestor de datos (exportación/importación).

---

## tucajero/utils/error_handler.py
Decorador @safe_slot para manejo de errores en UI.

---

## tucajero/utils/excel_exporter.py
Exportación a Excel con formato 12h.

---

## tucajero/utils/factura_diaria.py
Generación de facturas PDF (reportlab).

---

## tucajero/utils/formato.py
Funciones de formato de moneda.

---

## tucajero/utils/importador.py
Importador de productos desde Excel/CSV.

---

## tucajero/utils/impresora.py
Impresión ESC/POS (USB, red, serial).

---

## tucajero/utils/logging_config.py (NUEVO)
Configuración de logging para producción: %LOCALAPPDATA%\TuCajero\logs\

---

## tucajero/utils/store_config.py
Carga y guardado de configuración de tienda.

---

## tucajero/utils/theme.py
Temas y estilos de la UI: btn_primary, btn_secondary, btn_danger, btn_success.

---

## tucajero/utils/ticket.py
Generador de tickets con formato 12h.

---

## tucajero/migrar_iva.py
Script de migración de IVA.

---

## tucajero/verificar_iva.py
Script de verificación de IVA.

---

## tucajero/tools/license_generator.py
Generador de licencias.