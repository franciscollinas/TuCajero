import logging
from utils.store_config import (
    get_store_name,
    get_address,
    get_phone,
    get_nit,
    get_email,
)
from utils.formato import fmt_moneda


class ImpresoraTermica:
    """Maneja la impresion en impresoras termicas ESC/POS"""

    def __init__(self, config=None):
        self.config = config or {}
        self.ancho = config.get("ancho", 48) if config else 48
        self._printer = None

    def conectar(self):
        """Intenta conectar con la impresora"""
        try:
            tipo = self.config.get("tipo", "usb")
            if tipo == "usb":
                from escpos.printer import Usb

                vendor_id = int(self.config.get("vendor_id", "0x0416"), 16)
                product_id = int(self.config.get("product_id", "0x5011"), 16)
                self._printer = Usb(vendor_id, product_id)
            elif tipo == "red":
                from escpos.printer import Network

                self._printer = Network(
                    self.config.get("ip", "192.168.1.100"),
                    port=int(self.config.get("puerto", 9100)),
                )
            elif tipo == "serial":
                from escpos.printer import Serial

                self._printer = Serial(
                    self.config.get("puerto", "COM1"),
                    baudrate=int(self.config.get("baudrate", 9600)),
                )
            return True
        except Exception as e:
            logging.error(f"Error conectando impresora: {e}")
            self._printer = None
            return False

    def desconectar(self):
        try:
            if self._printer:
                self._printer.close()
        except:
            pass
        self._printer = None

    def esta_disponible(self):
        """Verifica si hay impresora configurada"""
        return bool(self.config.get("tipo"))

    def _linea(self, char="-"):
        return char * self.ancho

    def imprimir_ticket(self, venta, items):
        """Imprime el ticket de una venta"""
        if not self._printer:
            if not self.conectar():
                raise Exception("No se pudo conectar con la impresora")
        try:
            p = self._printer

            p.set(align="center", bold=True, height=2, width=2)
            p.text(get_store_name() + "\n")
            p.set(align="center", bold=False, height=1, width=1)
            if get_address():
                p.text(get_address() + "\n")
            if get_phone():
                p.text(f"Tel: {get_phone()}\n")
            if get_nit():
                p.text(f"NIT: {get_nit()}\n")

            p.set(align="left")
            p.text(self._linea("=") + "\n")

            from datetime import datetime

            p.set(bold=True)
            p.text(f"Ticket #{venta.id}\n")
            p.set(bold=False)
            p.text(f"{venta.fecha.strftime('%d/%m/%Y %I:%M:%S %p')}\n")
            if hasattr(venta, "metodo_pago") and venta.metodo_pago:
                p.text(f"Metodo: {venta.metodo_pago}\n")
            p.text(self._linea("=") + "\n")

            subtotal_total = 0
            iva_total = 0

            for item in items:
                nombre = (
                    item.producto.nombre
                    if hasattr(item, "producto") and item.producto
                    else f"Producto #{item.producto_id}"
                )
                precio = item.precio
                cantidad = item.cantidad
                iva = getattr(item, "iva_monto", 0) or 0
                subtotal = precio * cantidad

                if len(nombre) > self.ancho:
                    nombre = nombre[: self.ancho - 3] + "..."
                p.text(nombre + "\n")

                linea_precio = (
                    f"  {cantidad} x {fmt_moneda(precio)}"
                    f"{'':>5}{fmt_moneda(subtotal)}\n"
                )
                p.text(linea_precio)

                if iva > 0:
                    p.text(f"  IVA: {fmt_moneda(iva)}\n")

                subtotal_total += subtotal
                iva_total += iva

            p.text(self._linea("-") + "\n")

            p.set(align="right")
            p.text(f"Subtotal: {fmt_moneda(subtotal_total)}\n")
            if iva_total > 0:
                p.text(f"IVA (19%): {fmt_moneda(iva_total)}\n")

            if hasattr(venta, "descuento_total") and venta.descuento_total > 0:
                p.text(f"Descuento: -{fmt_moneda(venta.descuento_total)}\n")

            p.set(align="right", bold=True, height=2, width=2)
            p.text(f"TOTAL: {fmt_moneda(venta.total)}\n")
            p.set(align="left", bold=False, height=1, width=1)

            p.text(self._linea("=") + "\n")

            p.set(align="center")
            p.text("Gracias por su compra!\n")
            p.text(self._linea("=") + "\n")

            p.ln(3)
            p.cut()

        except Exception as e:
            logging.error(f"Error imprimiendo ticket: {e}")
            raise

    def prueba_impresion(self):
        """Imprime un ticket de prueba"""
        if not self._printer:
            if not self.conectar():
                raise Exception("No se pudo conectar con la impresora")
        try:
            p = self._printer
            p.set(align="center", bold=True)
            p.text("=== PRUEBA DE IMPRESION ===\n")
            p.set(align="center", bold=False)
            p.text(get_store_name() + "\n")
            p.text("TuCajero POS\n")
            p.text("Impresora funcionando correctamente\n")
            p.set(align="center", bold=True)
            p.text("=========================\n")
            p.ln(3)
            p.cut()
        except Exception as e:
            logging.error(f"Error en prueba de impresion: {e}")
            raise


def get_impresora():
    """Retorna una impresora configurada desde store_config"""
    from utils.store_config import get_printer_config

    config = get_printer_config()
    return ImpresoraTermica(config)
