import hashlib
import base64
import json
import os
import platform
import uuid

_S = b"dGl0b19jYXN0aWxsYV9wb3Nfc2VjcmV0"

def get_config_dir():
    """Siempre usa %LOCALAPPDATA%\TuCajero\config — nunca ruta relativa"""
    local_app = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    config_dir = os.path.join(local_app, 'TuCajero', 'config')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_machine_id():
    """Genera un Machine ID único basado en hardware"""
    try:
        mac = str(uuid.getnode())
        pc_name = platform.node()
        processor = platform.processor()
        raw = f"{mac}-{pc_name}-{processor}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
    except Exception:
        return "UNKNOWN00000000"

def generar_licencia(machine_id):
    """Genera la licencia correcta para un machine_id dado"""
    secret = base64.b64decode(_S).decode()
    combined = f"{machine_id}{secret}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()

def guardar_licencia(licencia):
    """Guarda la licencia en %LOCALAPPDATA%\TuCajero\config\license.json"""
    config_dir = get_config_dir()
    license_file = os.path.join(config_dir, 'license.json')
    with open(license_file, 'w') as f:
        json.dump({"license": licencia, "activated": True}, f)

def validar_licencia():
    """Retorna True si la licencia guardada es válida para esta máquina"""
    try:
        config_dir = get_config_dir()
        license_file = os.path.join(config_dir, 'license.json')
        if not os.path.exists(license_file):
            return False
        with open(license_file, 'r') as f:
            data = json.load(f)
        if not data.get('activated', False):
            return False
        saved = data.get('license', '')
        machine_id = get_machine_id()
        expected = generar_licencia(machine_id)
        return saved.upper() == expected.upper()
    except Exception:
        return False
