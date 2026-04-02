import os
import sys
import logging
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
            connect_args={
                "check_same_thread": False,
                "timeout": 30,
            },
            pool_pre_ping=True,
        )

        with _engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()

    return _engine


def get_session():
    """Creates and returns a database session"""
    engine = get_engine()
    Session = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )
    return Session()


def init_db():
    """Initializes the database creating all tables"""
    crear_carpetas()

    from tucajero.models.producto import Producto
    from tucajero.models.cliente import Cliente
    from tucajero.models.cajero import Cajero
    from tucajero.models.cotizacion import Cotizacion, CotizacionItem
    from tucajero.models.proveedor import Proveedor, OrdenCompra, OrdenCompraItem

    engine = get_engine()
    Base.metadata.create_all(engine)
    agregar_columnas_si_existen(engine)
    crear_indices()  # ← AGREGAR ESTA LÍNEA


def agregar_columnas_si_existen(engine):
    """Agrega las nuevas columnas a las tablas existentes si no existen"""
    from sqlalchemy import text

    columnas = [
        ("productos", "unidades_por_empaque", "INTEGER"),
        ("productos", "producto_fraccion_id", "INTEGER"),
        ("productos", "es_fraccion", "BOOLEAN DEFAULT 0"),
        ("productos", "stock_minimo", "INTEGER DEFAULT 0"),
        ("ventas", "cliente_id", "INTEGER"),
        ("ventas", "es_credito", "INTEGER DEFAULT 0"),
        ("ventas", "descuento_tipo", "VARCHAR(20)"),
        ("ventas", "descuento_valor", "FLOAT DEFAULT 0"),
        ("ventas", "descuento_total", "FLOAT DEFAULT 0"),
        ("ventas", "cajero_id", "INTEGER"),
        ("cortes_caja", "cajero_id", "INTEGER"),
        ("productos", "fecha_vencimiento", "DATETIME"),
        ("ventas", "comprobante", "VARCHAR(100)"),
        ("ventas", "numero_factura", "VARCHAR(20)"),
        ("ventas", "motivo_anulacion", "VARCHAR(500)"),
        ("ventas", "usuario_anulacion_id", "INTEGER"),
    ]
    with engine.connect() as conn:
        for tabla, columna, tipo in columnas:
            try:
                result = conn.execute(text(f"PRAGMA table_info({tabla})"))
                columnas_tabla = [row[1] for row in result]
                if columna not in columnas_tabla:
                    if tipo == "BOOLEAN DEFAULT 0":
                        conn.execute(
                            text(
                                f"ALTER TABLE {tabla} ADD COLUMN {columna} INTEGER DEFAULT 0"
                            )
                        )
                    else:
                        conn.execute(
                            text(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
                        )
                    conn.commit()
            except Exception:
                pass


def crear_indices():
    """Crea índices para optimizar consultas frecuentes"""
    from sqlalchemy import text
    
    engine = get_engine()
    
    indices = [
        # Búsqueda rápida de productos por código (muy frecuente)
        "CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo)",
        
        # Filtrar productos activos (casi todas las consultas)
        "CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo)",
        
        # Búsqueda de productos por nombre (búsqueda parcial)
        "CREATE INDEX IF NOT EXISTS idx_productos_nombre ON productos(nombre)",
        
        # Consultas de ventas por fecha (reportes, dashboard)
        "CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha)",
        
        # Filtrar ventas no anuladas (casi todas las consultas)
        "CREATE INDEX IF NOT EXISTS idx_ventas_anulada ON ventas(anulada)",
        
        # Ventas por cliente (historial de cliente)
        "CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(cliente_id)",
        
        # Ventas por cajero (auditoría)
        "CREATE INDEX IF NOT EXISTS idx_ventas_cajero ON ventas(cajero_id)",
        
        # Búsqueda de clientes por nombre
        "CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre)",
        
        # Filtrar clientes activos
        "CREATE INDEX IF NOT EXISTS idx_clientes_activo ON clientes(activo)",
        
        # Movimientos de inventario por producto (muy frecuente)
        "CREATE INDEX IF NOT EXISTS idx_movimientos_producto ON movimientos_inventario(producto_id)",
        
        # Movimientos por fecha (reportes)
        "CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos_inventario(fecha)",
        
        # Índice compuesto para consultas combinadas
        "CREATE INDEX IF NOT EXISTS idx_movimientos_producto_fecha ON movimientos_inventario(producto_id, fecha)",
        
        # Cortes de caja por fecha
        "CREATE INDEX IF NOT EXISTS idx_cortes_fecha ON cortes_caja(fecha_apertura)",
    ]
    
    with engine.connect() as conn:
        for idx_sql in indices:
            try:
                conn.execute(text(idx_sql))
                nombre_idx = idx_sql.split('idx_')[1].split(' ON')[0]
                print(f"  [OK] Índice creado: {nombre_idx}")
            except Exception as e:
                print(f"  [WARN] Error creando índice: {e}")
        conn.commit()

    print("[INFO] Índices de base de datos creados correctamente")


def close_db():
    """Cierra la base de datos correctamente con WAL checkpoint"""
    global _engine
    try:
        if _engine:
            with _engine.connect() as conn:
                conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
                conn.commit()
    except Exception as e:
        logging.error(f"WAL checkpoint error: {e}")
    finally:
        try:
            if _engine:
                _engine.dispose()
                _engine = None
        except Exception as e:
            logging.error(f"Engine dispose error: {e}")


def db_retry(func):
    """Decorador para retry en operaciones de BD"""
    import time
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "database is locked" in str(e).lower() and i < 2:
                    time.sleep(0.5)
                    continue
                raise
        raise Exception("DB bloqueada después de múltiples intentos")

    return wrapper
