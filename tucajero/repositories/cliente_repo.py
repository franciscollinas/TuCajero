from tucajero.models.cliente import Cliente
from sqlalchemy import or_


class ClienteRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return (
            self.session.query(Cliente)
            .filter(Cliente.activo == True)
            .order_by(Cliente.nombre)
            .all()
        )

    def get_by_id(self, cliente_id):
        return self.session.query(Cliente).filter(Cliente.id == cliente_id).first()

    def search(self, query):
        term = f"%{query}%"
        return (
            self.session.query(Cliente)
            .filter(
                Cliente.activo == True,
                or_(
                    Cliente.nombre.ilike(term),
                    Cliente.documento.ilike(term),
                    Cliente.telefono.ilike(term),
                ),
            )
            .all()
        )

    def create(self, nombre, documento="", telefono="", email="", direccion=""):
        c = Cliente(
            nombre=nombre,
            documento=documento,
            telefono=telefono,
            email=email,
            direccion=direccion,
        )
        self.session.add(c)
        self.session.commit()
        return c

    def update(self, cliente_id, **kwargs):
        c = self.get_by_id(cliente_id)
        if c:
            for k, v in kwargs.items():
                setattr(c, k, v)
            self.session.commit()
        return c

    def delete(self, cliente_id):
        c = self.get_by_id(cliente_id)
        if c:
            c.activo = False
            self.session.commit()

    def abonar(self, cliente_id, monto):
        """Reduce la deuda del cliente"""
        c = self.get_by_id(cliente_id)
        if not c:
            raise ValueError("Cliente no encontrado")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        c.saldo_credito = max(0, c.saldo_credito - monto)
        self.session.commit()
        return c

    def agregar_credito(self, cliente_id, monto):
        """Aumenta la deuda del cliente (fiado)"""
        c = self.get_by_id(cliente_id)
        if not c:
            raise ValueError("Cliente no encontrado")
        c.saldo_credito += monto
        self.session.commit()
        return c
