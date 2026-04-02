import sys

sys.path.insert(0, "tucajero")
from tucajero.config.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    migraciones = [
        "ALTER TABLE venta_items ADD COLUMN iva_monto REAL DEFAULT 0",
        "ALTER TABLE cortes_caja ADD COLUMN total_iva REAL DEFAULT 0",
    ]
    for sql in migraciones:
        try:
            conn.execute(text(sql))
            print(f"OK: {sql[:50]}...")
        except Exception as e:
            print(f"Ya existe o error: {e}")
    conn.commit()
print("Migración OK")
