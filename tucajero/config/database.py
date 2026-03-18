"""
Módulo de base de datos para TuCajero.
Usa context managers para manejo seguro de sesiones.
NO usar sesiones globales.
"""

import os
import sys
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

Base = declarative_base()
_engine = None
_SessionFactory = None

logger = logging.getLogger(__name__)


def get_data_dir():
    """Retorna el directorio de datos de la aplicación."""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        return os.path.join(base, "TuCajero")
    return os.path.join(os.path.expanduser("~"), ".tucajero")


def get_base_dir():
    """Retorna el directorio base de la aplicación."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def crear_carpetas():
    """Crea la estructura de carpetas necesaria."""
    data_dir = get_data_dir()

    for subdir in ["database", "database/backups", "logs", "config"]:
        path = os.path.join(data_dir, subdir)
        os.makedirs(path, exist_ok=True)


def get_db_path():
    """Retorna la ruta completa de la base de datos."""
    return os.path.join(get_data_dir(), "database", "pos.db")


def get_logs_dir():
    """Retorna el directorio de logs."""
    return os.path.join(get_data_dir(), "logs")


def get_log_file():
    """Retorna la ruta completa del archivo de log."""
    return os.path.join(get_logs_dir(), "app.log")


def _init_engine():
    """Crea el motor de base de datos (interno)."""
    global _engine, _SessionFactory

    if _engine is not None:
        return

    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    _engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        connect_args={
            "check_same_thread": False,
            "timeout": 30,
        },
        poolclass=StaticPool,
        pool_pre_ping=True,
    )

    _SessionFactory = sessionmaker(bind=_engine)

    logger.debug(f"Engine creado. DB: {db_path}")


def get_engine():
    """Retorna el motor de base de datos (crea si no existe)."""
    global _engine
    if _engine is None:
        _init_engine()
    return _engine


def get_session_factory():
    """Retorna la fábrica de sesiones."""
    global _SessionFactory
    if _SessionFactory is None:
        _init_engine()
    return _SessionFactory


@contextmanager
def session_scope():
    """
    Context manager para manejo de sesiones.

    Uso:
        with session_scope() as session:
            session.query(...)
            session.commit()

    La sesión se cierra automáticamente, incluso si hay excepciones.
    """
    Session = get_session_factory()
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session():
    """
    Retorna una sesión NUEVA (no reuse).
    USO PRINCIPAL: Donde se requiere compartir la misma sesión entre
    múltiples operaciones (ej: vista principal).

    RESPONSABILIDAD DEL CALLER: Cerrar la sesión cuando termine.

    Preferir session_scope() cuando sea posible.
    """
    Session = get_session_factory()
    return Session()


def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    crear_carpetas()

    from models.producto import (
        Producto,
        Venta,
        VentaItem,
        MovimientoInventario,
        CorteCaja,
        PagoVenta,
        Categoria,
    )

    engine = get_engine()
    Base.metadata.create_all(engine)

    logger.info("Base de datos inicializada")


def _wal_checkpoint():
    """Ejecuta checkpoint WAL internamente."""
    global _engine
    if _engine is not None:
        try:
            with _engine.connect() as conn:
                conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
                conn.commit()
            logger.debug("WAL checkpoint completado")
        except Exception as e:
            logger.warning(f"Error en wal_checkpoint: {e}")


def close_db():
    """
    CIERRE SEGURO de la base de datos.
    Llamar al terminar la aplicación.
    """
    global _engine, _SessionFactory

    try:
        _wal_checkpoint()
    except Exception as e:
        logger.warning(f"Error en checkpoint previo a cierre: {e}")

    if _engine is not None:
        try:
            _engine.dispose()
            _engine = None
            _SessionFactory = None
            logger.info("Motor de BD cerrado correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar motor de BD: {e}")
            _engine = None
            _SessionFactory = None


def is_db_locked():
    """Verifica si la BD parece estar bloqueada por archivos WAL."""
    db_path = get_db_path()
    wal_path = db_path + "-wal"
    shm_path = db_path + "-shm"

    if os.path.exists(wal_path):
        try:
            size = os.path.getsize(wal_path)
            if size > 4096:
                return True
        except:
            pass

    if os.path.exists(shm_path):
        return True

    return False


def cleanup_wal_files():
    """Elimina archivos WAL huerfanos de forma segura."""
    db_path = get_db_path()
    cleaned = []

    for ext in ["-wal", "-shm"]:
        path = db_path + ext
        if os.path.exists(path):
            try:
                os.remove(path)
                cleaned.append(ext.replace("-", ""))
                logger.info(f"Archivo {ext} eliminado")
            except Exception as e:
                logger.warning(f"No se pudo eliminar {path}: {e}")

    return cleaned
