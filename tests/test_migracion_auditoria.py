"""
Pruebas de integración para validación de migración de columnas de auditoría

Estas pruebas verifican que la función `agregar_columnas_si_existen()` en
`tucajero.config.database` agrega correctamente las columnas:
- motivo_anulacion (VARCHAR(500))
- usuario_anulacion_id (INTEGER)

a la tabla `ventas` cuando no existen.
"""

import unittest
import os
import sys
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock

# Agregar ruta al proyecto para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestMigracionAuditoriaVentas(unittest.TestCase):
    """Pruebas para la migración de columnas de auditoría en tabla ventas"""

    def setUp(self):
        """Configura una base de datos temporal para cada prueba"""
        # Crear archivo temporal para la BD
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # Conectar a la BD temporal
        self.conn = sqlite3.connect(self.temp_db_path)
        self.cursor = self.conn.cursor()
        
        # Crear tabla ventas SIN las columnas de auditoría
        self.cursor.execute('''
            CREATE TABLE ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATETIME,
                total FLOAT,
                anulada INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
        
        # Mantener referencia al engine para dispose
        self.engine = None

    def tearDown(self):
        """Limpia la base de datos temporal"""
        # Cerrar engine si existe
        if self.engine:
            try:
                self.engine.dispose()
            except:
                pass
        
        self.conn.close()
        
        # Intentar eliminar el archivo temporal
        try:
            os.unlink(self.temp_db_path)
        except PermissionError:
            # En Windows, a veces el archivo queda bloqueado temporalmente
            pass

    def _crear_engine_temporal(self):
        """Crea un engine de SQLAlchemy apuntando a la BD temporal"""
        from sqlalchemy import create_engine
        self.engine = create_engine(
            f"sqlite:///{self.temp_db_path}",
            connect_args={"check_same_thread": False}
        )
        return self.engine

    def test_funcion_agregar_columnas_si_existen_existe(self):
        """Verifica que la función agregar_columnas_si_existen existe"""
        from tucajero.config.database import agregar_columnas_si_existen
        
        self.assertTrue(callable(agregar_columnas_si_existen))

    def test_columnas_auditoria_en_lista_migracion(self):
        """Verifica que las columnas de auditoría están en la lista de migración"""
        # Leer el código fuente para verificar que las columnas están declaradas
        database_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'tucajero',
            'config',
            'database.py'
        )
        
        with open(database_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar que las columnas están en la lista
        self.assertIn('"motivo_anulacion"', contenido,
            "motivo_anulacion debe estar en la lista de columnas")
        self.assertIn('"usuario_anulacion_id"', contenido,
            "usuario_anulacion_id debe estar en la lista de columnas")
        self.assertIn('"ventas"', contenido,
            "ventas debe estar como tabla para las columnas")

    def test_migracion_agrega_motivo_anulacion(self):
        """Prueba que la migración agrega la columna motivo_anulacion"""
        from tucajero.config.database import agregar_columnas_si_existen
        
        engine = self._crear_engine_temporal()
        
        # Verificar que la columna NO existe antes de la migración
        self.cursor.execute("PRAGMA table_info(ventas)")
        columnas_antes = [row[1] for row in self.cursor.fetchall()]
        self.assertNotIn('motivo_anulacion', columnas_antes,
            "motivo_anulacion NO debe existir antes de la migración")
        
        # Ejecutar migración
        agregar_columnas_si_existen(engine)
        
        # Verificar que la columna existe después de la migración
        self.cursor.execute("PRAGMA table_info(ventas)")
        columnas_despues = [row[1] for row in self.cursor.fetchall()]
        self.assertIn('motivo_anulacion', columnas_despues,
            "motivo_anulacion debe existir después de la migración")

    def test_migracion_agrega_usuario_anulacion_id(self):
        """Prueba que la migración agrega la columna usuario_anulacion_id"""
        from tucajero.config.database import agregar_columnas_si_existen
        
        engine = self._crear_engine_temporal()
        
        # Verificar que la columna NO existe antes de la migración
        self.cursor.execute("PRAGMA table_info(ventas)")
        columnas_antes = [row[1] for row in self.cursor.fetchall()]
        self.assertNotIn('usuario_anulacion_id', columnas_antes,
            "usuario_anulacion_id NO debe existir antes de la migración")
        
        # Ejecutar migración
        agregar_columnas_si_existen(engine)
        
        # Verificar que la columna existe después de la migración
        self.cursor.execute("PRAGMA table_info(ventas)")
        columnas_despues = [row[1] for row in self.cursor.fetchall()]
        self.assertIn('usuario_anulacion_id', columnas_despues,
            "usuario_anulacion_id debe existir después de la migración")

    def test_migracion_tipo_columna_motivo_anulacion(self):
        """Verifica que motivo_anulacion tiene el tipo correcto (VARCHAR)"""
        from tucajero.config.database import agregar_columnas_si_existen
        
        engine = self._crear_engine_temporal()
        agregar_columnas_si_existen(engine)
        
        # Obtener información de la columna
        self.cursor.execute("PRAGMA table_info(ventas)")
        columnas = self.cursor.fetchall()
        
        motivo_col = None
        for col in columnas:
            if col[1] == 'motivo_anulacion':
                motivo_col = col
                break
        
        self.assertIsNotNone(motivo_col, "motivo_anulacion debe existir")
        # SQLite usa VARCHAR pero internamente es TEXT
        self.assertIn('VARCHAR', motivo_col[2].upper(),
            f"motivo_anulacion debe ser VARCHAR, obtenido: {motivo_col[2]}")

    def test_migracion_tipo_columna_usuario_anulacion_id(self):
        """Verifica que usuario_anulacion_id tiene el tipo correcto (INTEGER)"""
        from tucajero.config.database import agregar_columnas_si_existen
        
        engine = self._crear_engine_temporal()
        agregar_columnas_si_existen(engine)
        
        # Obtener información de la columna
        self.cursor.execute("PRAGMA table_info(ventas)")
        columnas = self.cursor.fetchall()
        
        usuario_col = None
        for col in columnas:
            if col[1] == 'usuario_anulacion_id':
                usuario_col = col
                break
        
        self.assertIsNotNone(usuario_col, "usuario_anulacion_id debe existir")
        self.assertEqual(usuario_col[2].upper(), 'INTEGER',
            f"usuario_anulacion_id debe ser INTEGER, obtenido: {usuario_col[2]}")

    def test_migracion_no_falla_si_columnas_ya_existen(self):
        """Verifica que la migración no falla si las columnas ya existen"""
        from tucajero.config.database import agregar_columnas_si_existen
        
        engine = self._crear_engine_temporal()
        
        # Agregar columnas manualmente primero
        self.cursor.execute("ALTER TABLE ventas ADD COLUMN motivo_anulacion VARCHAR(500)")
        self.cursor.execute("ALTER TABLE ventas ADD COLUMN usuario_anulacion_id INTEGER")
        self.conn.commit()
        
        # Ejecutar migración nuevamente - NO debe fallar
        try:
            agregar_columnas_si_existen(engine)
            exito = True
        except Exception as e:
            exito = False
            print(f"Error: {e}")
        
        self.assertTrue(exito,
            "La migración no debe fallar si las columnas ya existen")

    def test_migracion_orden_logico_columnas(self):
        """Verifica que las columnas de auditoría están después de otras columnas de ventas"""
        # Leer el código para verificar el orden
        database_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'tucajero',
            'config',
            'database.py'
        )
        
        with open(database_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Buscar la lista de columnas
        # Las columnas de auditoría deben estar después de numero_factura
        idx_numero_factura = contenido.find('"numero_factura"')
        idx_motivo = contenido.find('"motivo_anulacion"')
        idx_usuario = contenido.find('"usuario_anulacion_id"')
        
        self.assertGreater(idx_motivo, idx_numero_factura,
            "motivo_anulacion debe estar después de numero_factura en la lista")
        self.assertGreater(idx_usuario, idx_motivo,
            "usuario_anulacion_id debe estar después de motivo_anulacion en la lista")

    def test_migracion_sintaxis_consistente(self):
        """Verifica que la sintaxis de las columnas es consistente con las demás"""
        database_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'tucajero',
            'config',
            'database.py'
        )
        
        with open(database_path, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        
        # Buscar las líneas con las columnas de auditoría
        linea_motivo = None
        linea_usuario = None
        
        for i, linea in enumerate(lineas):
            if '"motivo_anulacion"' in linea:
                linea_motivo = linea.strip()
            if '"usuario_anulacion_id"' in linea:
                linea_usuario = linea.strip()
        
        self.assertIsNotNone(linea_motivo, "Debe existir línea para motivo_anulacion")
        self.assertIsNotNone(linea_usuario, "Debe existir línea para usuario_anulacion_id")
        
        # Verificar formato: ("tabla", "columna", "TIPO")
        self.assertIn('("ventas"', linea_motivo,
            "motivo_anulacion debe tener formato de tupla correcto")
        self.assertIn('("ventas"', linea_usuario,
            "usuario_anulacion_id debe tener formato de tupla correcto")
        
        # Verificar que terminan con coma
        self.assertTrue(linea_motivo.endswith(','),
            "motivo_anulacion debe terminar con coma")
        self.assertTrue(linea_usuario.endswith(','),
            "usuario_anulacion_id debe terminar con coma")

    def test_migracion_sql_generado_correcto(self):
        """Verifica que el SQL generado para agregar columnas es correcto"""
        from tucajero.config.database import agregar_columnas_si_existen
        from sqlalchemy import create_engine, text
        
        engine = self._crear_engine_temporal()
        
        # Ejecutar migración
        agregar_columnas_si_existen(engine)
        
        # Verificar que las columnas existen y son utilizables
        # Insertar un registro de prueba
        self.cursor.execute('''
            INSERT INTO ventas (fecha, total, anulada, motivo_anulacion, usuario_anulacion_id)
            VALUES (?, ?, ?, ?, ?)
        ''', ('2026-04-02 10:00:00', 100.0, 1, 'Error en cobro', 5))
        self.conn.commit()
        
        # Leer el registro
        self.cursor.execute('''
            SELECT id, motivo_anulacion, usuario_anulacion_id FROM ventas WHERE id = 1
        ''')
        resultado = self.cursor.fetchone()
        
        self.assertIsNotNone(resultado, "Debe poder leer las columnas")
        self.assertEqual(resultado[1], 'Error en cobro',
            "motivo_anulacion debe almacenar el valor correcto")
        self.assertEqual(resultado[2], 5,
            "usuario_anulacion_id debe almacenar el valor correcto")

    def test_migracion_permite_null(self):
        """Verifica que las columnas permiten valores NULL"""
        from tucajero.config.database import agregar_columnas_si_existen
        
        engine = self._crear_engine_temporal()
        agregar_columnas_si_existen(engine)
        
        # Insertar registro SIN las columnas de auditoría (deben ser NULL)
        self.cursor.execute('''
            INSERT INTO ventas (fecha, total, anulada)
            VALUES (?, ?, ?)
        ''', ('2026-04-02 11:00:00', 200.0, 0))
        self.conn.commit()
        
        # Leer y verificar que son NULL - usar last_insert_rowid para obtener el ID correcto
        self.cursor.execute('''
            SELECT motivo_anulacion, usuario_anulacion_id FROM ventas WHERE id = (SELECT MAX(id) FROM ventas)
        ''')
        resultado = self.cursor.fetchone()
        
        self.assertIsNotNone(resultado, "Debe haber un registro en la tabla")
        self.assertIsNone(resultado[0], "motivo_anulacion debe permitir NULL")
        self.assertIsNone(resultado[1], "usuario_anulacion_id debe permitir NULL")


class TestMigracionIntegracionCompleta(unittest.TestCase):
    """Pruebas de integración completa de la migración"""

    def test_init_db_ejecuta_migracion(self):
        """Verifica que init_db() ejecuta la migración automáticamente"""
        # Leer el código de init_db
        database_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'tucajero',
            'config',
            'database.py'
        )
        
        with open(database_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar que init_db llama a agregar_columnas_si_existen
        self.assertIn('agregar_columnas_si_existen(engine)', contenido,
            "init_db debe llamar a agregar_columnas_si_existen")
        
        # Verificar el orden: después de create_all
        idx_create_all = contenido.find('Base.metadata.create_all(engine)')
        idx_migracion = contenido.find('agregar_columnas_si_existen(engine)')
        
        self.assertGreater(idx_migracion, idx_create_all,
            "La migración debe ejecutarse después de create_all")

    def test_columnas_en_contexto_otras_columnas(self):
        """Verifica que las columnas nuevas están en contexto con otras columnas existentes"""
        database_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'tucajero',
            'config',
            'database.py'
        )
        
        with open(database_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar que hay otras columnas de ventas antes de las de auditoría
        columnas_ventas = [
            '"cliente_id"',
            '"es_credito"',
            '"descuento_tipo"',
            '"descuento_valor"',
            '"descuento_total"',
            '"cajero_id"',
            '"comprobante"',
            '"numero_factura"',
        ]
        
        idx_ultima_columna = 0
        for col in columnas_ventas:
            idx = contenido.find(col)
            if idx > 0:
                idx_ultima_columna = idx
        
        idx_motivo = contenido.find('"motivo_anulacion"')
        idx_usuario = contenido.find('"usuario_anulacion_id"')
        
        self.assertGreater(idx_motivo, idx_ultima_columna,
            "motivo_anulacion debe estar después de las demás columnas de ventas")
        self.assertGreater(idx_usuario, idx_ultima_columna,
            "usuario_anulacion_id debe estar después de las demás columnas de ventas")


if __name__ == '__main__':
    unittest.main()
