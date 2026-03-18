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
            raise ValueError("No hay caja abierta")
        if not concepto or not concepto.strip():
            raise ValueError("El concepto es obligatorio")
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")
        gasto = GastoCaja(
            corte_id=corte.id,
            concepto=concepto.strip(),
            monto=monto,
            fecha=datetime.now(),
        )
        self.session.add(gasto)
        self.session.commit()
        return gasto

    def get_gastos_hoy(self):
        """Retorna los gastos del corte actual"""
        corte = self.get_corte_actual()
        if not corte:
            return []
        return (
            self.session.query(GastoCaja)
            .filter(GastoCaja.corte_id == corte.id)
            .order_by(GastoCaja.fecha.asc())
            .all()
        )

    def get_total_gastos_hoy(self):
        """Retorna el total de gastos del día"""
        gastos = self.get_gastos_hoy()
        return sum(g.monto for g in gastos)

    def cerrar_caja(self):
        """Cierra la caja actual"""
        corte = self.get_corte_actual()
        if not corte:
            return None

        total = self.venta_repo.get_total_hoy()
        num_ventas = self.venta_repo.get_count_hoy()
        total_gastos = self.get_total_gastos_hoy()
        totales_metodo = self.venta_repo.get_totales_por_metodo_hoy()
        total_iva = self.venta_repo.get_total_iva_hoy()

        corte.fecha_cierre = datetime.now()
        corte.total_ventas = total
        corte.numero_ventas = num_ventas
        corte.total_gastos = total_gastos
        corte.ganancia_neta = total - total_gastos
        corte.total_efectivo = totales_metodo["efectivo"]
        corte.total_transferencias = totales_metodo["transferencias"]
        corte.total_iva = total_iva
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
        total_ventas = self.venta_repo.get_total_hoy()
        total_gastos = sum(g.monto for g in gastos)
        totales_metodo = self.venta_repo.get_totales_por_metodo_hoy()
        return {
            "total": total_ventas,
            "num_ventas": self.venta_repo.get_count_hoy(),
            "ventas": self.venta_repo.get_ventas_hoy(),
            "gastos": gastos,
            "total_gastos": total_gastos,
            "ganancia_neta": total_ventas - total_gastos,
            "total_efectivo": totales_metodo["efectivo"],
            "total_transferencias": totales_metodo["transferencias"],
            "total_iva": self.venta_repo.get_total_iva_hoy(),
        }

    def get_historial_cortes(self):
        """Retorna el historial de cortes de caja"""
        return (
            self.session.query(CorteCaja)
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )
