from tucajero.models.cotizacion import Cotizacion


class CotizacionRepository:
    """Repositorio para acceso a datos de cotizaciones"""

    def __init__(self, session):
        self.session = session

    def get_all(self, estado=None):
        """Retorna todas las cotizaciones, filtradas por estado si se especifica"""
        query = self.session.query(Cotizacion)
        if estado:
            query = query.filter(Cotizacion.estado == estado)
        return query.order_by(Cotizacion.fecha.desc()).all()

    def get_by_id(self, cotizacion_id):
        """Retorna una cotización por su ID"""
        return (
            self.session.query(Cotizacion)
            .filter(Cotizacion.id == cotizacion_id)
            .first()
        )

    def create(self, fecha, cliente_id=None, cajero_id=None, estado="pendiente", total=0, notas=""):
        """Crea una nueva cotización"""
        cotizacion = Cotizacion(
            fecha=fecha,
            cliente_id=cliente_id,
            cajero_id=cajero_id,
            estado=estado,
            total=total,
            notas=notas,
        )
        self.session.add(cotizacion)
        self.session.commit()
        return cotizacion

    def update(self, cotizacion_id, **kwargs):
        """Actualiza una cotización"""
        cotizacion = self.get_by_id(cotizacion_id)
        if cotizacion:
            for key, value in kwargs.items():
                setattr(cotizacion, key, value)
            self.session.commit()
        return cotizacion

    def delete(self, cotizacion_id):
        """Elimina una cotización"""
        cotizacion = self.get_by_id(cotizacion_id)
        if cotizacion:
            self.session.delete(cotizacion)
            self.session.commit()
        return cotizacion

    def get_by_cliente(self, cliente_id):
        """Retorna las cotizaciones de un cliente"""
        return (
            self.session.query(Cotizacion)
            .filter(Cotizacion.cliente_id == cliente_id)
            .order_by(Cotizacion.fecha.desc())
            .all()
        )

    def get_by_estado(self, estado):
        """Retorna las cotizaciones por estado"""
        return (
            self.session.query(Cotizacion)
            .filter(Cotizacion.estado == estado)
            .order_by(Cotizacion.fecha.desc())
            .all()
        )
