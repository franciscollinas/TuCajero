"""
TuCajero - Generador de Licencias
Herramienta para generar licencias para clientes.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.license_manager import get_machine_id, generar_licencia
from utils.store_config import get_store_name


def main():
    """Función principal"""
    store_name = get_store_name()
    print()
    print("=" * 30)
    print(f"{store_name.upper()}")
    print("GENERADOR DE LICENCIAS")
    print("=" * 30)
    print()

    print("Opciones:")
    print("1. Generar licencia para esta computadora")
    print("2. Generar licencia con Machine ID personalizado")
    print()

    opcion = input("Seleccione una opcion (1/2): ").strip()

    print()

    if opcion == "1":
        machine_id = get_machine_id()
        print(f"Machine ID de esta computadora:")
        print(f"  {machine_id}")
    elif opcion == "2":
        machine_id = input("Ingresar Machine ID: ").strip()
        if not machine_id:
            print("Error: Debe ingresar un Machine ID")
            return
    else:
        print("Opcion invalida")
        return

    licencia = generar_licencia(machine_id)

    print()
    print("-" * 30)
    print("RESULTADO:")
    print("-" * 30)
    print()
    print(f"Machine ID: {machine_id}")
    print(f"Licencia:   {licencia}")
    print()
    print("=" * 30)
    print()
    print("Instrucciones:")
    print("1. Copie la licencia generada")
    print("2. En el sistema del cliente, vaya a Activacion")
    print("3. Ingrese la licencia")
    print("4. El sistema se activara automaticamente")
    print()


if __name__ == "__main__":
    main()
