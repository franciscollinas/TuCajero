from tucajero.models.producto import Venta, VentaItem, MovimientoInventario, Producto, ConsecutivoFactura
from sqlalchemy import and_
from datetime import datetime, timedelta

IVA_RATE = 0.19


class VentaRepository:
    """Repositorio para acceso a datos de ventas"""

    def __init__(self, session):
        self.session = session

    def obtener_siguiente_consecutivo(self, prefijo="FAC"):
        """Obtiene el siguiente número consecutivo para una factura"""
        consecutivo = (
            self.session.query(ConsecutivoFactura)
            .filter(ConsecutivoFactura.prefijo == prefijo)
            .with_for_update()
            .first()
        )
        
        if not consecutivo:
            # Crear nuevo consecutivo si no existe
            consecutivo = ConsecutivoFactura(prefijo=prefijo, ultimo_numero=0)
            self.session.add(consecutivo)
        
        consecutivo.ultimo_numero += 1
        self.session.commit()
        
        return f"{prefijo}-{consecutivo.ultimo_numero:08d}"

    def create_venta(
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
        """Crea una venta con sus items (incluye IVA)"""

        # Validar stock disponible antes de crear la venta
        for item in items:
            producto = self.session.query(Producto).get(item["producto_id"])
            if producto:
                if producto.stock < item["cantidad"]:
                    raise ValueError(
                        f"⚠️ Stock insuficiente para {producto.nombre}\n\n"
                        f"Disponible: {producto.stock}\n"
                        f"Solicitado: {item['cantidad']}\n\n"
                        "Por favor ajuste la cantidad o reabastezca el inventario."
                    )

        total_bruto = 0
        for item in items:
            subtotal = item["cantidad"] * item["precio"]
            if item.get("aplica_iva", True):
                iva = round(subtotal * IVA_RATE, 2)
            else:
                iva = 0
            total_bruto += subtotal + iva

        total_final = max(0, total_bruto - descuento_total)

        # Obtener número de factura único usando el consecutivo
        numero_factura = self.obtener_siguiente_consecutivo("FAC")

        venta = Venta(
            total=round(total_final, 2),
            fecha=datetime.now(),
            metodo_pago=metodo_pago,
            cliente_id=cliente_id,
            es_credito=es_credito,
            descuento_tipo=descuento_tipo,
            descuento_valor=descuento_valor,
            descuento_total=descuento_total,
            comprobante=comprobante,
            cajero_id=cajero_id,
            numero_factura=numero_factura,
        )
        self.session.add(venta)
        self.session.flush()

        for item in items:
            subtotal = item["cantidad"] * item["precio"]
            if item.get("aplica_iva", True):
                iva_monto = round(subtotal * IVA_RATE, 2)
            else:
                iva_monto = 0
            venta_item = VentaItem(
                venta_id=venta.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio=item["precio"],
                iva_monto=iva_monto,
            )
            self.session.add(venta_item)

        self.session.commit()
        return venta

    def get_ventas_hoy(self, incluir_anuladas=False):
        """Retorna las ventas de hoy"""
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        fin_dia = datetime.combine(hoy, datetime.max.time())

        query = self.session.query(Venta).filter(
            and_(Venta.fecha >= inicio_dia, Venta.fecha <= fin_dia)
        )
        if not incluir_anuladas:
            query = query.filter(Venta.anulada == False)
        return query.all()

    def get_total_hoy(self):
        """Retorna el total de ventas de hoy"""
        ventas = self.get_ventas_hoy()
        return sum(v.total for v in ventas)

    def get_count_hoy(self):
        """Retorna el número de ventas de hoy"""
        return len(self.get_ventas_hoy())

    def get_venta_by_id(self, venta_id):
        """Retorna una venta por su ID"""
        return self.session.query(Venta).filter(Venta.id == venta_id).first()

    def anular_venta(self, venta_id, motivo=None, usuario_id=None):
        """Anula una venta y la marca como cancelada"""
        venta = self.get_venta_by_id(venta_id)
        if not venta:
            raise ValueError(f"Venta #{venta_id} no encontrada")
        if venta.anulada:
            raise ValueError(f"Venta #{venta_id} ya está anulada")
        venta.anulada = True
        venta.motivo_anulacion = motivo
        venta.usuario_anulacion_id = usuario_id
        self.session.commit()
        return venta

    def get_all(self, incluir_anuladas=False):
        """Retorna todas las ventas"""
        query = self.session.query(Venta)
        if not incluir_anuladas:
            query = query.filter(Venta.anulada == False)
        return query.order_by(Venta.fecha.desc()).all()


class InventarioRepository:
    """Repositorio para acceso a datos de inventario"""

    def __init__(self, session):
        self.session = session

    def create_movimiento(self, producto_id, tipo, cantidad):
        """Crea un movimiento de inventario"""
        movimiento = MovimientoInventario(
            producto_id=producto_id, tipo=tipo, cantidad=cantidad, fecha=datetime.now()
        )
        self.session.add(movimiento)
        self.session.commit()
        return movimiento

    def get_movimientos_producto(self, producto_id):
        """Retorna los movimientos de un producto"""
        return (
            self.session.query(MovimientoInventario)
            .filter(MovimientoInventario.producto_id == producto_id)
            .order_by(MovimientoInventario.fecha.desc())
            .all()
        )

    def get_movimientos_hoy(self):
        """Retorna los movimientos de hoy"""
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
