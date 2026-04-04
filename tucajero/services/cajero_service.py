from tucajero.models.cajero import Cajero, hash_pin


class CajeroService:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return (
            self.session.query(Cajero)
            .filter(Cajero.activo == True)
            .order_by(Cajero.nombre)
            .all()
        )

    def get_by_id(self, cajero_id):
        return self.session.query(Cajero).filter(Cajero.id == cajero_id).first()

    def crear(self, nombre, pin, rol="cajero"):
        if not nombre.strip():
            raise ValueError("El nombre es requerido")
        if len(str(pin)) != 4 or not str(pin).isdigit():
            raise ValueError("El PIN debe ser de 4 dígitos")
        cajero = Cajero(nombre=nombre.strip(), pin_hash=hash_pin(pin), rol=rol)
        self.session.add(cajero)
        self.session.commit()
        return cajero

    def cambiar_pin(self, cajero_id, nuevo_pin):
        cajero = self.get_by_id(cajero_id)
        if not cajero:
            raise ValueError("Cajero no encontrado")
        if len(str(nuevo_pin)) != 4 or not str(nuevo_pin).isdigit():
            raise ValueError("El PIN debe ser de 4 dígitos")
        cajero.pin_hash = hash_pin(nuevo_pin)
        self.session.commit()

    def verificar_login(self, cajero_id, pin):
        cajero = self.get_by_id(cajero_id)
        if not cajero:
            return False
        return cajero.verificar_pin(pin)

    def eliminar(self, cajero_id):
        cajero = self.get_by_id(cajero_id)
        if cajero:
            cajero.activo = False
            self.session.commit()

    def crear_admin_default(self):
        """Crea cajero admin por defecto si no existe ninguno"""
        total = self.session.query(Cajero).count()
        if total == 0:
            self.crear("Admin", "0000", rol="admin")
        else:
            # Migración: renombrar "Administrador" a "Admin" si existe
            admin_viejo = self.session.query(Cajero).filter(
                Cajero.nombre == "Administrador"
            ).first()
            if admin_viejo:
                admin_viejo.nombre = "Admin"
                self.session.commit()
