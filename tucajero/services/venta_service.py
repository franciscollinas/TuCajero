"""Servicio para lógica de negocio de ventas"""

from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
from tucajero.models.producto import Venta, VentaItem
from tucajero.repositories.venta_repo import VentaRepository
from tucajero.repositories.producto_repo import ProductoRepository
from tucajero.repositories.inventario_repo import InventarioRepository


class VentaService:
    """Servicio para operaciones de ventas"""

    def __init__(self, session, venta_repo=None, producto_repo=None, inventario_repo=None, corte_service=None, cliente_repo=None):
        self.session = session
        self.venta_repo = venta_repo or VentaRepository(session)
        self.producto_repo = producto_repo or ProductoRepository(session)
        self.inventario_repo = inventario_repo or InventarioRepository(session)
        if corte_service is None:
            from tucajero.services.corte_service import CorteCajaService
            self.corte_service = CorteCajaService(session)
        else:
            self.corte_service = corte_service
        self.cliente_repo = cliente_repo

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

    def get_total_ayer(self):
        """Obtiene el total vendido ayer"""
        ayer = datetime.now().date() - timedelta(days=1)
        resultado = (
            self.session.query(func.sum(Venta.total))
            .filter(
                and_(
                    extract("year", Venta.fecha) == ayer.year,
                    extract("month", Venta.fecha) == ayer.month,
                    extract("day", Venta.fecha) == ayer.day,
                    Venta.anulada == False,
                )
            )
            .scalar()
        )
        return resultado or 0.0

    def get_num_ventas_ayer(self):
        """Obtiene el número de ventas de ayer"""
        ayer = datetime.now().date() - timedelta(days=1)
        resultado = (
            self.session.query(func.count(Venta.id))
            .filter(
                and_(
                    extract("year", Venta.fecha) == ayer.year,
                    extract("month", Venta.fecha) == ayer.month,
                    extract("day", Venta.fecha) == ayer.day,
                    Venta.anulada == False,
                )
            )
            .scalar()
        )
        return resultado or 0

    def get_total_mes_anterior(self):
        """Obtiene el total vendido en el mes anterior"""
        hoy = datetime.now()
        mes_anterior = hoy.month - 1 if hoy.month > 1 else 12
        anio_anterior = hoy.year if hoy.month > 1 else hoy.year - 1
        resultado = (
            self.session.query(func.sum(Venta.total))
            .filter(
                and_(
                    extract("year", Venta.fecha) == anio_anterior,
                    extract("month", Venta.fecha) == mes_anterior,
                    Venta.anulada == False,
                )
            )
            .scalar()
        )
        return resultado or 0.0

    def get_num_ventas_ultima_semana(self):
        """Obtiene el número de ventas de la semana anterior"""
        hoy = datetime.now()
        inicio_semana_pasada = hoy - timedelta(days=14)
        fin_semana_pasada = hoy - timedelta(days=7)
        resultado = (
            self.session.query(func.count(Venta.id))
            .filter(
                and_(
                    Venta.fecha >= inicio_semana_pasada,
                    Venta.fecha < fin_semana_pasada,
                    Venta.anulada == False,
                )
            )
            .scalar()
        )
        return resultado or 0

    def get_num_ventas_semana_actual(self):
        """Obtiene el número de ventas de la semana actual"""
        hoy = datetime.now()
        inicio_semana = hoy - timedelta(days=7)
        resultado = (
            self.session.query(func.count(Venta.id))
            .filter(
                and_(
                    Venta.fecha >= inicio_semana,
                    Venta.anulada == False,
                )
            )
            .scalar()
        )
        return resultado or 0

    def registrar_venta(
        self,
        items,
        metodo_pago=None,
        cliente_id=None,
        es_credito=False,
        descuento_tipo=None,
        descuento_valor=0,
        descuento_total=0,
        comprobante=None,
        cajero_id=None,
    ):
        """Registra una venta y descuenta inventario"""
        if not self.corte_service.esta_caja_abierta():
            raise Exception(
                "No se puede registrar la venta porque la caja está cerrada."
            )

        for item in items:
            producto = self.producto_repo.get_by_id(item["producto_id"])
            if producto.stock < item["cantidad"]:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

        subtotal = sum(item["cantidad"] * item["precio"] for item in items)
        iva = 0
        for item in items:
            if item.get("aplica_iva", True):
                iva += round(item["cantidad"] * item["precio"] * 0.19, 2)
        total = max(0, (subtotal + iva) - descuento_total)

        venta = self.venta_repo.create_venta(
            items,
            metodo_pago=metodo_pago,
            cliente_id=cliente_id,
            es_credito=es_credito,
            descuento_tipo=descuento_tipo,
            descuento_valor=descuento_valor,
            descuento_total=descuento_total,
            comprobante=comprobante,
            cajero_id=cajero_id,
        )

        if es_credito and cliente_id and self.cliente_repo:
            self.cliente_repo.agregar_credito(cliente_id, total)

        for item in items:
            self.producto_repo.update_stock(item["producto_id"], -item["cantidad"])
            self.inventario_repo.create_movimiento(
                item["producto_id"], "salida", item["cantidad"]
            )

        return venta

    def anular_venta(self, venta_id, motivo=None, usuario_id=None):
        """Anula una venta y restaura el stock"""
        venta = self.venta_repo.get_venta_by_id(venta_id)
        if not venta:
            raise ValueError(f"Venta #{venta_id} no encontrada")
        if venta.anulada:
            raise ValueError(f"Venta #{venta_id} ya está anulada")

        for item in venta.items:
            self.producto_repo.update_stock(item.producto_id, item.cantidad)
            self.inventario_repo.create_movimiento(
                item.producto_id, "entrada", item.cantidad
            )

        self.venta_repo.anular_venta(venta_id, motivo=motivo, usuario_id=usuario_id)
        return venta

    def get_ventas_hoy(self):
        """Retorna las ventas de hoy"""
        return self.venta_repo.get_ventas_hoy()
