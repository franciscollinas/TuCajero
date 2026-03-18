from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Table,
)
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


producto_categorias = Table(
    "producto_categorias",
    Base.metadata,
    Column("producto_id", Integer, ForeignKey("productos.id"), primary_key=True),
    Column("categoria_id", Integer, ForeignKey("categorias.id"), primary_key=True),
)


class Producto(Base):
    """Modelo de Producto"""

    __tablename__ = "productos"
    __table_args__ = (
        Index("idx_producto_codigo", "codigo"),
        Index("idx_producto_nombre", "nombre"),
    )

    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    costo = Column(Float, default=0)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)

    venta_items = relationship("VentaItem", back_populates="producto")
    movimientos = relationship("MovimientoInventario", back_populates="producto")
    categorias = relationship(
        "Categoria",
        secondary="producto_categorias",
        back_populates="productos",
    )

    def __repr__(self):
        return f"<Producto {self.nombre}>"


class Venta(Base):
    """Modelo de Venta"""

    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=lambda: datetime.now())
    total = Column(Float, nullable=False)
    metodo_pago = Column(String(20), default="efectivo")
    anulada = Column(Boolean, default=False)
    motivo_anulacion = Column(String(200), nullable=True)

    items = relationship(
        "VentaItem", back_populates="venta", cascade="all, delete-orphan"
    )
    pagos = relationship(
        "PagoVenta", back_populates="venta", cascade="all, delete-orphan"
    )

    @property
    def total_iva(self):
        return round(sum(item.iva for item in self.items), 2)

    @property
    def subtotal_sin_iva(self):
        return round(sum(item.subtotal for item in self.items), 2)

    def __repr__(self):
        return f"<Venta {self.id} - {self.total}>"


class VentaItem(Base):
    """Modelo de Item de Venta"""

    __tablename__ = "venta_items"

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    iva_monto = Column(Float, default=0)

    venta = relationship("Venta", back_populates="items")
    producto = relationship("Producto", back_populates="venta_items")

    @property
    def iva(self):
        return round(self.cantidad * self.precio * 0.19, 2)

    @property
    def subtotal(self):
        return round(self.cantidad * self.precio, 2)

    @property
    def total_con_iva(self):
        return round(self.subtotal + self.iva, 2)

    def __repr__(self):
        return f"<VentaItem {self.producto_id} x {self.cantidad}>"


class PagoVenta(Base):
    """Modelo de pago de una venta (permite pagos mixtos)"""

    __tablename__ = "pagos_venta"
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    metodo = Column(String(20), nullable=False)
    monto = Column(Float, nullable=False)
    venta = relationship("Venta", back_populates="pagos")

    def __repr__(self):
        return f"<PagoVenta {self.metodo} - {self.monto}>"


class MovimientoInventario(Base):
    """Modelo de Movimiento de Inventario"""

    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String(10), nullable=False)  # 'entrada' o 'salida'
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now())

    producto = relationship("Producto", back_populates="movimientos")

    def __repr__(self):
        return f"<Movimiento {self.tipo} - {self.cantidad}>"


class CorteCaja(Base):
    """Modelo de Corte de Caja"""

    __tablename__ = "cortes_caja"

    id = Column(Integer, primary_key=True)
    fecha_apertura = Column(DateTime, default=lambda: datetime.now())
    fecha_cierre = Column(DateTime, nullable=True)
    total_ventas = Column(Float, default=0)
    numero_ventas = Column(Integer, default=0)
    total_gastos = Column(Float, default=0)
    ganancia_neta = Column(Float, default=0)
    total_efectivo = Column(Float, default=0)
    total_transferencias = Column(Float, default=0)
    total_iva = Column(Float, default=0)
    gastos = relationship(
        "GastoCaja", back_populates="corte", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<CorteCaja {self.id}>"


class GastoCaja(Base):
    """Modelo de Gasto de Caja"""

    __tablename__ = "gastos_caja"
    id = Column(Integer, primary_key=True)
    corte_id = Column(Integer, ForeignKey("cortes_caja.id"), nullable=False)
    concepto = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now())
    corte = relationship("CorteCaja", back_populates="gastos")

    def __repr__(self):
        return f"<GastoCaja {self.concepto} - {self.monto}>"


class Categoria(Base):
    """Modelo de Categoría / Tag de producto"""

    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), nullable=True)
    productos = relationship(
        "Producto",
        secondary="producto_categorias",
        back_populates="categorias",
    )

    def __repr__(self):
        return f"<Categoria {self.nombre}>"
