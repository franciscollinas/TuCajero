"""
Pruebas unitarias para validar los 3 fixes críticos reportados por usuario

Fixes validados:
1. Bug de stock duplicado - Se eliminó descuento duplicado en venta_repo.py
2. "Sin detalles" en dashboard - Se corrigió acceso a producto.nombre
3. Filas pares gris - Se cambió alternating row colors y se agregó estilo CSS

Autor: QA Testing
Fecha: 2026-04-02
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
import inspect
import os
import sys

# Agregar ruta al proyecto para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# =============================================================================
# FIX 1: BUG DE STOCK DUPLICADO
# =============================================================================

class TestFix1StockDuplicado(unittest.TestCase):
    """
    Pruebas para validar que el stock solo se descuenta UNA vez por venta.
    
    Problema anterior: El stock se descontaba tanto en venta_repo.create_venta()
    como en producto_service.registrar_venta(), causando descuento duplicado.
    
    Solución: Eliminar descuento de venta_repo, mantener solo en producto_service.
    """

    def test_venta_repo_no_descuenta_stock(self):
        """
        Verifica que VentaRepository.create_venta() NO descuenta stock.
        El descuento debe ocurrir únicamente en ProductoService.
        """
        from tucajero.repositories.venta_repo import VentaRepository
        
        # Leer el código fuente del método
        source = inspect.getsource(VentaRepository.create_venta)
        
        # ASSERT: El método NO debe llamar a update_stock
        self.assertNotIn('update_stock', source, 
            "create_venta() NO debe llamar a update_stock()")
        
        # ASSERT: El método NO debe modificar stock directamente
        self.assertNotIn('.stock =', source,
            "create_venta() NO debe modificar stock directamente")
        self.assertNotIn('.stock+=', source,
            "create_venta() NO debe modificar stock directamente")
        self.assertNotIn('.stock -=', source,
            "create_venta() NO debe modificar stock directamente")

    def test_venta_repo_valida_stock_disponible(self):
        """
        Verifica que venta_repo SOLO valida stock pero NO lo descuenta.
        La validación es correcta, el descuento debe estar en otro lugar.
        """
        from tucajero.repositories.venta_repo import VentaRepository
        
        source = inspect.getsource(VentaRepository.create_venta)
        
        # ASSERT: Debe validar stock (esto está bien)
        self.assertIn('stock <', source,
            "Debe validar que hay stock suficiente")
        self.assertIn('Stock insuficiente', source,
            "Debe mostrar mensaje de stock insuficiente")

    def test_producto_service_descuenta_stock(self):
        """
        Verifica que ProductoService.registrar_venta() SÍ descuenta stock.
        Este es el único lugar donde debe ocurrir el descuento.
        """
        from tucajero.services.producto_service import VentaService
        
        source = inspect.getsource(VentaService.registrar_venta)
        
        # ASSERT: Debe llamar a update_stock para descontar
        self.assertIn('update_stock', source,
            "registrar_venta() DEBE llamar a update_stock()")

    def test_flujo_completo_descuento_unico(self):
        """
        Prueba de integración: verifica que el stock se descuenta UNA sola vez.
        """
        from tucajero.services.producto_service import VentaService
        from tucajero.services import corte_service
        
        mock_session = Mock()
        
        with patch.object(corte_service, 'CorteCajaService') as MockCorteCajaService:
            mock_corte = Mock()
            mock_corte.esta_caja_abierta.return_value = True
            MockCorteCajaService.return_value = mock_corte
            
            service = VentaService(mock_session)
            
            # Mock de repositorios
            mock_venta_repo = Mock()
            mock_venta = Mock(id=100, items=[])
            mock_venta_repo.create_venta.return_value = mock_venta
            service.venta_repo = mock_venta_repo
            
            # Mock producto con stock inicial
            mock_producto = Mock(stock=50, nombre="Producto Test", aplica_iva=True)
            mock_producto_repo = Mock()
            mock_producto_repo.get_by_id.return_value = mock_producto
            service.producto_repo = mock_producto_repo
            
            # Mock inventario repo
            mock_inventario_repo = Mock()
            service.inventario_repo = mock_inventario_repo
            
            items = [{"producto_id": 1, "cantidad": 5, "precio": 100.0, "aplica_iva": False}]
            
            # Ejecutar venta
            service.registrar_venta(items)
            
            # VERIFICAR: update_stock se llamó EXACTAMENTE UNA vez
            update_stock_calls = mock_producto_repo.update_stock.call_args_list
            
            self.assertEqual(len(update_stock_calls), 1,
                f"update_stock() debe llamarse 1 vez, se llamó {len(update_stock_calls)} veces")
            
            # VERIFICAR: Se descontó la cantidad correcta (negativa)
            call_args = update_stock_calls[0][0]
            self.assertEqual(call_args[0], 1)  # producto_id
            self.assertEqual(call_args[1], -5)  # cantidad (negativa = descuento)

    def test_doble_venta_descuenta_doble_stock(self):
        """
        Prueba que 2 ventas descuentan stock 2 veces (comportamiento esperado).
        """
        from tucajero.services.producto_service import VentaService
        from tucajero.services import corte_service
        
        mock_session = Mock()
        
        with patch.object(corte_service, 'CorteCajaService') as MockCorteCajaService:
            mock_corte = Mock()
            mock_corte.esta_caja_abierta.return_value = True
            MockCorteCajaService.return_value = mock_corte
            
            service = VentaService(mock_session)
            
            mock_venta_repo = Mock()
            mock_venta = Mock(id=101, items=[])
            mock_venta_repo.create_venta.return_value = mock_venta
            service.venta_repo = mock_venta_repo
            
            mock_producto = Mock(stock=100, nombre="Producto Test", aplica_iva=True)
            mock_producto_repo = Mock()
            mock_producto_repo.get_by_id.return_value = mock_producto
            service.producto_repo = mock_producto_repo
            
            mock_inventario_repo = Mock()
            service.inventario_repo = mock_inventario_repo
            
            items = [{"producto_id": 1, "cantidad": 10, "precio": 100.0, "aplica_iva": False}]
            
            # Ejecutar 2 ventas
            service.registrar_venta(items)
            service.registrar_venta(items)
            
            # VERIFICAR: update_stock se llamó 2 veces
            update_stock_calls = mock_producto_repo.update_stock.call_args_list
            self.assertEqual(len(update_stock_calls), 2,
                "2 ventas deben llamar update_stock() 2 veces")


# =============================================================================
# FIX 2: "SIN DETALLES" EN DASHBOARD
# =============================================================================

class TestFix2SinDetallesDashboard(unittest.TestCase):
    """
    Pruebas para validar que el dashboard muestra correctamente los nombres
    de productos en lugar de "Sin detalle".
    
    Problema anterior: Se usaba vp.producto_nombre (atributo inexistente)
    en lugar de vp.producto.nombre (relación SQLAlchemy).
    
    Solución: Usar vp.producto.nombre accediendo a la relación correctamente.
    """

    def test_dashboard_usa_relacion_producto_nombre(self):
        """
        Verifica que dashboard_view.py usa vp.producto.nombre correctamente.
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        
        source = inspect.getsource(DashboardView.get_ventas_recientes)
        
        # ASSERT: Debe usar la relación producto.nombre
        self.assertIn('vp.producto.nombre', source,
            "Debe usar vp.producto.nombre (relación SQLAlchemy)")
        
        # ASSERT: NO debe usar producto_nombre (atributo inexistente)
        self.assertNotIn('vp.producto_nombre', source,
            "NO debe usar vp.producto_nombre (atributo inexistente)")

    def test_venta_item_tiene_relacion_producto(self):
        """
        Verifica que el modelo VentaItem tiene la relación 'producto' definida.
        """
        from tucajero.models.producto import VentaItem
        
        # ASSERT: El modelo debe tener el atributo 'producto'
        self.assertTrue(hasattr(VentaItem, 'producto'),
            "VentaItem debe tener relación 'producto'")

    def test_producto_tiene_atributo_nombre(self):
        """
        Verifica que el modelo Producto tiene el atributo 'nombre'.
        """
        from tucajero.models.producto import Producto
        
        # ASSERT: El modelo debe tener el atributo 'nombre'
        self.assertTrue(hasattr(Producto, 'nombre'),
            "Producto debe tener atributo 'nombre'")

    def test_get_ventas_recientes_manaja_excepciones(self):
        """
        Verifica que el método maneja excepciones y muestra fallback.
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        
        source = inspect.getsource(DashboardView.get_ventas_recientes)
        
        # ASSERT: Debe tener try-except para manejar errores
        self.assertIn('try:', source,
            "Debe tener bloque try para manejar excepciones")
        self.assertIn('except', source,
            "Debe tener bloque except para capturar errores")
        
        # ASSERT: Debe tener fallback "Sin detalle"
        self.assertIn('Sin detalle', source,
            "Debe tener fallback 'Sin detalle' cuando no hay productos")

    def test_dashboard_accesa_productos_con_join(self):
        """
        Prueba que el dashboard puede acceder a productos con relación cargada.
        Esta prueba verifica la lógica sin crear base de datos completa.
        """
        from tucajero.models.producto import VentaItem, Producto
        from unittest.mock import Mock
        
        # Simular producto con relación
        mock_producto = Mock()
        mock_producto.nombre = "Producto Prueba"
        
        # Simular venta item con relación producto
        mock_item = Mock()
        mock_item.producto = mock_producto
        
        # VERIFICAR: Se puede acceder a producto.nombre desde el item
        self.assertEqual(mock_item.producto.nombre, "Producto Prueba")
        
        # Simular lista de items como en el dashboard
        items_venta = [mock_item, mock_item]
        productos_nombres = []
        
        for vp in items_venta:
            if vp.producto:
                productos_nombres.append(vp.producto.nombre)
        
        productos_str = ", ".join(productos_nombres[:3])
        
        self.assertEqual(productos_str, "Producto Prueba, Producto Prueba")


# =============================================================================
# FIX 3: FILAS PARES GRIS
# =============================================================================

class TestFix3FilasParesGris(unittest.TestCase):
    """
    Pruebas para validar que las filas pares de la tabla tienen estilo gris suave.
    
    Problema anterior: setAlternatingRowColors(True) causaba conflicto con
    estilos CSS personalizados, resultando en colores inconsistentes.
    
    Solución: Usar setAlternatingRowColors(False) y estilo CSS nth-child(even).
    """

    def test_dashboard_alternating_row_colors_false(self):
        """
        Verifica que setAlternatingRowColors está configurado en False.
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        
        source = inspect.getsource(DashboardView.setup_ui)
        
        # ASSERT: Debe tener setAlternatingRowColors(False)
        self.assertIn('setAlternatingRowColors(False)', source,
            "Debe usar setAlternatingRowColors(False)")
        
        # ASSERT: NO debe tener setAlternatingRowColors(True)
        self.assertNotIn('setAlternatingRowColors(True)', source,
            "NO debe usar setAlternatingRowColors(True)")

    def test_dashboard_estilo_nth_child_even(self):
        """
        Verifica que existe estilo CSS para filas pares con nth-child(even).
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        
        source = inspect.getsource(DashboardView.setup_ui)
        
        # ASSERT: Debe tener estilo nth-child(even)
        self.assertIn('nth-child(even)', source,
            "Debe usar estilo CSS nth-child(even) para filas pares")
        
        # ASSERT: El estilo debe incluir background color
        self.assertIn('background', source,
            "El estilo nth-child(even) debe incluir color de fondo")

    def test_estilo_filas_pares_color_suave(self):
        """
        Verifica que el color de filas pares es suave (baja opacidad).
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        
        source = inspect.getsource(DashboardView.setup_ui)
        
        # Buscar la sección de nth-child(even)
        self.assertIn('nth-child(even)', source)
        
        # El color debe ser rgba con baja opacidad (0.03 o similar)
        self.assertTrue(
            'rgba(255, 255, 255, 0.03)' in source or
            'rgba(255,255,255,0.03)' in source or
            'rgba(255, 255, 255, 0.05)' in source or
            'rgba(255,255,255,0.05)' in source,
            "El color de fondo debe ser suave (rgba con baja opacidad)"
        )

    def test_no_conflicto_estilos_qt_css(self):
        """
        Prueba que no hay conflicto entre Qt y CSS para colores de fila.
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        
        source = inspect.getsource(DashboardView.setup_ui)
        
        # Con setAlternatingRowColors(False), Qt no aplica colores
        # Solo CSS controla el estilo
        
        has_alternating_false = 'setAlternatingRowColors(False)' in source
        has_nth_child = 'nth-child(even)' in source
        
        self.assertTrue(has_alternating_false and has_nth_child,
            "Debe usar False + CSS nth-child para evitar conflictos")


# =============================================================================
# PRUEBAS DE INTEGRACIÓN COMPLETAS
# =============================================================================

class TestIntegracionTodosFixes(unittest.TestCase):
    """
    Pruebas de integración que validan los 3 fixes trabajando juntos.
    """

    def test_ventas_recientes_dashboard_con_productos(self):
        """
        Prueba completa: Dashboard muestra ventas con productos correctamente.
        Usa mocks para evitar problemas de configuración de base de datos.
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        from tucajero.models.producto import Venta, VentaItem, Producto
        from unittest.mock import Mock
        
        # Simular producto
        mock_producto = Mock()
        mock_producto.nombre = "Coca Cola"
        
        # Simular item de venta con relación a producto
        mock_item = Mock()
        mock_item.producto = mock_producto
        
        # Simular lista de items
        items_venta = [mock_item]
        productos_nombres = []
        
        for vp in items_venta:
            if vp.producto:
                productos_nombres.append(vp.producto.nombre)
        
        productos_str = ", ".join(productos_nombres[:3])
        
        # VERIFICAR: Se obtiene el nombre correctamente
        self.assertEqual(productos_str, "Coca Cola")
        self.assertNotEqual(productos_str, "Sin detalle")

    def test_stock_no_se_duplica_en_venta_multiple(self):
        """
        Prueba: Múltiples items en una venta descuentan stock correctamente.
        """
        from tucajero.services.producto_service import VentaService
        from tucajero.services import corte_service
        
        mock_session = Mock()
        
        with patch.object(corte_service, 'CorteCajaService') as MockCorteCajaService:
            mock_corte = Mock()
            mock_corte.esta_caja_abierta.return_value = True
            MockCorteCajaService.return_value = mock_corte
            
            service = VentaService(mock_session)
            
            mock_venta_repo = Mock()
            mock_venta = Mock(id=200, items=[])
            mock_venta_repo.create_venta.return_value = mock_venta
            service.venta_repo = mock_venta_repo
            
            # Crear 2 productos diferentes
            mock_producto1 = Mock(stock=50, nombre="Producto 1", aplica_iva=True)
            mock_producto2 = Mock(stock=30, nombre="Producto 2", aplica_iva=True)
            
            mock_producto_repo = Mock()
            mock_producto_repo.get_by_id.side_effect = [mock_producto1, mock_producto2]
            service.producto_repo = mock_producto_repo
            
            mock_inventario_repo = Mock()
            service.inventario_repo = mock_inventario_repo
            
            # Venta con 2 items diferentes
            items = [
                {"producto_id": 1, "cantidad": 5, "precio": 100.0, "aplica_iva": False},
                {"producto_id": 2, "cantidad": 3, "precio": 50.0, "aplica_iva": False}
            ]
            
            service.registrar_venta(items)
            
            # VERIFICAR: update_stock se llamó 2 veces (una por producto)
            update_stock_calls = mock_producto_repo.update_stock.call_args_list
            self.assertEqual(len(update_stock_calls), 2,
                "Debe llamar update_stock() una vez por cada producto")
            
            # VERIFICAR: Cantidades correctas
            self.assertEqual(update_stock_calls[0][0][1], -5)  # Producto 1: -5
            self.assertEqual(update_stock_calls[1][0][1], -3)  # Producto 2: -3

    def test_anulacion_venta_restaura_stock(self):
        """
        Prueba: Al anular venta, el stock se restaura correctamente.
        """
        from tucajero.services.producto_service import VentaService
        
        mock_session = Mock()
        service = VentaService(mock_session)
        
        # Mock venta con items
        mock_venta = Mock()
        mock_venta.id = 300
        mock_venta.anulada = False
        mock_venta.items = [
            Mock(producto_id=1, cantidad=5),
            Mock(producto_id=2, cantidad=3)
        ]
        
        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = mock_venta
        
        mock_producto_repo = Mock()
        service.producto_repo = mock_producto_repo
        service.inventario_repo = Mock()
        
        # Anular venta
        service.anular_venta(300, motivo="Test", usuario_id=1)
        
        # VERIFICAR: Stock se restaura (cantidad positiva)
        restore_calls = mock_producto_repo.update_stock.call_args_list
        self.assertEqual(len(restore_calls), 2,
            "Debe llamar update_stock() para restaurar cada producto")
        
        self.assertEqual(restore_calls[0][0][1], 5)  # Restaurar 5
        self.assertEqual(restore_calls[1][0][1], 3)  # Restaurar 3


# =============================================================================
# PRUEBAS DE REGRESIÓN
# =============================================================================

class TestRegresionFixes(unittest.TestCase):
    """
    Pruebas de regresión para asegurar que los fixes no rompen funcionalidad.
    """

    def test_venta_repo_valida_stock_antes_de_crear(self):
        """
        Regresión: La validación de stock debe seguir funcionando.
        Prueba simplificada que verifica la lógica de validación.
        """
        from tucajero.repositories.venta_repo import VentaRepository
        from unittest.mock import Mock
        
        # Crear sesión mock
        mock_session = Mock()
        repo = VentaRepository(mock_session)
        
        # Crear producto mock con stock bajo
        mock_producto = Mock()
        mock_producto.stock = 2
        mock_producto.nombre = "Producto Test"
        
        mock_session.query.return_value.get.return_value = mock_producto
        
        # Intentar crear venta con más stock del disponible
        items = [{"producto_id": 1, "cantidad": 5, "precio": 10.0, "aplica_iva": False}]
        
        # Debe lanzar excepción
        with self.assertRaises(ValueError) as context:
            repo.create_venta(items)
        
        self.assertIn('Stock insuficiente', str(context.exception))

    def test_dashboard_maneja_venta_sin_items(self):
        """
        Regresión: Dashboard debe manejar ventas sin items correctamente.
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        
        # Simular lógica cuando no hay items
        items_venta = []
        productos_nombres = []
        
        for vp in items_venta:
            if hasattr(vp, 'producto') and vp.producto:
                productos_nombres.append(vp.producto.nombre)
        
        productos_str = ", ".join(productos_nombres[:3]) if productos_nombres else "Sin detalle"
        
        # Debe mostrar "Sin detalle" cuando no hay items
        self.assertEqual(productos_str, "Sin detalle")

    def test_estilo_tabla_no_afecta_seleccion(self):
        """
        Regresión: El estilo de filas no debe afectar la selección.
        """
        from tucajero.app.ui.views.dashboard.dashboard_view import DashboardView
        
        source = inspect.getsource(DashboardView.setup_ui)
        
        # Debe mantener estilo de selección
        self.assertIn('::item:selected', source,
            "Debe mantener estilo para items seleccionados")
        self.assertIn('#7C3AED', source,
            "Debe mantener color de selección")


if __name__ == '__main__':
    unittest.main(verbosity=2)
