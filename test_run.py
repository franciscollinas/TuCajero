import sys
import os
import traceback

# Agregar tucajero al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tucajero'))

print("=" * 60)
print("INICIANDO PRUEBA DE TUCAJERO")
print("=" * 60)

try:
    print("\n[1/5] Importando main...")
    from tucajero.main import main
    print("    OK - main importado")
    
    print("\n[2/5] Ejecutando main()...")
    main()
    print("    OK - main ejecutado")
    
except Exception as e:
    print("\n" + "=" * 60)
    print("ERROR CRÍTICO DETECTADO")
    print("=" * 60)
    print(f"\nExcepción: {e}")
    print(f"\nTraceback completo:\n")
    traceback.print_exc()
    print("\n" + "=" * 60)
    input("Presiona Enter para salir...")
    sys.exit(1)
