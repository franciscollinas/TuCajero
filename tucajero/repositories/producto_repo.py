from models.producto import Producto
from sqlalchemy import and_


class ProductoRepository:
    """Repositorio para acceso a datos de productos"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todos los productos activos"""
        return self.session.query(Producto).filter(Producto.activo == True).all()

    def get_by_id(self, producto_id):
        """Retorna un producto por su ID"""
        return self.session.query(Producto).filter(Producto.id == producto_id).first()

    def get_by_codigo(self, codigo):
        """Retorna un producto por su código de barras"""
        return (
            self.session.query(Producto)
            .filter(and_(Producto.codigo == codigo, Producto.activo == True))
            .first()
        )

    def existe_codigo(self, codigo, exclude_id=None):
        """Verifica si existe un código (excluyendo un ID opcional)"""
        query = self.session.query(Producto).filter(Producto.codigo == codigo)
        if exclude_id:
            query = query.filter(Producto.id != exclude_id)
        return query.filter(Producto.activo == True).first() is not None

    def create(
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
        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            precio=precio,
            costo=costo,
            stock=stock,
            aplica_iva=aplica_iva,
            categoria_id=categoria_id,
        )
        self.session.add(producto)
        self.session.commit()
        return producto

    def update(self, producto_id, **kwargs):
        """Actualiza un producto"""
        producto = self.get_by_id(producto_id)
        if producto:
            for key, value in kwargs.items():
                if key == "categoria_id" and value is None:
                    setattr(producto, key, None)
                elif value is not None:
                    setattr(producto, key, value)
            self.session.commit()
        return producto

    def delete(self, producto_id):
        """Elimina (desactiva) un producto"""
        producto = self.get_by_id(producto_id)
        if producto:
            producto.activo = False
            self.session.commit()
        return producto

    def update_stock(self, producto_id, cantidad):
        """Actualiza el stock de un producto"""
        producto = self.get_by_id(producto_id)
        if producto:
            producto.stock += cantidad
            self.session.commit()
        return producto

    def search(self, query):
        """Busca productos por código, nombre o parte del nombre"""
        search_term = f"%{query}%"
        return (
            self.session.query(Producto)
            .filter(
                and_(
                    Producto.activo == True,
                    (
                        Producto.codigo.ilike(search_term)
                        | Producto.nombre.ilike(search_term)
                    ),
                )
            )
            .all()
        )

    def search_por_nombre(self, nombre):
        """Busca productos por nombre parcial"""
        search_term = f"%{nombre}%"
        return (
            self.session.query(Producto)
            .filter(
                and_(
                    Producto.activo == True,
                    Producto.nombre.ilike(search_term),
                )
            )
            .all()
        )

    def search_por_categoria(self, categoria_id):
        """Busca productos por categoría"""
        return (
            self.session.query(Producto)
            .filter(
                and_(
                    Producto.activo == True,
                    Producto.categoria_id == categoria_id,
                )
            )
            .all()
        )
