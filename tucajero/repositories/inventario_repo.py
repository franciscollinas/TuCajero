"""
Repositorio de Inventario para TuCajeroPOS
Acceso a datos de movimientos de inventario
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from tucajero.models.producto import MovimientoInventario
from datetime import datetime


class InventarioRepository:
    """Repositorio para acceso a datos de inventario"""

    def __init__(self, session: Session):
        self.session = session

    def create_movimiento(self, producto_id: int, tipo: str, cantidad: int, motivo: str = "") -> MovimientoInventario:
        """Crea un movimiento de inventario"""
        movimiento = MovimientoInventario(
            producto_id=producto_id,
            tipo=tipo,
            cantidad=cantidad,
            motivo=motivo,
            fecha=datetime.now()
        )
        self.session.add(movimiento)
        self.session.commit()
        self.session.refresh(movimiento)
        return movimiento

    def get_movimientos_producto(self, producto_id: int) -> List[MovimientoInventario]:
        """Retorna los movimientos de un producto"""
        return (
            self.session.query(MovimientoInventario)
            .filter(MovimientoInventario.producto_id == producto_id)
            .order_by(MovimientoInventario.fecha.desc())
            .all()
        )

    def get_movimientos_hoy(self) -> List[MovimientoInventario]:
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
