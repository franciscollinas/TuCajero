import openpyxl
import csv
import os


def leer_archivo(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    filas = []
    if ext in [".xlsx", ".xls"]:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws = wb.active
        headers = [str(c.value).strip().lower() if c.value else "" for c in ws[1]]
        for row in ws.iter_rows(min_row=2, values_only=True):
            if any(v is not None for v in row):
                filas.append({headers[i]: row[i] for i in range(len(headers))})
    elif ext == ".csv":
        with open(filepath, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filas.append({k.strip().lower(): v for k, v in row.items()})
    return filas


def importar_productos(filepath, session):
    from models.producto import Producto, Categoria

    filas = leer_archivo(filepath)
    importados = actualizados = 0
    errores = []
    categorias_cache = {}

    for i, fila in enumerate(filas, start=2):
        try:
            codigo = str(fila.get("codigo", "") or "").strip()
            nombre = str(fila.get("nombre", "") or "").strip()
            if not codigo or not nombre:
                errores.append({"fila": i, "msg": "Código y nombre requeridos"})
                continue

            precio = float(str(fila.get("precio", 0) or 0).replace(",", "."))
            costo = float(str(fila.get("costo", 0) or 0).replace(",", "."))
            stock = int(float(str(fila.get("stock", 0) or 0)))
            iva_raw = str(fila.get("aplica_iva", "SI") or "SI").upper().strip()
            aplica_iva = iva_raw not in ["NO", "FALSE", "0", "N"]

            cat_nombre = str(fila.get("categoria", "") or "").strip()
            categoria_id = None
            if cat_nombre:
                if cat_nombre not in categorias_cache:
                    cat = session.query(Categoria).filter_by(nombre=cat_nombre).first()
                    if not cat:
                        cat = Categoria(nombre=cat_nombre)
                        session.add(cat)
                        session.flush()
                    categorias_cache[cat_nombre] = cat.id
                categoria_id = categorias_cache[cat_nombre]

            existente = session.query(Producto).filter_by(codigo=codigo).first()
            if existente:
                existente.nombre = nombre
                existente.precio = precio
                existente.costo = costo
                existente.stock = stock
                existente.aplica_iva = aplica_iva
                existente.categoria_id = categoria_id
                existente.activo = True
                actualizados += 1
            else:
                session.add(
                    Producto(
                        codigo=codigo,
                        nombre=nombre,
                        precio=precio,
                        costo=costo,
                        stock=stock,
                        aplica_iva=aplica_iva,
                        categoria_id=categoria_id,
                    )
                )
                importados += 1
        except Exception as e:
            errores.append({"fila": i, "msg": str(e)})

    session.commit()
    return {
        "importados": importados,
        "actualizados": actualizados,
        "errores": errores,
    }
