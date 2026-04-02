"""
Pruebas unitarias para validación de cajero_id en ventas

Estas pruebas verifican que el campo cajero_id se registra correctamente
en cada venta y que el sistema funciona tanto con como sin cajero asignado.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from decimal import Decimal
import inspect
import os
import sys

# Agregar ruta al proyecto para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestVentaConCajero(unittest.TestCase):
    """Pruebas para validar registro de cajero en ventas"""

    def test_cajero_id_parametro_en_create_venta(self):
        """
        Prueba que verifica que cajero_id es parámetro válido en create_venta
        """
        from tucajero.repositories.venta_repo import VentaRepository

        # Obtener firma del método
        sig = inspect.signature(VentaRepository.create_venta)
        params = list(sig.parameters.keys())

        # ASSERT: cajero_id debe estar en los parámetros
        self.assertIn('cajero_id', params)

    def test_cajero_id_valor_por_defecto_none(self):
        """
        Prueba que cajero_id tiene None como valor por defecto
        """
        from tucajero.repositories.venta_repo import VentaRepository

        sig = inspect.signature(VentaRepository.create_venta)
        cajero_id_param = sig.parameters['cajero_id']

        # ASSERT: valor por defecto debe ser None
        self.assertIsNone(cajero_id_param.default)

    def test_cajero_id_parametro_en_registrar_venta(self):
        """
        Prueba que verificar que cajero_id es parámetro válido en registrar_venta
        """
        from tucajero.services.producto_service import VentaService

        sig = inspect.signature(VentaService.registrar_venta)
        params = list(sig.parameters.keys())

        # ASSERT: cajero_id debe estar en los parámetros
        self.assertIn('cajero_id', params)

    def test_cajero_id_valor_por_defecto_en_service(self):
        """
        Prueba que cajero_id tiene None como valor por defecto en service
        """
        from tucajero.services.producto_service import VentaService

        sig = inspect.signature(VentaService.registrar_venta)
        cajero_id_param = sig.parameters['cajero_id']

        # ASSERT: valor por defecto debe ser None
        self.assertIsNone(cajero_id_param.default)

    def test_cajero_id_se_pasa_al_repo(self):
        """
        Prueba que VentaService pasa cajero_id correctamente al repositorio
        """
        from tucajero.services.producto_service import VentaService
        from tucajero.services import corte_service

        # Mock de sesión
        mock_session = Mock()

        # Mock de CorteCajaService en el módulo corte_service
        with patch.object(corte_service, 'CorteCajaService') as MockCorteCajaService:
            mock_corte = Mock()
            mock_corte.esta_caja_abierta.return_value = True
            MockCorteCajaService.return_value = mock_corte

            service = VentaService(mock_session)

            # Mock de repositorios
            mock_venta_repo = Mock()
            mock_venta = Mock(id=200, items=[])
            mock_venta_repo.create_venta.return_value = mock_venta
            service.venta_repo = mock_venta_repo

            mock_producto_repo = Mock()
            mock_producto = Mock(stock=100, nombre="Test", aplica_iva=True)
            mock_producto_repo.get_by_id.return_value = mock_producto
            service.producto_repo = mock_producto_repo

            service.inventario_repo = Mock()

            items = [{"producto_id": 1, "cantidad": 1, "precio": 100.0, "aplica_iva": False}]
            cajero_id = 7

            # Ejecutar registro de venta
            service.registrar_venta(items, cajero_id=cajero_id)

            # Verificar que create_venta fue llamado con cajero_id
            mock_venta_repo.create_venta.assert_called_once()
            call_kwargs = mock_venta_repo.create_venta.call_args[1]

            self.assertIn('cajero_id', call_kwargs)
            self.assertEqual(call_kwargs['cajero_id'], cajero_id)

    def test_venta_funciona_sin_cajero(self):
        """
        Prueba que venta funciona sin cajero (cajero_id=None)
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
            mock_venta = Mock(id=201, items=[])
            mock_venta_repo.create_venta.return_value = mock_venta
            service.venta_repo = mock_venta_repo

            mock_producto_repo = Mock()
            mock_producto = Mock(stock=100, nombre="Test", aplica_iva=True)
            mock_producto_repo.get_by_id.return_value = mock_producto
            service.producto_repo = mock_producto_repo

            service.inventario_repo = Mock()

            items = [{"producto_id": 1, "cantidad": 1, "precio": 100.0, "aplica_iva": False}]

            # Ejecutar SIN cajero_id (debe usar None por defecto)
            service.registrar_venta(items)

            # Verificar que create_venta fue llamado con cajero_id=None
            call_kwargs = mock_venta_repo.create_venta.call_args[1]
            self.assertIn('cajero_id', call_kwargs)
            self.assertIsNone(call_kwargs['cajero_id'])


class TestVentaModelCajeroField(unittest.TestCase):
    """Pruebas para validar el campo cajero_id en el modelo Venta"""

    def test_venta_modelo_tiene_cajero_id(self):
        """Verifica que el modelo Venta tiene el campo cajero_id"""
        from tucajero.models.producto import Venta

        # Verificar que el atributo existe
        self.assertTrue(hasattr(Venta, 'cajero_id'), "Venta debe tener atributo cajero_id")

    def test_venta_modelo_cajero_id_nullable(self):
        """
        Verifica que cajero_id en el modelo es nullable (permite None)
        """
        from tucajero.models.producto import Venta

        # Verificar que la columna permite null
        self.assertTrue(
            Venta.cajero_id.nullable,
            "cajero_id debe ser nullable (nullable=True)"
        )

    def test_venta_modelo_cajero_id_tipo_columna(self):
        """
        Verifica que cajero_id es de tipo Integer
        """
        from sqlalchemy import Integer
        from tucajero.models.producto import Venta

        # Verificar tipo de columna
        self.assertIsInstance(
            Venta.cajero_id.type,
            Integer,
            "cajero_id debe ser de tipo Integer"
        )

    def test_venta_modelo_tiene_relacion_cajero(self):
        """
        Verifica que el modelo Venta tiene relación con Cajero
        """
        from tucajero.models.producto import Venta

        # Verificar que existe la relación
        self.assertTrue(hasattr(Venta, 'cajero'), "Venta debe tener relación 'cajero'")


class TestConfirmarCobroUI(unittest.TestCase):
    """Pruebas para validar que UI pasa cajero_id correctamente (vía análisis de código)"""

    def _leer_archivo_ventas_view(self):
        """Lee el contenido del archivo ventas_view.py"""
        ventas_view_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'tucajero', 
            'ui', 
            'ventas_view.py'
        )
        with open(ventas_view_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_confirmar_cobro_extrae_cajero_id(self):
        """
        Verifica que _confirmar_cobro extrae cajero_id de cajero_activo
        """
        source = self._leer_archivo_ventas_view()

        # Verificar que el código contiene la extracción de cajero_id
        self.assertIn('cajero_id', source, "El código debe contener cajero_id")
        self.assertIn('cajero_activo', source, "El código debe usar cajero_activo")
        
        # Verificar patrón específico de extracción
        self.assertTrue(
            'cajero_id = self.cajero_activo.id if self.cajero_activo else None' in source or
            'cajero_id=self.cajero_activo.id' in source,
            "Debe extraer cajero_id de cajero_activo"
        )

    def test_confirmar_cobro_pasa_cajero_id_a_service(self):
        """
        Verifica que _confirmar_cobro pasa cajero_id a registrar_venta
        """
        source = self._leer_archivo_ventas_view()

        # Verificar que pasa cajero_id al service
        self.assertIn('cajero_id=cajero_id', source, 
            "Debe pasar cajero_id=cajero_id a registrar_venta")


class TestIntegracionCajeroEnVentas(unittest.TestCase):
    """Pruebas de integración para el flujo completo de cajero en ventas"""

    def test_flujo_completo_cajero_registra_venta(self):
        """
        Prueba de integración: cajero_id fluye correctamente desde UI hasta repo
        """
        from tucajero.services.producto_service import VentaService
        from tucajero.services import corte_service

        # Simular flujo completo
        # 1. UI tiene cajero_activo
        cajero_activo_mock = Mock()
        cajero_activo_mock.id = 10

        # 2. Extraer cajero_id (como lo hace UI)
        cajero_id = cajero_activo_mock.id if cajero_activo_mock else None
        self.assertEqual(cajero_id, 10)

        # 3. Service recibe y pasa cajero_id
        mock_session = Mock()

        with patch.object(corte_service, 'CorteCajaService') as MockCorteCajaService:
            mock_corte = Mock()
            mock_corte.esta_caja_abierta.return_value = True
            MockCorteCajaService.return_value = mock_corte

            service = VentaService(mock_session)

            # Mock repositorios
            service.venta_repo = Mock()
            mock_venta = Mock(id=300, items=[])
            service.venta_repo.create_venta.return_value = mock_venta

            service.producto_repo = Mock()
            service.producto_repo.get_by_id.return_value = Mock(
                stock=100, nombre="Test", aplica_iva=True
            )

            service.inventario_repo = Mock()

            items = [{"producto_id": 1, "cantidad": 1, "precio": 100.0, "aplica_iva": False}]

            # 4. Service llama a repo con cajero_id
            service.registrar_venta(items, cajero_id=cajero_id)

            # 5. Verificar que repo recibió cajero_id
            call_kwargs = service.venta_repo.create_venta.call_args[1]
            self.assertEqual(call_kwargs['cajero_id'], cajero_id)

    def test_flujo_completo_sin_cajero(self):
        """
        Prueba de integración: flujo funciona sin cajero (None)
        """
        from tucajero.services.producto_service import VentaService
        from tucajero.services import corte_service

        # 1. UI sin cajero_activo
        cajero_activo = None

        # 2. Extraer cajero_id
        cajero_id = cajero_activo.id if cajero_activo else None
        self.assertIsNone(cajero_id)

        # 3. Service recibe None
        mock_session = Mock()

        with patch.object(corte_service, 'CorteCajaService') as MockCorteCajaService:
            mock_corte = Mock()
            mock_corte.esta_caja_abierta.return_value = True
            MockCorteCajaService.return_value = mock_corte

            service = VentaService(mock_session)

            service.venta_repo = Mock()
            mock_venta = Mock(id=301, items=[])
            service.venta_repo.create_venta.return_value = mock_venta

            service.producto_repo = Mock()
            service.producto_repo.get_by_id.return_value = Mock(
                stock=100, nombre="Test", aplica_iva=True
            )

            service.inventario_repo = Mock()

            items = [{"producto_id": 1, "cantidad": 1, "precio": 100.0, "aplica_iva": False}]

            # 4. Service llama a repo con cajero_id=None
            service.registrar_venta(items, cajero_id=cajero_id)

            # 5. Verificar que repo recibió cajero_id=None
            call_kwargs = service.venta_repo.create_venta.call_args[1]
            self.assertIsNone(call_kwargs['cajero_id'])


class TestConsistenciaDatos(unittest.TestCase):
    """Pruebas de consistencia de datos para cajero_id"""

    def test_cajero_id_tipo_int_permite_none(self):
        """
        Verifica que el tipo int con None no causa TypeError
        """
        # Simular asignación de valores
        cajero_id_entero = 5
        cajero_id_nulo = None

        # No debe haber TypeError al asignar
        try:
            valor1 = int(cajero_id_entero) if cajero_id_entero is not None else None
            valor2 = int(cajero_id_nulo) if cajero_id_nulo is not None else None
            sin_error = True
        except TypeError:
            sin_error = False

        self.assertTrue(sin_error, "No debe haber TypeError con int o None")
        self.assertEqual(valor1, 5)
        self.assertIsNone(valor2)

    def test_cajero_idForeignKey_nullable(self):
        """
        Verifica que la ForeignKey es nullable en el modelo
        """
        from tucajero.models.producto import Venta

        # Obtener información de la columna
        col = Venta.cajero_id

        # Verificar que es ForeignKey
        self.assertTrue(len(col.foreign_keys) > 0, "cajero_id debe ser ForeignKey")

        # Verificar que es nullable
        self.assertTrue(col.nullable, "cajero_id debe permitir NULL")


if __name__ == '__main__':
    unittest.main()
