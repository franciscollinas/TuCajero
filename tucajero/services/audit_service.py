"""Servicio para registro de auditoría del sistema"""

from datetime import datetime
import logging
from tucajero.models.producto import AuditLog


class AuditService:
    """Servicio para registrar eventos de auditoría"""

    # Tipos de eventos
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ANULACION = "ANULACION"
    CAMBIO_PRECIO = "CAMBIO_PRECIO"
    REIMPRESION = "REIMPRESION"
    EMAIL_TICKET = "EMAIL_TICKET"
    VENTA_REGISTRADA = "VENTA_REGISTRADA"
    CORTE_APERTURA = "CORTE_APERTURA"
    CORTE_CIERRE = "CORTE_CIERRE"
    PRODUCTO_CREADO = "PRODUCTO_CREADO"
    PRODUCTO_EDITADO = "PRODUCTO_EDITADO"
    PRODUCTO_ELIMINADO = "PRODUCTO_ELIMINADO"

    def __init__(self, session):
        self.session = session

    def registrar(
        self,
        tipo_evento,
        descripcion,
        usuario_id=None,
        entidad_tipo=None,
        entidad_id=None,
        valor_anterior=None,
        valor_nuevo=None,
    ):
        """Registra un evento de auditoría"""
        try:
            log = AuditLog(
                fecha=datetime.now(),
                tipo_evento=tipo_evento,
                descripcion=descripcion,
                usuario_id=usuario_id,
                entidad_tipo=entidad_tipo,
                entidad_id=entidad_id,
                valor_anterior=valor_anterior,
                valor_nuevo=valor_nuevo,
            )
            self.session.add(log)
            self.session.commit()
            logging.info(f"AUDIT [{tipo_evento}]: {descripcion}")
            return log
        except Exception as e:
            try:
                self.session.rollback()
            except Exception:
                pass
            logging.error(f"Error al registrar auditoría: {e}")
            return None

    def get_logs(
        self,
        fecha_desde=None,
        fecha_hasta=None,
        tipo_evento=None,
        usuario_id=None,
        limit=100,
    ):
        """Obtiene logs de auditoría con filtros opcionales"""
        from sqlalchemy import and_

        query = self.session.query(AuditLog)
        filtros = []

        if fecha_desde:
            filtros.append(AuditLog.fecha >= fecha_desde)
        if fecha_hasta:
            filtros.append(AuditLog.fecha <= fecha_hasta)
        if tipo_evento:
            filtros.append(AuditLog.tipo_evento == tipo_evento)
        if usuario_id:
            filtros.append(AuditLog.usuario_id == usuario_id)

        if filtros:
            query = query.filter(and_(*filtros))

        return query.order_by(AuditLog.fecha.desc()).limit(limit).all()
