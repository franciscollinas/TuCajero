from models.producto import Producto, MovimientoInventario
from datetime import datetime


class FraccionService:
    def __init__(self, session):
        self.session = session

    def desempacar(self, producto_padre_id, num_cajas):
        """Desempaca N cajas del producto padre y agrega las unidades correspondientes al producto hijo."""
        padre = self.session.query(Producto).get(producto_padre_id)
        if not padre:
            raise ValueError("Producto no encontrado")
        if not padre.producto_fraccion_id:
            raise ValueError("Este producto no tiene un producto unitario vinculado")
        if not padre.unidades_por_empaque:
            raise ValueError(
                "Este producto no tiene definidas las unidades por empaque"
            )
        if padre.stock < num_cajas:
            raise ValueError(f"Stock insuficiente. Disponible: {padre.stock} cajas")

        hijo = self.session.query(Producto).get(padre.producto_fraccion_id)
        if not hijo:
            raise ValueError("Producto unitario no encontrado")

        unidades_a_agregar = num_cajas * padre.unidades_por_empaque

        padre.stock -= num_cajas
        self.session.add(
            MovimientoInventario(
                producto_id=padre.id,
                tipo="salida",
                cantidad=num_cajas,
                fecha=datetime.now(),
            )
        )

        hijo.stock += unidades_a_agregar
        self.session.add(
            MovimientoInventario(
                producto_id=hijo.id,
                tipo="entrada",
                cantidad=unidades_a_agregar,
                fecha=datetime.now(),
            )
        )

        self.session.commit()
        return {
            "cajas_descontadas": num_cajas,
            "unidades_agregadas": unidades_a_agregar,
            "stock_padre": padre.stock,
            "stock_hijo": hijo.stock,
        }

    def vincular_fraccion(self, padre_id, hijo_id, unidades_por_empaque):
        """Vincula un producto empaque con su producto unitario"""
        padre = self.session.query(Producto).get(padre_id)
        hijo = self.session.query(Producto).get(hijo_id)
        if not padre or not hijo:
            raise ValueError("Producto no encontrado")
        padre.producto_fraccion_id = hijo_id
        padre.unidades_por_empaque = unidades_por_empaque
        hijo.es_fraccion = True
        self.session.commit()

    def crear_producto_fraccion(self, padre_id, unidades_por_empaque):
        """Crea automáticamente el producto unitario vinculado al empaque"""
        padre = self.session.query(Producto).get(padre_id)
        if not padre:
            raise ValueError("Producto no encontrado")
        precio_unitario = round(padre.precio / unidades_por_empaque, 2)
        hijo = Producto(
            codigo=f"{padre.codigo}-UND",
            nombre=f"{padre.nombre} (und)",
            precio=precio_unitario,
            costo=round(padre.costo / unidades_por_empaque, 2) if padre.costo else 0,
            stock=0,
            aplica_iva=padre.aplica_iva,
            categoria_id=padre.categoria_id,
            es_fraccion=True,
        )
        self.session.add(hijo)
        self.session.flush()
        padre.producto_fraccion_id = hijo.id
        padre.unidades_por_empaque = unidades_por_empaque
        self.session.commit()
        return hijo
