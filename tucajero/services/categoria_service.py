from tucajero.models.producto import Categoria, Producto
from sqlalchemy.exc import IntegrityError

COLORES_DEFAULT = [
    "#3498db",
    "#27ae60",
    "#e67e22",
    "#8e44ad",
    "#e74c3c",
    "#16a085",
    "#d35400",
    "#2980b9",
    "#1abc9c",
    "#f39c12",
]


class CategoriaService:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Categoria).order_by(Categoria.nombre.asc()).all()

    def crear(self, nombre, color=None):
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre de la categoría es obligatorio")
        if not color:
            total = self.session.query(Categoria).count()
            color = COLORES_DEFAULT[total % len(COLORES_DEFAULT)]
        cat = Categoria(nombre=nombre, color=color)
        self.session.add(cat)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise ValueError(f"La categoría '{nombre}' ya existe")
        return cat

    def renombrar(self, categoria_id, nuevo_nombre):
        cat = self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        if not cat:
            raise ValueError("Categoría no encontrada")
        cat.nombre = nuevo_nombre.strip()
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise ValueError(f"Ya existe una categoría con ese nombre")
        return cat

    def eliminar(self, categoria_id):
        cat = self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        if cat:
            self.session.delete(cat)
            self.session.commit()

    def asignar_a_producto(self, producto_id, categoria_ids):
        """Reemplaza las categorías de un producto con la lista dada"""
        producto = (
            self.session.query(Producto).filter(Producto.id == producto_id).first()
        )
        if not producto:
            raise ValueError("Producto no encontrado")
        categorias = (
            self.session.query(Categoria).filter(Categoria.id.in_(categoria_ids)).all()
        )
        producto.categorias = categorias
        self.session.commit()
        return producto

    def get_productos_de_categoria(self, categoria_id):
        cat = self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        if not cat:
            return []
        return [p for p in cat.productos if p.activo]
