"""
Constantes centralizadas para TuCajero POS
Todas las constantes globales del sistema deben estar aquí
"""

# ==================== IMPUESTOS ====================
IVA_RATE = 0.19  # 19% IVA estándar Colombia
IVA_INCLUIDO_DEFAULT = False

# ==================== MONEDA ====================
MONEDA_DEFAULT = "COP"
MONEDA_SIMBOLO = "$"
MONEDA_DECIMALES = 2

# ==================== CONFIGURACIÓN APP ====================
APP_NAME = "TuCajero"
APP_VERSION = "3.1"
APP_AUTHOR = "Francisco Collinas"

# ==================== RUTAS ====================
DATA_DIR_NAME = "TuCajero"
DATABASE_NAME = "pos.db"
BACKUP_DIR_NAME = "backups"
LOGS_DIR_NAME = "logs"
CONFIG_DIR_NAME = "config"
ASSETS_DIR_NAME = "assets"

# ==================== UI CONSTANTS ====================
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768
TABLE_ROW_HEIGHT = 40
BUTTON_HEIGHT = 36
INPUT_HEIGHT = 32

# ==================== PAGINACIÓN ====================
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# ==================== TIMEOUTS ====================
DB_TIMEOUT_SECONDS = 30
BACKUP_RETENTION_DAYS = 30

# ==================== MÉTODOS DE PAGO ====================
METODOS_PAGO = [
    "Efectivo",
    "Tarjeta Débito",
    "Tarjeta Crédito",
    "Transferencia",
    "Otro",
]

# ==================== ESTADOS ====================
ESTADO_ACTIVO = "activo"
ESTADO_INACTIVO = "inactivo"
ESTADO_VENTA_PENDIENTE = "pendiente"
ESTADO_VENTA_COMPLETADA = "completada"
ESTADO_VENTA_CANCELADA = "cancelada"

# ==================== VALIDACIONES ====================
CODIGO_PRODUCTO_MAX_LENGTH = 50
NOMBRE_PRODUCTO_MAX_LENGTH = 200
NOMBRE_CLIENTE_MAX_LENGTH = 150
NIT_MAX_LENGTH = 20

# ==================== COLORES THEME ====================
# Paleta de colores del sistema de diseño
COLORS = {
    "primary": "#3498db",
    "primary_dark": "#2980b9",
    "primary_light": "#5dade2",
    "secondary": "#2ecc71",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#3498db",
    "dark": "#2c3e50",
    "light": "#ecf0f1",
    "muted": "#95a5a6",
    "white": "#ffffff",
    "bg_app": "#f5f6fa",
    "bg_card": "#ffffff",
    "bg_input": "#ffffff",
    "text_primary": "#2c3e50",
    "text_secondary": "#7f8c8d",
    "border": "#dcdde1",
}
