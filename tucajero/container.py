"""
Contenedor de Dependency Injection para TuCajero POS
Proporciona instancias únicas de servicios y repositorios con lazy loading
"""

import threading
from tucajero.config.database import get_session


class Container:
    """
    Contenedor de dependencias para TuCajero POS.
    
    Proporciona registro lazy de servicios y repositorios, asegurando
    que cada instancia se crea solo la primera vez que se solicita.
    
    Thread-safe: utiliza locks para proteger el acceso a las instancias cacheadas.
    """

    _instance = None
    _lock = threading.Lock()
    
    # Cache de instancias
    _services = {}
    _repositories = {}
    _session_factory = None

    def __new__(cls, session_factory=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, session_factory=None):
        if self._initialized:
            return
        self._initialized = True
        if session_factory:
            self._session_factory = session_factory

    def get_session(self):
        """Obtiene una sesión de base de datos"""
        if self._session_factory:
            return self._session_factory()
        return get_session()

    # ==================== REPOSITORIOS ====================

    def get_producto_repository(self) -> "ProductoRepository":
        """Obtiene ProductoRepository (lazy loading)"""
        from tucajero.repositories.producto_repo import ProductoRepository
        
        if "producto_repo" not in self._repositories:
            self._repositories["producto_repo"] = ProductoRepository(self.get_session())
        return self._repositories["producto_repo"]

    def get_venta_repository(self) -> "VentaRepository":
        """Obtiene VentaRepository (lazy loading)"""
        from tucajero.repositories.venta_repo import VentaRepository
        
        if "venta_repo" not in self._repositories:
            self._repositories["venta_repo"] = VentaRepository(self.get_session())
        return self._repositories["venta_repo"]

    def get_cliente_repository(self) -> "ClienteRepository":
        """Obtiene ClienteRepository (lazy loading)"""
        from tucajero.repositories.cliente_repo import ClienteRepository
        
        if "cliente_repo" not in self._repositories:
            self._repositories["cliente_repo"] = ClienteRepository(self.get_session())
        return self._repositories["cliente_repo"]

    def get_categoria_repository(self) -> "CategoriaRepository":
        """Obtiene CategoriaRepository (lazy loading)"""
        from tucajero.repositories.categoria_repo import CategoriaRepository
        
        if "categoria_repo" not in self._repositories:
            self._repositories["categoria_repo"] = CategoriaRepository(self.get_session())
        return self._repositories["categoria_repo"]

    def get_inventario_repository(self) -> "InventarioRepository":
        """Obtiene InventarioRepository (lazy loading)"""
        from tucajero.repositories.venta_repo import InventarioRepository
        
        if "inventario_repo" not in self._repositories:
            self._repositories["inventario_repo"] = InventarioRepository(self.get_session())
        return self._repositories["inventario_repo"]

    def get_cajero_repository(self) -> "CajeroRepository":
        """Obtiene CajeroRepository (lazy loading)"""
        from tucajero.repositories.cajero_repo import CajeroRepository
        
        if "cajero_repo" not in self._repositories:
            self._repositories["cajero_repo"] = CajeroRepository(self.get_session())
        return self._repositories["cajero_repo"]

    def get_proveedor_repository(self) -> "ProveedorRepository":
        """Obtiene ProveedorRepository (lazy loading)"""
        from tucajero.repositories.proveedor_repo import ProveedorRepository
        
        if "proveedor_repo" not in self._repositories:
            self._repositories["proveedor_repo"] = ProveedorRepository(self.get_session())
        return self._repositories["proveedor_repo"]

    def get_cotizacion_repository(self) -> "CotizacionRepository":
        """Obtiene CotizacionRepository (lazy loading)"""
        from tucajero.repositories.cotizacion_repo import CotizacionRepository
        
        if "cotizacion_repo" not in self._repositories:
            self._repositories["cotizacion_repo"] = CotizacionRepository(self.get_session())
        return self._repositories["cotizacion_repo"]

    def get_corte_caja_repository(self) -> "CorteCajaRepository":
        """Obtiene CorteCajaRepository (lazy loading)"""
        from tucajero.repositories.corte_caja_repo import CorteCajaRepository
        
        if "corte_caja_repo" not in self._repositories:
            self._repositories["corte_caja_repo"] = CorteCajaRepository(self.get_session())
        return self._repositories["corte_caja_repo"]

    # ==================== SERVICIOS ====================

    def get_backup_service(self) -> "BackupService":
        """Obtiene BackupService (lazy loading)"""
        from tucajero.services.backup_service import BackupService
        
        if "backup_service" not in self._services:
            self._services["backup_service"] = BackupService()
        return self._services["backup_service"]

    def get_corte_caja_service(self) -> "CorteCajaService":
        """Obtiene CorteCajaService (lazy loading)"""
        from tucajero.services.corte_service import CorteCajaService
        
        if "corte_caja_service" not in self._services:
            self._services["corte_caja_service"] = CorteCajaService(
                self.get_session(),
                self.get_venta_repository(),
                self.get_backup_service()
            )
        return self._services["corte_caja_service"]

    def get_producto_service(self) -> "ProductoService":
        """Obtiene ProductoService (lazy loading)"""
        from tucajero.services.producto_service import ProductoService

        if "producto_service" not in self._services:
            self._services["producto_service"] = ProductoService(
                self.get_session(),
                self.get_producto_repository(),
                self.get_categoria_repository()
            )
        return self._services["producto_service"]

    def get_venta_service(self) -> "VentaService":
        """Obtiene VentaService (lazy loading)"""
        from tucajero.services.venta_service import VentaService
        
        if "venta_service" not in self._services:
            self._services["venta_service"] = VentaService(
                self.get_session(),
                self.get_venta_repository(),
                self.get_producto_repository(),
                self.get_inventario_repository(),
                self.get_corte_caja_service(),
                self.get_cliente_repository()
            )
        return self._services["venta_service"]

    def get_cliente_service(self) -> "ClienteService":
        """Obtiene ClienteService (lazy loading)"""
        from tucajero.services.cliente_service import ClienteService
        
        if "cliente_service" not in self._services:
            self._services["cliente_service"] = ClienteService(
                self.get_session(),
                self.get_cliente_repository()
            )
        return self._services["cliente_service"]

    def get_categoria_service(self) -> "CategoriaService":
        """Obtiene CategoriaService (lazy loading)"""
        from tucajero.services.categoria_service import CategoriaService
        
        if "categoria_service" not in self._services:
            self._services["categoria_service"] = CategoriaService(
                self.get_session(),
                self.get_categoria_repository()
            )
        return self._services["categoria_service"]

    def get_proveedor_service(self) -> "ProveedorService":
        """Obtiene ProveedorService (lazy loading)"""
        from tucajero.services.proveedor_service import ProveedorService
        
        if "proveedor_service" not in self._services:
            self._services["proveedor_service"] = ProveedorService(
                self.get_session(),
                self.get_proveedor_repository()
            )
        return self._services["proveedor_service"]

    def get_cajero_service(self) -> "CajeroService":
        """Obtiene CajeroService (lazy loading)"""
        from tucajero.services.cajero_service import CajeroService
        
        if "cajero_service" not in self._services:
            self._services["cajero_service"] = CajeroService(
                self.get_session(),
                self.get_cajero_repository()
            )
        return self._services["cajero_service"]

    def get_cotizacion_service(self) -> "CotizacionService":
        """Obtiene CotizacionService (lazy loading)"""
        from tucajero.services.cotizacion_service import CotizacionService
        
        if "cotizacion_service" not in self._services:
            self._services["cotizacion_service"] = CotizacionService(
                self.get_session(),
                self.get_cotizacion_repository(),
                self.get_cliente_repository(),
                self.get_producto_repository()
            )
        return self._services["cotizacion_service"]

    def get_orden_compra_service(self) -> "OrdenCompraService":
        """Obtiene OrdenCompraService (lazy loading)"""
        from tucajero.services.proveedor_service import OrdenCompraService
        
        if "orden_compra_service" not in self._services:
            self._services["orden_compra_service"] = OrdenCompraService(
                self.get_session(),
                self.get_proveedor_repository(),
                self.get_producto_repository()
            )
        return self._services["orden_compra_service"]

    def get_historial_service(self) -> "HistorialService":
        """Obtiene HistorialService (lazy loading)"""
        from tucajero.services.historial_service import HistorialService
        
        if "historial_service" not in self._services:
            self._services["historial_service"] = HistorialService(
                self.get_session()
            )
        return self._services["historial_service"]

    def get_fraccion_service(self) -> "FraccionService":
        """Obtiene FraccionService (lazy loading)"""
        from tucajero.services.fraccion_service import FraccionService

        if "fraccion_service" not in self._services:
            self._services["fraccion_service"] = FraccionService(
                self.get_session(),
                self.get_producto_repository(),
                self.get_inventario_repository()
            )
        return self._services["fraccion_service"]

    def get_inventario_service(self) -> "InventarioService":
        """Obtiene InventarioService (lazy loading)"""
        from tucajero.services.producto_service import InventarioService

        if "inventario_service" not in self._services:
            self._services["inventario_service"] = InventarioService(
                self.get_session(),
            )
        return self._services["inventario_service"]

    # ==================== UTILIDADES ====================

    def get_repository(self, name):
        """Obtiene un repositorio por nombre (método genérico)"""
        repos_map = {
            "producto": self.get_producto_repository,
            "venta": self.get_venta_repository,
            "cliente": self.get_cliente_repository,
            "categoria": self.get_categoria_repository,
            "inventario": self.get_inventario_repository,
            "cajero": self.get_cajero_repository,
            "proveedor": self.get_proveedor_repository,
            "cotizacion": self.get_cotizacion_repository,
            "corte_caja": self.get_corte_caja_repository,
        }

        if name not in repos_map:
            raise ValueError(f"Repositorio '{name}' no encontrado")

        return repos_map[name]()

    def get_service(self, name):
        """Obtiene un servicio por nombre (método genérico)"""
        services_map = {
            "producto": self.get_producto_service,
            "venta": self.get_venta_service,
            "cliente": self.get_cliente_service,
            "categoria": self.get_categoria_service,
            "proveedor": self.get_proveedor_service,
            "cajero": self.get_cajero_service,
            "cotizacion": self.get_cotizacion_service,
            "orden_compra": self.get_orden_compra_service,
            "corte_caja": self.get_corte_caja_service,
            "historial": self.get_historial_service,
            "fraccion": self.get_fraccion_service,
            "inventario": self.get_inventario_service,
            "backup": self.get_backup_service,
        }

        if name not in services_map:
            raise ValueError(f"Servicio '{name}' no encontrado")

        return services_map[name]()

    def clear(self):
        """Limpia todas las instancias cacheadas"""
        with self._lock:
            self._services.clear()
            self._repositories.clear()
            self._initialized = False

    def reset(self):
        """Resetea el container (útil para testing)"""
        self.clear()
        Container._instance = None


# Instancia global singleton
container = Container()
