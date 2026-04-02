import sys

sys.path.insert(0, "tucajero")
from tucajero.config.database import init_db, get_session

init_db()
session = get_session()

from sqlalchemy import inspect

cols_items = [c["name"] for c in inspect(session.bind).get_columns("venta_items")]
cols_corte = [c["name"] for c in inspect(session.bind).get_columns("cortes_caja")]
print(f"Columnas venta_items: {cols_items}")
print(f"Columnas cortes_caja: {cols_corte}")

assert "iva_monto" in cols_items, "Falta iva_monto en venta_items"
assert "total_iva" in cols_corte, "Falta total_iva en cortes_caja"
print("Columnas verificadas OK")

from tucajero.services.corte_service import CorteCajaService
from tucajero.services.producto_service import ProductoService
from tucajero.services.venta_service import VentaService

cs = CorteCajaService(session)
if not cs.esta_caja_abierta():
    cs.abrir_caja()
    print("Caja abierta")

ps = ProductoService(session)
p = ps.create_producto("TESTIVA", "Producto IVA Test", 10000.0, 5000.0, 10)
print(f"Producto creado: {p.nombre}")

vs = VentaService(session)
venta = vs.registrar_venta([{"producto_id": p.id, "cantidad": 2, "precio": 10000.0}])
session.expire_all()

print(f"\n--- VERIFICACIÓN IVA ---")
print(f"Venta #{venta.id}")
print(f"Base: 2 x $10,000 = $20,000.00")
iva_item = venta.items[0].iva_monto
print(f"IVA 19%: ${iva_item:,.2f}")
print(f"Total: ${venta.total:,.2f}")

assert abs(venta.total - 23800.0) < 0.01, (
    f"Total esperado $23.800, obtenido ${venta.total}"
)
assert abs(iva_item - 3800.0) < 0.01, f"IVA esperado $3.800, obtenido ${iva_item}"

total_iva_hoy = vs.venta_repo.get_total_iva_hoy()
print(f"\nTotal IVA hoy: ${total_iva_hoy:,.2f}")
assert total_iva_hoy >= 3800.0

ps.delete_producto(p.id)
print("\nVERIFICACIÓN IVA OK - TODO CORRECTO")
