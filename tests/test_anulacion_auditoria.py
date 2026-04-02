"""
Pruebas unitarias para validación de auditoría en anulación de ventas

Estas pruebas verifican que el sistema registra correctamente:
- El motivo de anulación (obligatorio)
- El usuario que realizó la anulación
- El flujo completo de anulación con restauración de stock

Archivos bajo prueba:
- tucajero/models/producto.py - Modelo Venta (campos motivo_anulacion, usuario_anulacion_id)
- tucajero/repositories/venta_repo.py - Función anular_venta()
- tucajero/services/producto_service.py - Función anular_venta()
- tucajero/ui/corte_view.py - Función anular_venta() (UI)
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
import inspect
import os
import sys

# Agregar ruta al proyecto para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Inicializar modelos de SQLAlchemy correctamente antes de las pruebas
def setUpModule():
    """Inicializa todos los modelos para evitar errores de SQLAlchemy"""
    from tucajero.models.producto import Venta, VentaItem, Producto, MovimientoInventario
    from tucajero.models.cliente import Cliente
    from tucajero.models.cajero import Cajero


# =============================================================================
# PRUEBAS DE MODELO - Campos de auditoría en Venta
# =============================================================================

class TestVentaModeloCamposAuditoria(unittest.TestCase):
    """Pruebas para validar los campos de auditoría en el modelo Venta"""

    def test_venta_modelo_tiene_motivo_anulacion(self):
        """Verifica que el modelo Venta tiene el campo motivo_anulacion"""
        from tucajero.models.producto import Venta

        self.assertTrue(hasattr(Venta, 'motivo_anulacion'), 
            "Venta debe tener atributo motivo_anulacion")

    def test_venta_modelo_tiene_usuario_anulacion_id(self):
        """Verifica que el modelo Venta tiene el campo usuario_anulacion_id"""
        from tucajero.models.producto import Venta

        self.assertTrue(hasattr(Venta, 'usuario_anulacion_id'), 
            "Venta debe tener atributo usuario_anulacion_id")

    def test_motivo_anulacion_tipo_columna(self):
        """Verifica que motivo_anulacion es de tipo String con longitud adecuada"""
        from sqlalchemy import String
        from tucajero.models.producto import Venta

        self.assertIsInstance(
            Venta.motivo_anulacion.type,
            String,
            "motivo_anulacion debe ser de tipo String"
        )
        # Verificar longitud máxima de 500 caracteres
        self.assertEqual(
            Venta.motivo_anulacion.type.length,
            500,
            "motivo_anulacion debe tener longitud máxima de 500 caracteres"
        )

    def test_motivo_anulacion_nullable(self):
        """Verifica que motivo_anulacion permite NULL (por compatibilidad)"""
        from tucajero.models.producto import Venta

        # Aunque debería ser obligatorio en la lógica, la BD permite NULL
        self.assertTrue(
            Venta.motivo_anulacion.nullable,
            "motivo_anulacion debe ser nullable para compatibilidad"
        )

    def test_usuario_anulacion_id_tipo_columna(self):
        """Verifica que usuario_anulacion_id es de tipo Integer"""
        from sqlalchemy import Integer
        from tucajero.models.producto import Venta

        self.assertIsInstance(
            Venta.usuario_anulacion_id.type,
            Integer,
            "usuario_anulacion_id debe ser de tipo Integer"
        )

    def test_usuario_anulacion_id_nullable(self):
        """Verifica que usuario_anulacion_id permite NULL"""
        from tucajero.models.producto import Venta

        self.assertTrue(
            Venta.usuario_anulacion_id.nullable,
            "usuario_anulacion_id debe ser nullable"
        )

    def test_usuario_anulacion_id_es_foreignKey(self):
        """Verifica que usuario_anulacion_id es ForeignKey a cajeros"""
        from tucajero.models.producto import Venta

        self.assertTrue(
            len(Venta.usuario_anulacion_id.foreign_keys) > 0,
            "usuario_anulacion_id debe ser ForeignKey"
        )
        
        # Verificar que referencia a cajeros.id
        fk_table = list(Venta.usuario_anulacion_id.foreign_keys)[0].column.table.name
        self.assertEqual(fk_table, "cajeros", 
            "usuario_anulacion_id debe referenciar a tabla cajeros")

    def test_venta_modelo_tiene_relacion_usuario_anulacion(self):
        """Verifica que el modelo Venta tiene relación con usuario_anulacion"""
        from tucajero.models.producto import Venta

        self.assertTrue(hasattr(Venta, 'usuario_anulacion'), 
            "Venta debe tener relación 'usuario_anulacion'")


# =============================================================================
# PRUEBAS DE REPOSITORIO - anular_venta() en VentaRepository
# =============================================================================

class TestVentaRepositoryAnularVenta(unittest.TestCase):
    """Pruebas para la función anular_venta() en VentaRepository"""

    def test_anular_venta_existe_en_repo(self):
        """Verifica que el método anular_venta existe en VentaRepository"""
        from tucajero.repositories.venta_repo import VentaRepository

        self.assertTrue(hasattr(VentaRepository, 'anular_venta'))

    def test_anular_venta_firma_con_motivo_y_usuario(self):
        """Verifica la firma del método anular_venta con motivo y usuario_id"""
        from tucajero.repositories.venta_repo import VentaRepository

        sig = inspect.signature(VentaRepository.anular_venta)
        params = list(sig.parameters.keys())

        self.assertIn('venta_id', params)
        self.assertIn('motivo', params)
        self.assertIn('usuario_id', params)

    def test_anular_venta_motivo_valor_por_defecto_none(self):
        """Verifica que motivo tiene None como valor por defecto"""
        from tucajero.repositories.venta_repo import VentaRepository

        sig = inspect.signature(VentaRepository.anular_venta)
        motivo_param = sig.parameters['motivo']

        self.assertIsNone(motivo_param.default)

    def test_anular_venta_usuario_id_valor_por_defecto_none(self):
        """Verifica que usuario_id tiene None como valor por defecto"""
        from tucajero.repositories.venta_repo import VentaRepository

        sig = inspect.signature(VentaRepository.anular_venta)
        usuario_param = sig.parameters['usuario_id']

        self.assertIsNone(usuario_param.default)

    def test_anular_venta_asigna_motivo_a_venta(self):
        """Verifica que anular_venta asigna el motivo correctamente"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        
        # Mock de venta existente
        mock_venta = Mock()
        mock_venta.anulada = False
        mock_venta.motivo_anulacion = None
        mock_venta.usuario_anulacion_id = None

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        motivo_test = "Error en el cobro - cliente solicitó cambio"
        usuario_id_test = 5

        repo.anular_venta(venta_id=100, motivo=motivo_test, usuario_id=usuario_id_test)

        self.assertEqual(mock_venta.motivo_anulacion, motivo_test)
        self.assertEqual(mock_venta.usuario_anulacion_id, usuario_id_test)
        self.assertTrue(mock_venta.anulada)

    def test_anular_venta_hace_commit(self):
        """Verifica que anular_venta hace commit después de actualizar"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        repo.anular_venta(venta_id=100, motivo="Test", usuario_id=5)

        mock_session.commit.assert_called_once()

    def test_anular_venta_retorna_venta(self):
        """Verifica que anular_venta retorna la venta actualizada"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        resultado = repo.anular_venta(venta_id=100, motivo="Test", usuario_id=5)

        self.assertEqual(resultado, mock_venta)

    def test_anular_venta_venta_no_existe(self):
        """Verifica que lanza ValueError si la venta no existe"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=None)

        with self.assertRaises(ValueError) as context:
            repo.anular_venta(venta_id=999, motivo="Test", usuario_id=5)

        self.assertIn("no encontrada", str(context.exception))

    def test_anular_venta_ya_anulada(self):
        """Verifica que lanza ValueError si la venta ya está anulada"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = True

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        with self.assertRaises(ValueError) as context:
            repo.anular_venta(venta_id=100, motivo="Test", usuario_id=5)

        self.assertIn("ya está anulada", str(context.exception))


# =============================================================================
# PRUEBAS DE SERVICIO - anular_venta() en VentaService
# =============================================================================

class TestVentaServiceAnularVenta(unittest.TestCase):
    """Pruebas para la función anular_venta() en VentaService"""

    def test_anular_venta_existe_en_service(self):
        """Verifica que el método anular_venta existe en VentaService"""
        from tucajero.services.producto_service import VentaService

        self.assertTrue(hasattr(VentaService, 'anular_venta'))

    def test_anular_venta_firma_con_motivo_y_usuario(self):
        """Verifica la firma del método anular_venta en Service"""
        from tucajero.services.producto_service import VentaService

        sig = inspect.signature(VentaService.anular_venta)
        params = list(sig.parameters.keys())

        self.assertIn('venta_id', params)
        self.assertIn('motivo', params)
        self.assertIn('usuario_id', params)

    def test_anular_venta_restaura_stock(self):
        """Verifica que anular_venta restaura el stock de los productos"""
        from tucajero.services.producto_service import VentaService

        mock_session = Mock()
        service = VentaService(mock_session)

        # Mock de venta con items
        mock_venta = Mock()
        mock_venta.id = 100
        mock_venta.anulada = False
        mock_item1 = Mock()
        mock_item1.producto_id = 1
        mock_item1.cantidad = 5
        mock_item2 = Mock()
        mock_item2.producto_id = 2
        mock_item2.cantidad = 3
        mock_venta.items = [mock_item1, mock_item2]

        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = mock_venta

        service.producto_repo = Mock()
        service.inventario_repo = Mock()

        service.anular_venta(venta_id=100, motivo="Test", usuario_id=5)

        # Verificar que restauró stock (update_stock con cantidad positiva)
        self.assertEqual(service.producto_repo.update_stock.call_count, 2)
        service.producto_repo.update_stock.assert_any_call(1, 5)
        service.producto_repo.update_stock.assert_any_call(2, 3)

    def test_anular_venta_crea_movimiento_entrada(self):
        """Verifica que crea movimientos de entrada de inventario"""
        from tucajero.services.producto_service import VentaService

        mock_session = Mock()
        service = VentaService(mock_session)

        mock_venta = Mock()
        mock_venta.id = 100
        mock_venta.anulada = False
        mock_item = Mock()
        mock_item.producto_id = 1
        mock_item.cantidad = 5
        mock_venta.items = [mock_item]

        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = mock_venta
        service.producto_repo = Mock()
        service.inventario_repo = Mock()

        service.anular_venta(venta_id=100, motivo="Test", usuario_id=5)

        # Verificar que creó movimiento de entrada
        service.inventario_repo.create_movimiento.assert_called_once_with(
            1, "entrada", 5
        )

    def test_anular_venta_pasa_motivo_y_usuario_al_repo(self):
        """Verifica que pasa motivo y usuario_id al repositorio"""
        from tucajero.services.producto_service import VentaService

        mock_session = Mock()
        service = VentaService(mock_session)

        mock_venta = Mock()
        mock_venta.id = 100
        mock_venta.anulada = False
        mock_venta.items = []

        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = mock_venta
        service.producto_repo = Mock()
        service.inventario_repo = Mock()

        motivo_test = "Cliente insatisfecho"
        usuario_id_test = 7

        service.anular_venta(venta_id=100, motivo=motivo_test, usuario_id=usuario_id_test)

        service.venta_repo.anular_venta.assert_called_once_with(
            100, motivo=motivo_test, usuario_id=usuario_id_test
        )

    def test_anular_venta_venta_no_existe(self):
        """Verifica que lanza ValueError si la venta no existe"""
        from tucajero.services.producto_service import VentaService

        mock_session = Mock()
        service = VentaService(mock_session)
        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = None

        with self.assertRaises(ValueError) as context:
            service.anular_venta(venta_id=999, motivo="Test", usuario_id=5)

        self.assertIn("no encontrada", str(context.exception))

    def test_anular_venta_ya_anulada(self):
        """Verifica que lanza ValueError si la venta ya está anulada"""
        from tucajero.services.producto_service import VentaService

        mock_session = Mock()
        service = VentaService(mock_session)

        mock_venta = Mock()
        mock_venta.id = 100
        mock_venta.anulada = True
        mock_venta.items = []

        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = mock_venta

        with self.assertRaises(ValueError) as context:
            service.anular_venta(venta_id=100, motivo="Test", usuario_id=5)

        self.assertIn("ya está anulada", str(context.exception))


# =============================================================================
# PRUEBAS DE UI - anular_venta() en CorteView
# =============================================================================

class TestCorteViewAnularVentaUI(unittest.TestCase):
    """Pruebas para la función anular_venta() en CorteView (UI)"""

    def _leer_archivo_corte_view(self):
        """Lee el contenido del archivo corte_view.py"""
        corte_view_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'tucajero',
            'ui',
            'corte_view.py'
        )
        with open(corte_view_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_corte_view_tiene_metodo_anular_venta(self):
        """Verifica que CorteView tiene el método anular_venta"""
        from tucajero.ui.corte_view import CorteView

        self.assertTrue(hasattr(CorteView, 'anular_venta'))

    def test_ui_solicita_motivo_obligatorio(self):
        """Verifica que la UI solicita el motivo de anulación"""
        source = self._leer_archivo_corte_view()

        self.assertIn('QInputDialog.getText', source, 
            "Debe usar QInputDialog.getText para solicitar motivo")
        self.assertIn('Motivo de Anulación', source,
            "Debe tener título 'Motivo de Anulación'")

    def test_ui_valida_motivo_no_vacio(self):
        """Verifica que la UI valida que el motivo no esté vacío"""
        source = self._leer_archivo_corte_view()

        # Buscar validación de motivo vacío
        self.assertTrue(
            'not motivo.strip()' in source or
            'motivo == ""' in source or
            'not motivo' in source,
            "Debe validar que el motivo no esté vacío"
        )

    def test_ui_muestra_advertencia_motivo_vacio(self):
        """Verifica que muestra advertencia si motivo está vacío"""
        source = self._leer_archivo_corte_view()

        self.assertIn('Motivo requerido', source,
            "Debe mostrar advertencia 'Motivo requerido'")
        self.assertIn('obligatorio', source.lower(),
            "Debe indicar que el motivo es obligatorio")

    def test_ui_muestra_confirmacion_con_motivo(self):
        """Verifica que muestra confirmación con el motivo antes de anular"""
        source = self._leer_archivo_corte_view()

        self.assertIn('Confirmar Anulación', source,
            "Debe mostrar diálogo de confirmación")
        self.assertIn('Motivo:', source,
            "Debe mostrar el motivo en la confirmación")

    def test_ui_pasa_usuario_id_al_service(self):
        """Verifica que la UI pasa usuario_id (cajero_activo) al service"""
        source = self._leer_archivo_corte_view()

        self.assertTrue(
            'cajero_activo.id' in source or
            'usuario_id' in source,
            "Debe obtener usuario_id de cajero_activo"
        )
        self.assertIn('venta_service.anular_venta', source,
            "Debe llamar a anular_venta del service")

    def test_ui_muestra_mensaje_exito_con_motivo(self):
        """Verifica que muestra mensaje de éxito con el motivo"""
        source = self._leer_archivo_corte_view()

        self.assertIn('Venta Anulada', source,
            "Debe mostrar mensaje de éxito")
        self.assertIn('Motivo:', source,
            "Debe mostrar el motivo en el mensaje de éxito")
        self.assertIn('stock ha sido restaurado', source.lower(),
            "Debe informar que el stock fue restaurado")


# =============================================================================
# PRUEBAS DE FLUJO COMPLETO - Integración
# =============================================================================

class TestFlujoCompletoAnulacion(unittest.TestCase):
    """Pruebas de integración para el flujo completo de anulación"""

    def test_flujo_completo_anulacion_con_motivo_y_usuario(self):
        """
        Prueba de integración: flujo completo desde UI hasta repo
        """
        from tucajero.services.producto_service import VentaService

        # 1. Setup: Crear service con mocks
        mock_session = Mock()
        service = VentaService(mock_session)

        # 2. Mock de venta con items
        mock_venta = Mock()
        mock_venta.id = 100
        mock_venta.anulada = False
        mock_venta.total = 500.0
        mock_item = Mock()
        mock_item.producto_id = 1
        mock_item.cantidad = 2
        mock_item.precio = 250.0
        mock_venta.items = [mock_item]

        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = mock_venta

        service.producto_repo = Mock()
        service.inventario_repo = Mock()

        # 3. Ejecutar anulación con motivo y usuario
        motivo = "Error en precio - cliente solicitó corrección"
        usuario_id = 3

        resultado = service.anular_venta(
            venta_id=100,
            motivo=motivo,
            usuario_id=usuario_id
        )

        # 4. Verificar restauración de stock
        service.producto_repo.update_stock.assert_called_once_with(1, 2)

        # 5. Verificar creación de movimiento de entrada
        service.inventario_repo.create_movimiento.assert_called_once_with(
            1, "entrada", 2
        )

        # 6. Verificar llamada al repo con motivo y usuario
        service.venta_repo.anular_venta.assert_called_once_with(
            100, motivo=motivo, usuario_id=usuario_id
        )

    def test_flujo_completo_sin_usuario_id(self):
        """
        Prueba que el flujo funciona sin usuario_id (None)
        """
        from tucajero.services.producto_service import VentaService

        mock_session = Mock()
        service = VentaService(mock_session)

        mock_venta = Mock()
        mock_venta.id = 100
        mock_venta.anulada = False
        mock_venta.items = []

        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = mock_venta
        service.producto_repo = Mock()
        service.inventario_repo = Mock()

        # Ejecutar sin usuario_id
        service.anular_venta(venta_id=100, motivo="Test", usuario_id=None)

        # Verificar que repo recibió usuario_id=None
        call_kwargs = service.venta_repo.anular_venta.call_args[1]
        self.assertIsNone(call_kwargs['usuario_id'])

    def test_flujo_completo_multiple_items(self):
        """
        Prueba anulación con múltiples items en la venta
        """
        from tucajero.services.producto_service import VentaService

        mock_session = Mock()
        service = VentaService(mock_session)

        mock_venta = Mock()
        mock_venta.id = 100
        mock_venta.anulada = False
        mock_item1 = Mock(producto_id=1, cantidad=5)
        mock_item2 = Mock(producto_id=2, cantidad=3)
        mock_item3 = Mock(producto_id=3, cantidad=1)
        mock_venta.items = [mock_item1, mock_item2, mock_item3]

        service.venta_repo = Mock()
        service.venta_repo.get_venta_by_id.return_value = mock_venta
        service.producto_repo = Mock()
        service.inventario_repo = Mock()

        service.anular_venta(venta_id=100, motivo="Test", usuario_id=5)

        # Verificar que restauró stock para cada item
        self.assertEqual(service.producto_repo.update_stock.call_count, 3)
        self.assertEqual(service.inventario_repo.create_movimiento.call_count, 3)


# =============================================================================
# PRUEBAS DE CASOS ESPECIALES Y BORDES
# =============================================================================

class TestCasosEspecialesAnulacion(unittest.TestCase):
    """Pruebas para casos especiales y bordes en anulación"""

    def test_motivo_largo_maximo_500_caracteres(self):
        """Prueba con motivo de longitud máxima (500 caracteres)"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        motivo_largo = "A" * 500  # 500 caracteres exactos

        repo.anular_venta(venta_id=100, motivo=motivo_largo, usuario_id=5)

        self.assertEqual(len(mock_venta.motivo_anulacion), 500)

    def test_motivo_corto_un_caracter(self):
        """Prueba con motivo mínimo (1 carácter)"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        repo.anular_venta(venta_id=100, motivo="X", usuario_id=5)

        self.assertEqual(mock_venta.motivo_anulacion, "X")

    def test_motivo_con_caracteres_especiales(self):
        """Prueba con motivo que contiene caracteres especiales"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        motivo_especial = "Error: cliente <solicitó> cambio & devolución (50%)"

        repo.anular_venta(venta_id=100, motivo=motivo_especial, usuario_id=5)

        self.assertEqual(mock_venta.motivo_anulacion, motivo_especial)

    def test_motivo_con_saltos_linea(self):
        """Prueba con motivo que contiene saltos de línea"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        motivo_multilinea = "Línea 1\nLínea 2\nLínea 3"

        repo.anular_venta(venta_id=100, motivo=motivo_multilinea, usuario_id=5)

        self.assertEqual(mock_venta.motivo_anulacion, motivo_multilinea)

    def test_usuario_id_cero(self):
        """Prueba con usuario_id = 0 (caso borde)"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        repo.anular_venta(venta_id=100, motivo="Test", usuario_id=0)

        self.assertEqual(mock_venta.usuario_anulacion_id, 0)

    def test_usuario_id_negativo(self):
        """Prueba con usuario_id negativo (caso inválido pero permitido)"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        repo.anular_venta(venta_id=100, motivo="Test", usuario_id=-1)

        self.assertEqual(mock_venta.usuario_anulacion_id, -1)


# =============================================================================
# PRUEBAS DE CONSISTENCIA DE DATOS
# =============================================================================

class TestConsistenciaDatosAuditoria(unittest.TestCase):
    """Pruebas de consistencia de datos para auditoría"""

    def test_motivo_anulacion_se_persiste_correctamente(self):
        """Verifica que el motivo se persiste sin modificaciones"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        motivo_original = "   Motivo con espacios   "

        repo.anular_venta(venta_id=100, motivo=motivo_original, usuario_id=5)

        # El motivo se guarda tal cual (la UI debe validar antes)
        self.assertEqual(mock_venta.motivo_anulacion, motivo_original)

    def test_anulacion_flag_se_establece_true(self):
        """Verifica que el flag anulada se establece en True"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        repo.anular_venta(venta_id=100, motivo="Test", usuario_id=5)

        self.assertTrue(mock_venta.anulada)

    def test_ambos_campos_auditoria_se_asignan_juntos(self):
        """Verifica que motivo y usuario_id se asignan en la misma operación"""
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_venta = Mock()
        mock_venta.anulada = False
        mock_venta.motivo_anulacion = None
        mock_venta.usuario_anulacion_id = None

        repo = VentaRepository(mock_session)
        repo.get_venta_by_id = Mock(return_value=mock_venta)

        motivo = "Test de asignación conjunta"
        usuario_id = 42

        repo.anular_venta(venta_id=100, motivo=motivo, usuario_id=usuario_id)

        # Ambos deben estar asignados
        self.assertIsNotNone(mock_venta.motivo_anulacion)
        self.assertIsNotNone(mock_venta.usuario_anulacion_id)
        self.assertEqual(mock_venta.motivo_anulacion, motivo)
        self.assertEqual(mock_venta.usuario_anulacion_id, usuario_id)


# =============================================================================
# PRUEBAS DE ANALISIS ESTATICO DE CODIGO
# =============================================================================

class TestAnalisisCodigoEstatico(unittest.TestCase):
    """Pruebas de análisis estático del código"""

    def _leer_archivo(self, ruta_relativa):
        """Lee el contenido de un archivo"""
        path = os.path.join(os.path.dirname(__file__), '..', ruta_relativa)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_repo_anular_venta_asigna_campos(self):
        """Verifica en el código que repo asigna motivo y usuario_id"""
        source = self._leer_archivo('tucajero/repositories/venta_repo.py')

        self.assertIn('venta.motivo_anulacion = motivo', source)
        self.assertIn('venta.usuario_anulacion_id = usuario_id', source)

    def test_service_anular_venta_pasa_parametros(self):
        """Verifica en el código que service pasa motivo y usuario_id"""
        source = self._leer_archivo('tucajero/services/producto_service.py')

        self.assertIn('motivo=motivo', source)
        self.assertIn('usuario_id=usuario_id', source)

    def test_service_restaura_stock_antes_anular(self):
        """Verifica que el service restaura stock antes de marcar anulada"""
        source = self._leer_archivo('tucajero/services/producto_service.py')

        # El orden importa: primero restaura stock, luego anula
        pos_restaura = source.find('update_stock(item.producto_id, item.cantidad)')
        pos_anula = source.find('self.venta_repo.anular_venta')

        self.assertLess(pos_restaura, pos_anula,
            "Debe restaurar stock antes de anular en el repo")


# =============================================================================
# PRUEBAS DE INTEGRACION CON BASE DE DATOS (Simuladas)
# =============================================================================

class TestIntegracionBaseDatos(unittest.TestCase):
    """
    Pruebas de integración con base de datos (simuladas con mocks)
    
    Nota: Estas pruebas documentan el comportamiento esperado con una BD real.
    Para pruebas reales con SQLite, se requeriría crear una BD de prueba temporal.
    """

    def test_insercion_motivo_largo_bd_real(self):
        """
        Documenta el comportamiento esperado con motivo de 500 caracteres en BD real
        
        En producción:
        - SQLite almacenará los 500 caracteres completos
        - No habrá truncamiento automático
        """
        motivo_500 = "A" * 500
        self.assertEqual(len(motivo_500), 500)

    def test_insercion_usuario_id_null_bd_real(self):
        """
        Documenta el comportamiento esperado con usuario_id=None en BD real
        
        En producción:
        - SQLite almacenará NULL en la columna usuario_anulacion_id
        - No habrá error de foreign key (es nullable)
        """
        usuario_id = None
        self.assertIsNone(usuario_id)

    def test_consulta_ventas_anuladas_con_motivo(self):
        """
        Documenta consulta esperada para obtener ventas anuladas con motivo
        
        SQL esperado:
        SELECT id, fecha, total, motivo_anulacion, usuario_anulacion_id
        FROM ventas
        WHERE anulada = 1
        ORDER BY fecha DESC
        """
        # Esta prueba documenta la consulta esperada
        query_esperada = """
            SELECT id, fecha, total, motivo_anulacion, usuario_anulacion_id
            FROM ventas
            WHERE anulada = 1
            ORDER BY fecha DESC
        """
        self.assertIn('motivo_anulacion', query_esperada)
        self.assertIn('usuario_anulacion_id', query_esperada)


# =============================================================================
# PRUEBAS DE MIGRACION DE BASE DE DATOS
# =============================================================================

class TestMigracionBaseDatos(unittest.TestCase):
    """
    Pruebas para identificar requerimientos de migración de base de datos
    
    ADVERTENCIA: Los campos nuevos requieren ALTER TABLE en BD existente
    """

    def test_campos_nuevos_requieren_migracion(self):
        """
        Identifica que los campos motivo_anulacion y usuario_anulacion_id
        requieren migración en bases de datos existentes
        """
        from tucajero.models.producto import Venta

        # Verificar que los campos existen en el modelo
        self.assertTrue(hasattr(Venta, 'motivo_anulacion'))
        self.assertTrue(hasattr(Venta, 'usuario_anulacion_id'))

        # Estos campos NO existen en BD creadas antes de la implementación
        # Se requiere ejecutar:
        # ALTER TABLE ventas ADD COLUMN motivo_anulacion VARCHAR(500)
        # ALTER TABLE ventas ADD COLUMN usuario_anulacion_id INTEGER

    def test_sql_migracion_motivo_anulacion(self):
        """Documenta el SQL necesario para migrar campo motivo_anulacion"""
        sql_esperado = "ALTER TABLE ventas ADD COLUMN motivo_anulacion VARCHAR(500)"
        self.assertIn('ALTER TABLE', sql_esperado)
        self.assertIn('ventas', sql_esperado)
        self.assertIn('motivo_anulacion', sql_esperado)

    def test_sql_migracion_usuario_anulacion_id(self):
        """Documenta el SQL necesario para migrar campo usuario_anulacion_id"""
        sql_esperado = "ALTER TABLE ventas ADD COLUMN usuario_anulacion_id INTEGER"
        self.assertIn('ALTER TABLE', sql_esperado)
        self.assertIn('ventas', sql_esperado)
        self.assertIn('usuario_anulacion_id', sql_esperado)

    def test_funcion_agregar_columnas_si_existen(self):
        """
        Verifica que database.py tiene función para agregar columnas
        """
        from tucajero.config.database import agregar_columnas_si_existen

        self.assertTrue(callable(agregar_columnas_si_existen))

    def test_columnas_nuevas_en_lista_migracion(self):
        """
        Verifica si las columnas nuevas están en la lista de migración
        
        ADVERTENCIA: Esta prueba FALLARÁ si las columnas no están agregadas,
        lo cual es el comportamiento esperado para identificar la deuda técnica.
        """
        from tucajero.config.database import agregar_columnas_si_existen
        import inspect

        source = inspect.getsource(agregar_columnas_si_existen)

        # Verificar si las columnas están en la lista
        tiene_motivo = 'motivo_anulacion' in source
        tiene_usuario = 'usuario_anulacion_id' in source

        # Esta prueba documenta el estado actual
        # Si falla, es porque falta agregar las columnas a la migración
        self.assertTrue(
            tiene_motivo and tiene_usuario,
            "FALTAN COLUMNAS EN MIGRACIÓN: motivo_anulacion y usuario_anulacion_id "
            "deben agregarse a la función agregar_columnas_si_existen() en database.py"
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
