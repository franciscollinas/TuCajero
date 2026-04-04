"""Sistema de diseño - NO MODIFICAR"""

# ============================================================
# TEMA CLARO (estilo Login) - TEMA POR DEFECTO
# ============================================================
class LightColors:
    # FONDOS - Tema claro estilo login
    BG_APP = "#F1F5F9"           # Fondo principal (slate-100)
    BG_PANEL = "#FFFFFF"         # Sidebar y paneles
    BG_CARD = "#FFFFFF"          # Cards principales
    BG_ELEVATED = "#F8FAFC"      # Elementos elevados
    BG_INPUT = "#FFFFFF"         # Inputs
    BG_HOVER = "#F1F5F9"         # Hover state
    BG_ACTIVE = "#E2E8F0"        # Active state

    # TEXTO - Jerarquía clara (estilo login)
    TEXT_PRIMARY = "#0F172A"     # Texto principal (slate-900)
    TEXT_SECONDARY = "#475569"   # Texto secundario (slate-600)
    TEXT_TERTIARY = "#64748B"    # Texto terciario (slate-500)
    TEXT_MUTED = "#94A3B8"       # Texto deshabilitado (slate-400)
    TEXT_INVERSE = "#FFFFFF"     # Para fondos oscuros

    # BORDES - Estilo login
    BORDER_SUBTLE = "#F1F5F9"    # Bordes muy sutiles
    BORDER_DEFAULT = "#E2E8F0"   # Bordes normales (slate-200)
    BORDER_STRONG = "#CBD5E1"    # Bordes marcados (slate-300)
    BORDER_FOCUS = "#2563EB"     # Borde focus (blue-600)

    # GRADIENTES PREMIUM (mismos gradientes)
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

    # COLORES PLANOS
    PRIMARY = "#2563EB"          # Azul login (blue-600)
    PRIMARY_DARK = "#1D4ED8"     # Azul hover (blue-700)
    PRIMARY_DEEPER = "#1E40AF"   # Azul pressed (blue-800)
    PRIMARY_DEEPEST = "#1E3A8A"  # Azul profundo (blue-900)
    SUCCESS = "#10B981"          # Verde éxito (emerald-500)
    SUCCESS_DARK = "#059669"
    SUCCESS_LIGHT = "#D1FAE5"
    WARNING = "#F59E0B"          # Naranja advertencia (amber-500)
    WARNING_DARK = "#D97706"
    WARNING_LIGHT = "#FEF3C7"
    DANGER = "#EF4444"           # Rojo peligro (red-500)
    DANGER_DARK = "#DC2626"
    DANGER_LIGHT = "#FEE2E2"
    INFO = "#06B6D4"             # Cyan info (cyan-500)
    INFO_DARK = "#0891B2"
    INFO_LIGHT = "#CFFAFE"
    PURPLE = "#8B5CF6"           # Púrpura acento (violet-500)
    PURPLE_DARK = "#7C3AED"

    # FOCUS (estilo login)
    FOCUS_BG = "#DBEAFE"         # Fondo focus (blue-100)

    # SOMBRAS
    SHADOW_SM = "0 1px 3px 0 rgba(0, 0, 0, 0.08)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    SHADOW_LG = "0 10px 20px -3px rgba(0, 0, 0, 0.12)"
    SHADOW_XL = "0 20px 40px -8px rgba(0, 0, 0, 0.15)"
    SHADOW_GLOW_CYAN = "0 0 20px 0 rgba(6, 182, 212, 0.2)"
    SHADOW_GLOW_GREEN = "0 0 20px 0 rgba(16, 185, 129, 0.2)"
    SHADOW_GLOW_PINK = "0 0 20px 0 rgba(236, 72, 153, 0.2)"


# ============================================================
# TEMA OSCURO (Maxton) - MANTENIDO POR COMPATIBILIDAD
# ============================================================
class DarkColors:
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
    PRIMARY_DARK = "#1e40af"
    SUCCESS = "#00ff88"
    SUCCESS_DARK = "#00cc66"
    SUCCESS_LIGHT = "#34d399"
    WARNING = "#fbbf24"
    WARNING_DARK = "#b45309"
    DANGER = "#ff0080"
    DANGER_DARK = "#cc0066"
    DANGER_LIGHT = "#f87171"
    INFO = "#00d4ff"
    INFO_DARK = "#0e7490"
    PURPLE = "#a855f7"
    PURPLE_DARK = "#6d28d9"

    # SOMBRAS
    SHADOW_SM = "0 1px 3px 0 rgba(0, 0, 0, 0.4)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.5)"
    SHADOW_LG = "0 10px 20px -3px rgba(0, 0, 0, 0.6)"
    SHADOW_XL = "0 20px 40px -8px rgba(0, 0, 0, 0.7)"
    SHADOW_GLOW_CYAN = "0 0 30px 0 rgba(0, 212, 255, 0.3)"
    SHADOW_GLOW_GREEN = "0 0 30px 0 rgba(0, 255, 136, 0.3)"
    SHADOW_GLOW_PINK = "0 0 30px 0 rgba(255, 0, 128, 0.3)"


# Alias para compatibilidad: Colors = LightColors (tema por defecto)
Colors = LightColors


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
