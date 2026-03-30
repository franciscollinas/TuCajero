from repositories.cliente_repo import ClienteRepository


class ClienteService:
    def __init__(self, session):
        self.session = session
        self.repo = ClienteRepository(session)

    def get_all(self):
        return self.repo.get_all()

    def get_by_id(self, cliente_id):
        return self.repo.get_by_id(cliente_id)

    def search(self, query):
        return self.repo.search(query)

    def create(self, nombre, documento="", telefono="", email="", direccion=""):
        if not nombre.strip():
            raise ValueError("El nombre es requerido")
        return self.repo.create(nombre.strip(), documento, telefono, email, direccion)

    def update(self, cliente_id, **kwargs):
        return self.repo.update(cliente_id, **kwargs)

    def delete(self, cliente_id):
        self.repo.delete(cliente_id)

    def abonar(self, cliente_id, monto):
        return self.repo.abonar(cliente_id, monto)

    def get_ventas_cliente(self, cliente_id):
        """Retorna todas las ventas de un cliente"""
        from models.producto import Venta

        return (
            self.session.query(Venta)
            .filter(Venta.cliente_id == cliente_id, Venta.anulada == False)
            .order_by(Venta.fecha.desc())
            .all()
        )

    def get_clientes_con_deuda(self):
        """Retorna clientes con saldo pendiente"""
        from models.cliente import Cliente

        return (
            self.session.query(Cliente)
            .filter(Cliente.activo == True, Cliente.saldo_credito > 0)
            .order_by(Cliente.saldo_credito.desc())
            .all()
        )
