"""
Utilidades de backup para TuCajero.
"""

import shutil
import datetime
import os
import logging

logger = logging.getLogger(__name__)


def get_backups_dir():
    """Retorna el directorio de backups."""
    from config.database import get_data_dir

    data_dir = get_data_dir()
    return os.path.join(data_dir, "database", "backups")


def backup_database():
    """Crea un backup de la base de datos."""
    from config.database import get_db_path

    db_path = get_db_path()

    if not os.path.exists(db_path):
        logger.warning("BD no existe, no se puede hacer backup")
        return None

    os.makedirs(get_backups_dir(), exist_ok=True)

    now = datetime.datetime.now()
    filename = f"pos_backup_{now.strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(get_backups_dir(), filename)

    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"Backup creado: {filename}")
        return backup_path
    except Exception as e:
        logger.error(f"Error al crear backup: {e}")
        return None


def cleanup_old_backups(keep_days=7):
    """Elimina backups mayores a keep_days."""
    backups_dir = get_backups_dir()

    if not os.path.exists(backups_dir):
        return 0

    now = datetime.datetime.now()
    deleted = 0

    for filename in os.listdir(backups_dir):
        if filename.startswith("pos_backup_") and filename.endswith(".db"):
            filepath = os.path.join(backups_dir, filename)
            try:
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                if (now - file_time).days > keep_days:
                    os.remove(filepath)
                    deleted += 1
            except Exception as e:
                logger.warning(f"Error al eliminar backup antiguo {filename}: {e}")

    if deleted:
        logger.info(f"Eliminados {deleted} backups antiguos")

    return deleted
