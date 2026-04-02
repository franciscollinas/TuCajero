import sys
import os
import traceback
import logging

# Configurar logging básico
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

print("=" * 70)
print("TEST DE EJECUCIÓN - TuCajeroPOS")
print("=" * 70)

try:
    # Importar main
    print("\n[1/6] Importando tucajero.main...")
    from tucajero.main import main
    print("  ✓ main importado")
    
    # Ejecutar main (esto iniciará la app)
    print("\n[2/6] Ejecutando main()...")
    print("  → Si hay error de licencia/setup, la app saldrá normalmente")
    
    main()
    
    print("\n[3/6] main() completó sin errores")
    
except SystemExit as e:
    print(f"\n⚠ SystemExit: {e.code}")
    if e.code == 0:
        print("  → Salida normal (probablemente sin licencia/setup)")
    else:
        print("  → Salida con error")
        traceback.print_exc()
        
except Exception as e:
    print(f"\n❌ ERROR CRÍTICO: {e}")
    print("\nTraceback:")
    traceback.print_exc()
    
    # Guardar log
    log_file = 'error_test_ejecucion.log'
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(traceback.format_exc())
    print(f"\n📄 Error guardado en: {log_file}")

print("\n" + "=" * 70)
