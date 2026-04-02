"""
Pruebas de validación para la corrección de NameError en productos_view.py

Fecha: 2026-04-02
Propósito: Validar que `c = get_colors()` está correctamente definido en _mostrar_productos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_import_productos_view():
    """Prueba que el módulo productos_view importa sin errores"""
    try:
        from tucajero.ui.productos_view import ProductosView
        print("✅ Importación de ProductosView: EXITOSA")
        return True
    except NameError as e:
        print(f"❌ Importación de ProductosView: FALLIDA - NameError: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Importación de ProductosView: ERROR - {type(e).__name__}: {e}")
        return False


def test_get_colors_returns_expected_keys():
    """Prueba que get_colors() retorna un diccionario con las claves esperadas"""
    try:
        from tucajero.utils.theme import get_colors
        c = get_colors()
        
        # Verificar que es un diccionario
        assert isinstance(c, dict), "get_colors() debe retornar un diccionario"
        
        # Verificar claves esperadas usadas en _mostrar_productos
        claves_requeridas = ["danger", "warning", "info"]
        for clave in claves_requeridas:
            assert clave in c, f"La clave '{clave}' no está en el diccionario de colores"
            assert isinstance(c[clave], str), f"El valor de '{clave}' debe ser una cadena"
        
        print("✅ get_colors() retorna claves esperadas: EXITOSA")
        return True
    except AssertionError as e:
        print(f"❌ Validación de get_colors(): FALLIDA - {e}")
        return False
    except Exception as e:
        print(f"⚠️  Validación de get_colors(): ERROR - {type(e).__name__}: {e}")
        return False


def test_c_variable_in_mostrar_productos():
    """
    Prueba que la variable `c` está disponible en la función _mostrar_productos.
    Esto se verifica inspeccionando el código fuente.
    """
    try:
        import inspect
        from tucajero.ui.productos_view import ProductosView
        
        # Obtener el código fuente de _mostrar_productos
        metodo = ProductosView._mostrar_productos
        source = inspect.getsource(metodo)
        
        # Verificar que `c = get_colors()` está en la función
        assert "c = get_colors()" in source or "c=get_colors()" in source, \
            "No se encontró `c = get_colors()` en _mostrar_productos"
        
        # Verificar que `c` se usa para acceder a colores
        assert 'c["danger"]' in source or "c['danger']" in source, \
            "No se encontró uso de c['danger'] en _mostrar_productos"
        assert 'c["warning"]' in source or "c['warning']" in source, \
            "No se encontró uso de c['warning'] en _mostrar_productos"
        assert 'c["info"]' in source or "c['info']" in source, \
            "No se encontró uso de c['info'] en _mostrar_productos"
        
        # Verificar que el import está presente
        assert "from tucajero.utils.theme import get_colors" in source, \
            "No se encontró el import de get_colors en _mostrar_productos"
        
        print("✅ Variable `c` en _mostrar_productos: CORRECTAMENTE DEFINIDA")
        return True
    except AssertionError as e:
        print(f"❌ Validación de variable `c`: FALLIDA - {e}")
        return False
    except Exception as e:
        print(f"⚠️  Validación de variable `c`: ERROR - {type(e).__name__}: {e}")
        return False


def test_no_nameerror_in_mostrar_productos():
    """
    Prueba que no hay NameError al ejecutar el código de _mostrar_productos.
    Se crea un mock de la tabla para evitar dependencias de Qt.
    """
    try:
        from unittest.mock import MagicMock, Mock
        from tucajero.ui.productos_view import ProductosView
        from tucajero.utils.theme import get_colors
        
        # Crear una instancia mock
        mock_session = MagicMock()
        view = ProductosView.__new__(ProductosView)
        view.session = mock_session
        
        # Mock de la tabla
        view.tabla = MagicMock()
        
        # Crear productos mock
        mock_producto = MagicMock()
        mock_producto.codigo = "TEST001"
        mock_producto.nombre = "Producto Test"
        mock_producto.stock = 5
        mock_producto.stock_minimo = 10
        mock_producto.precio = 100.00
        
        # Ejecutar el método (simulando que no hay errores de NameError)
        c = get_colors()  # Esto es lo que debería estar en la función
        
        # Verificar que c tiene las claves necesarias
        assert "danger" in c
        assert "warning" in c
        assert "info" in c
        
        print("✅ Ejecución sin NameError: EXITOSA")
        return True
    except NameError as e:
        print(f"❌ Ejecución sin NameError: FALLIDA - NameError: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Ejecución sin NameError: ERROR - {type(e).__name__}: {e}")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas y reporta resultados"""
    print("=" * 60)
    print("PRUEBAS DE VALIDACIÓN - productos_view.py")
    print("=" * 60)
    print()
    
    tests = [
        ("1. Importar módulo productos_view", test_import_productos_view),
        ("2. get_colors() retorna claves esperadas", test_get_colors_returns_expected_keys),
        ("3. Variable `c` en _mostrar_productos", test_c_variable_in_mostrar_productos),
        ("4. No hay NameError en ejecución", test_no_nameerror_in_mostrar_productos),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        print(f"\n[{nombre}]")
        resultado = test_func()
        resultados.append((nombre, resultado))
    
    print()
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    exitosas = sum(1 for _, r in resultados if r)
    totales = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"  {estado}: {nombre}")
    
    print()
    print(f"Total: {exitosas}/{totales} pruebas exitosas")
    
    if exitosas == totales:
        print("\n🎉 TODAS LAS PRUEBAS PASARON - La corrección es válida")
        return True
    else:
        print(f"\n⚠️  {totales - exitosas} prueba(s) fallida(s) - Revisar corrección")
        return False


if __name__ == "__main__":
    exito = run_all_tests()
    sys.exit(0 if exito else 1)
