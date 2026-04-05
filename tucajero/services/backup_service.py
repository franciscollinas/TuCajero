"""
Servicio para operaciones de backup de la base de datos
"""

import shutil
import datetime
import os


class BackupService:
    """Servicio para gestión de backups de la base de datos"""

    def __init__(self):
        pass

    def get_backups_dir(self):
        """Retorna el directorio de backups"""
        from tucajero.config.database import get_data_dir

        data_dir = get_data_dir()
        backups_dir = os.path.join(data_dir, "backups")
        os.makedirs(backups_dir, exist_ok=True)
        return backups_dir

    def create_backup(self):
        """Crea un backup de la base de datos"""
        from tucajero.config.database import get_db_path

        db_path = get_db_path()

        if not os.path.exists(db_path):
            return None

        now = datetime.datetime.now()
        filename = f"pos_backup_{now.strftime('%Y%m%d_%H%M%S')}.db"
        backup_path = os.path.join(self.get_backups_dir(), filename)

        try:
            shutil.copy2(db_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error al crear backup: {e}")
            return None

    def cleanup_old_backups(self, keep_days=7):
        """Elimina backups mayores a keep_days"""
        import logging
        backups_dir = self.get_backups_dir()
        now = datetime.datetime.now()

        for filename in os.listdir(backups_dir):
            if filename.startswith("pos_backup_") and filename.endswith(".db"):
                filepath = os.path.join(backups_dir, filename)
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                if (now - file_time).days > keep_days:
                    try:
                        os.remove(filepath)
                    except OSError as e:
                        # SEC-004 FIX: Log the error instead of silently swallowing it
                        logging.warning(f"Failed to remove old backup {filepath}: {e}")

    def restore_backup(self, backup_path):
        """Restaura un backup, reemplazando la DB actual"""
        from tucajero.config.database import get_db_path, close_db

        db_path = get_db_path()

        if not os.path.exists(backup_path):
            raise Exception("Backup no encontrado")

        close_db()

        respaldo_actual = db_path + ".old"
        try:
            if os.path.exists(db_path):
                shutil.copy2(db_path, respaldo_actual)
        except Exception as e:
            print(f"Warning: No se pudo crear respaldo de seguridad: {e}")

        try:
            shutil.copy2(backup_path, db_path)
            return True
        except Exception as e:
            raise Exception(f"Error al restaurar backup: {e}")

    def get_available_backups(self):
        """Retorna la lista de backups disponibles"""
        backups_dir = self.get_backups_dir()
        backups = []

        if os.path.exists(backups_dir):
            for filename in os.listdir(backups_dir):
                if filename.startswith("pos_backup_") and filename.endswith(".db"):
                    filepath = os.path.join(backups_dir, filename)
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                    backups.append({
                        "filename": filename,
                        "path": filepath,
                        "date": file_time,
                        "size": os.path.getsize(filepath),
                    })

        return sorted(backups, key=lambda x: x["date"], reverse=True)
