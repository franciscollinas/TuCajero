import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
_engine = None


def get_data_dir():
    """Returns the data directory for the application.

    Uses %LOCALAPPDATA%/TuCajero for Windows.
    Falls back to user home directory for other platforms.
    """
    if sys.platform == "win32":
        return os.path.join(
            os.environ.get("LOCALAPPDATA", os.environ["APPDATA"]), "TuCajero"
        )
    else:
        return os.path.join(os.path.expanduser("~"), ".tucajero")


def get_base_dir():
    """Returns the base directory of the application"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def crear_carpetas():
    """Creates necessary folders if they don't exist"""
    data_dir = get_data_dir()

    db_dir = os.path.join(data_dir, "database")
    os.makedirs(db_dir, exist_ok=True)

    backups_dir = os.path.join(db_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)

    logs_dir = os.path.join(data_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    config_dir = os.path.join(data_dir, "config")
    os.makedirs(config_dir, exist_ok=True)


def get_db_path():
    """Returns the database path - always uses %LOCALAPPDATA%"""
    data_dir = get_data_dir()
    db_dir = os.path.join(data_dir, "database")
    return os.path.join(db_dir, "pos.db")


def get_logs_dir():
    """Returns the logs directory"""
    data_dir = get_data_dir()
    return os.path.join(data_dir, "logs")


def get_log_file():
    """Returns the full path to the log file"""
    return os.path.join(get_logs_dir(), "app.log")


def get_engine():
    """Creates and returns the database engine with production config"""
    global _engine
    if _engine is None:
        db_path = get_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        _engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )

        with _engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA foreign_keys=ON"))

    return _engine


def get_session():
    """Creates and returns a database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initializes the database creating all tables"""
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
