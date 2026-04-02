from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship
from tucajero.config.database import Base
from datetime import datetime


class Cotizacion(Base):
    __tablename__ = "cotizaciones"
    __table_args__ = (
        Index("idx_cotizacion_fecha", "fecha"),
        Index("idx_cotizacion_cliente", "cliente_id"),
        Index("idx_cotizacion_estado", "estado"),
        {"extend_existing": True},
    )

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
    __table_args__ = (
        Index("idx_cotizacion_item_cotizacion", "cotizacion_id"),
        Index("idx_cotizacion_item_producto", "producto_id"),
        {"extend_existing": True},
    )

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
