"""
Premium Design System - TuCajero POS
Sistema de diseño global con paleta de colores premium y componentes estandarizados.
"""

import winreg


def get_theme():
    """Detecta el tema del sistema (claro/oscuro)"""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if value == 1 else "dark"
    except:
        return "dark"


def get_colors():
    """
    Obtiene la paleta de colores premium.
    
    Dark Mode: Basado en Slate profundo (#1E293B) con acentos vibrantes
    Light Mode: Basado en blanco limpio con contrastes sutiles
    """
    if get_theme() == "dark":
        return {
            # Fondos - Paleta Slate profunda
            "bg_app": "#0F172A",          # Slate 950 - Fondo principal
            "bg_sidebar": "#1E293B",      # Slate 800 - Barra lateral
            "bg_card": "#1E293B",         # Slate 800 - Tarjetas
            "bg_card_hover": "#334155",   # Slate 700 - Hover cards
            "bg_input": "#334155",        # Slate 700 - Inputs
            "bg_elevated": "#334155",     # Slate 700 - Elementos elevados
            "bg_surface": "#1E293B",      # Slate 800 - Superficies
            
            # Texto - Jerarquía clara
            "text_primary": "#F1F5F9",    # Slate 100 - Texto principal
            "text_secondary": "#94A3B8",  # Slate 400 - Texto secundario
            "text_muted": "#64748B",      # Slate 500 - Texto atenuado
            "text_inverse": "#0F172A",    # Slate 950 - Texto sobre claro
            "text_accent": "#60A5FA",     # Blue 400 - Texto acento
            
            # Bordes - Sutiles pero definidos
            "border": "#475569",          # Slate 600 - Bordes estándar
            "border_strong": "#64748B",   # Slate 500 - Bordes fuertes
            "border_light": "#334155",    # Slate 700 - Bordes ligeros
            
            # Colores semánticos - Design Kit exacto
            "primary": "#3B82F6",         # Blue 500 - Color primario
            "primary_hover": "#2563EB",   # Blue 600 - Hover primario
            "primary_light": "#3B82F620", # Blue 500 con 12% alpha
            "primary_container": "#1E40AF", # Blue 800 - Contenedor primario
            
            "secondary": "#1E293B",       # Slate 800 - Color secundario
            "secondary_hover": "#334155", # Slate 700 - Hover secundario
            
            "success": "#10B981",         # Emerald 500 - Éxito
            "success_light": "#10B98120", # Emerald con 12% alpha
            "success_hover": "#059669",   # Emerald 600
            
            "warning": "#F59E0B",         # Amber 500 - Advertencia (Fiado)
            "warning_light": "#F59E0B20", # Amber con 12% alpha
            "warning_hover": "#D97706",   # Amber 600
            
            "danger": "#EF4444",          # Red 500 - Peligro/Error
            "danger_light": "#EF444420",  # Red con 12% alpha
            "danger_hover": "#DC2626",    # Red 600
            
            "info": "#06B6D4",            # Cyan 500 - Información
            "info_light": "#06B6D420",    # Cyan con 12% alpha
            
            "purple": "#8B5CF6",          # Violet 500 - Acento especial
            "purple_light": "#8B5CF620",  # Violet con 12% alpha
            
            # Acento (alias para primary)
            "accent": "#3B82F6",
            "accent_hover": "#2563EB",
            "accent_light": "#3B82F620",
            
            # Sombras - Profundidad realista
            "shadow_sm": "0px 1px 3px rgba(0,0,0,0.3), 0px 1px 2px rgba(0,0,0,0.2)",
            "shadow_md": "0px 4px 6px rgba(0,0,0,0.4), 0px 2px 4px rgba(0,0,0,0.3)",
            "shadow_lg": "0px 10px 15px rgba(0,0,0,0.5), 0px 4px 6px rgba(0,0,0,0.4)",
            "shadow_xl": "0px 20px 25px rgba(0,0,0,0.6), 0px 10px 10px rgba(0,0,0,0.5)",
            
            # Glassmorphism
            "glass_bg": "rgba(30, 41, 59, 0.7)",
            "glass_border": "rgba(71, 85, 105, 0.5)",
        }
    else:
        return {
            # Fondos - Blanco limpio
            "bg_app": "#F8FAFC",          # Slate 50 - Fondo principal
            "bg_sidebar": "#1E293B",      # Slate 800 - Barra lateral (contraste)
            "bg_card": "#FFFFFF",         # Blanco - Tarjetas
            "bg_card_hover": "#F1F5F9",   # Slate 100 - Hover cards
            "bg_input": "#FFFFFF",        # Blanco - Inputs
            "bg_elevated": "#FFFFFF",     # Blanco - Elementos elevados
            "bg_surface": "#F1F5F9",      # Slate 100 - Superficies
            
            # Texto - Alto contraste
            "text_primary": "#0F172A",    # Slate 900 - Texto principal
            "text_secondary": "#475569",  # Slate 600 - Texto secundario
            "text_muted": "#94A3B8",      # Slate 400 - Texto atenuado
            "text_inverse": "#FFFFFF",    # Blanco - Texto sobre oscuro
            "text_accent": "#2563EB",     # Blue 600 - Texto acento
            
            # Bordes - Sutiles
            "border": "#E2E8F0",          # Slate 200 - Bordes estándar
            "border_strong": "#CBD5E1",   # Slate 300 - Bordes fuertes
            "border_light": "#F1F5F9",    # Slate 100 - Bordes ligeros
            
            # Colores semánticos - Design Kit exacto
            "primary": "#3B82F6",         # Blue 500
            "primary_hover": "#2563EB",   # Blue 600
            "primary_light": "#3B82F618", # Blue 500 con 9% alpha
            "primary_container": "#DBEAFE", # Blue 100
            
            "secondary": "#64748B",       # Slate 500
            "secondary_hover": "#475569", # Slate 600
            
            "success": "#10B981",         # Emerald 500
            "success_light": "#10B98118", # Emerald con 9% alpha
            "success_hover": "#059669",   # Emerald 600
            
            "warning": "#F59E0B",         # Amber 500 (Fiado)
            "warning_light": "#F59E0B18", # Amber con 9% alpha
            "warning_hover": "#D97706",   # Amber 600
            
            "danger": "#EF4444",          # Red 500
            "danger_light": "#EF444418",  # Red con 9% alpha
            "danger_hover": "#DC2626",    # Red 600
            
            "info": "#06B6D4",            # Cyan 500
            "info_light": "#06B6D418",    # Cyan con 9% alpha
            
            "purple": "#8B5CF6",          # Violet 500
            "purple_light": "#8B5CF618",  # Violet con 9% alpha
            
            # Acento (alias para primary)
            "accent": "#3B82F6",
            "accent_hover": "#2563EB",
            "accent_light": "#3B82F618",
            
            # Sombras - Sutiles para modo claro
            "shadow_sm": "0px 1px 3px rgba(0,0,0,0.08), 0px 1px 2px rgba(0,0,0,0.06)",
            "shadow_md": "0px 4px 6px rgba(0,0,0,0.07), 0px 2px 4px rgba(0,0,0,0.06)",
            "shadow_lg": "0px 10px 15px rgba(0,0,0,0.08), 0px 4px 6px rgba(0,0,0,0.05)",
            "shadow_xl": "0px 20px 25px rgba(0,0,0,0.1), 0px 10px 10px rgba(0,0,0,0.08)",
            
            # Glassmorphism
            "glass_bg": "rgba(255, 255, 255, 0.8)",
            "glass_border": "rgba(226, 232, 240, 0.5)",
        }


def get_stylesheet():
    """
    Hoja de estilo global QSS con sistema de diseño premium.
    Incluye estilos para todos los componentes Qt estándar.
    """
    c = get_colors()
    bg = c["bg_app"]
    
    return f"""
        /* ========================================
           CONTENEDORES PRINCIPALES
           ======================================== */
        QMainWindow, QDialog {{
            background-color: {bg};
        }}
        QWidget#centralWidget, QStackedWidget, QWidget {{
            background-color: transparent;
        }}
        QWidget {{
            background-color: {bg};
            color: {c["text_primary"]};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }}
        
        /* ========================================
           TEXTO
           ======================================== */
        QLabel {{
            color: {c["text_primary"]};
            background: transparent;
        }}
        QLabel[disabled="true"] {{
            color: {c["text_muted"]};
        }}
        
        /* ========================================
           INPUTS - Campos de texto
           Border-radius: 12px (estándar premium)
           ======================================== */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1.5px solid {c["border"]};
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 13px;
            selection-background-color: {c["primary"]};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border: 1.5px solid {c["primary"]};
            background-color: {c["bg_elevated"]};
        }}
        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {c["bg_surface"]};
            color: {c["text_muted"]};
        }}
        
        /* ========================================
           COMBOBOX - Selects desplegables
           ======================================== */
        QComboBox {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1.5px solid {c["border"]};
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 13px;
            min-height: 40px;
        }}
        QComboBox:focus {{
            border: 1.5px solid {c["primary"]};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 12px;
        }}
        QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {c["bg_card"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
            border-radius: 12px;
            selection-background-color: {c["primary"]};
            outline: none;
            padding: 4px;
        }}
        QComboBox QAbstractItemView::item {{
            min-height: 36px;
            padding: 6px 12px;
            border-radius: 8px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {c["bg_card_hover"]};
        }}
        
        /* ========================================
           SPINBOX - Inputs numéricos
           ======================================== */
        QSpinBox, QDoubleSpinBox {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1.5px solid {c["border"]};
            border-radius: 12px;
            padding: 10px 14px;
            font-size: 13px;
            min-height: 40px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1.5px solid {c["primary"]};
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: transparent;
            border: none;
            width: 24px;
            margin: 2px;
        }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {c["bg_card_hover"]};
            border-radius: 6px;
        }}
        
        /* ========================================
           BOTONES - Premium con gradiente sutil
           Border-radius: 12px (estándar)
           ======================================== */
        QPushButton {{
            background-color: {c["primary"]};
            color: white;
            border: none;
            border-radius: 12px;
            padding: 11px 20px;
            font-size: 13px;
            font-weight: 600;
            min-height: 42px;
        }}
        QPushButton:hover {{
            background-color: {c["primary_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {c["primary"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
        
        /* ========================================
           TABWIDGET - Pestañas
           ======================================== */
        QTabWidget::pane {{
            border: 1px solid {c["border"]};
            border-radius: 12px;
            background-color: {c["bg_card"]};
            top: -1px;
        }}
        QTabWidget::tab-bar {{
            alignment: left;
        }}
        QTabBar::tab {{
            background-color: {c["bg_surface"]};
            color: {c["text_secondary"]};
            border: none;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            padding: 10px 20px;
            margin-right: 4px;
            font-weight: 500;
            min-width: 100px;
        }}
        QTabBar::tab:selected {{
            background-color: {c["bg_card"]};
            color: {c["text_primary"]};
            font-weight: 600;
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {c["bg_card_hover"]};
            color: {c["text_primary"]};
        }}
        
        /* ========================================
           GROUPBOX - Contenedores agrupados
           ======================================== */
        QGroupBox {{
            background-color: {c["bg_card"]};
            border: 1.5px solid {c["border"]};
            border-radius: 16px;
            margin-top: 16px;
            padding-top: 16px;
            font-weight: 600;
            color: {c["text_primary"]};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 16px;
            padding: 0 12px;
            color: {c["text_secondary"]};
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* ========================================
           PROGRESSBAR - Barras de progreso
           ======================================== */
        QProgressBar {{
            background-color: {c["bg_surface"]};
            border: none;
            border-radius: 8px;
            height: 10px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background-color: {c["primary"]};
            border-radius: 8px;
        }}
        QProgressBar {{
            color: {c["text_muted"]};
            font-size: 11px;
        }}
        
        /* ========================================
           TOOLTIP - Información emergente
           ======================================== */
        QToolTip {{
            background-color: {c["bg_elevated"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
        }}
        
        /* ========================================
           SCROLLBAR - Barras de desplazamiento
           ======================================== */
        QScrollBar:vertical {{
            background-color: {c["bg_surface"]};
            width: 10px;
            border-radius: 5px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background-color: {c["border_strong"]};
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {c["text_muted"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QScrollBar:horizontal {{
            background-color: {c["bg_surface"]};
            height: 10px;
            border-radius: 5px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {c["border_strong"]};
            border-radius: 5px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {c["text_muted"]};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0;
        }}
        
        /* ========================================
           LISTA Y TABLA
           ======================================== */
        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {c["bg_card"]};
            color: {c["text_primary"]};
            border: 1px solid {c["border"]};
            border-radius: 12px;
            outline: none;
            gridline-color: transparent;
        }}
        QListWidget::item, QTreeWidget::item, QTableWidget::item {{
            padding: 8px 12px;
            border-radius: 8px;
            margin: 2px 4px;
        }}
        QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
            background-color: {c["bg_card_hover"]};
        }}
        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
            background-color: {c["primary"]};
            color: white;
        }}
        
        /* ========================================
           HEADER DE TABLA
           ======================================== */
        QHeaderView::section {{
            background-color: {c["bg_surface"]};
            color: {c["text_secondary"]};
            padding: 10px 12px;
            border: none;
            border-bottom: 2px solid {c["border"]};
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* ========================================
           MENU BAR
           ======================================== */
        QMenuBar {{
            background-color: {c["bg_sidebar"]};
            color: {c["text_primary"]};
            padding: 4px;
        }}
        QMenuBar::item {{
            padding: 6px 12px;
            border-radius: 6px;
        }}
        QMenuBar::item:selected {{
            background-color: {c["bg_card_hover"]};
        }}
        QMenu {{
            background-color: {c["bg_card"]};
            border: 1px solid {c["border"]};
            border-radius: 12px;
            padding: 6px;
        }}
        QMenu::item {{
            padding: 8px 16px;
            border-radius: 8px;
        }}
        QMenu::item:selected {{
            background-color: {c["primary"]};
            color: white;
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {c["border"]};
            margin: 6px 8px;
        }}
    """


def btn_sidebar():
    """
    Estilo para botones de navegación lateral.
    Sidebar en Slate oscuro con indicador redondeado de selección.
    """
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {c["text_secondary"]};
            border: none;
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 13px;
            font-weight: 500;
            text-align: left;
            min-height: 44px;
            margin: 4px 8px;
        }}
        QPushButton:hover {{
            background-color: {c["bg_card_hover"]};
            color: {c["text_primary"]};
        }}
        QPushButton:pressed {{
            background-color: {c["bg_surface"]};
            color: {c["primary"]};
        }}
        QPushButton:checked {{
            background-color: {c["primary"]};
            color: white;
            font-weight: 600;
        }}
        QPushButton:disabled {{
            color: {c["text_muted"]};
        }}
    """


def btn_primary():
    """Botón primario con color azul (#3B82F6)"""
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["primary"]};
            color: white;
            border: none;
            border-radius: 12px;
            padding: 11px 20px;
            font-size: 13px;
            font-weight: 600;
            min-height: 42px;
        }}
        QPushButton:hover {{
            background-color: {c["primary_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {c["primary"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
    """


def btn_success():
    """Botón de éxito en verde esmeralda (#10B981)"""
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["success"]};
            color: white;
            border: none;
            border-radius: 12px;
            padding: 11px 20px;
            font-size: 13px;
            font-weight: 600;
            min-height: 42px;
        }}
        QPushButton:hover {{
            background-color: {c["success_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {c["success"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
    """


def btn_warning():
    """Botón de advertencia en ámbar (#F59E0B) - Para Fiado"""
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["warning"]};
            color: white;
            border: none;
            border-radius: 12px;
            padding: 11px 20px;
            font-size: 13px;
            font-weight: 600;
            min-height: 42px;
        }}
        QPushButton:hover {{
            background-color: {c["warning_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {c["warning"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
    """


def btn_danger():
    """Botón de peligro en rojo (#EF4444)"""
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["danger"]};
            color: white;
            border: none;
            border-radius: 12px;
            padding: 11px 20px;
            font-size: 13px;
            font-weight: 600;
            min-height: 42px;
        }}
        QPushButton:hover {{
            background-color: {c["danger_hover"]};
        }}
        QPushButton:pressed {{
            background-color: {c["danger"]};
        }}
        QPushButton:disabled {{
            background-color: {c["border"]};
            color: {c["text_muted"]};
        }}
    """


def btn_secondary():
    """Botón secundario con borde"""
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: {c["bg_input"]};
            color: {c["text_primary"]};
            border: 1.5px solid {c["border"]};
            border-radius: 12px;
            padding: 11px 20px;
            font-size: 13px;
            font-weight: 500;
            min-height: 42px;
        }}
        QPushButton:hover {{
            background-color: {c["bg_card_hover"]};
            border-color: {c["border_strong"]};
        }}
        QPushButton:pressed {{
            background-color: {c["bg_surface"]};
        }}
        QPushButton:disabled {{
            background-color: {c["bg_surface"]};
            color: {c["text_muted"]};
            border-color: {c["border"]};
        }}
    """


def btn_ghost():
    """Botón fantasma - solo texto, para acciones secundarias"""
    c = get_colors()
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {c["text_secondary"]};
            border: none;
            border-radius: 10px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 500;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: {c["bg_card_hover"]};
            color: {c["text_primary"]};
        }}
        QPushButton:pressed {{
            background-color: {c["bg_surface"]};
        }}
        QPushButton:disabled {{
            color: {c["text_muted"]};
        }}
    """


def card_style(elevated=False, padding=16):
    """
    Tarjeta premium con border-radius: 16px.
    
    Args:
        elevated: Si True, usa sombra más pronunciada
        padding: Padding interno en píxeles (default: 16)
    """
    c = get_colors()
    bg = c["bg_elevated"] if elevated else c["bg_card"]
    shadow = c["shadow_lg"] if elevated else c["shadow_sm"]
    return f"""
        background-color: {bg};
        border-radius: 16px;
        border: 1px solid {c["border"]};
        padding: {padding}px;
    """


def elevated_card_style():
    """
    Tarjeta elevada con efecto de profundidad premium.
    Usa sombra XL y fondo más claro para destacar.
    """
    c = get_colors()
    return f"""
        background-color: {c["bg_elevated"]};
        border-radius: 16px;
        border: 1px solid {c["border_light"]};
        padding: 20px;
    """


def glass_style():
    """
    Efecto Glassmorphism premium.
    Fondo semitransparente con blur simulado (backdrop-filter no disponible en Qt).
    Ideal para overlays, modales y paneles flotantes.
    """
    c = get_colors()
    return f"""
        background-color: {c["glass_bg"]};
        border-radius: 16px;
        border: 1px solid {c["glass_border"]};
        padding: 16px;
    """


def label_style(size="md", weight="normal", color_key="text_primary"):
    """
    Estilo tipográfico consistente para jerarquía visual.
    
    Args:
        size: xs (10px), sm (12px), md (13px), lg (16px), xl (20px), xxl (28px)
        weight: normal, medium (500), semibold (600), bold (700)
        color_key: Clave de color del tema (text_primary, text_secondary, etc.)
    """
    c = get_colors()
    sizes = {
        "xs": "10px",
        "sm": "12px",
        "md": "13px",
        "lg": "16px",
        "xl": "20px",
        "xxl": "28px",
        "display": "36px",
    }
    weights = {
        "normal": "400",
        "medium": "500",
        "semibold": "600",
        "bold": "700",
    }
    return f"color: {c[color_key]}; font-size: {sizes.get(size, '13px')}; font-weight: {weights.get(weight, '400')}; background: transparent;"


def separator_style():
    """Separador horizontal sutil"""
    c = get_colors()
    return f"background-color: {c['border']}; max-height: 1px; border: none; border-radius: 1px;"


def input_style():
    """Estilo base para todos los inputs"""
    c = get_colors()
    return f"""
        background-color: {c["bg_input"]};
        color: {c["text_primary"]};
        border: 1.5px solid {c["border"]};
        border-radius: 12px;
        padding: 10px 14px;
        font-size: 13px;
        selection-background-color: {c["primary"]};
    """


def header_style():
    """Estilo para encabezados de sección"""
    c = get_colors()
    return f"""
        background-color: {c["bg_sidebar"]};
        color: {c["text_primary"]};
        border-radius: 16px;
        padding: 16px 20px;
        font-size: 18px;
        font-weight: 700;
    """
