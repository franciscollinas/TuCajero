from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from config.database import Base
from datetime import datetime


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    documento = Column(String(20), nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    saldo_credito = Column(Float, default=0)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Cliente {self.nombre}>"
