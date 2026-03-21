import hashlib
import base64

_S = b"dGl0b19jYXN0aWxsYV9wb3Nfc2VjcmV0"

def generar_licencia(machine_id):
    secret = base64.b64decode(_S).decode()
    combined = f"{machine_id}{secret}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()

if __name__ == "__main__":
    print("=" * 40)
    print("  TuCajero — Generador de Licencias")
    print("=" * 40)
    machine_id = input("\nIngresa el Machine ID del cliente: ").strip().upper()
    if not machine_id:
        print("Error: Machine ID no puede estar vacío")
    else:
        licencia = generar_licencia(machine_id)
        print(f"\n✅ Licencia generada: {licencia}")
        print("\nEntrega este código al cliente para activar el sistema.")
    input("\nPresiona Enter para cerrar...")
