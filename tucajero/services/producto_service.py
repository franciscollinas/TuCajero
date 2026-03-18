"""
Servicios de productos y ventas.
Recibén sesión inyectada, no crean sesiones propias.
"""

from repositories.producto_repo import ProductoRepository
from repositories.venta_repo import VentaRepository, InventarioRepository
from models.producto import VentaItem


class ProductoService:
    def __init__(self, session):
        self.session = session
        self.repo = ProductoRepository(session)

    def validar_codigo(self, codigo, exclude_id=None):
        """Valida que el código no esté repetido."""
        if self.repo.existe_codigo(codigo, exclude_id):
            raise ValueError(f"El código '{codigo}' ya está en uso")

    def get_all_productos(self):
        return self.repo.get_all()

    def get_producto_by_id(self, producto_id):
        return self.repo.get_by_id(producto_id)

    def get_producto_by_codigo(self, codigo):
        return self.repo.get_by_codigo(codigo)

    def create_producto(self, codigo, nombre, precio, costo=0, stock=0):
        self.validar_codigo(codigo)
        return self.repo.create(codigo, nombre, precio, costo, stock)

    def update_producto(self, producto_id, **kwargs):
        if "codigo" in kwargs:
            self.validar_codigo(kwargs["codigo"], exclude_id=producto_id)
        return self.repo.update(producto_id, **kwargs)

    def delete_producto(self, producto_id):
        return self.repo.delete(producto_id)

    def search_productos(self, query):
        return self.repo.search(query)


class VentaService:
    def __init__(self, session):
        self.session = session
        self.venta_repo = VentaRepository(session)
        self.producto_repo = ProductoRepository(session)
        self.inventario_repo = InventarioRepository(session)
        self.corte_service = None

    def set_corte_service(self, corte_service):
        """Permite inyectar el servicio de corte para evitar importación circular."""
        self.corte_service = corte_service

    def registrar_venta(self, items, pagos=None, metodo_pago="efectivo"):
        """Registra una venta con método de pago."""
        if self.corte_service and not self.corte_service.esta_caja_abierta():
            raise Exception(
                "No se puede registrar la venta porque la caja está cerrada."
            )

        for item in items:
            producto = self.producto_repo.get_by_id(item["producto_id"])
            if producto.stock < item["cantidad"]:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

        venta = self.venta_repo.create_venta(items, pagos, metodo_pago)

        for item in items:
            self.producto_repo.update_stock(item["producto_id"], -item["cantidad"])
            self.inventario_repo.create_movimiento(
                item["producto_id"], "salida", item["cantidad"]
            )

        return venta

    def anular_venta(self, venta_id, motivo):
        """Anula una venta y restaura el stock."""
        if self.corte_service and not self.corte_service.esta_caja_abierta():
            raise Exception("No se puede anular: la caja está cerrada.")
        if not motivo or not motivo.strip():
            raise ValueError("Debe ingresar un motivo de anulación")

        venta = self.venta_repo.anular_venta(venta_id, motivo.strip())

        items = self.session.query(VentaItem).filter_by(venta_id=venta_id).all()
        for item in items:
            self.producto_repo.update_stock(item.producto_id, item.cantidad)
            self.inventario_repo.create_movimiento(
                item.producto_id, "entrada", item.cantidad
            )
        return venta

    def get_ventas_hoy(self):
        return self.venta_repo.get_ventas_hoy()

    def get_total_hoy(self):
        return self.venta_repo.get_total_hoy()

    def get_count_hoy(self):
        return self.venta_repo.get_count_hoy()


class InventarioService:
    def __init__(self, session):
        self.session = session
        self.producto_repo = ProductoRepository(session)
        self.inventario_repo = InventarioRepository(session)

    def entrada_inventario(self, producto_id, cantidad):
        """Registra entrada de inventario."""
        self.producto_repo.update_stock(producto_id, cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "entrada", cantidad)

    def salida_inventario(self, producto_id, cantidad):
        """Registra salida manual de inventario."""
        producto = self.producto_repo.get_by_id(producto_id)
        if producto.stock < cantidad:
            raise ValueError("Stock insuficiente")
        self.producto_repo.update_stock(producto_id, -cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "salida", cantidad)

    def descontar_por_venta(self, producto_id, cantidad):
        """Descuenta inventario por venta."""
        producto = self.producto_repo.get_by_id(producto_id)
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para {producto.nombre}")
        self.producto_repo.update_stock(producto_id, -cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "salida", cantidad)

    def obtener_stock(self, producto_id):
        producto = self.producto_repo.get_by_id(producto_id)
        return producto.stock if producto else 0

    def get_movimientos_producto(self, producto_id):
        return self.inventario_repo.get_movimientos_producto(producto_id)

    def get_all_productos(self):
        return self.producto_repo.get_all()
