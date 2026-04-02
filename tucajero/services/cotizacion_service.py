from tucajero.models.cotizacion import Cotizacion, CotizacionItem
from datetime import datetime

IVA_RATE = 0.19


class CotizacionService:
    def __init__(self, session):
        self.session = session

    def get_all(self, estado=None):
        q = self.session.query(Cotizacion)
        if estado:
            q = q.filter(Cotizacion.estado == estado)
        return q.order_by(Cotizacion.fecha.desc()).all()

    def get_by_id(self, cotizacion_id):
        return (
            self.session.query(Cotizacion)
            .filter(Cotizacion.id == cotizacion_id)
            .first()
        )

    def crear(self, carrito, cliente_id=None, cajero_id=None, notas=""):
        total = 0
        for item in carrito:
            subtotal = item["cantidad"] * item["precio"]
            if item.get("aplica_iva", True):
                subtotal += round(subtotal * IVA_RATE, 2)
            total += subtotal

        cotizacion = Cotizacion(
            fecha=datetime.now(),
            cliente_id=cliente_id,
            cajero_id=cajero_id,
            estado="pendiente",
            total=round(total, 2),
            notas=notas,
        )
        self.session.add(cotizacion)
        self.session.flush()

        for item in carrito:
            ci = CotizacionItem(
                cotizacion_id=cotizacion.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio=item["precio"],
                aplica_iva=item.get("aplica_iva", True),
            )
            self.session.add(ci)

        self.session.commit()
        return cotizacion

    def cancelar(self, cotizacion_id):
        c = self.get_by_id(cotizacion_id)
        if not c:
            raise ValueError("Cotización no encontrada")
        if c.estado == "facturada":
            raise ValueError("No se puede cancelar una cotización ya facturada")
        c.estado = "cancelada"
        self.session.commit()

    def marcar_facturada(self, cotizacion_id):
        c = self.get_by_id(cotizacion_id)
        if c:
            c.estado = "facturada"
            self.session.commit()

    def cotizacion_a_carrito(self, cotizacion_id):
        c = self.get_by_id(cotizacion_id)
        if not c:
            raise ValueError("Cotización no encontrada")
        carrito = []
        for item in c.items:
            carrito.append(
                {
                    "producto_id": item.producto_id,
                    "cantidad": item.cantidad,
                    "precio": item.precio,
                    "aplica_iva": item.aplica_iva,
                }
            )
        return carrito, c.cliente_id
