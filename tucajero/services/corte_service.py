from models.producto import CorteCaja, GastoCaja
from repositories.venta_repo import VentaRepository
from datetime import datetime


class CorteCajaService:
    """Servicio para lógica de negocio de corte de caja"""

    def __init__(self, session):
        self.session = session
        self.venta_repo = VentaRepository(session)

    def get_corte_actual(self):
        """Retorna el corte de caja del día"""
        return (
            self.session.query(CorteCaja)
            .filter(CorteCaja.fecha_cierre.is_(None))
            .first()
        )

    def abrir_caja(self):
        """Abre la caja creando un nuevo corte"""
        corte_existente = self.get_corte_actual()
        if corte_existente:
            return corte_existente

        corte = CorteCaja(fecha_apertura=datetime.now(), total_ventas=0)
        self.session.add(corte)
        self.session.commit()
        return corte

    def registrar_gasto(self, concepto, monto):
        """Registra un gasto de caja en el corte actual"""
        corte = self.get_corte_actual()
        if not corte:
            raise Exception("No hay caja abierta")
        gasto = GastoCaja(corte_id=corte.id, concepto=concepto, monto=monto)
        self.session.add(gasto)
        self.session.commit()
        return gasto

    def get_gastos_hoy(self):
        """Retorna los gastos del corte actual"""
        corte = self.get_corte_actual()
        if not corte:
            return []
        return (
            self.session.query(GastoCaja).filter(GastoCaja.corte_id == corte.id).all()
        )

    def get_total_gastos_hoy(self):
        """Retorna el total de gastos de hoy"""
        return sum(g.monto for g in self.get_gastos_hoy())

    def cerrar_caja(self):
        """Cierra la caja actual"""
        corte = self.get_corte_actual()
        if not corte:
            return None

        total = self.venta_repo.get_total_hoy()
        num_ventas = self.venta_repo.get_count_hoy()
        total_gastos = self.get_total_gastos_hoy()
        corte.fecha_cierre = datetime.now()
        corte.total_ventas = total
        corte.numero_ventas = num_ventas
        corte.total_gastos = total_gastos
        corte.ganancia_neta = total - total_gastos
        self.session.commit()

        try:
            from utils.backup import backup_database

            backup_database()
        except Exception as e:
            print(f"Error al crear backup: {e}")

        return corte

    def obtener_total_vendido(self):
        """Retorna el total vendido hoy"""
        return self.venta_repo.get_total_hoy()

    def obtener_numero_ventas(self):
        """Retorna el número de ventas hoy"""
        return self.venta_repo.get_count_hoy()

    def esta_caja_abierta(self):
        """Retorna True si la caja está abierta"""
        return self.get_corte_actual() is not None

    def get_estadisticas_hoy(self):
        """Retorna las estadísticas de ventas de hoy"""
        gastos = self.get_gastos_hoy()
        total_gastos = sum(g.monto for g in gastos)
        total_ventas = self.venta_repo.get_total_hoy()
        return {
            "total": total_ventas,
            "num_ventas": self.venta_repo.get_count_hoy(),
            "ventas": self.venta_repo.get_ventas_hoy(),
            "gastos": gastos,
            "total_gastos": total_gastos,
            "ganancia_neta": total_ventas - total_gastos,
        }

    def get_historial_cortes(self):
        """Retorna el historial de cortes de caja"""
        return (
            self.session.query(CorteCaja)
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )
