from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class Proveedor(Base):
    __tablename__ = "proveedores"
    __table_args__ = (Index("idx_proveedor_nombre", "nombre"),)

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    nit = Column(String(20), nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True)

    ordenes = relationship("OrdenCompra", back_populates="proveedor")

    def __repr__(self):
        return f"<Proveedor {self.nombre}>"


class OrdenCompra(Base):
    __tablename__ = "ordenes_compra"
    __table_args__ = (
        Index("idx_orden_fecha", "fecha"),
        Index("idx_orden_proveedor", "proveedor_id"),
        Index("idx_orden_estado", "estado"),
    )

    id = Column(Integer, primary_key=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    fecha = Column(DateTime, default=datetime.now)
    estado = Column(String(20), default="pendiente")
    total = Column(Float, default=0)
    notas = Column(String(500), default="")

    proveedor = relationship("Proveedor", back_populates="ordenes")
    items = relationship(
        "OrdenCompraItem", back_populates="orden", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<OrdenCompra #{self.id} — {self.estado}>"


class OrdenCompraItem(Base):
    __tablename__ = "orden_compra_items"
    __table_args__ = (
        Index("idx_orden_item_orden", "orden_id"),
        Index("idx_orden_item_producto", "producto_id"),
    )

    id = Column(Integer, primary_key=True)
    orden_id = Column(Integer, ForeignKey("ordenes_compra.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_compra = Column(Float, nullable=False)

    orden = relationship("OrdenCompra", back_populates="items")

    @property
    def subtotal(self):
        return self.cantidad * self.precio_compra
