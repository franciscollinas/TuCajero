"""
Repositorio de ventas e inventario.
Las operaciones usan la sesión inyectada.
"""

from models.producto import Venta, VentaItem, MovimientoInventario, PagoVenta
from sqlalchemy import and_
from datetime import datetime


class VentaRepository:
    def __init__(self, session):
        self.session = session

    def create_venta(self, items, pagos=None, metodo_pago="efectivo"):
        """Crea una venta con sus items, pagos e IVA."""
        IVA_RATE = 0.19
        total = 0
        for item in items:
            subtotal = item["cantidad"] * item["precio"]
            iva = round(subtotal * IVA_RATE, 2)
            total += subtotal + iva

        venta = Venta(
            total=round(total, 2),
            fecha=datetime.now(),
            metodo_pago=metodo_pago,
            anulada=False,
        )
        self.session.add(venta)
        self.session.flush()

        for item in items:
            subtotal = item["cantidad"] * item["precio"]
            iva_monto = round(subtotal * IVA_RATE, 2)
            venta_item = VentaItem(
                venta_id=venta.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio=item["precio"],
                iva_monto=iva_monto,
            )
            self.session.add(venta_item)

        if pagos:
            for pago in pagos:
                pago_obj = PagoVenta(
                    venta_id=venta.id, metodo=pago["metodo"], monto=pago["monto"]
                )
                self.session.add(pago_obj)

        self.session.commit()
        return venta

    def anular_venta(self, venta_id, motivo):
        """Anula una venta."""
        venta = self.session.query(Venta).filter(Venta.id == venta_id).first()
        if not venta:
            raise ValueError("Venta no encontrada")
        if venta.anulada:
            raise ValueError("La venta ya está anulada")
        venta.anulada = True
        venta.motivo_anulacion = motivo
        self.session.commit()
        return venta

    def get_ventas_hoy(self):
        """Retorna las ventas de hoy (incluidas anuladas)."""
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        fin_dia = datetime.combine(hoy, datetime.max.time())

        return (
            self.session.query(Venta)
            .filter(and_(Venta.fecha >= inicio_dia, Venta.fecha <= fin_dia))
            .all()
        )

    def get_total_hoy(self):
        """Retorna el total de ventas válidas de hoy."""
        ventas = self.get_ventas_hoy()
        return sum(v.total for v in ventas if not v.anulada)

    def get_count_hoy(self):
        """Retorna el número de ventas válidas de hoy."""
        return len([v for v in self.get_ventas_hoy() if not v.anulada])

    def get_totales_por_metodo_hoy(self):
        """Retorna totales por método de pago del día."""
        ventas = [v for v in self.get_ventas_hoy() if not v.anulada]
        total_efectivo = 0
        total_transferencias = 0
        metodos = ["nequi", "daviplata", "transferencia"]

        for v in ventas:
            if v.metodo_pago == "mixto":
                for pago in v.pagos:
                    if pago.metodo == "efectivo":
                        total_efectivo += pago.monto
                    else:
                        total_transferencias += pago.monto
            elif v.metodo_pago == "efectivo":
                total_efectivo += v.total
            else:
                total_transferencias += v.total

        return {"efectivo": total_efectivo, "transferencias": total_transferencias}

    def get_all(self):
        """Retorna todas las ventas."""
        return self.session.query(Venta).order_by(Venta.fecha.desc()).all()

    def get_total_iva_hoy(self):
        """Retorna el total de IVA recaudado hoy."""
        ventas = [v for v in self.get_ventas_hoy() if not v.anulada]
        total = 0
        for v in ventas:
            for item in v.items:
                total += item.iva_monto or 0
        return round(total, 2)


class InventarioRepository:
    def __init__(self, session):
        self.session = session

    def create_movimiento(self, producto_id, tipo, cantidad):
        """Crea un movimiento de inventario."""
        movimiento = MovimientoInventario(
            producto_id=producto_id, tipo=tipo, cantidad=cantidad, fecha=datetime.now()
        )
        self.session.add(movimiento)
        self.session.commit()
        return movimiento

    def get_movimientos_producto(self, producto_id):
        """Retorna los movimientos de un producto."""
        return (
            self.session.query(MovimientoInventario)
            .filter(MovimientoInventario.producto_id == producto_id)
            .order_by(MovimientoInventario.fecha.desc())
            .all()
        )

    def get_movimientos_hoy(self):
        """Retorna los movimientos de hoy."""
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        fin_dia = datetime.combine(hoy, datetime.max.time())

        return (
            self.session.query(MovimientoInventario)
            .filter(
                and_(
                    MovimientoInventario.fecha >= inicio_dia,
                    MovimientoInventario.fecha <= fin_dia,
                )
            )
            .all()
        )
