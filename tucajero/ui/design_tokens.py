"""Sistema de diseño premium - NO MODIFICAR"""

class Colors:
    # FONDOS - Inspirado en Maxton
    BG_APP = "#0f1320"           # Fondo principal ultra oscuro
    BG_PANEL = "#151825"         # Sidebar y paneles
    BG_CARD = "#1a1d2e"          # Cards principales
    BG_ELEVATED = "#1f2333"      # Elementos elevados
    BG_INPUT = "#232639"         # Inputs
    BG_HOVER = "#2a2f3e"         # Hover state
    BG_ACTIVE = "#2f3544"        # Active state

    # TEXTO - Jerarquía clara
    TEXT_PRIMARY = "#ffffff"     # Blanco puro
    TEXT_SECONDARY = "#cbd5e1"   # Gris claro
    TEXT_TERTIARY = "#94a3b8"    # Gris medio
    TEXT_MUTED = "#64748b"       # Gris oscuro
    TEXT_INVERSE = "#0f172a"     # Para fondos claros

    # BORDES - Sutiles pero visibles
    BORDER_SUBTLE = "#1e293b"
    BORDER_DEFAULT = "#334155"
    BORDER_STRONG = "#475569"
    BORDER_FOCUS = "#3b82f6"

    # GRADIENTES PREMIUM (Maxton style)
    GRADIENT_CYAN_START = "#00d4ff"
    GRADIENT_CYAN_END = "#00a3cc"
    GRADIENT_GREEN_START = "#00ff88"
    GRADIENT_GREEN_END = "#00cc66"
    GRADIENT_PINK_START = "#ff0080"
    GRADIENT_PINK_END = "#cc0066"
    GRADIENT_PURPLE_START = "#a855f7"
    GRADIENT_PURPLE_END = "#7c3aed"
    GRADIENT_BLUE_START = "#3b82f6"
    GRADIENT_BLUE_END = "#1e40af"
    GRADIENT_ORANGE_START = "#ff8c00"
    GRADIENT_ORANGE_END = "#cc7000"

    # COLORES PLANOS (para elementos sin gradiente)
    PRIMARY = "#3b82f6"
    SUCCESS = "#00ff88"
    WARNING = "#fbbf24"
    DANGER = "#ff0080"
    INFO = "#00d4ff"
    PURPLE = "#a855f7"

    # SOMBRAS
    SHADOW_SM = "0 1px 3px 0 rgba(0, 0, 0, 0.4)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.5)"
    SHADOW_LG = "0 10px 20px -3px rgba(0, 0, 0, 0.6)"
    SHADOW_XL = "0 20px 40px -8px rgba(0, 0, 0, 0.7)"
    SHADOW_GLOW_CYAN = "0 0 30px 0 rgba(0, 212, 255, 0.3)"
    SHADOW_GLOW_GREEN = "0 0 30px 0 rgba(0, 255, 136, 0.3)"
    SHADOW_GLOW_PINK = "0 0 30px 0 rgba(255, 0, 128, 0.3)"


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
