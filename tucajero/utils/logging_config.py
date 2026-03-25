import os
import sys


def get_logs_path():
    """Retorna la ruta del archivo de logs según la plataforma"""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        logs_dir = os.path.join(base, "TuCajero", "logs")
    else:
        logs_dir = os.path.join(os.path.expanduser("~"), ".tucajero", "logs")

    os.makedirs(logs_dir, exist_ok=True)
    return os.path.join(logs_dir, "app.log")


def get_data_dir():
    """Retorna el directorio de datos de la aplicación"""
    if sys.platform == "win32":
        return os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
    else:
        return os.path.expanduser("~")


def setup_logging():
    """Configura el logging global para producción"""
    log_path = get_logs_path()

    import logging
    from logging.handlers import RotatingFileHandler

    handler = RotatingFileHandler(log_path, maxBytes=1000000, backupCount=3)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    if not getattr(sys, "frozen", False):
        root_logger.addHandler(logging.StreamHandler())

    return log_path
