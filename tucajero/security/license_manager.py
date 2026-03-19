import uuid
import hashlib
import json
import os
import sys
import platform

SECRET = "tito_castilla_pos_secret"


def get_config_dir():
    """Retorna el directorio de configuración en %LOCALAPPDATA%"""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        return os.path.join(base, "TuCajero", "config")
    return os.path.join(os.path.expanduser("~"), ".tucajero", "config")


def get_machine_id():
    """Obtiene un identificador único robusto de la computadora"""
    components = [
        str(uuid.getnode()),
        platform.node(),
        platform.processor() or "unknown",
        platform.machine() or "unknown",
    ]
    combined = "|".join(components)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def generar_licencia(machine_id):
    """Genera una licencia basada en el machine_id"""
    licencia = hashlib.sha256((machine_id + SECRET).encode()).hexdigest()[:16]
    return licencia.upper()


def get_license_path():
    """Retorna la ruta del archivo de licencia en %LOCALAPPDATA%"""
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "license.json")


def cargar_licencia():
    """Carga la configuración de licencia"""
    license_path = get_license_path()
    if not os.path.exists(license_path):
        return {"activated": False, "license_key": ""}

    try:
        with open(license_path, "r") as f:
            return json.load(f)
    except:
        return {"activated": False, "license_key": ""}


def guardar_licencia(license_key):
    """Guarda la licencia en el archivo"""
    license_path = get_license_path()
    data = {"activated": True, "license_key": license_key.upper()}
    with open(license_path, "w") as f:
        json.dump(data, f, indent=4)
    return True


def validar_licencia():
    """Valida si la licencia es correcta"""
    licencia_data = cargar_licencia()

    if not licencia_data.get("activated", False):
        return False

    machine_id = get_machine_id()
    licencia_correcta = generar_licencia(machine_id)

    return licencia_data.get("license_key", "").upper() == licencia_correcta


def crear_license_default():
    """Crea el archivo de licencia por defecto"""
    license_path = get_license_path()
    if not os.path.exists(license_path):
        data = {"activated": False, "license_key": ""}
        with open(license_path, "w") as f:
            json.dump(data, f, indent=4)
