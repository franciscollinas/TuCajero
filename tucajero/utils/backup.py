import shutil
import datetime
import os
import sys


def get_backups_dir():
    """Retorna el directorio de backups"""
    from config.database import get_data_dir

    data_dir = get_data_dir()
    backups_dir = os.path.join(data_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)
    return backups_dir


def backup_database():
    """Crea un backup de la base de datos"""
    from config.database import get_db_path

    db_path = get_db_path()

    if not os.path.exists(db_path):
        return None

    now = datetime.datetime.now()
    filename = f"pos_backup_{now.strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(get_backups_dir(), filename)

    try:
        shutil.copy2(db_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Error al crear backup: {e}")
        return None


def cleanup_old_backups(keep_days=7):
    """Elimina backups mayores a keep_days"""
    backups_dir = get_backups_dir()
    now = datetime.datetime.now()

    for filename in os.listdir(backups_dir):
        if filename.startswith("pos_backup_") and filename.endswith(".db"):
            filepath = os.path.join(backups_dir, filename)
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            if (now - file_time).days > keep_days:
                try:
                    os.remove(filepath)
                except:
                    pass
