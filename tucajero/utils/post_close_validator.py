"""
Validador post-cierre para verificar que la app se cerró correctamente.
"""

import os
import sys
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)


def get_data_dir():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        return os.path.join(base, "TuCajero")
    return os.path.join(os.path.expanduser("~"), ".tucajero")


def get_db_path():
    return os.path.join(get_data_dir(), "database", "pos.db")


class PostCloseValidator:
    """Valida que la aplicación se cerró correctamente."""

    def __init__(self):
        self.db_path = get_db_path()
        self.issues = []

    def check_db_exists(self):
        """Verifica que la BD existe."""
        if not os.path.exists(self.db_path):
            self.issues.append("BD no existe")
            return False
        return True

    def check_db_accessible(self):
        """Verifica que la BD es accesible (no bloqueada)."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=1)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()
            conn.close()
            logger.info(f"BD accesible. Journal mode: {journal_mode[0]}")
            return True
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                self.issues.append("BD bloqueada después del cierre")
                logger.error("BD bloqueada")
            else:
                self.issues.append(f"BD no accesible: {e}")
                logger.error(f"BD no accesible: {e}")
            return False
        except Exception as e:
            self.issues.append(f"Error al verificar BD: {e}")
            logger.error(f"Error al verificar BD: {e}")
            return False

    def check_wal_files(self):
        """Verifica archivos WAL residuales."""
        wal_path = self.db_path + "-wal"
        shm_path = self.db_path + "-shm"

        for path, name in [(wal_path, "WAL"), (shm_path, "SHM")]:
            if os.path.exists(path):
                size = os.path.getsize(path) if os.path.getsize(path) > 0 else 0
                if size > 0:
                    self.issues.append(f"Archivo {name} residual ({size} bytes)")
                    logger.warning(f"Archivo {name} residual encontrado")
                else:
                    try:
                        os.remove(path)
                        logger.info(f"Archivo {name} vacío eliminado")
                    except:
                        pass

    def check_integrity(self):
        """Verifica integridad de la BD."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=5)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()

            if result and result[0] != "ok":
                self.issues.append(f"BD corrupta: {result[0]}")
                logger.error(f"BD corrupta: {result[0]}")
                return False
            return True
        except Exception as e:
            self.issues.append(f"Error en integridad: {e}")
            logger.error(f"Error en integridad: {e}")
            return False

    def validate(self):
        """
        Ejecuta validación completa post-cierre.
        Retorna (success, issues).
        """
        logger.info("Iniciando validación post-cierre...")

        if not self.check_db_exists():
            return False, self.issues

        self.check_db_accessible()
        self.check_wal_files()
        self.check_integrity()

        if self.issues:
            logger.warning(f"Problemas post-cierre: {self.issues}")
            return False, self.issues

        logger.info("Validación post-cierre: OK")
        return True, []

    def cleanup_if_needed(self):
        """
        Limpia archivos residuales si los hay.
        Retorna True si se limpió algo.
        """
        cleaned = []

        wal_path = self.db_path + "-wal"
        shm_path = self.db_path + "-shm"

        for path, name in [(wal_path, "WAL"), (shm_path, "SHM")]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    cleaned.append(name)
                    logger.info(f"Limpiado archivo {name}")
                except Exception as e:
                    logger.warning(f"No se pudo limpiar {name}: {e}")

        return cleaned


def validate_post_close():
    """Función de conveniencia para validación."""
    validator = PostCloseValidator()
    success, issues = validator.validate()

    if issues:
        cleaned = validator.cleanup_if_needed()
        if cleaned:
            logger.info(f"Archivos limpiados: {cleaned}")

    return success, issues
