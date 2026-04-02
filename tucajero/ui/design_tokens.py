"""Sistema de diseño premium - NO MODIFICAR"""

class Colors:
    # FONDOS - Modo oscuro premium
    BG_APP = "#0a0e1a"           # Fondo principal ultra oscuro
    BG_PANEL = "#131824"         # Paneles principales
    BG_CARD = "#1a1f2e"          # Cards y contenedores
    BG_ELEVATED = "#1f2533"      # Elementos elevados
    BG_INPUT = "#242938"         # Inputs y campos
    BG_HOVER = "#2a2f3e"         # Estado hover
    BG_ACTIVE = "#2f3544"        # Estado activo
    
    # TEXTO - Jerarquía visual clara
    TEXT_PRIMARY = "#f8fafc"     # Texto principal 100% blanco
    TEXT_SECONDARY = "#cbd5e1"   # Texto secundario 80% opacidad
    TEXT_TERTIARY = "#94a3b8"    # Texto terciario 60% opacidad
    TEXT_MUTED = "#64748b"       # Texto deshabilitado 40% opacidad
    TEXT_INVERSE = "#0f172a"     # Texto sobre fondos claros
    
    # BORDES - Separadores sutiles
    BORDER_SUBTLE = "#1e293b"    # Bordes muy suaves
    BORDER_DEFAULT = "#334155"   # Bordes normales
    BORDER_STRONG = "#475569"    # Bordes marcados
    BORDER_FOCUS = "#3b82f6"     # Borde al hacer focus
    
    # COLORES DE MARCA (Gradientes premium)
    PRIMARY = "#3b82f6"          # Azul principal
    PRIMARY_DARK = "#1e40af"
    PRIMARY_LIGHT = "#60a5fa"
    
    SUCCESS = "#10b981"          # Verde éxito
    SUCCESS_DARK = "#047857"
    SUCCESS_LIGHT = "#34d399"
    
    WARNING = "#f59e0b"          # Naranja advertencia
    WARNING_DARK = "#b45309"
    WARNING_LIGHT = "#fbbf24"
    
    DANGER = "#ef4444"           # Rojo peligro
    DANGER_DARK = "#b91c1c"
    DANGER_LIGHT = "#f87171"
    
    INFO = "#06b6d4"             # Cyan información
    INFO_DARK = "#0e7490"
    INFO_LIGHT = "#22d3ee"
    
    PURPLE = "#8b5cf6"           # Púrpura acento
    PURPLE_DARK = "#6d28d9"
    PURPLE_LIGHT = "#a78bfa"
    
    # SOMBRAS (para CSS box-shadow)
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.3)"
    SHADOW_MD = "0 4px 8px -2px rgba(0, 0, 0, 0.4)"
    SHADOW_LG = "0 12px 24px -4px rgba(0, 0, 0, 0.5)"
    SHADOW_XL = "0 20px 40px -8px rgba(0, 0, 0, 0.6)"
    SHADOW_GLOW = "0 0 20px 0 rgba(59, 130, 246, 0.3)"
    
    # OVERLAYS
    OVERLAY_LIGHT = "rgba(255, 255, 255, 0.05)"
    OVERLAY_MEDIUM = "rgba(255, 255, 255, 0.1)"
    OVERLAY_STRONG = "rgba(255, 255, 255, 0.15)"
    OVERLAY_DARK = "rgba(0, 0, 0, 0.5)"
    OVERLAY_GLASS = "rgba(26, 31, 46, 0.8)"


class Typography:
    # TAMAÑOS (en píxeles - NO CAMBIAR)
    H1 = 36  # Títulos de página
    H2 = 28  # Títulos de sección
    H3 = 22  # Subtítulos
    H4 = 18  # Encabezados pequeños
    H5 = 16  # Etiquetas destacadas
    BODY_LG = 15  # Texto grande
    BODY = 14  # Texto normal (default)
    BODY_SM = 13  # Texto pequeño
    CAPTION = 12  # Captions y ayuda
    TINY = 11  # Texto muy pequeño
    
    # PESOS (NO CAMBIAR)
    THIN = 300
    REGULAR = 400
    MEDIUM = 500
    SEMIBOLD = 600
    BOLD = 700
    EXTRABOLD = 800
    
    # ALTURAS DE LÍNEA (NO CAMBIAR)
    LEADING_TIGHT = 1.25
    LEADING_NORMAL = 1.5
    LEADING_RELAXED = 1.75
    
    # FAMILIAS
    SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    MONO = "JetBrains Mono, Consolas, Monaco, monospace"
    DISPLAY = "Plus Jakarta Sans, Inter, sans-serif"


class Spacing:
    # ESPACIADO (en píxeles - NO CAMBIAR)
    XXXS = 2
    XXS = 4
    XS = 6
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    XXXXL = 40
    XXXXXL = 48
    XXXXXXL = 64


class BorderRadius:
    # RADIOS DE BORDE (NO CAMBIAR)
    NONE = 0
    SM = 6
    MD = 8
    LG = 12
    XL = 16
    XXL = 20
    XXXL = 24
    FULL = 9999


class Transitions:
    # DURACIONES (en ms - NO CAMBIAR)
    FAST = 150
    NORMAL = 200
    SLOW = 300
    SLOWER = 500
    
    # EASING (NO CAMBIAR)
    EASE = "cubic-bezier(0.4, 0, 0.2, 1)"
    EASE_IN = "cubic-bezier(0.4, 0, 1, 1)"
    EASE_OUT = "cubic-bezier(0, 0, 0.2, 1)"
    EASE_IN_OUT = "cubic-bezier(0.4, 0, 0.2, 1)"


class Elevation:
    # Z-INDEX (NO CAMBIAR)
    BASE = 0
    DROPDOWN = 1000
    STICKY = 1100
    FIXED = 1200
    MODAL_BACKDROP = 1300
    MODAL = 1400
    POPOVER = 1500
    TOOLTIP = 1600


# GRADIENTES PREMIUM (NO MODIFICAR)
GRADIENTS = {
    "blue": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b82f6, stop:1 #1e40af)",
    "green": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10b981, stop:1 #047857)",
    "purple": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8b5cf6, stop:1 #6d28d9)",
    "orange": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f59e0b, stop:1 #ea580c)",
    "cyan": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #06b6d4, stop:1 #0e7490)",
    "pink": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ec4899, stop:1 #be185d)",
    "indigo": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366f1, stop:1 #4338ca)",
    "teal": "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #14b8a6, stop:1 #0f766e)",
}


# ICONOS (tamaños exactos - NO CAMBIAR)
class IconSize:
    XS = 12
    SM = 16
    MD = 20
    LG = 24
    XL = 32
    XXL = 48
    XXXL = 64
