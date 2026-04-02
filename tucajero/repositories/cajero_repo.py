from tucajero.models.cajero import Cajero


class CajeroRepository:
    """Repositorio para acceso a datos de cajeros"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todos los cajeros activos"""
        return (
            self.session.query(Cajero)
            .filter(Cajero.activo == True)
            .order_by(Cajero.nombre)
            .all()
        )

    def get_by_id(self, cajero_id):
        """Retorna un cajero por su ID"""
        return self.session.query(Cajero).filter(Cajero.id == cajero_id).first()

    def create(self, nombre, pin_hash, rol="cajero"):
        """Crea un nuevo cajero"""
        cajero = Cajero(nombre=nombre, pin_hash=pin_hash, rol=rol)
        self.session.add(cajero)
        self.session.commit()
        return cajero

    def update(self, cajero_id, **kwargs):
        """Actualiza un cajero"""
        cajero = self.get_by_id(cajero_id)
        if cajero:
            for key, value in kwargs.items():
                setattr(cajero, key, value)
            self.session.commit()
        return cajero

    def delete(self, cajero_id):
        """Elimina (desactiva) un cajero"""
        cajero = self.get_by_id(cajero_id)
        if cajero:
            cajero.activo = False
            self.session.commit()
        return cajero

    def get_by_nombre(self, nombre):
        """Retorna un cajero por su nombre"""
        return (
            self.session.query(Cajero)
            .filter(Cajero.nombre == nombre)
            .first()
        )
