"""
Pruebas unitarias para validación de número de factura en ventas

Estas pruebas verifican que el campo numero_factura se genera correctamente
con el formato FAC-XXXXXXXX y que el consecutivo se incrementa apropiadamente.
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
    # Importar todos los modelos para que se registren correctamente
    from tucajero.models.producto import Venta, VentaItem, ConsecutivoFactura, Producto, MovimientoInventario
    from tucajero.models.cliente import Cliente
    from tucajero.models.cajero import Cajero


class TestNumeroFacturaFormato(unittest.TestCase):
    """Pruebas para validar el formato del número de factura"""

    def test_formato_numero_factura_correcto(self):
        """
        Prueba que el formato del número de factura es FAC-XXXXXXXX
        donde X son 8 dígitos con ceros a la izquierda
        """
        from tucajero.repositories.venta_repo import VentaRepository

        # Crear sesión mock
        mock_session = Mock()

        # Mock del consecutivo existente
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 1
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)
        numero = repo.obtener_siguiente_consecutivo("FAC")

        # ASSERT: El formato debe ser FAC-00000002 (ya que incrementa de 1 a 2)
        self.assertRegex(numero, r'^FAC-\d{8}$', "El formato debe ser FAC-XXXXXXXX")
        self.assertEqual(numero, "FAC-00000002")

    def test_formato_numero_factura_con_numero_alto(self):
        """
        Prueba que el formato mantiene 8 dígitos incluso con números altos
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 12345
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)
        numero = repo.obtener_siguiente_consecutivo("FAC")

        # ASSERT: Debe ser FAC-00012346
        self.assertEqual(numero, "FAC-00012346")
        self.assertRegex(numero, r'^FAC-\d{8}$')

    def test_formato_numero_factura_desde_cero(self):
        """
        Prueba que el formato es correcto cuando empieza desde 0
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 0
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)
        numero = repo.obtener_siguiente_consecutivo("FAC")

        # ASSERT: Debe ser FAC-00000001
        self.assertEqual(numero, "FAC-00000001")


class TestNumeroFacturaIncremento(unittest.TestCase):
    """Pruebas para validar el incremento del consecutivo"""

    def test_consecutivo_se_incrementa_en_uno(self):
        """
        Prueba que el consecutivo se incrementa en 1 cada vez
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 5

        # Configurar el mock para que devuelva el mismo objeto consecutivo
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)

        # Primera llamada
        numero1 = repo.obtener_siguiente_consecutivo("FAC")
        self.assertEqual(numero1, "FAC-00000006")
        self.assertEqual(mock_consecutivo.ultimo_numero, 6)

        # Segunda llamada
        numero2 = repo.obtener_siguiente_consecutivo("FAC")
        self.assertEqual(numero2, "FAC-00000007")
        self.assertEqual(mock_consecutivo.ultimo_numero, 7)

    def test_consecutivo_commit_se_llama(self):
        """
        Prueba que se hace commit después de incrementar el consecutivo
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 10
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)
        repo.obtener_siguiente_consecutivo("FAC")

        # ASSERT: commit debe haber sido llamado
        mock_session.commit.assert_called_once()

    def test_consecutivo_crea_nuevo_si_no_existe(self):
        """
        Prueba que crea un nuevo consecutivo si no existe
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_session.query().filter().first.return_value = None

        # Variable para capturar el objeto creado
        objeto_creado = None

        def capture_add(obj):
            nonlocal objeto_creado
            objeto_creado = obj

        mock_session.add.side_effect = capture_add

        # Parchear ConsecutivoFactura para evitar inicialización de SQLAlchemy
        with patch('tucajero.repositories.venta_repo.ConsecutivoFactura') as MockConsecutivo:
            mock_consecutivo_instance = Mock()
            mock_consecutivo_instance.prefijo = "FAC"
            mock_consecutivo_instance.ultimo_numero = 0  # Se crea con 0
            MockConsecutivo.return_value = mock_consecutivo_instance

            repo = VentaRepository(mock_session)
            numero = repo.obtener_siguiente_consecutivo("FAC")

            # ASSERT: Se debe haber creado un nuevo ConsecutivoFactura
            self.assertEqual(mock_session.add.call_count, 1)
            self.assertIsNotNone(objeto_creado)
            self.assertEqual(objeto_creado.prefijo, "FAC")
            # Después de incrementar (ultimo_numero += 1), debería ser 1
            self.assertEqual(objeto_creado.ultimo_numero, 1)
            self.assertEqual(numero, "FAC-00000001")


class TestNumeroFacturaEnVenta(unittest.TestCase):
    """Pruebas para validar que numero_factura se asigna correctamente a Venta"""

    def test_create_venta_asigna_numero_factura(self):
        """
        Prueba que create_venta asigna numero_factura al modelo Venta
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()

        # Mock del consecutivo
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 100
        mock_session.query().filter().first.return_value = mock_consecutivo

        # Mock del producto para validación de stock
        mock_producto = Mock()
        mock_producto.stock = 100
        mock_producto.nombre = "Producto Test"
        mock_producto.aplica_iva = True
        mock_session.query().get.return_value = mock_producto

        # Mock de la venta creada
        mock_venta = Mock()
        mock_venta.id = 1
        mock_venta.numero_factura = None  # Se actualizará después

        def capture_venta(*args, **kwargs):
            """Captura los argumentos pasados al constructor Venta"""
            mock_venta.numero_factura = kwargs.get('numero_factura')
            return mock_venta

        # Parchear la clase Venta para evitar inicialización de SQLAlchemy
        with patch('tucajero.repositories.venta_repo.Venta', side_effect=capture_venta):
            repo = VentaRepository(mock_session)
            items = [
                {"producto_id": 1, "cantidad": 2, "precio": 50.0, "aplica_iva": True}
            ]

            venta = repo.create_venta(
                items=items,
                metodo_pago="efectivo",
                cliente_id=None,
                cajero_id=5
            )

            # ASSERT: Verificar que se asignó numero_factura
            self.assertIsNotNone(venta.numero_factura)
            self.assertRegex(venta.numero_factura, r'^FAC-\d{8}$')
            # Después de incrementar, debería ser FAC-00000101
            self.assertEqual(venta.numero_factura, "FAC-00000101")

    def test_create_venta_pasa_numero_factura_a_modelo(self):
        """
        Prueba que el numero_factura se pasa correctamente al constructor de Venta
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()

        # Mock del consecutivo
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 50
        mock_session.query().filter().first.return_value = mock_consecutivo

        # Mock del producto
        mock_producto = Mock()
        mock_producto.stock = 100
        mock_producto.nombre = "Producto Test"
        mock_producto.aplica_iva = True
        mock_session.query().get.return_value = mock_producto

        # Variable para capturar el numero_factura pasado
        numero_factura_capturado = None

        def capture_venta(*args, **kwargs):
            nonlocal numero_factura_capturado
            numero_factura_capturado = kwargs.get('numero_factura')
            return Mock(id=1)

        with patch('tucajero.repositories.venta_repo.Venta', side_effect=capture_venta):
            repo = VentaRepository(mock_session)
            items = [{"producto_id": 1, "cantidad": 1, "precio": 100.0, "aplica_iva": False}]

            repo.create_venta(items=items)

            # ASSERT: Verificar que numero_factura fue pasado
            self.assertIsNotNone(numero_factura_capturado)
            self.assertRegex(numero_factura_capturado, r'^FAC-\d{8}$')


class TestConsistenciaNumeroFactura(unittest.TestCase):
    """Pruebas de consistencia para numero_factura"""

    def test_numero_factura_no_es_nulo(self):
        """
        Prueba que numero_factura nunca es None
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 0
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)
        numero = repo.obtener_siguiente_consecutivo("FAC")

        # ASSERT: No debe ser None
        self.assertIsNotNone(numero)
        self.assertIsInstance(numero, str)
        self.assertGreater(len(numero), 0)

    def test_numero_factura_es_string(self):
        """
        Prueba que numero_factura es de tipo string
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 0
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)
        numero = repo.obtener_siguiente_consecutivo("FAC")

        # ASSERT: Debe ser string
        self.assertIsInstance(numero, str)

    def test_prefijo_diferente_fac(self):
        """
        Prueba que funciona con otros prefijos además de FAC
        """
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "BOL"
        mock_consecutivo.ultimo_numero = 25
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)
        numero = repo.obtener_siguiente_consecutivo("BOL")

        # ASSERT: Debe usar el prefijo correcto
        self.assertEqual(numero, "BOL-00000026")
        self.assertRegex(numero, r'^BOL-\d{8}$')


class TestAnalisisCodigoEstatico(unittest.TestCase):
    """Pruebas de análisis estático del código"""

    def test_obtener_siguiente_consecutivo_existe(self):
        """
        Verifica que el método obtener_siguiente_consecutivo existe
        """
        from tucajero.repositories.venta_repo import VentaRepository

        self.assertTrue(hasattr(VentaRepository, 'obtener_siguiente_consecutivo'))

    def test_create_venta_llama_obtener_consecutivo(self):
        """
        Verifica que create_venta llama a obtener_siguiente_consecutivo
        """
        # Leer el código fuente
        from tucajero.repositories import venta_repo
        import inspect

        source = inspect.getsource(venta_repo.VentaRepository.create_venta)

        # ASSERT: Debe contener la llamada
        self.assertIn('obtener_siguiente_consecutivo', source)
        self.assertIn('"FAC"', source)

    def test_create_venta_asigna_numero_factura_a_venta(self):
        """
        Verifica que create_venta asigna numero_factura al crear Venta
        """
        from tucajero.repositories import venta_repo
        import inspect

        source = inspect.getsource(venta_repo.VentaRepository.create_venta)

        # ASSERT: Debe asignar numero_factura
        self.assertIn('numero_factura=numero_factura', source)

    def test_venta_modelo_tiene_campo_numero_factura(self):
        """
        Verifica que el modelo Venta tiene el campo numero_factura
        """
        from tucajero.models.producto import Venta

        self.assertTrue(hasattr(Venta, 'numero_factura'))

    def test_venta_numero_factura_es_nullable(self):
        """
        Verifica que numero_factura es nullable en el modelo
        """
        from tucajero.models.producto import Venta

        # En el modelo, nullable=True permite None, pero el sistema
        # siempre debe asignar un valor
        self.assertTrue(Venta.numero_factura.nullable)


class TestPosiblesBugs(unittest.TestCase):
    """Pruebas para identificar posibles bugs"""

    def test_commit_temprano_en_obtener_consecutivo(self):
        """
        ADVERTENCIA: Esta prueba documenta el comportamiento de commit temprano

        El método obtener_siguiente_consecutivo() hace commit inmediatamente
        después de incrementar el consecutivo, ANTES de crear la venta.

        Esto significa que si create_venta() falla después de obtener el
        consecutivo, se pierde un número en la secuencia.
        """
        from tucajero.repositories import venta_repo
        import inspect

        source = inspect.getsource(venta_repo.VentaRepository.obtener_siguiente_consecutivo)

        # Verificar que hay commit en el método
        self.assertIn('self.session.commit()', source)

        # Esta prueba es informativa - documenta el comportamiento
        # El commit temprano es un problema potencial de consistencia

    def test_no_hay_rollback_si_falla_venta(self):
        """
        ADVERTENCIA: Esta prueba documenta la falta de rollback

        Si create_venta() falla después de obtener_siguiente_consecutivo(),
        no hay mecanismo de rollback para revertir el incremento del consecutivo.
        """
        from tucajero.repositories import venta_repo
        import inspect

        source = inspect.getsource(venta_repo.VentaRepository.create_venta)

        # Verificar que no hay try/except con rollback
        self.assertNotIn('rollback', source.lower())

    def test_posible_condicion_carrera(self):
        """
        ADVERTENCIA: Esta prueba documenta la posible condición de carrera

        En un escenario multi-usuario, dos hilos podrían:
        1. Leer el mismo valor de ultimo_numero
        2. Incrementarlo
        3. Hacer commit

        Resultando en duplicación de números de factura.
        """
        # Esta prueba es informativa - no se puede probar con mocks
        # pero documenta el problema potencial
        from tucajero.repositories.venta_repo import VentaRepository

        mock_session = Mock()
        mock_consecutivo = Mock()
        mock_consecutivo.prefijo = "FAC"
        mock_consecutivo.ultimo_numero = 100
        mock_session.query().filter().first.return_value = mock_consecutivo

        repo = VentaRepository(mock_session)

        # Simular lectura del valor antes del commit
        valor_antes_commit = mock_consecutivo.ultimo_numero + 1

        # Otro hilo podría leer el mismo valor aquí (condición de carrera)
        # Esto es una limitación del diseño actual

        self.assertEqual(valor_antes_commit, 101)


if __name__ == '__main__':
    unittest.main(verbosity=2)
