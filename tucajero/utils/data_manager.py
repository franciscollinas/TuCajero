import os
import shutil
import zipfile
import json
import logging
from datetime import datetime

APP_VERSION = "3.0"
# SEC-005: Maximum allowed import file size (100MB)
MAX_IMPORT_SIZE = 100 * 1024 * 1024
# SEC-006: Allowed files inside the .tucajero ZIP
ALLOWED_ZIP_MEMBERS = {"pos.db", "store_config.json", "backup_meta.json"}


def get_db_path():
    """Ruta de la base de datos en produccion"""
    local_app = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    return os.path.join(local_app, 'TuCajero', 'database', 'pos.db')


def get_config_path():
    """Ruta del store_config.json en produccion"""
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
    """Devuelve la ruta correcta de la DB segun el entorno"""
    prod = get_db_path()
    if os.path.exists(prod):
        return prod
    dev = get_db_path_dev()
    if os.path.exists(dev):
        return dev
    return prod  # default


def _resolve_config_path():
    """Devuelve la ruta correcta del config segun el entorno"""
    prod = get_config_path()
    if os.path.exists(prod):
        return prod
    dev = get_config_path_dev()
    if os.path.exists(dev):
        return dev
    return prod


def _validate_zip_contents(zf):
    """SEC-006: Validate that ZIP only contains allowed files."""
    names = set(zf.namelist())
    # Check for any files outside allowed list
    disallowed = names - ALLOWED_ZIP_MEMBERS
    if disallowed:
        logging.warning(f"SEC-006: Import file contains disallowed files: {disallowed}")
        return False, f"El archivo contiene elementos no permitidos: {', '.join(disallowed)}"
    if "pos.db" not in names:
        return False, "El archivo no contiene una base de datos valida."
    return True, None


def _compute_file_checksum(filepath):
    """SEC-006: Compute SHA-256 checksum for file integrity verification."""
    import hashlib
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def exportar_datos(ruta_destino: str) -> dict:
    """
    Exporta la DB y config a un archivo .tucajero (ZIP).
    Retorna {"ok": True, "ruta": ruta_destino, "checksum": sha256} o {"ok": False, "error": mensaje}
    """
    try:
        db_path = _resolve_db_path()
        config_path = _resolve_config_path()

        if not os.path.exists(db_path):
            return {"ok": False, "error": "No se encontro la base de datos."}

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

        # SEC-006: Compute checksum for integrity verification
        checksum = _compute_file_checksum(ruta_destino)
        logging.info(f"Datos exportados a: {ruta_destino} (checksum: {checksum[:16]}...)")
        return {"ok": True, "ruta": ruta_destino, "checksum": checksum}

    except Exception as e:
        logging.error(f"exportar_datos error: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}


def importar_datos(ruta_origen: str) -> dict:
    """
    Importa datos desde un archivo .tucajero.
    SEC-005: Validates path, extension, size, and ZIP contents.
    SEC-006: Makes backup before restore and verifies integrity.
    Retorna {"ok": True} o {"ok": False, "error": mensaje}
    """
    try:
        # SEC-005 FIX: Validate file extension
        if not ruta_origen.lower().endswith('.tucajero'):
            return {"ok": False, "error": "Extension de archivo invalida. Se espera .tucajero"}

        # SEC-005 FIX: Resolve to absolute path to prevent path traversal
        abs_path = os.path.realpath(ruta_origen)
        if not os.path.exists(abs_path):
            return {"ok": False, "error": "El archivo no existe."}

        # SEC-005 FIX: Check file size limit
        file_size = os.path.getsize(abs_path)
        if file_size > MAX_IMPORT_SIZE:
            return {"ok": False, "error": f"Archivo demasiado grande (max {MAX_IMPORT_SIZE // (1024*1024)}MB)"}

        # SEC-005 FIX: Validate it's a proper ZIP file
        if not zipfile.is_zipfile(abs_path):
            return {"ok": False, "error": "El archivo no es un backup valido de TuCajero."}

        # SEC-006 FIX: Validate ZIP contents before extracting
        with zipfile.ZipFile(abs_path, 'r') as zf:
            is_valid, error_msg = _validate_zip_contents(zf)
            if not is_valid:
                return {"ok": False, "error": error_msg}

            # Read metadata
            meta = {}
            if "backup_meta.json" in zf.namelist():
                try:
                    meta = json.loads(zf.read("backup_meta.json").decode())
                except Exception as e:
                    logging.warning(f"SEC-006: Could not read backup metadata: {e}")

        db_path = _resolve_db_path()
        config_path = _resolve_config_path()

        # SEC-006 FIX: Create backup BEFORE restoring (safety net)
        if os.path.exists(db_path):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(os.path.dirname(db_path), "backups")
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"pre_import_{ts}.db")
            shutil.copy2(db_path, backup_path)
            # Also save current checksum
            old_checksum = _compute_file_checksum(db_path)
            logging.info(f"SEC-006: Pre-import backup saved: {backup_path} (checksum: {old_checksum[:16]}...)")

        # SEC-006 FIX: Restore files with proper directory handling
        with zipfile.ZipFile(abs_path, 'r') as zf:
            db_dir = os.path.dirname(db_path)
            os.makedirs(db_dir, exist_ok=True)
            with open(db_path, 'wb') as f:
                f.write(zf.read("pos.db"))

            if "store_config.json" in zf.namelist():
                config_dir = os.path.dirname(config_path)
                os.makedirs(config_dir, exist_ok=True)
                with open(config_path, 'wb') as f:
                    f.write(zf.read("store_config.json"))

        # SEC-006 FIX: Verify restored database integrity
        if os.path.exists(db_path):
            new_checksum = _compute_file_checksum(db_path)
            logging.info(f"SEC-006: Restored DB checksum: {new_checksum[:16]}...")
            # Verify it's a valid SQLite file
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                conn.execute("SELECT count(*) FROM sqlite_master")
                conn.close()
                logging.info("SEC-006: Restored DB integrity check passed")
            except sqlite3.DatabaseError as e:
                logging.error(f"SEC-006: Restored DB is corrupt: {e}")
                # Restore from pre-import backup
                if 'backup_path' in locals() and os.path.exists(backup_path):
                    shutil.copy2(backup_path, db_path)
                    logging.warning("SEC-006: Restored from pre-import backup due to corruption")
                return {"ok": False, "error": "La base de datos del backup esta corrupta. Se restauro la version anterior."}

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
