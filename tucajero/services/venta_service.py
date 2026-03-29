"""Servicio para lógica de negocio de ventas"""

from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
from models.producto import Venta, VentaItem


class VentaService:
    """Servicio para operaciones de ventas"""

    def __init__(self, session):
        self.session = session

    def get_total_hoy(self):
        """Obtiene el total vendido hoy"""
        hoy = datetime.now().date()
        resultado = (
            self.session.query(func.sum(Venta.total))
            .filter(
                and_(
                    extract("year", Venta.fecha) == hoy.year,
                    extract("month", Venta.fecha) == hoy.month,
                    extract("day", Venta.fecha) == hoy.day,
                    Venta.anulada == False,
                )
            )
            .scalar()
        )
        return resultado or 0.0

    def get_total_mes(self):
        """Obtiene el total vendido en el mes actual"""
        hoy = datetime.now()
        resultado = (
            self.session.query(func.sum(Venta.total))
            .filter(
                and_(
                    extract("year", Venta.fecha) == hoy.year,
                    extract("month", Venta.fecha) == hoy.month,
                    Venta.anulada == False,
                )
            )
            .scalar()
        )
        return resultado or 0.0

    def get_num_ventas_hoy(self):
        """Obtiene el número de ventas de hoy"""
        hoy = datetime.now().date()
        resultado = (
            self.session.query(func.count(Venta.id))
            .filter(
                and_(
                    extract("year", Venta.fecha) == hoy.year,
                    extract("month", Venta.fecha) == hoy.month,
                    extract("day", Venta.fecha) == hoy.day,
                    Venta.anulada == False,
                )
            )
            .scalar()
        )
        return resultado or 0

    def get_ventas_ultimos_7_dias(self):
        """Obtiene ventas de los últimos 7 días agrupadas por día"""
        hoy = datetime.now()
        hace_7_dias = hoy - timedelta(days=7)

        resultados = (
            self.session.query(
                extract("day", Venta.fecha).label("dia"),
                func.sum(Venta.total).label("total"),
            )
            .filter(
                and_(
                    Venta.fecha >= hace_7_dias,
                    Venta.anulada == False,
                )
            )
            .group_by(extract("day", Venta.fecha))
            .order_by(extract("day", Venta.fecha))
            .all()
        )

        labels = []
        valores = []
        for dia, total in resultados:
            labels.append(f"{int(dia)}/{hoy.month}")
            valores.append(total or 0.0)

        return labels, valores

    def get_ventas_por_metodo(self):
        """Obtiene ventas agrupadas por método de pago"""
        resultados = (
            self.session.query(
                Venta.metodo_pago,
                func.sum(Venta.total).label("total"),
            )
            .filter(Venta.anulada == False)
            .group_by(Venta.metodo_pago)
            .all()
        )

        labels = []
        valores = []
        for metodo, total in resultados:
            if metodo:
                labels.append(metodo)
                valores.append(total or 0.0)

        return labels, valores
