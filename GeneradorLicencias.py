"""
TuCajero POS - License Generator (SEC-001 Fixed)

SEC-001 FIX: Uses Ed25519 asymmetric signatures for license generation.
The PRIVATE KEY is generated once and kept here — NEVER distributed with the app.

Setup required:
1. Run: python -c "import nacl.signing; sk = nacl.signing.SigningKey.generate();
   print('Private:', sk.encode().hex()); print('Public:', sk.verify_key.encode().hex())"
2. Replace _PRIVATE_KEY_HEX below with the actual private key
3. Copy the public key to tucajero/security/license_manager.py
"""
import base64

# SEC-001: PRIVATE KEY — KEEP THIS FILE SECURE AND NEVER DISTRIBUTE IT
# TODO: Replace with actual private key after running key generation command above.
_PRIVATE_KEY_HEX = ""  # <-- REPLACE WITH ACTUAL PRIVATE KEY (hex)


def generar_licencia(machine_id):
    """
    SEC-001 FIX: Signs the machine_id with Ed25519 private key.
    The resulting signature can only be verified (not forged) by the app's public key.
    """
    import nacl.signing

    if not _PRIVATE_KEY_HEX:
        raise ValueError(
            "SEC-001: Private key not configured in GeneradorLicencias.py. "
            "Run the key generation command and update this file."
        )

    signing_key = nacl.signing.SigningKey(bytes.fromhex(_PRIVATE_KEY_HEX))
    message = machine_id.upper().strip().encode('utf-8')
    signed = signing_key.sign(message)
    # Return the signature as hex (the app will verify this against its public key)
    return signed.signature.hex()


if __name__ == "__main__":
    print("=" * 50)
    print("  TuCajero — Generador de Licencias (Ed25519)")
    print("=" * 50)

    if _PRIVATE_KEY_HEX == "":
        print("\n⚠️  ERROR: Private key not configured!")
        print("Generate a key pair with:")
        print('  python -c "import nacl.signing; sk = nacl.signing.SigningKey.generate();')
        print('  print(\'Private:\', sk.encode().hex()); print(\'Public:\', sk.verify_key.encode().hex())"')
        print("\nThen paste the keys in GeneradorLicencias.py and license_manager.py")
        input("\nPresiona Enter para cerrar...")
        exit(1)

    machine_id = input("\nIngresa el Machine ID del cliente: ").strip().upper()
    if not machine_id:
        print("Error: Machine ID no puede estar vacio")
    else:
        try:
            licencia = generar_licencia(machine_id)
            print(f"\n✅ Licencia generada (signature): {licencia}")
            print("\nEntrega este codigo al cliente para activar el sistema.")
        except Exception as e:
            print(f"\n❌ Error generando licencia: {e}")
    input("\nPresiona Enter para cerrar...")
