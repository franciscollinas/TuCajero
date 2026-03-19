from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class Cotizacion(Base):
    __tablename__ = "cotizaciones"

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.now)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    cajero_id = Column(Integer, ForeignKey("cajeros.id"), nullable=True)
    estado = Column(String(20), default="pendiente")
    total = Column(Float, default=0)
    notas = Column(String(500), default="")

    items = relationship(
        "CotizacionItem", back_populates="cotizacion", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Cotizacion #{self.id} — {self.estado}>"


class CotizacionItem(Base):
    __tablename__ = "cotizacion_items"

    id = Column(Integer, primary_key=True)
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    aplica_iva = Column(Boolean, default=True)

    cotizacion = relationship("Cotizacion", back_populates="items")

    @property
    def subtotal(self):
        return self.cantidad * self.precio
