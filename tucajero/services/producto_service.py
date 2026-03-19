from repositories.producto_repo import ProductoRepository
from repositories.venta_repo import VentaRepository, InventarioRepository
from models.producto import Categoria


class ProductoService:
    """Servicio para lógica de negocio de productos"""

    def __init__(self, session):
        self.session = session
        self.repo = ProductoRepository(session)

    def validar_codigo(self, codigo, exclude_id=None):
        """Valida que el código no esté repetido"""
        if self.repo.existe_codigo(codigo, exclude_id):
            raise ValueError(f"El código '{codigo}' ya está en uso")

    def get_all_productos(self):
        """Retorna todos los productos"""
        return self.repo.get_all()

    def get_producto_by_id(self, producto_id):
        """Retorna un producto por ID"""
        return self.repo.get_by_id(producto_id)

    def get_producto_by_codigo(self, codigo):
        """Retorna un producto por código"""
        return self.repo.get_by_codigo(codigo)

    def get_producto_by_nombre(self, nombre):
        """Busca productos por nombre parcial"""
        return self.repo.search_por_nombre(nombre)

    def create_producto(
        self,
        codigo,
        nombre,
        precio,
        costo=0,
        stock=0,
        aplica_iva=True,
        categoria_id=None,
    ):
        """Crea un nuevo producto"""
        self.validar_codigo(codigo)
        return self.repo.create(
            codigo, nombre, precio, costo, stock, aplica_iva, categoria_id
        )

    def update_producto(self, producto_id, **kwargs):
        """Actualiza un producto"""
        if "codigo" in kwargs:
            self.validar_codigo(kwargs["codigo"], exclude_id=producto_id)
        return self.repo.update(producto_id, **kwargs)

    def delete_producto(self, producto_id):
        """Elimina un producto"""
        return self.repo.delete(producto_id)

    def search_productos(self, query):
        """Busca productos"""
        return self.repo.search(query)


class CategoriaService:
    """Servicio para gestión de categorías"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todas las categorías ordenadas"""
        return self.session.query(Categoria).order_by(Categoria.nombre).all()

    def get_by_id(self, categoria_id):
        """Retorna una categoría por ID"""
        return (
            self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        )

    def create(self, nombre, descripcion=""):
        """Crea una nueva categoría"""
        if self.session.query(Categoria).filter(Categoria.nombre == nombre).first():
            raise ValueError(f"La categoría '{nombre}' ya existe")
        c = Categoria(nombre=nombre, descripcion=descripcion)
        self.session.add(c)
        self.session.commit()
        return c

    def update(self, categoria_id, nombre, descripcion=""):
        """Actualiza una categoría"""
        c = self.get_by_id(categoria_id)
        if not c:
            raise ValueError("Categoría no encontrada")
        if nombre != c.nombre:
            existente = (
                self.session.query(Categoria).filter(Categoria.nombre == nombre).first()
            )
            if existente:
                raise ValueError(f"La categoría '{nombre}' ya existe")
        c.nombre = nombre
        c.descripcion = descripcion
        self.session.commit()
        return c

    def delete(self, categoria_id):
        """Elimina una categoría (solo si no tiene productos)"""
        c = self.get_by_id(categoria_id)
        if not c:
            raise ValueError("Categoría no encontrada")
        if c.productos and len([p for p in c.productos if p.activo]) > 0:
            raise ValueError("No se puede eliminar: hay productos en esta categoría")
        self.session.delete(c)
        self.session.commit()


class VentaService:
    """Servicio para lógica de negocio de ventas"""

    def __init__(self, session):
        self.session = session
        self.venta_repo = VentaRepository(session)
        self.producto_repo = ProductoRepository(session)
        self.inventario_repo = InventarioRepository(session)
        from services.corte_service import CorteCajaService

        self.corte_service = CorteCajaService(session)

    def registrar_venta(self, items, metodo_pago=None):
        """Registra una venta y descuenta inventario"""
        if not self.corte_service.esta_caja_abierta():
            raise Exception(
                "No se puede registrar la venta porque la caja está cerrada."
            )

        for item in items:
            producto = self.producto_repo.get_by_id(item["producto_id"])
            if producto.stock < item["cantidad"]:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

        venta = self.venta_repo.create_venta(items, metodo_pago=metodo_pago)

        for item in items:
            self.producto_repo.update_stock(item["producto_id"], -item["cantidad"])
            self.inventario_repo.create_movimiento(
                item["producto_id"], "salida", item["cantidad"]
            )

        return venta

    def anular_venta(self, venta_id):
        """Anula una venta y restaura el stock"""
        venta = self.venta_repo.get_venta_by_id(venta_id)
        if not venta:
            raise ValueError(f"Venta #{venta_id} no encontrada")
        if venta.anulada:
            raise ValueError(f"Venta #{venta_id} ya está anulada")

        for item in venta.items:
            self.producto_repo.update_stock(item.producto_id, item.cantidad)
            self.inventario_repo.create_movimiento(
                item.producto_id, "entrada", item.cantidad
            )

        self.venta_repo.anular_venta(venta_id)
        return venta

    def get_ventas_hoy(self):
        """Retorna las ventas de hoy"""
        return self.venta_repo.get_ventas_hoy()

    def get_total_hoy(self):
        """Retorna el total de ventas de hoy"""
        return self.venta_repo.get_total_hoy()

    def get_count_hoy(self):
        """Retorna el número de ventas de hoy"""
        return self.venta_repo.get_count_hoy()


class InventarioService:
    """Servicio para lógica de negocio de inventario"""

    def __init__(self, session):
        self.session = session
        self.producto_repo = ProductoRepository(session)
        self.inventario_repo = InventarioRepository(session)

    def entrada_inventario(self, producto_id, cantidad):
        """Registra entrada de inventario"""
        self.producto_repo.update_stock(producto_id, cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "entrada", cantidad)

    def salida_inventario(self, producto_id, cantidad):
        """Registra salida manual de inventario"""
        producto = self.producto_repo.get_by_id(producto_id)
        if producto.stock < cantidad:
            raise ValueError("Stock insuficiente")
        self.producto_repo.update_stock(producto_id, -cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "salida", cantidad)

    def descontar_por_venta(self, producto_id, cantidad):
        """Descuenta inventario por venta (usado desde ventas)"""
        producto = self.producto_repo.get_by_id(producto_id)
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para {producto.nombre}")
        self.producto_repo.update_stock(producto_id, -cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "salida", cantidad)

    def obtener_stock(self, producto_id):
        """Obtiene el stock actual de un producto"""
        producto = self.producto_repo.get_by_id(producto_id)
        return producto.stock if producto else 0

    def get_movimientos_producto(self, producto_id):
        """Retorna los movimientos de un producto"""
        return self.inventario_repo.get_movimientos_producto(producto_id)

    def get_all_productos(self):
        """Retorna todos los productos con su stock"""
        return self.producto_repo.get_all()
