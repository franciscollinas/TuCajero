import hashlib
from sqlalchemy import Column, Integer, String, Boolean, Index
from config.database import Base


def hash_pin(pin):
    return hashlib.sha256(str(pin).encode()).hexdigest()


class Cajero(Base):
    __tablename__ = "cajeros"
    __table_args__ = (Index("idx_cajero_activo", "activo"),)

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    pin_hash = Column(String(64), nullable=False)
    rol = Column(String(20), default="cajero")
    activo = Column(Boolean, default=True)

    def verificar_pin(self, pin):
        return self.pin_hash == hash_pin(pin)

    def __repr__(self):
        return f"<Cajero {self.nombre}>"
