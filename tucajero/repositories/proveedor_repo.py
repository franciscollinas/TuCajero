from tucajero.models.proveedor import Proveedor


class ProveedorRepository:
    """Repositorio para acceso a datos de proveedores"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todos los proveedores activos"""
        return (
            self.session.query(Proveedor)
            .filter(Proveedor.activo == True)
            .order_by(Proveedor.nombre)
            .all()
        )

    def get_by_id(self, proveedor_id):
        """Retorna un proveedor por su ID"""
        return self.session.query(Proveedor).filter(Proveedor.id == proveedor_id).first()

    def get_by_nombre(self, nombre):
        """Retorna un proveedor por su nombre"""
        return self.session.query(Proveedor).filter(Proveedor.nombre == nombre).first()

    def create(self, nombre, nit="", telefono="", email="", direccion=""):
        """Crea un nuevo proveedor"""
        proveedor = Proveedor(
            nombre=nombre,
            nit=nit,
            telefono=telefono,
            email=email,
            direccion=direccion,
        )
        self.session.add(proveedor)
        self.session.commit()
        return proveedor

    def update(self, proveedor_id, **kwargs):
        """Actualiza un proveedor"""
        proveedor = self.get_by_id(proveedor_id)
        if proveedor:
            for key, value in kwargs.items():
                setattr(proveedor, key, value)
            self.session.commit()
        return proveedor

    def delete(self, proveedor_id):
        """Elimina (desactiva) un proveedor"""
        proveedor = self.get_by_id(proveedor_id)
        if proveedor:
            proveedor.activo = False
            self.session.commit()
        return proveedor

    def search(self, query):
        """Busca proveedores por nombre o NIT"""
        search_term = f"%{query}%"
        return (
            self.session.query(Proveedor)
            .filter(
                Proveedor.activo == True,
                (Proveedor.nombre.ilike(search_term) | Proveedor.nit.ilike(search_term))
            )
            .all()
        )
