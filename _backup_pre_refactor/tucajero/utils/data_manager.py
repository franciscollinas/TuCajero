import os
import shutil
import zipfile
import json
import logging
from datetime import datetime

APP_VERSION = "3.0"

def get_db_path():
    """Ruta de la base de datos en producción"""
    local_app = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    return os.path.join(local_app, 'TuCajero', 'database', 'pos.db')

def get_config_path():
    """Ruta del store_config.json en producción"""
    local_app = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    return os.path.join(local_app, 'TuCajero', 'config', 'store_config.json')

def get_db_path_dev():
    """Ruta de la DB en modo desarrollo"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'database', 'pos.db')

def get_config_path_dev():
    """Ruta del config en modo desarrollo"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'config', 'store_config.json')

def _resolve_db_path():
    """Devuelve la ruta correcta de la DB según el entorno"""
    prod = get_db_path()
    if os.path.exists(prod):
        return prod
    dev = get_db_path_dev()
    if os.path.exists(dev):
        return dev
    return prod  # default

def _resolve_config_path():
    """Devuelve la ruta correcta del config según el entorno"""
    prod = get_config_path()
    if os.path.exists(prod):
        return prod
    dev = get_config_path_dev()
    if os.path.exists(dev):
        return dev
    return prod

def exportar_datos(ruta_destino: str) -> dict:
    """
    Exporta la DB y config a un archivo .tucajero (ZIP).
    Retorna {"ok": True, "ruta": ruta_destino} o {"ok": False, "error": mensaje}
    """
    try:
        db_path = _resolve_db_path()
        config_path = _resolve_config_path()

        if not os.path.exists(db_path):
            return {"ok": False, "error": "No se encontró la base de datos."}

        # Metadata del backup
        meta = {
            "version": APP_VERSION,
            "fecha": datetime.now().isoformat(),
            "archivos": ["pos.db", "store_config.json"]
        }

        with zipfile.ZipFile(ruta_destino, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(db_path, "pos.db")
            if os.path.exists(config_path):
                zf.write(config_path, "store_config.json")
            zf.writestr("backup_meta.json", json.dumps(meta, indent=2))

        logging.info(f"Datos exportados a: {ruta_destino}")
        return {"ok": True, "ruta": ruta_destino}

    except Exception as e:
        logging.error(f"exportar_datos error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}

def importar_datos(ruta_origen: str) -> dict:
    """
    Importa datos desde un archivo .tucajero.
    Hace backup automático antes de restaurar.
    Retorna {"ok": True} o {"ok": False, "error": mensaje}
    """
    try:
        if not os.path.exists(ruta_origen):
            return {"ok": False, "error": "El archivo no existe."}

        if not zipfile.is_zipfile(ruta_origen):
            return {"ok": False, "error": "El archivo no es un backup válido de TuCajero."}

        with zipfile.ZipFile(ruta_origen, 'r') as zf:
            nombres = zf.namelist()
            if "pos.db" not in nombres:
                return {"ok": False, "error": "El archivo no contiene una base de datos válida."}

            # Leer metadata
            meta = {}
            if "backup_meta.json" in nombres:
                meta = json.loads(zf.read("backup_meta.json").decode())

        db_path = _resolve_db_path()
        config_path = _resolve_config_path()

        # Backup automático antes de restaurar
        if os.path.exists(db_path):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.dirname(db_path)
            backup_path = os.path.join(backup_dir, f"pos_antes_import_{ts}.db")
            shutil.copy2(db_path, backup_path)
            logging.info(f"Backup automático guardado: {backup_path}")

        # Restaurar archivos
        with zipfile.ZipFile(ruta_origen, 'r') as zf:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            with open(db_path, 'wb') as f:
                f.write(zf.read("pos.db"))

            if "store_config.json" in zf.namelist():
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'wb') as f:
                    f.write(zf.read("store_config.json"))

        version_backup = meta.get("version", "desconocida")
        fecha_backup = meta.get("fecha", "desconocida")[:10]
        logging.info(f"Datos importados desde backup v{version_backup} del {fecha_backup}")
        return {
            "ok": True,
            "version": version_backup,
            "fecha": fecha_backup
        }

    except Exception as e:
        logging.error(f"importar_datos error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}
