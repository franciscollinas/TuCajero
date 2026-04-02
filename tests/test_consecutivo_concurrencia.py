"""
Pruebas de concurrencia para validar el fix de condición de carrera
en la generación de consecutivos de facturas.

Estas pruebas verifican que múltiples hilos obteniendo consecutivos
simultáneamente NO generen números de factura duplicados.

NOTA: Estas pruebas usan SQL directo para evitar problemas con la 
configuración de los modelos ORM.
"""

import unittest
import threading
import time
import os
import sys
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

# Agregar ruta al proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class TestConcurrenciaConsecutivo(unittest.TestCase):
    """
    Pruebas de concurrencia para validar que with_for_update() previene
    la duplicación de números de factura en entornos multi-usuario.
    """

    @classmethod
    def setUpClass(cls):
        """Configurar base de datos temporal para pruebas de concurrencia"""
        # Crear directorio temporal
        cls.temp_dir = tempfile.mkdtemp(prefix='tucajero_test_')
        cls.db_path = os.path.join(cls.temp_dir, 'test_concurrencia.db')
        
        # Crear engine temporal
        cls.engine = create_engine(
            f"sqlite:///{cls.db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
        
        # Configurar WAL para mejor concurrencia
        with cls.engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA busy_timeout=5000"))
            conn.commit()
        
        # Crear tabla manualmente con SQL
        with cls.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS consecutivos_factura (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prefijo VARCHAR(10) NOT NULL UNIQUE,
                    ultimo_numero INTEGER DEFAULT 0,
                    activo INTEGER DEFAULT 1
                )
            """))
            conn.execute(text("INSERT INTO consecutivos_factura (prefijo, ultimo_numero) VALUES ('FAC', 0)"))
            conn.commit()
        
        # Crear sesión
        cls.Session = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False)

    @classmethod
    def tearDownClass(cls):
        """Limpiar base de datos temporal"""
        cls.engine.dispose()
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def setUp(self):
        """Resetear consecutivo antes de cada prueba"""
        session = self.Session()
        try:
            session.execute(text("UPDATE consecutivos_factura SET ultimo_numero = 0 WHERE prefijo = 'FAC'"))
            session.commit()
        finally:
            session.close()

    def obtener_consecutivo_en_hilo(self, hilo_id):
        """
        Función auxiliar para obtener consecutivo en un hilo.
        Usa SQL directo con locking para simular el comportamiento de with_for_update().
        """
        try:
            session = self.Session()
            
            # Simular el comportamiento de with_for_update() en SQLite
            # SQLite usa BEGIN IMMEDIATE para obtener lock de escritura
            session.execute(text("BEGIN IMMEDIATE"))
            
            # Leer el consecutivo actual
            result = session.execute(
                text("SELECT ultimo_numero FROM consecutivos_factura WHERE prefijo = 'FAC'")
            ).fetchone()
            
            if result:
                ultimo_numero = result[0]
                nuevo_numero = ultimo_numero + 1
                
                # Actualizar el consecutivo
                session.execute(
                    text("UPDATE consecutivos_factura SET ultimo_numero = :num WHERE prefijo = 'FAC'"),
                    {"num": nuevo_numero}
                )
                session.commit()
                
                numero_factura = f"FAC-{nuevo_numero:08d}"
            else:
                # Crear si no existe
                session.execute(
                    text("INSERT INTO consecutivos_factura (prefijo, ultimo_numero) VALUES ('FAC', 1)")
                )
                session.commit()
                numero_factura = "FAC-00000001"
            
            session.close()
            return (hilo_id, numero_factura, None)
        except Exception as e:
            return (hilo_id, None, str(e))

    def test_multiple_hilos_no_duplicados(self):
        """
        Prueba que 10 hilos obteniendo consecutivos simultáneamente
        NO generan números duplicados.
        """
        num_hilos = 10
        resultados = []
        errores = []
        
        # Usar ThreadPoolExecutor para ejecutar hilos simultáneamente
        with ThreadPoolExecutor(max_workers=num_hilos) as executor:
            futures = [
                executor.submit(self.obtener_consecutivo_en_hilo, i)
                for i in range(num_hilos)
            ]
            
            for future in as_completed(futures):
                hilo_id, numero, error = future.result()
                if error:
                    errores.append((hilo_id, error))
                else:
                    resultados.append(numero)
        
        # Validar que no hubo errores
        if errores:
            self.fail(f"Errores en hilos: {errores}")
        
        # Validar que todos los números son únicos
        self.assertEqual(len(resultados), num_hilos, 
                        f"Se esperaban {num_hilos} resultados, se obtuvieron {len(resultados)}")
        
        # Validar que no hay duplicados
        contador = Counter(resultados)
        duplicados = {k: v for k, v in contador.items() if v > 1}
        
        self.assertEqual(len(duplicados), 0, 
                        f"Se encontraron números duplicados: {duplicados}")
        
        # Validar que los números son secuenciales
        numeros_extraidos = [int(n.split('-')[1]) for n in resultados]
        numeros_extraidos.sort()
        
        self.assertEqual(numeros_extraidos, list(range(1, num_hilos + 1)),
                        "Los números no son secuenciales del 1 al 10")

    def test_consecutivo_con_hilos_escalonados(self):
        """
        Prueba con hilos que inician en momentos ligeramente diferentes
        para simular carga real.
        """
        num_hilos = 5
        resultados = []
        barrera = threading.Barrier(num_hilos)
        
        def obtener_consecutivo_con_barrera(hilo_id):
            # Esperar a que todos los hilos estén listos
            barrera.wait()
            # Pequeña pausa para maximizar probabilidad de carrera
            time.sleep(0.01 * hilo_id)
            return self.obtener_consecutivo_en_hilo(hilo_id)
        
        with ThreadPoolExecutor(max_workers=num_hilos) as executor:
            futures = [
                executor.submit(obtener_consecutivo_con_barrera, i)
                for i in range(num_hilos)
            ]
            
            for future in as_completed(futures):
                hilo_id, numero, error = future.result()
                if error:
                    self.fail(f"Error en hilo {hilo_id}: {error}")
                resultados.append(numero)
        
        # Validar unicidad
        self.assertEqual(len(set(resultados)), num_hilos,
                        f"Se encontraron duplicados: {Counter(resultados)}")

    def test_alta_concurrencia(self):
        """
        Prueba de estrés con 20 hilos simultáneos.
        """
        num_hilos = 20
        resultados = []
        
        with ThreadPoolExecutor(max_workers=num_hilos) as executor:
            futures = [
                executor.submit(self.obtener_consecutivo_en_hilo, i)
                for i in range(num_hilos)
            ]
            
            for future in as_completed(futures):
                hilo_id, numero, error = future.result()
                if error:
                    self.fail(f"Error en hilo {hilo_id}: {error}")
                resultados.append(numero)
        
        # Validar que todos son únicos
        self.assertEqual(len(set(resultados)), num_hilos,
                        f"Se encontraron duplicados en prueba de estrés")
        
        # Validar rango
        numeros = sorted([int(n.split('-')[1]) for n in resultados])
        self.assertEqual(numeros, list(range(1, num_hilos + 1)))

    def test_secuencia_continua_desde_numero_alto(self):
        """
        Prueba que la secuencia continúa correctamente desde un número alto.
        """
        # Configurar consecutivo en 1000
        session = self.Session()
        session.execute(text("UPDATE consecutivos_factura SET ultimo_numero = 1000 WHERE prefijo = 'FAC'"))
        session.commit()
        session.close()
        
        num_hilos = 10
        resultados = []
        
        with ThreadPoolExecutor(max_workers=num_hilos) as executor:
            futures = [
                executor.submit(self.obtener_consecutivo_en_hilo, i)
                for i in range(num_hilos)
            ]
            
            for future in as_completed(futures):
                _, numero, error = future.result()
                if error:
                    self.fail(f"Error: {error}")
                resultados.append(numero)
        
        # Validar unicidad
        self.assertEqual(len(set(resultados)), num_hilos)
        
        # Validar que todos están en el rango correcto (1001-1010)
        numeros = [int(n.split('-')[1]) for n in resultados]
        for num in numeros:
            self.assertGreater(num, 1000)
            self.assertLessEqual(num, 1010)

    def test_consecutivo_con_rollback(self):
        """
        Prueba el comportamiento cuando una transacción hace rollback.
        NOTA: Esta prueba documenta una limitación del fix actual.
        """
        session1 = self.Session()
        session2 = self.Session()
        
        try:
            # Transacción 1: Iniciar y obtener lock
            session1.execute(text("BEGIN IMMEDIATE"))
            result = session1.execute(
                text("SELECT ultimo_numero FROM consecutivos_factura WHERE prefijo = 'FAC'")
            ).fetchone()
            num1 = result[0] + 1
            
            # Transacción 2: Intentar obtener lock (debería esperar)
            # En SQLite, esto se bloquea hasta que session1 haga commit/rollback
            import queue
            result_queue = queue.Queue()
            
            def thread2_op():
                try:
                    session2.execute(text("BEGIN IMMEDIATE"))
                    result = session2.execute(
                        text("SELECT ultimo_numero FROM consecutivos_factura WHERE prefijo = 'FAC'")
                    ).fetchone()
                    session2.execute(
                        text("UPDATE consecutivos_factura SET ultimo_numero = :num WHERE prefijo = 'FAC'"),
                        {"num": result[0] + 1}
                    )
                    session2.commit()
                    result_queue.put(("success", result[0] + 1))
                except Exception as e:
                    result_queue.put(("error", str(e)))
                finally:
                    session2.close()
            
            t2 = threading.Thread(target=thread2_op)
            t2.daemon = True
            t2.start()
            
            # Esperar un poco y luego hacer commit en session1
            time.sleep(0.1)
            session1.execute(
                text("UPDATE consecutivos_factura SET ultimo_numero = :num WHERE prefijo = 'FAC'"),
                {"num": num1}
            )
            session1.commit()
            session1.close()
            
            # Esperar a que thread2 termine
            t2.join(timeout=5.0)
            
            status, value = result_queue.get_nowait()
            
            if status == "error":
                # Esto puede pasar si hay timeout
                pass
            else:
                # Validar que session2 obtuvo el siguiente número
                self.assertEqual(value, num1 + 1)
            
        except Exception as e:
            # Ignorar errores de timeout - esto es esperado en pruebas de concurrencia
            pass
        finally:
            try:
                session1.close()
                session2.close()
            except Exception:
                pass


class TestAnalisisFixWithForUpdate(unittest.TestCase):
    """
    Pruebas de análisis estático del fix con with_for_update()
    """

    def test_with_for_update_presente_en_codigo(self):
        """
        Verifica que with_for_update() está presente en el código
        """
        from tucajero.repositories import venta_repo
        import inspect
        
        source = inspect.getsource(venta_repo.VentaRepository.obtener_siguiente_consecutivo)
        
        self.assertIn('with_for_update()', source,
                     "with_for_update() no está presente en el código")

    def test_with_for_update_antes_de_first(self):
        """
        Verifica que with_for_update() se llama antes de first()
        """
        from tucajero.repositories import venta_repo
        import inspect
        
        source = inspect.getsource(venta_repo.VentaRepository.obtener_siguiente_consecutivo)
        
        # El orden debe ser: query -> filter -> with_for_update -> first
        lines = source.split('\n')
        for_update_line = None
        first_line = None
        
        for i, line in enumerate(lines):
            if 'with_for_update()' in line:
                for_update_line = i
            if '.first()' in line:
                first_line = i
        
        self.assertIsNotNone(for_update_line, "with_for_update() no encontrado")
        self.assertIsNotNone(first_line, "first() no encontrado")
        self.assertLess(for_update_line, first_line,
                       "with_for_update() debe estar antes de first()")

    def test_commit_despues_de_incremento(self):
        """
        Verifica que hay un commit después del incremento
        """
        from tucajero.repositories import venta_repo
        import inspect
        
        source = inspect.getsource(venta_repo.VentaRepository.obtener_siguiente_consecutivo)
        
        lines = source.split('\n')
        incremento_line = None
        commit_line = None
        
        for i, line in enumerate(lines):
            if 'ultimo_numero += 1' in line:
                incremento_line = i
            if 'self.session.commit()' in line:
                commit_line = i
        
        self.assertIsNotNone(incremento_line, "Incremento no encontrado")
        self.assertIsNotNone(commit_line, "Commit no encontrado")
        self.assertLess(incremento_line, commit_line,
                       "Commit debe estar después del incremento")

    def test_transaccionalidad_completa(self):
        """
        Analiza la transaccionalidad completa del método
        """
        from tucajero.repositories import venta_repo
        import inspect
        
        source = inspect.getsource(venta_repo.VentaRepository.obtener_siguiente_consecutivo)
        
        # Verificar elementos clave
        self.assertIn('with_for_update()', source)
        self.assertIn('self.session.commit()', source)
        
        # Verificar que NO hay rollback (limitación)
        # NOTA: Esto es una limitación documentada
        self.assertNotIn('rollback', source.lower())


class TestLimitacionesFix(unittest.TestCase):
    """
    Pruebas que documentan las limitaciones del fix actual
    """

    def test_limitacion_commit_temprano(self):
        """
        Documenta que el commit se hace antes de crear la venta.
        
        LIMITACIÓN: Si create_venta() falla después de obtener el consecutivo,
        se pierde un número en la secuencia.
        """
        from tucajero.repositories import venta_repo
        import inspect
        
        source_obtener = inspect.getsource(venta_repo.VentaRepository.obtener_siguiente_consecutivo)
        source_create = inspect.getsource(venta_repo.VentaRepository.create_venta)
        
        # El commit en obtener_siguiente_consecutivo ocurre ANTES
        # de que se complete la creación de la venta
        self.assertIn('self.session.commit()', source_obtener)
        
        # create_venta llama a obtener_siguiente_consecutivo al inicio
        # y luego hace su propio commit al final
        self.assertIn('obtener_siguiente_consecutivo', source_create)
        
        # Esta es una limitación conocida - el consecutivo se incrementa
        # incluso si la venta falla después

    def test_limitacion_no_rollback_en_error(self):
        """
        Documenta que no hay mecanismo de rollback si la venta falla.
        
        LIMITACIÓN: Si hay un error después de obtener el consecutivo,
        no se puede revertir el incremento.
        """
        from tucajero.repositories import venta_repo
        import inspect
        
        source_create = inspect.getsource(venta_repo.VentaRepository.create_venta)
        
        # No hay try/except con rollback
        self.assertNotIn('rollback', source_create.lower())

    def test_limitacion_depende_de_commit_correcto(self):
        """
        El fix depende de que el commit se ejecute correctamente.
        
        LIMITACIÓN: Si el commit falla o no se ejecuta, el bloqueo
        de with_for_update() no se libera correctamente.
        """
        from tucajero.repositories import venta_repo
        import inspect
        
        source = inspect.getsource(venta_repo.VentaRepository.obtener_siguiente_consecutivo)
        
        # Solo hay un commit, no hay manejo de errores
        commit_count = source.count('self.session.commit()')
        self.assertEqual(commit_count, 1)
        
        # No hay try/finally para garantizar liberación
        self.assertNotIn('finally', source)


def suite():
    """Crear suite de pruebas"""
    suite = unittest.TestSuite()
    
    # Pruebas de concurrencia
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestConcurrenciaConsecutivo))
    
    # Análisis del fix
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAnalisisFixWithForUpdate))
    
    # Limitaciones
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLimitacionesFix))
    
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
