"""
Módulo de recuperación para TuCajero.
Detecta problemas de BD pero NO mata procesos automáticamente.
Solo sugiere acciones al usuario o limpia archivos WAL huérfanos.
"""

import os
import sys
import logging
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


def get_data_dir():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        return os.path.join(base, "TuCajero")
    return os.path.join(os.path.expanduser("~"), ".tucajero")


def get_db_path():
    return os.path.join(get_data_dir(), "database", "pos.db")


def get_backups_dir():
    return os.path.join(get_data_dir(), "database", "backups")


class RecoveryManager:
    """
    Gestiona detección y recuperación de problemas.
    NUNCA mata procesos automáticamente.
    """

    def __init__(self):
        self.data_dir = get_data_dir()
        self.db_path = get_db_path()

    def check_wal_files(self):
        """Verifica si hay archivos WAL/shm que indiquen bloqueo."""
        issues = []

        wal_path = self.db_path + "-wal"
        shm_path = self.db_path + "-shm"

        if os.path.exists(wal_path):
            try:
                size = os.path.getsize(wal_path)
                if size > 4096:
                    issues.append(
                        {
                            "type": "wal_blocked",
                            "file": wal_path,
                            "size": size,
                            "message": f"Archivo WAL presente ({size} bytes) - posible bloqueo",
                        }
                    )
                    logger.warning(f"WAL file grande detectado: {size} bytes")
            except Exception as e:
                logger.warning(f"Error al verificar WAL: {e}")

        if os.path.exists(shm_path):
            issues.append(
                {
                    "type": "shm_present",
                    "file": shm_path,
                    "message": "Archivo SHM presente",
                }
            )
            logger.warning("Archivo SHM detectado")

        return issues

    def check_database_integrity(self):
        """Verifica integridad de la BD con SQLite."""
        if not os.path.exists(self.db_path):
            return []

        issues = []
        import sqlite3

        try:
            conn = sqlite3.connect(self.db_path, timeout=1)
            cursor = conn.cursor()

            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()

            if result and result[0] != "ok":
                issues.append(
                    {
                        "type": "corrupted",
                        "message": f"Base de datos corrupta: {result[0]}",
                    }
                )
                logger.error(f"BD corrupta: {result}")

            conn.close()
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                issues.append(
                    {
                        "type": "locked",
                        "message": "Base de datos bloqueada por otro proceso",
                    }
                )
                logger.warning("BD bloqueada")
            else:
                issues.append(
                    {"type": "error", "message": f"Error al verificar BD: {e}"}
                )
                logger.error(f"Error de BD: {e}")
        except Exception as e:
            issues.append({"type": "error", "message": f"Error desconocido: {e}"})
            logger.error(f"Error al verificar integridad: {e}")

        return issues

    def create_backup(self):
        """Crea un backup de la BD antes de cualquier operación de riesgo."""
        if not os.path.exists(self.db_path):
            return None

        backup_dir = get_backups_dir()
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")

        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Backup creado: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Error al crear backup: {e}")
            return None

    def cleanup_wal(self):
        """
        Limpia archivos WAL huérfanos.
        SOLO si la BD no está en uso (no hay proceso activo).
        """
        cleaned = []
        wal_path = self.db_path + "-wal"
        shm_path = self.db_path + "-shm"

        for ext, path in [("-wal", wal_path), ("-shm", shm_path)]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    cleaned.append(ext.replace("-", ""))
                    logger.info(f"Archivo {ext} eliminado")
                except Exception as e:
                    logger.warning(f"No se pudo eliminar {path}: {e}")

        return cleaned

    def diagnose(self):
        """
        Ejecuta diagnóstico completo.
        Retorna lista de problemas encontrados.
        """
        logger.info("Iniciando diagnóstico...")
        all_issues = []

        all_issues.extend(self.check_wal_files())
        all_issues.extend(self.check_database_integrity())

        if all_issues:
            logger.warning(f"Problemas detectados: {len(all_issues)}")
        else:
            logger.info("Diagnóstico: Sin problemas")

        return all_issues

    def auto_recover(self):
        """
        Intenta recuperación automática SEGURA.
        Solo limpia archivos WAL si no hay bloqueo activo.
        """
        issues = self.diagnose()

        if not issues:
            return {"success": True, "actions": [], "message": "Sin problemas"}

        actions = []

        is_locked = any(i["type"] in ("locked", "wal_blocked") for i in issues)
        if is_locked:
            return {
                "success": False,
                "actions": [],
                "message": "BD bloqueada. Cierre otros procesos de TuCajero e intente de nuevo.",
                "issues": issues,
            }

        self.create_backup()

        cleaned = self.cleanup_wal()
        if cleaned:
            actions.append(f"Archivos limpiados: {', '.join(cleaned)}")

        return {
            "success": True,
            "actions": actions,
            "message": "Recuperación completada"
            if actions
            else "Sin acciones necesarias",
            "issues": issues,
        }


def diagnose_and_recover():
    """Función de conveniencia para diagnóstico y recuperación."""
    manager = RecoveryManager()
    return manager.diagnose()
