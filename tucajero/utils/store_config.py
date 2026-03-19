import json
import os
import sys

DEFAULT_CONFIG = {
    "store_name": "",
    "logo_path": "",
    "address": "",
    "phone": "",
    "email": "",
    "nit": "",
    "setup_complete": False,
}

_store_config = None


def get_config_dir():
    """Retorna el directorio de configuración en %LOCALAPPDATA%"""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        return os.path.join(base, "TuCajero", "config")
    return os.path.join(os.path.expanduser("~"), ".tucajero", "config")


def _get_config_path():
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "store_config.json")


def config_exists():
    """Retorna True si ya existe configuración guardada"""
    path = _get_config_path()
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return bool(data.get("store_name", "").strip())
    except Exception:
        return False


def load_store_config():
    global _store_config
    config_path = _get_config_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                _store_config = json.load(f)
        else:
            _store_config = DEFAULT_CONFIG.copy()
    except (json.JSONDecodeError, IOError):
        _store_config = DEFAULT_CONFIG.copy()
    return _store_config


def save_store_config(config_data):
    config_path = _get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        global _store_config
        _store_config = config_data
        return True
    except IOError:
        return False


def get_store_name():
    if _store_config is None:
        load_store_config()
    return _store_config.get("store_name", "")


def _get_default_logo():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo = os.path.join(base, "assets", "icons", "logo.png")
    if os.path.exists(logo):
        return logo
    return ""


def get_logo_path():
    if _store_config is None:
        load_store_config()
    logo = _store_config.get("logo_path", "")
    if logo and os.path.exists(logo):
        return logo
    return _get_default_logo()


def get_address():
    if _store_config is None:
        load_store_config()
    return _store_config.get("address", "")


def get_phone():
    if _store_config is None:
        load_store_config()
    return _store_config.get("phone", "")


def get_email():
    if _store_config is None:
        load_store_config()
    return _store_config.get("email", "")


def get_nit():
    if _store_config is None:
        load_store_config()
    return _store_config.get("nit", "")


def is_setup_complete():
    if _store_config is None:
        load_store_config()
    return _store_config.get("setup_complete", False)
