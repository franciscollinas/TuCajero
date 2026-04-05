import hashlib
import re
from sqlalchemy import Column, Integer, String, Boolean, Index
from tucajero.config.database import Base


def hash_pin(pin):
    """
    SEC-003 FIX: Use bcrypt for PIN hashing instead of SHA-256.
    bcrypt provides:
    - Automatic per-hash salt generation
    - Computational cost factor (slow, resistant to brute-force)
    - Output format: $2b$12$<22-char-salt><31-char-hash> (60 chars total)
    """
    import bcrypt
    pin_bytes = str(pin).encode('utf-8')
    # bcrypt.gensalt() generates a random 128-bit salt
    # rounds=12 means 2^12 iterations (~400ms per hash on modern hardware)
    hashed = bcrypt.hashpw(pin_bytes, bcrypt.gensalt(rounds=12))
    return hashed.decode('utf-8')


def _is_bcrypt_hash(pin_hash):
    """Check if a stored hash is in bcrypt format ($2b$...)."""
    if pin_hash is None:
        return False
    return bool(re.match(r'^\$2[aby]\$\d{2}\$.{53}$', pin_hash))


def needs_migration(pin_hash):
    """
    SEC-003: Detect if a PIN hash is still using the old SHA-256 format.
    Old hashes are 64 hex chars; bcrypt hashes start with '$2b$'.
    """
    if pin_hash is None:
        return False
    return not _is_bcrypt_hash(pin_hash)


class Cajero(Base):
    __tablename__ = "cajeros"
    __table_args__ = (Index("idx_cajero_activo", "activo"),)

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    pin_hash = Column(String(128), nullable=False)  # Increased from 64 to accommodate bcrypt
    rol = Column(String(20), default="cajero")
    activo = Column(Boolean, default=True)
    # SEC-011: Rate limiting fields
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(String(50), nullable=True)
    # SEC-008: Flag to force PIN setup on first login
    pin_must_be_set = Column(Boolean, default=False)

    def verificar_pin(self, pin):
        """
        SEC-003 FIX: Use bcrypt.checkw for verification.
        Also handles migration from old SHA-256 hashes transparently.
        Returns tuple: (success: bool, needs_rehash: bool)
        """
        import bcrypt
        # Check if this is an old SHA-256 hash that needs migration
        if not _is_bcrypt_hash(self.pin_hash):
            # Old SHA-256 hash — verify the old way, then signal need for rehash
            old_hash = hashlib.sha256(str(pin).encode()).hexdigest()
            if self.pin_hash == old_hash:
                return True, True  # Valid but needs rehash to bcrypt
            return False, False

        # bcrypt verification
        pin_bytes = str(pin).encode('utf-8')
        stored_hash_bytes = self.pin_hash.encode('utf-8')
        try:
            if bcrypt.checkpw(pin_bytes, stored_hash_bytes):
                return True, False
            return False, False
        except (ValueError, TypeError):
            # Corrupted hash — reject
            return False, False

    def rehash_pin(self, pin):
        """Re-hashes the PIN using bcrypt (for migration from SHA-256)."""
        self.pin_hash = hash_pin(pin)

    def is_locked(self):
        """SEC-011: Check if the account is currently locked out."""
        if self.locked_until is None:
            return False
        from datetime import datetime
        try:
            lock_expiry = datetime.fromisoformat(self.locked_until)
            if datetime.now() >= lock_expiry:
                # Lock has expired, reset
                self.failed_attempts = 0
                self.locked_until = None
                return False
            return True
        except (ValueError, TypeError):
            return False

    def record_failed_attempt(self):
        """SEC-011: Record a failed login attempt and lock if threshold reached."""
        from datetime import datetime, timedelta
        self.failed_attempts = (self.failed_attempts or 0) + 1
        if self.failed_attempts >= 5:
            # Lock for 15 minutes
            self.locked_until = (datetime.now() + timedelta(minutes=15)).isoformat()

    def reset_failed_attempts(self):
        """SEC-011: Reset failed attempts counter on successful login."""
        self.failed_attempts = 0
        self.locked_until = None

    def __repr__(self):
        return f"<Cajero {self.nombre}>"
