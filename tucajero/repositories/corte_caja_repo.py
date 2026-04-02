from tucajero.models.producto import CorteCaja


class CorteCajaRepository:
    """Repositorio para acceso a datos de cortes de caja"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todos los cortes de caja"""
        return (
            self.session.query(CorteCaja)
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )

    def get_by_id(self, corte_id):
        """Retorna un corte por su ID"""
        return self.session.query(CorteCaja).filter(CorteCaja.id == corte_id).first()

    def get_corte_actual(self):
        """Retorna el corte de caja actual (abierto)"""
        return (
            self.session.query(CorteCaja)
            .filter(CorteCaja.fecha_cierre.is_(None))
            .first()
        )

    def create(self, fecha_apertura, cajero_id=None, total_ventas=0):
        """Crea un nuevo corte de caja"""
        corte = CorteCaja(
            fecha_apertura=fecha_apertura,
            cajero_id=cajero_id,
            total_ventas=total_ventas,
        )
        self.session.add(corte)
        self.session.commit()
        return corte

    def update(self, corte_id, **kwargs):
        """Actualiza un corte de caja"""
        corte = self.get_by_id(corte_id)
        if corte:
            for key, value in kwargs.items():
                setattr(corte, key, value)
            self.session.commit()
        return corte

    def cerrar_corte(self, corte_id, fecha_cierre, total_ventas=0, numero_ventas=0, total_gastos=0, ganancia_neta=0):
        """Cierra un corte de caja"""
        corte = self.get_by_id(corte_id)
        if corte:
            corte.fecha_cierre = fecha_cierre
            corte.total_ventas = total_ventas
            corte.numero_ventas = numero_ventas
            corte.total_gastos = total_gastos
            corte.ganancia_neta = ganancia_neta
            self.session.commit()
        return corte

    def get_cortes_by_fecha(self, fecha_desde, fecha_hasta):
        """Retorna los cortes en un rango de fechas"""
        return (
            self.session.query(CorteCaja)
            .filter(
                CorteCaja.fecha_apertura >= fecha_desde,
                CorteCaja.fecha_apertura <= fecha_hasta,
            )
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )

    def get_historial(self):
        """Retorna el historial de cortes cerrados"""
        return (
            self.session.query(CorteCaja)
            .filter(CorteCaja.fecha_cierre.isnot(None))
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )
