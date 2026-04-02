import subprocess
import sys
import os

print("=" * 60)
print("TuCajeroPOS - Debug de Ejecución")
print("=" * 60)
print()

exe_path = os.path.join(os.path.dirname(__file__), 'dist', 'TuCajero.exe')
print(f"Ejecutando: {exe_path}")
print()

try:
    result = subprocess.run(
        [exe_path],
        capture_output=True,
        text=True,
        timeout=10
    )
    print("STDOUT:")
    print(result.stdout)
    print()
    print("STDERR:")
    print(result.stderr)
    print()
    print(f"Código de retorno: {result.returncode}")
except subprocess.TimeoutExpired:
    print("La aplicación está corriendo (no se cerró en 10 segundos)")
except Exception as e:
    print(f"Error: {e}")

input("\nPresiona Enter para salir...")
