from tucajero.models.cajero import Cajero, hash_pin
import logging


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
        cajero.pin_must_be_set = False
        self.session.commit()

    def verificar_login(self, cajero_id, pin):
        """
        SEC-011 FIX: Login with rate limiting.
        SEC-003 FIX: Also handles transparent PIN hash migration to bcrypt.
        
        Returns tuple: (cajero, success, error_message)
        - On success: (cajero_obj, True, None)
        - On failure: (None, False, "error message")
        """
        from datetime import datetime

        cajero = self.get_by_id(cajero_id)
        if not cajero:
            return None, False, "Cajero no encontrado"

        # SEC-011: Check if account is locked
        if cajero.is_locked():
            logging.warning(f"SEC-011: Locked account login attempt: {cajero.nombre} (ID: {cajero_id})")
            return None, False, "Cuenta bloqueada. Intente de nuevo en 15 minutos."

        # SEC-003: Verify PIN with automatic migration support
        success, needs_rehash = cajero.verificar_pin(pin)

        if success:
            # SEC-003: Migrate old SHA-256 hash to bcrypt
            if needs_rehash:
                logging.info(f"SEC-003: Migrating PIN hash for cajero {cajero.nombre} (ID: {cajero_id})")
                cajero.rehash_pin(pin)
            # SEC-011: Reset failed attempts on successful login
            cajero.reset_failed_attempts()
            self.session.commit()
            return cajero, True, None
        else:
            # SEC-011: Record failed attempt
            cajero.record_failed_attempt()
            self.session.commit()
            remaining = 5 - (cajero.failed_attempts or 0)
            if cajero.is_locked():
                logging.warning(f"SEC-011: Account locked after 5 failed attempts: {cajero.nombre} (ID: {cajero_id})")
                return None, False, "Cuenta bloqueada después de 5 intentos fallidos. Intente en 15 minutos."
            logging.info(f"SEC-011: Failed login attempt {cajero.failed_attempts}/5 for cajero {cajero.nombre} (ID: {cajero_id})")
            return None, False, f"PIN incorrecto. Intentos restantes: {remaining}"

    def eliminar(self, cajero_id):
        cajero = self.get_by_id(cajero_id)
        if cajero:
            cajero.activo = False
            self.session.commit()

    def crear_admin_default(self):
        """
        SEC-008 FIX: No longer creates admin with hardcoded '0000' PIN.
        Instead, creates a placeholder admin that requires PIN setup on first launch.
        """
        import secrets
        import string
        from tucajero.models.cajero import hash_pin

        total = self.session.query(Cajero).count()
        if total == 0:
            # SEC-008: Create admin with a random PIN that the user must change.
            # We use a random 12-char string — nobody can guess it.
            random_pin = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            cajero = Cajero(
                nombre="Admin",
                pin_hash=hash_pin(random_pin),
                rol="admin",
                # SEC-008: Flag that indicates PIN has never been set by the user
                pin_must_be_set=True,
            )
            self.session.add(cajero)
            self.session.commit()
            logging.info("SEC-008: Created default admin with pin_must_be_set=True")
            return cajero
        else:
            # Migración: renombrar "Administrador" a "Admin" si existe
            admin_viejo = self.session.query(Cajero).filter(
                Cajero.nombre == "Administrador"
            ).first()
            if admin_viejo:
                admin_viejo.nombre = "Admin"
                self.session.commit()
