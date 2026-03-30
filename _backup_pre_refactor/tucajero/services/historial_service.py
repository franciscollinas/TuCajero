from models.producto import CorteCaja, Venta, VentaItem, Producto, GastoCaja
from sqlalchemy import and_, func
from datetime import datetime


class HistorialService:
    def __init__(self, session):
        self.session = session

    def get_cierres(self, fecha_desde=None, fecha_hasta=None):
        """Retorna cierres cerrados con filtro opcional de fechas"""
        query = self.session.query(CorteCaja).filter(CorteCaja.fecha_cierre.isnot(None))
        if fecha_desde:
            query = query.filter(CorteCaja.fecha_apertura >= fecha_desde)
        if fecha_hasta:
            query = query.filter(CorteCaja.fecha_apertura <= fecha_hasta)
        return query.order_by(CorteCaja.fecha_apertura.desc()).all()

    def get_ventas_del_cierre(self, corte_id):
        """Retorna las ventas de un corte específico"""
        corte = self.session.query(CorteCaja).filter(CorteCaja.id == corte_id).first()
        if not corte:
            return []
        return (
            self.session.query(Venta)
            .filter(
                and_(
                    Venta.fecha >= corte.fecha_apertura,
                    Venta.fecha <= corte.fecha_cierre,
                )
            )
            .order_by(Venta.fecha.asc())
            .all()
        )

    def get_ranking_productos(self, fecha_desde=None, fecha_hasta=None):
        """Retorna ranking de productos más y menos vendidos"""
        query = (
            self.session.query(
                Producto.codigo,
                Producto.nombre,
                func.sum(VentaItem.cantidad).label("total_vendido"),
                func.sum(VentaItem.cantidad * VentaItem.precio).label("total_ingresos"),
            )
            .join(VentaItem, Producto.id == VentaItem.producto_id)
            .join(Venta, VentaItem.venta_id == Venta.id)
        )
        if fecha_desde:
            query = query.filter(Venta.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Venta.fecha <= fecha_hasta)
        return (
            query.group_by(Producto.id)
            .order_by(func.sum(VentaItem.cantidad).desc())
            .all()
        )

    def get_resumen_periodo(self, fecha_desde=None, fecha_hasta=None):
        """Retorna totales consolidados del período"""
        cierres = self.get_cierres(fecha_desde, fecha_hasta)
        return {
            "total_ventas": sum(c.total_ventas for c in cierres),
            "total_gastos": sum(c.total_gastos or 0 for c in cierres),
            "ganancia_neta": sum(c.ganancia_neta or 0 for c in cierres),
            "num_cierres": len(cierres),
            "num_ventas": sum(c.numero_ventas for c in cierres),
        }
