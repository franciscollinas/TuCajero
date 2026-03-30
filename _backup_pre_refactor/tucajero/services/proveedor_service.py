from models.proveedor import Proveedor, OrdenCompra, OrdenCompraItem
from datetime import datetime


class ProveedorService:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return (
            self.session.query(Proveedor)
            .filter(Proveedor.activo == True)
            .order_by(Proveedor.nombre)
            .all()
        )

    def get_by_id(self, proveedor_id):
        return (
            self.session.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
        )

    def crear(self, nombre, nit="", telefono="", email="", direccion=""):
        if not nombre.strip():
            raise ValueError("El nombre es requerido")
        p = Proveedor(
            nombre=nombre.strip(),
            nit=nit,
            telefono=telefono,
            email=email,
            direccion=direccion,
        )
        self.session.add(p)
        self.session.commit()
        return p

    def actualizar(self, proveedor_id, **kwargs):
        p = self.get_by_id(proveedor_id)
        if p:
            for k, v in kwargs.items():
                setattr(p, k, v)
            self.session.commit()
        return p

    def eliminar(self, proveedor_id):
        p = self.get_by_id(proveedor_id)
        if p:
            p.activo = False
            self.session.commit()


class OrdenCompraService:
    def __init__(self, session):
        self.session = session

    def get_all(self, estado=None):
        q = self.session.query(OrdenCompra)
        if estado:
            q = q.filter(OrdenCompra.estado == estado)
        return q.order_by(OrdenCompra.fecha.desc()).all()

    def get_by_id(self, orden_id):
        return (
            self.session.query(OrdenCompra).filter(OrdenCompra.id == orden_id).first()
        )

    def crear(self, proveedor_id, items, notas=""):
        total = sum(i["cantidad"] * i["precio_compra"] for i in items)
        orden = OrdenCompra(
            proveedor_id=proveedor_id,
            fecha=datetime.now(),
            estado="pendiente",
            total=round(total, 2),
            notas=notas,
        )
        self.session.add(orden)
        self.session.flush()

        for item in items:
            oci = OrdenCompraItem(
                orden_id=orden.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio_compra=item["precio_compra"],
            )
            self.session.add(oci)

        self.session.commit()
        return orden

    def recibir_orden(self, orden_id):
        orden = self.get_by_id(orden_id)
        if not orden:
            raise ValueError("Orden no encontrada")
        if orden.estado == "recibida":
            raise ValueError("Esta orden ya fue recibida")
        if orden.estado == "cancelada":
            raise ValueError("No se puede recibir una orden cancelada")

        from models.producto import Producto, MovimientoInventario

        for item in orden.items:
            producto = self.session.query(Producto).get(item.producto_id)
            if producto:
                producto.stock += item.cantidad
                producto.costo = item.precio_compra
                mov = MovimientoInventario(
                    producto_id=item.producto_id,
                    tipo="entrada",
                    cantidad=item.cantidad,
                    fecha=datetime.now(),
                )
                self.session.add(mov)

        orden.estado = "recibida"
        self.session.commit()
        return orden

    def cancelar(self, orden_id):
        orden = self.get_by_id(orden_id)
        if not orden:
            raise ValueError("Orden no encontrada")
        if orden.estado == "recibida":
            raise ValueError("No se puede cancelar una orden ya recibida")
        orden.estado = "cancelada"
        self.session.commit()
