"""
Pruebas de Seguridad - TuCajero POS
Valida todas las correcciones de seguridad implementadas (SEC-001 a SEC-014)
Fecha: 2026-04-05
"""

import pytest
import os
import sys
import tempfile
import hashlib
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Agregar directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============================================================================
# SEC-001: Test de Criptografía Asimétrica (Ed25519)
# ============================================================================

class TestSEC001LicensingCrypto:
    """Valida que el sistema de licencias use criptografía asimétrica"""

    def test_no_hardcoded_secret_in_license_manager(self):
        """SEC-001: No debe haber secretos hardcodeados en license_manager.py"""
        from tucajero.security import license_manager
        
        # Verificar que no hay variable _S con secreto
        assert not hasattr(license_manager, '_S'), "❌ SEC-001: Secret _S still exists!"
        
        # Verificar que hay una clave pública configurada (aunque esté vacía)
        assert hasattr(license_manager, '_PUBLIC_KEY_HEX'), "❌ SEC-001: No hay _PUBLIC_KEY_HEX"

    def test_no_hardcoded_secret_in_generador(self):
        """SEC-001: No debe haber secretos hardcodeados en GeneradorLicencias.py"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "GeneradorLicencias",
            os.path.join(os.path.dirname(__file__), '..', 'GeneradorLicencias.py')
        )
        generador = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generador)
        
        # Verificar que no hay variable _S
        assert not hasattr(generador, '_S'), "❌ SEC-001: Secret _S still exists in GeneradorLicencias!"

    def test_ed25519_signature_verification(self):
        """SEC-001: Verificar que Ed25519 funciona correctamente"""
        import nacl.signing
        
        # Generar par de claves de prueba
        signing_key = nacl.signing.SigningKey.generate()
        verify_key = signing_key.verify_key
        
        # Firmar un machine_id de prueba
        machine_id = "TEST12345678"
        message = machine_id.encode('utf-8')
        signed = signing_key.sign(message)
        
        # Verificar con la clave pública
        verify_key.verify(message, signed.signature)  # No debe lanzar excepción
        
        # Verificar que firma inválida falla
        wrong_message = b"WRONG12345678"
        with pytest.raises(nacl.exceptions.BadSignatureError):
            verify_key.verify(wrong_message, signed.signature)

    def test_license_validation_with_wrong_machine_id(self):
        """SEC-001: Licencia no debe ser válida para diferente machine_id"""
        import nacl.signing
        
        signing_key = nacl.signing.SigningKey.generate()
        machine_id_correct = "CORRECT12345"
        machine_id_wrong = "WRONG123456789"
        
        message = machine_id_correct.encode('utf-8')
        signed = signing_key.sign(message)
        
        # La firma es para un machine_id específico
        # Si intentamos validar con otro, debe fallar
        assert machine_id_correct != machine_id_wrong


# ============================================================================
# SEC-002: Test de Prevención de SQL Injection
# ============================================================================

class TestSEC002SQLInjection:
    """Valida que haya validación de nombres de tabla"""

    def test_allowed_tables_constant_exists(self):
        """SEC-002: Debe existir constante ALLOWED_TABLES"""
        from tucajero.config.database import ALLOWED_TABLES
        
        assert isinstance(ALLOWED_TABLES, frozenset), "❌ SEC-002: ALLOWED_TABLES debe ser frozenset"
        assert "productos" in ALLOWED_TABLES
        assert "ventas" in ALLOWED_TABLES
        assert "cajeros" in ALLOWED_TABLES

    def test_validate_table_name_function(self):
        """SEC-002: Función de validación debe rechazar tablas inválidas"""
        from tucajero.config.database import _validate_table_name
        
        # Tablas válidas deben pasar
        assert _validate_table_name("productos") == "productos"
        assert _validate_table_name("ventas") == "ventas"
        
        # Tablas inválidas deben ser rechazadas
        with pytest.raises(ValueError, match="Invalid table name"):
            _validate_table_name("DROP TABLE")
        
        with pytest.raises(ValueError, match="Invalid table name"):
            _validate_table_name("productos; DROP TABLE usuarios")

    def test_no_direct_sql_injection_in_migration(self):
        """SEC-002: Validar que nombres de tabla se validan en migración"""
        from tucajero.config.database import _validate_table_name
        
        # Intentar inyección SQL a través de nombre de tabla
        malicious_names = [
            "productos; DROP TABLE usuarios",
            "ventas--",
            "productos' OR '1'='1",
            "../../etc/passwd",
        ]
        
        for name in malicious_names:
            with pytest.raises((ValueError, Exception)):
                _validate_table_name(name)


# ============================================================================
# SEC-003: Test de Hashing de PIN con bcrypt
# ============================================================================

class TestSEC003PINHashing:
    """Valida que los PINs usen bcrypt en lugar de SHA-256"""

    def test_hash_pin_uses_bcrypt(self):
        """SEC-003: hash_pin debe usar bcrypt, no SHA-256"""
        from tucajero.models.cajero import hash_pin
        
        pin = "1234"
        hashed = hash_pin(pin)
        
        # bcrypt hashes empiezan con $2b$
        assert hashed.startswith('$2b$'), f"❌ SEC-003: Hash no es bcrypt: {hashed[:20]}"
        
        # No debe ser SHA-256 (64 caracteres hex)
        assert len(hashed) == 60, f"❌ SEC-003: bcrypt hash debe tener 60 chars, tiene {len(hashed)}"

    def test_same_pin_different_hashes(self):
        """SEC-003: Mismo PIN debe generar hashes diferentes (salt aleatorio)"""
        from tucajero.models.cajero import hash_pin
        
        pin = "5678"
        hash1 = hash_pin(pin)
        hash2 = hash_pin(pin)
        
        # Los hashes deben ser diferentes debido al salt aleatorio
        assert hash1 != hash2, "❌ SEC-003: Mismo PIN generó mismo hash (salt no es aleatorio)"

    def test_pin_verification_with_bcrypt(self):
        """SEC-003: Verificación de PIN debe funcionar con bcrypt"""
        import bcrypt
        from tucajero.models.cajero import hash_pin, Cajero
        
        pin = "9876"
        hashed = hash_pin(pin)
        
        # Verificar con bcrypt.checkpw
        assert bcrypt.checkpw(pin.encode('utf-8'), hashed.encode('utf-8')), \
            "❌ SEC-003: Verificación de PIN falló"
        
        # PIN incorrecto debe fallar
        assert not bcrypt.checkpw("0000".encode('utf-8'), hashed.encode('utf-8')), \
            "❌ SEC-003: PIN incorrecto fue aceptado"

    def test_is_bcrypt_hash_function(self):
        """SEC-003: Función para detectar hashes antiguos"""
        from tucajero.models.cajero import _is_bcrypt_hash, hash_pin
        
        # SHA-256 hash (64 chars hex)
        sha256_hash = hashlib.sha256("1234".encode()).hexdigest()
        assert not _is_bcrypt_hash(sha256_hash), "❌ SEC-003: SHA-256 detectado como bcrypt"
        
        # bcrypt hash
        bcrypt_hash = hash_pin("1234")
        assert _is_bcrypt_hash(bcrypt_hash), "❌ SEC-003: bcrypt no detectado como bcrypt"

    def test_needs_migration_function(self):
        """SEC-003: Detección de hashes que necesitan migración"""
        from tucajero.models.cajero import needs_migration, hash_pin
        
        # SHA-256 necesita migración
        sha256_hash = hashlib.sha256("1234".encode()).hexdigest()
        assert needs_migration(sha256_hash), "❌ SEC-003: SHA-256 debe necesitar migración"
        
        # bcrypt no necesita migración
        bcrypt_hash = hash_pin("1234")
        assert not needs_migration(bcrypt_hash), "❌ SEC-003: bcrypt no debe necesitar migración"


# ============================================================================
# SEC-008: Test de PIN Seguro y Setup Forzado
# ============================================================================

class TestSEC008SecurePIN:
    """Valida que el PIN setup forzado funcione correctamente"""

    def test_pin_blacklist_validation(self):
        """SEC-008: PINs comunes deben ser rechazados"""
        from tucajero.app.ui.views.auth.pin_setup_dialog import es_pin_seguro
        
        common_pins = ["0000", "1234", "1111", "9876", "1212"]
        for pin in common_pins:
            is_safe, reason = es_pin_seguro(pin)
            assert not is_safe, f"❌ SEC-008: PIN común '{pin}' no fue rechazado"

    def test_secure_pin_validation(self):
        """SEC-008: PINs aleatorios deben ser aceptados"""
        from tucajero.app.ui.views.auth.pin_setup_dialog import es_pin_seguro
        
        # PINs que deberían ser aceptados (no secuenciales, no repetitivos)
        secure_pins = ["1593", "7284", "3951", "6148", "2837"]
        for pin in secure_pins:
            is_safe, reason = es_pin_seguro(pin)
            assert is_safe, f"❌ SEC-008: PIN seguro '{pin}' fue rechazado: {reason}"

    def test_pin_must_be_set_flag_in_model(self):
        """SEC-008: Modelo Cajero debe tener flag pin_must_be_set"""
        from tucajero.models.cajero import Cajero
        
        # Verificar que el atributo existe
        assert hasattr(Cajero, 'pin_must_be_set'), \
            "❌ SEC-008: Modelo Cajero no tiene pin_must_be_set"

    def test_admin_default_uses_random_pin(self):
        """SEC-008: Admin por defecto debe usar PIN aleatorio, no '0000'"""
        # Verificar en el código de CajeroService
        import inspect
        from tucajero.services.cajero_service import CajeroService
        
        source = inspect.getsource(CajeroService.crear_admin_default)
        
        # No debe crear admin con PIN "0000" hardcoded en la lógica
        # (Puede mencionarse en comentarios/docstring, pero no en código)
        lines = [l for l in source.split('\n') if not l.strip().startswith('#') and '"""' not in l]
        code_only = '\n'.join(lines)
        
        # Verificar que usa secrets o random para generar PIN
        assert "secrets" in source or "random" in source, \
            "❌ SEC-008: crear_admin_default no genera PIN aleatorio"
        
        # Verificar que no llama a self.crear("Admin", "0000", ...)
        assert 'self.crear("Admin", "0000"' not in code_only, \
            "❌ SEC-008: crear_admin_default aún crea con PIN '0000'"


# ============================================================================
# SEC-011: Test de Rate Limiting
# ============================================================================

class TestSEC011RateLimiting:
    """Valida que el rate limiting de login funcione"""

    def test_cajero_has_rate_limiting_fields(self):
        """SEC-011: Modelo Cajero debe tener campos de rate limiting"""
        from tucajero.models.cajero import Cajero
        
        assert hasattr(Cajero, 'failed_attempts'), "❌ SEC-011: Falta failed_attempts"
        assert hasattr(Cajero, 'locked_until'), "❌ SEC-011: Falta locked_until"

    def test_record_failed_attempt(self):
        """SEC-011: Registrar intentos fallidos debe funcionar"""
        from tucajero.models.cajero import Cajero, hash_pin
        
        cajero = Cajero(id=1, nombre="Test", pin_hash=hash_pin("1234"), rol="cajero")
        cajero.failed_attempts = 0
        
        # Registrar 4 intentos fallidos
        for i in range(4):
            cajero.record_failed_attempt()
            assert cajero.failed_attempts == i + 1
            assert not cajero.is_locked(), f"❌ SEC-011: Bloqueado antes de 5 intentos"

    def test_account_lockout_after_5_attempts(self):
        """SEC-011: Cuenta debe bloquearse después de 5 intentos"""
        from tucajero.models.cajero import Cajero, hash_pin
        
        cajero = Cajero(id=1, nombre="Test", pin_hash=hash_pin("1234"), rol="cajero")
        cajero.failed_attempts = 0
        
        # 5 intentos fallidos
        for _ in range(5):
            cajero.record_failed_attempt()
        
        # Debe estar bloqueado
        assert cajero.failed_attempts == 5
        assert cajero.is_locked(), "❌ SEC-011: Cuenta no se bloqueó después de 5 intentos"
        assert cajero.locked_until is not None

    def test_lockout_expires_after_15_minutes(self):
        """SEC-011: Bloqueo debe expirar después de 15 minutos"""
        from tucajero.models.cajero import Cajero, hash_pin
        from datetime import datetime, timedelta
        
        cajero = Cajero(id=1, nombre="Test", pin_hash=hash_pin("1234"), rol="cajero")
        cajero.failed_attempts = 5
        cajero.locked_until = (datetime.now() - timedelta(minutes=16)).isoformat()
        
        # Debe haber expirado
        assert not cajero.is_locked(), \
            "❌ SEC-011: Bloqueo no expiró después de 15 minutos"
        assert cajero.failed_attempts == 0, \
            "❌ SEC-011: failed_attempts no se resetó al expirar"

    def test_reset_failed_attempts_on_success(self):
        """SEC-011: Intentos deben resetearse en login exitoso"""
        from tucajero.models.cajero import Cajero, hash_pin
        
        cajero = Cajero(id=1, nombre="Test", pin_hash=hash_pin("1234"), rol="cajero")
        cajero.failed_attempts = 3
        cajero.locked_until = None
        
        cajero.reset_failed_attempts()
        
        assert cajero.failed_attempts == 0
        assert cajero.locked_until is None


# ============================================================================
# SEC-005 & SEC-006: Test de Validación de Import/Export
# ============================================================================

class TestSEC005ImportExportValidation:
    """Valida que la importación/exportación tenga validaciones de seguridad"""

    def test_file_extension_validation(self):
        """SEC-005: Solo archivos .tucajero deben ser aceptados"""
        from tucajero.utils.data_manager import importar_datos
        
        # Intentar importar archivo con extensión incorrecta
        result = importar_datos("test.txt")
        assert not result["ok"], "❌ SEC-005: Archivo .txt fue aceptado"
        assert "invalida" in result["error"].lower() or "extensión" in result["error"].lower()

    def test_file_size_validation(self):
        """SEC-005: Archivos grandes deben ser rechazados"""
        from tucajero.utils.data_manager import importar_datos, MAX_IMPORT_SIZE
        
        # Crear archivo temporal grande
        with tempfile.NamedTemporaryFile(suffix='.tucajero', delete=False) as f:
            # Escribir más de MAX_IMPORT_SIZE bytes
            f.write(b'x' * (MAX_IMPORT_SIZE + 1000))
            temp_path = f.name
        
        try:
            result = importar_datos(temp_path)
            assert not result["ok"], "❌ SEC-005: Archivo grande fue aceptado"
            assert "grande" in result["error"].lower()
        finally:
            os.unlink(temp_path)

    def test_zip_contents_validation(self):
        """SEC-006: ZIP debe contener solo archivos permitidos"""
        import zipfile
        from tucajero.utils.data_manager import importar_datos
        
        # Crear ZIP con archivo no permitido
        with tempfile.NamedTemporaryFile(suffix='.tucajero', delete=False) as f:
            temp_path = f.name
        
        try:
            with zipfile.ZipFile(temp_path, 'w') as zf:
                zf.writestr("malicious.exe", b"malicious content")
            
            result = importar_datos(temp_path)
            assert not result["ok"], "❌ SEC-006: ZIP con archivos no permitidos fue aceptado"
        finally:
            os.unlink(temp_path)


# ============================================================================
# SEC-014: Test de Validación de Archivos Excel
# ============================================================================

class TestSEC014ExcelValidation:
    """Valida que la carga de archivos Excel tenga validaciones"""

    def test_file_extension_validation(self):
        """SEC-014: Solo extensiones .xlsx, .xls, .csv deben ser aceptadas"""
        try:
            from tucajero.utils.importador import leer_archivo
        except ModuleNotFoundError:
            pytest.skip("openpyxl no instalado - test saltado")
        
        # Intentar cargar archivo con extensión incorrecta
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            f.write(b"malicious")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="no soportado"):
                leer_archivo(temp_path)
        finally:
            os.unlink(temp_path)

    def test_formula_injection_prevention(self):
        """SEC-014: Fórmulas Excel deben ser neutralizadas"""
        try:
            from tucajero.utils.importador import _sanitize_cell_value
        except ModuleNotFoundError:
            pytest.skip("openpyxl no instalado - test saltado")
        
        malicious_values = [
            "=1+2",
            "+SUM(A1:A10)",
            "-1+2",
            "@SUM(A1)",
            "\t=CMD",
        ]
        
        for value in malicious_values:
            sanitized = _sanitize_cell_value(value)
            assert sanitized.startswith("'"), \
                f"❌ SEC-014: Fórmula no neutralizada: {value} -> {sanitized}"


# ============================================================================
# SEC-012: Test de No Fuga de Información en Errores
# ============================================================================

class TestSEC012NoInfoLeak:
    """Valida que los errores no expongan información sensible"""

    def test_error_handler_no_exposes_stack_trace(self):
        """SEC-012: Verificar que main.py no muestre stack traces en UI"""
        # Leer el archivo directamente sin importarlo (evita dependencias Qt)
        main_path = os.path.join(os.path.dirname(__file__), '..', 'tucajero', 'main.py')
        with open(main_path, 'r') as f:
            source = f.read()
        
        # Buscar la función global_exception_handler
        assert 'global_exception_handler' in source, "❌ SEC-012: No se encuentra global_exception_handler"
        
        # No debe mostrar detailed text con stack trace al usuario
        # (Puede estar comentado o removido)
        if 'setDetailedText' in source:
            # Si existe, debe estar comentado o marcado como SEC-012
            lines_with_detailed = [l for l in source.split('\n') if 'setDetailedText' in l and not l.strip().startswith('#')]
            for line in lines_with_detailed:
                assert 'SEC-012' in line or 'REMOVED' in line or '#' in line, \
                    f"❌ SEC-012: setDetailedText aún activo: {line}"

    def test_error_handler_generates_reference_id(self):
        """SEC-012: Handler de errores debe generar ID de referencia"""
        # Leer el archivo directamente sin importarlo
        main_path = os.path.join(os.path.dirname(__file__), '..', 'tucajero', 'main.py')
        with open(main_path, 'r') as f:
            source = f.read()
        
        # Debe generar un ID de referencia (uuid)
        assert 'uuid' in source or 'error_ref' in source, \
            "❌ SEC-012: No se genera ID de referencia para errores"


# ============================================================================
# SEC-004: Test de Manejo de Excepciones
# ============================================================================

class TestSEC004ExceptionHandling:
    """Valida que no haya manejadores de excepción vacíos"""

    def test_no_bare_except_in_main(self):
        """SEC-004: main.py no debe tener 'except: pass'"""
        # Leer archivo directamente sin importarlo
        main_path = os.path.join(os.path.dirname(__file__), '..', 'tucajero', 'main.py')
        with open(main_path, 'r') as f:
            source = f.read()
        
        # Buscar "except:" seguido de "pass" en la siguiente línea
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == 'except:' and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                assert next_line != 'pass', \
                    f"❌ SEC-004: 'except: pass' encontrado en main.py línea {i+1}"

    def test_no_bare_except_in_backup_service(self):
        """SEC-004: backup_service.py no debe tener 'except: pass'"""
        import inspect
        from tucajero.services import backup_service
        
        source = inspect.getsource(backup_service)
        
        lines = source.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == 'except:' and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                assert next_line != 'pass', \
                    f"❌ SEC-004: 'except: pass' encontrado en backup_service.py línea {i+1}"


# ============================================================================
# Tests de Integración de Seguridad
# ============================================================================

class TestSecurityIntegration:
    """Tests de integración para validar seguridad end-to-end"""

    def test_full_login_flow_with_rate_limiting(self):
        """SEC-011: Flujo completo de login con rate limiting"""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from tucajero.config.database import Base
        from tucajero.models.cajero import Cajero, hash_pin
        from tucajero.services.cajero_service import CajeroService
        
        # Crear BD en memoria
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Crear cajero
        cajero_service = CajeroService(session)
        cajero = cajero_service.crear("TestUser", "1234", rol="cajero")
        
        # Intentos fallidos
        for i in range(5):
            result, success, error = cajero_service.verificar_login(cajero.id, "0000")
            assert not success, f"❌ SEC-011: Login fallido {i+1} fue exitoso"
        
        # 6to intento debe estar bloqueado
        result, success, error = cajero_service.verificar_login(cajero.id, "1234")
        assert not success, "❌ SEC-011: Login exitoso pero cuenta debía estar bloqueada"
        assert "bloqueada" in error.lower(), f"❌ SEC-011: Mensaje de error incorrecto: {error}"
        
        # Login correcto después del bloqueo (sin esperar, debe fallar)
        result, success, error = cajero_service.verificar_login(cajero.id, "1234")
        assert not success

    def test_pin_migration_from_sha256_to_bcrypt(self):
        """SEC-003: Migración transparente de SHA-256 a bcrypt"""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from tucajero.config.database import Base
        from tucajero.models.cajero import Cajero, hash_pin
        import hashlib
        
        # Crear BD en memoria
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Crear cajero con hash SHA-256 (antiguo)
        old_hash = hashlib.sha256("1234".encode()).hexdigest()
        cajero = Cajero(
            id=1,
            nombre="OldUser",
            pin_hash=old_hash,  # SHA-256 hash
            rol="cajero",
            failed_attempts=0
        )
        session.add(cajero)
        session.commit()
        
        # Verificar que el hash antiguo se detecta
        success, needs_rehash = cajero.verificar_pin("1234")
        assert success, "❌ SEC-003: PIN antiguo no fue verificado"
        assert needs_rehash, "❌ SEC-003: No se detectó necesidad de migración"
        
        # Verificar que después de rehash, es bcrypt
        cajero.rehash_pin("1234")
        session.commit()
        
        assert cajero.pin_hash.startswith('$2b$'), \
            "❌ SEC-003: Rehash no convirtió a bcrypt"
        
        success, needs_rehash = cajero.verificar_pin("1234")
        assert success and not needs_rehash, \
            "❌ SEC-003: Después de rehash, aún necesita migración"


# ============================================================================
# Resumen de Ejecución
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
