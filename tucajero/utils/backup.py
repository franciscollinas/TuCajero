import shutil
import datetime
import os
import sys


def get_backups_dir():
    """Retorna el directorio de backups"""
    from tucajero.config.database import get_data_dir

    data_dir = get_data_dir()
    backups_dir = os.path.join(data_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)
    return backups_dir


def backup_database():
    """Crea un backup de la base de datos"""
    from tucajero.config.database import get_db_path

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


def backup_semanal():
    """Crea backup automático semanal (solo lunes) y mantiene 4 backups"""
    from tucajero.config.database import get_db_path

    db_path = get_db_path()

    if not os.path.exists(db_path):
        return None

    hoy = datetime.datetime.now()

    if hoy.weekday() != 0:
        return None

    backup_dir = get_backups_dir()
    nombre = f"backup_semanal_{hoy.strftime('%Y%m%d')}.db"
    destino = os.path.join(backup_dir, nombre)

    try:
        if not os.path.exists(destino):
            shutil.copy2(db_path, destino)
    except Exception as e:
        print(f"Error en backup semanal: {e}")

    limpiar_backups(4)
    return destino


def limpiar_backups(max_backups=4):
    """Mantiene solo los últimos N backups"""
    backup_dir = get_backups_dir()

    if not os.path.exists(backup_dir):
        return

    archivos = sorted([f for f in os.listdir(backup_dir) if f.endswith(".db")])

    while len(archivos) > max_backups:
        try:
            os.remove(os.path.join(backup_dir, archivos[0]))
            archivos.pop(0)
        except Exception as e:
            print(f"Error al eliminar backup: {e}")
            break


def restaurar_backup(ruta_backup):
    """Restaura un backup, reemplazando la DB actual (hace backup de seguridad primero)"""
    from tucajero.config.database import get_db_path, close_db

    db_path = get_db_path()

    if not os.path.exists(ruta_backup):
        raise Exception("Backup no encontrado")

    close_db()

    respaldo_actual = db_path + ".old"
    try:
        if os.path.exists(db_path):
            shutil.copy2(db_path, respaldo_actual)
    except Exception as e:
        print(f"Warning: No se pudo crear respaldo de seguridad: {e}")

    try:
        shutil.copy2(ruta_backup, db_path)
        return True
    except Exception as e:
        raise Exception(f"Error al restaurar backup: {e}")
