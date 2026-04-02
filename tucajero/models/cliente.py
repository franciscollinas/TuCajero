from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from tucajero.config.database import Base
from datetime import datetime


class Cliente(Base):
    __tablename__ = "clientes"
    __table_args__ = (
        Index("idx_cliente_documento", "documento"),
        Index("idx_cliente_nombre", "nombre"),
        Index("idx_cliente_activo", "activo"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    documento = Column(String(20), nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    saldo_credito = Column(Float, default=0)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.now)

    ventas = relationship("Venta", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente {self.nombre}>"
