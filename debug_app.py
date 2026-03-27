import sys
import os
import traceback
import ctypes

# Mostrar consola para debug
ctypes.windll.user32.MessageBoxW(0, "Iniciando debug...", "TuCajero Debug", 0)

try:
    print("=" * 60)
    print("DEBUG DE TUCAJERO - Paso a paso")
    print("=" * 60)
    
    # Paso 1: Verificar ruta
    print("\n[1] Verificando rutas...")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    print(f"    BASE_DIR: {BASE_DIR}")
    
    # Paso 2: Importar main
    print("\n[2] Importando tucajero.main...")
    sys.path.insert(0, os.path.join(BASE_DIR, 'tucajero'))
    import main
    print("    OK - main importado")
    
    # Paso 3: Ejecutar main
    print("\n[3] Ejecutando main()...")
    main.main()
    print("    OK - main ejecutado")
    
except Exception as e:
    error_text = f"ERROR: {e}\n\n{traceback.format_exc()}"
    print(error_text)
    ctypes.windll.user32.MessageBoxW(0, error_text, "TuCajero - Error Crítico", 0)
    sys.exit(1)
