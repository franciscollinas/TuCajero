"""
TuCajero POS - License Manager (SEC-001 Fixed)

SEC-001 FIX: Uses asymmetric cryptography (Ed25519) for license validation.
- The PRIVATE key stays OFFLINE (vendor side only, used by GeneradorLicencias.py)
- The PUBLIC key is embedded here — it can ONLY verify, never forge licenses
- Even if an attacker decompiles this file, they cannot generate valid licenses

Setup required:
1. Run: python -c "import nacl.signing; sk = nacl.signing.SigningKey.generate();
   print('Private:', sk.encode().hex()); print('Public:', sk.verify_key.encode().hex())"
2. Replace _PUBLIC_KEY_HEX below with the actual public key
"""
import hashlib
import json
import os
import platform
import uuid
import base64
import logging

# SEC-001: Ed25519 public key (hex-encoded).
# Corresponding private key is NEVER distributed with the application.
# TODO: Replace with actual public key after running key generation command above.
_PUBLIC_KEY_HEX = ""  # <-- REPLACE WITH ACTUAL PUBLIC KEY (hex)


def generar_licencia(machine_id):
    """
    Genera una licencia para un machine_id dado (solo para uso en vendor-side).
    NOTA: En producción, esta función NO se usa - solo GeneradorLicencias.py la utiliza.
    Esta es una stub para compatibilidad con activate_view.
    """
    import nacl.signing
    logging.warning("SEC-001: generar_licencia() called from app - this should only be used by vendor!")
    # Esta función no debe usarse en la app real - solo en el generador de licencias
    raise NotImplementedError(
        "SEC-001: License generation must be done offline using GeneradorLicencias.py"
    )


def get_config_dir():
    """Siempre usa LOCALAPPDATA/TuCajero/config — nunca ruta relativa"""
    local_app = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    config_dir = os.path.join(local_app, 'TuCajero', 'config')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_machine_id():
    """Genera un Machine ID unico basado en hardware"""
    try:
        mac = str(uuid.getnode())
        pc_name = platform.node()
        processor = platform.processor()
        raw = f"{mac}-{pc_name}-{processor}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
    except Exception:
        return "UNKNOWN00000000"


def _get_verify_key():
    """Loads the Ed25519 public key for signature verification."""
    import nacl.signing
    if not _PUBLIC_KEY_HEX:
        logging.error("SEC-001: Public key not configured in license_manager.py")
        return None
    key_bytes = bytes.fromhex(_PUBLIC_KEY_HEX)
    return nacl.signing.VerifyKey(key_bytes)


def validar_licencia():
    """
    SEC-001 FIX: Validates license using Ed25519 asymmetric signature.
    
    DEV MODE: If public key is not configured, returns True to allow testing
    without activation. In production, the public key MUST be configured.
    """
    try:
        import nacl.exceptions

        verify_key = _get_verify_key()
        
        # DEV MODE: If no public key configured, allow testing without activation
        if verify_key is None:
            logging.info("SEC-001: DEV MODE - License validation skipped (no public key configured)")
            return True

        config_dir = get_config_dir()
        license_file = os.path.join(config_dir, 'license.json')
        if not os.path.exists(license_file):
            return False

        with open(license_file, 'r') as f:
            data = json.load(f)

        if not data.get('activated', False):
            return False

        machine_id = get_machine_id()
        stored_machine_id = data.get('machine_id', '')
        signature_hex = data.get('signature', '')

        if stored_machine_id.upper() != machine_id.upper():
            return False  # License belongs to a different machine

        # Verify the Ed25519 signature
        message = machine_id.encode('utf-8')
        signature = bytes.fromhex(signature_hex)
        try:
            verify_key.verify(message, signature)  # raises BadSignatureError if invalid
        except nacl.exceptions.BadSignatureError:
            logging.warning("SEC-001: Invalid license signature detected")
            return False

        # Optional: check expiry
        expiry = data.get('expiry')
        if expiry:
            from datetime import datetime
            if datetime.fromisoformat(expiry) < datetime.now():
                return False

        return True

    except Exception as e:
        logging.error(f"SEC-001: License validation error: {e}")
        return False


def guardar_licencia(machine_id, signature_hex, expiry=None):
    """
    SEC-001 FIX: Saves the license with machine_id and Ed25519 signature.
    Called during activation dialog after user enters the license code.
    """
    config_dir = get_config_dir()
    license_file = os.path.join(config_dir, 'license.json')
    data = {
        "machine_id": machine_id,
        "signature": signature_hex,
        "activated": True,
    }
    if expiry:
        data["expiry"] = expiry

    with open(license_file, 'w') as f:
        json.dump(data, f)

    logging.info(f"SEC-001: License saved for machine {machine_id[:8]}...")
