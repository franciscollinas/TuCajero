from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class Categoria(Base):
    """Modelo de Categoría de producto"""

    __tablename__ = "categorias"
    __table_args__ = (Index("idx_categoria_nombre", "nombre"),)

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(200), default="")
    color = Column(String(7), default="#3498db")

    productos = relationship("Producto", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class Producto(Base):
    """Modelo de Producto"""

    __tablename__ = "productos"
    __table_args__ = (
        Index("idx_producto_codigo", "codigo"),
        Index("idx_producto_nombre", "nombre"),
        Index("idx_producto_categoria", "categoria_id"),
        Index("idx_producto_activo", "activo"),
        Index("idx_producto_fraccion", "producto_fraccion_id"),
    )

    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    costo = Column(Float, default=0)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    aplica_iva = Column(Boolean, default=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    unidades_por_empaque = Column(Integer, nullable=True)
    producto_fraccion_id = Column(
        Integer, 
        ForeignKey("productos.id", ondelete="SET NULL"), 
        nullable=True
    )
    es_fraccion = Column(Boolean, default=False)
    stock_minimo = Column(Integer, default=0, nullable=True)
    fecha_vencimiento = Column(DateTime, nullable=True)

    producto_fraccion = relationship(
        "Producto", 
        foreign_keys=[producto_fraccion_id],
        remote_side="Producto.id",  # ← IMPORTANTE: evita ambigüedad
        uselist=False,
        lazy="joined"  # Reduce N+1 queries
    )

    venta_items = relationship("VentaItem", back_populates="producto")
    movimientos = relationship("MovimientoInventario", back_populates="producto")
    categoria = relationship("Categoria", back_populates="productos")

    def __repr__(self):
        return f"<Producto {self.nombre}>"


class Venta(Base):
    """Modelo de Venta"""

    __tablename__ = "ventas"
    __table_args__ = (
        Index("idx_venta_fecha", "fecha"),
        Index("idx_venta_cliente", "cliente_id"),
        Index("idx_venta_cajero", "cajero_id"),
    )

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)
    anulada = Column(Boolean, default=False)
    metodo_pago = Column(String(50), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    es_credito = Column(Boolean, default=False)
    descuento_tipo = Column(String(20), nullable=True)
    descuento_valor = Column(Float, default=0)
    descuento_total = Column(Float, default=0)
    cajero_id = Column(Integer, ForeignKey("cajeros.id"), nullable=True)
    comprobante = Column(String(100), nullable=True)
    numero_factura = Column(String(20), nullable=True)

    items = relationship(
        "VentaItem", back_populates="venta", cascade="all, delete-orphan"
    )
    cliente = relationship("Cliente", back_populates="ventas")
    cajero = relationship("Cajero")

    def __repr__(self):
        return f"<Venta {self.id} - {self.total}>"


class ConsecutivoFactura(Base):
    """Modelo para controlar el consecutivo de facturas"""

    __tablename__ = "consecutivos_factura"
    __table_args__ = (Index("idx_consecutivo_prefijo", "prefijo"),)

    id = Column(Integer, primary_key=True)
    prefijo = Column(String(10), nullable=False, unique=True)  # Ej: "FAC", "BOL"
    ultimo_numero = Column(Integer, default=0)
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<ConsecutivoFactura {self.prefijo} - {self.ultimo_numero}>"


class VentaItem(Base):
    """Modelo de Item de Venta"""

    __tablename__ = "venta_items"
    __table_args__ = (
        Index("idx_venta_item_venta", "venta_id"),
        Index("idx_venta_item_producto", "producto_id"),
    )

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    iva_monto = Column(Float, default=0)

    venta = relationship("Venta", back_populates="items")
    producto = relationship("Producto", back_populates="venta_items")

    @property
    def subtotal(self):
        return self.cantidad * self.precio

    def __repr__(self):
        return f"<VentaItem {self.producto_id} x {self.cantidad}>"


class MovimientoInventario(Base):
    """Modelo de Movimiento de Inventario"""

    __tablename__ = "movimientos_inventario"
    __table_args__ = (
        Index("idx_movimiento_producto", "producto_id"),
        Index("idx_movimiento_fecha", "fecha"),
    )

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String(10), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    producto = relationship("Producto", back_populates="movimientos")

    def __repr__(self):
        return f"<Movimiento {self.tipo} - {self.cantidad}>"


class CorteCaja(Base):
    """Modelo de Corte de Caja"""

    __tablename__ = "cortes_caja"
    __table_args__ = (Index("idx_corte_cajero", "cajero_id"),)

    id = Column(Integer, primary_key=True)
    fecha_apertura = Column(DateTime, default=datetime.now)
    fecha_cierre = Column(DateTime, nullable=True)
    total_ventas = Column(Float, default=0)
    numero_ventas = Column(Integer, default=0)
    total_gastos = Column(Float, default=0)
    ganancia_neta = Column(Float, default=0)
    cajero_id = Column(Integer, ForeignKey("cajeros.id"), nullable=True)

    gastos = relationship("GastoCaja", backref="corte", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CorteCaja {self.id}>"


class GastoCaja(Base):
    """Modelo de Gasto de Caja"""

    __tablename__ = "gastos_caja"

    id = Column(Integer, primary_key=True)
    corte_id = Column(Integer, ForeignKey("cortes_caja.id"), nullable=False)
    concepto = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<GastoCaja {self.concepto} - {self.monto}>"
