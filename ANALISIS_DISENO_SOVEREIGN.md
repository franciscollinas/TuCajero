# 🎨 TuCajero POS → Sovereign Analyst: Análisis de Diseño UI/UX

## 📋 Executive Summary

**Fecha:** 30 de Marzo 2026  
**Objetivo:** Transformar TuCajero POS de un diseño "Dark Mode Genérico" a un diseño **"Sovereign Analyst - Executive POS"** premium.

**Estado Actual:** Diseño funcional pero con elementos visuales que delatan una estética "template" (bordes marcados, gradientes neón, inconsistencias en spacing).

**Estado Deseado:** Diseño ejecutivo, sofisticado, con profundidad tonal, tipografía editorial, y componentes que transmiten autoridad profesional.

---

## 🔍 Análisis Comparativo Detallado

### 1. SISTEMA DE COLORES

| Aspecto | TuCajero Actual | Sovereign Analyst (Referencia) | Brecha |
|---------|-----------------|-------------------------------|--------|
| **Background Base** | `#0F172A` (Slate 900) | `#0b1326` (Obsidian) | ✅ Cercano |
| **Surface/Cards** | `#1E293B` (Slate 800) | `#171f33` (Surface Container) | ⚠️ Ajustar |
| **Primary Accent** | `#7C3AED` (Purple) | `#adc6ff` → `#3b82f6` (Executive Blue) | 🔴 Cambiar |
| **Success** | `#22C55E` (Green) | `#4edea3` (Soft Emerald) | ⚠️ Ajustar |
| **Text Primary** | `#FFFFFF` | `#dae2fd` / `#f8fafc` (Off-white blue) | ⚠️ Ajustar |
| **Text Secondary** | `#94A3B8` | `#c2c6d6` / `#94a3b8` (Slate con tinte azul) | ✅ Cercano |
| **Bordes** | `rgba(255,255,255,0.08)` visible | **Prohibidos** (usar tonal shifts) | 🔴 Crítico |

#### 🎯 Acciones Requeridas

```python
# tucajero/app/ui/theme/theme.py - NUEVA PALETA
# =============================================

# Backgrounds (Obsidian Foundation)
BG_OBSIDIAN = "#0b1326"           # Surface base (reemplaza #0F172A)
BG_SURFACE = "#131b2e"            # Surface container low (sidebar)
BG_CARD = "#171f33"               # Surface container (cards)
BG_CARD_HIGH = "#222a3d"          # Surface container high (hover)

# Primary (Executive Blue - reemplaza Purple)
PRIMARY = "#3b82f6"               # Azul ejecutivo principal
PRIMARY_CONTAINER = "#1e293b"     # Para gradientes sutiles
PRIMARY_FIXED = "#d2e4ff"         # Para hover states
PRIMARY_ON_FIXED = "#001d37"      # Texto sobre primary

# Success (Soft Emerald)
SUCCESS = "#4edea3"               # Esmeralda vibrante
SUCCESS_CONTAINER = "#064e3b"     # Para backgrounds de éxito

# Text (Con tinte azul para cohesión)
TEXT_PRIMARY = "#f8fafc"          # Casi blanco con tinte azul
TEXT_SECONDARY = "#94a3b8"        # Slate profesional
TEXT_MUTED = "#64748b"            # Para texto deshabilitado

# Borders (Ghost Borders - 15% opacity)
OUTLINE_VARIANT = "#424754"       # Usar con 15% opacidad máximo
```

---

### 2. TIPOGRAFÍA

| Aspecto | TuCajero Actual | Sovereign Analyst | Brecha |
|---------|-----------------|-------------------|--------|
| **Familia Principal** | Segoe UI | Inter + Manrope | 🔴 Cambiar |
| **Display (KPIs)** | 36px Bold | 44px Medium (Manrope) | ⚠️ Ajustar |
| **Headlines** | 24px Bold | 28px Semi-Bold | ⚠️ Ajustar |
| **Body** | 14-16px | 14px Inter Regular | ✅ OK |
| **Labels/Caption** | 12px | 11px Bold Uppercase +0.05em | ⚠️ Ajustar |
| **Letter Spacing** | Default | -0.02em (Display), +0.05em (Labels) | 🔴 Agregar |

#### 🎯 Acciones Requeridas

```python
# tucajero/app/ui/theme/theme.py - TIPOGRAFÍA
# ============================================

_font_family_body = "Inter"       # Para body, labels, utilitarios
_font_family_display = "Manrope"  # Para KPIs, títulos principales

# Si no están disponibles, usar Segoe UI con ajustes:
_font_family_body = "Segoe UI"
_font_family_display = "Segoe UI"

# Tamaños ajustados (en px)
FONT_DISPLAY_LG = 44              # KPIs principales (era 36px)
FONT_DISPLAY_MD = 36              # KPIs secundarios
FONT_HEADLINE_LG = 28             # Títulos de sección (era 24px)
FONT_HEADLINE_MD = 22             # Subtítulos
FONT_TITLE_MD = 18                # Títulos de cards
FONT_BODY_MD = 14                 # Cuerpo principal
FONT_BODY_SM = 13                 # Texto secundario
FONT_LABEL_SM = 11                # Labels, hints (era 12px)

# Letter spacing (em)
LETTER_SPACING_DISPLAY = -0.02    # KPIs (más compacto)
LETTER_SPACING_LABEL = 0.05       # Labels (más espaciado)
LETTER_SPACING_NORMAL = 0         # Body
```

```css
/* En QSS - Ejemplo de aplicación */
QLabel#kpi_value {
    font-family: "Segoe UI";
    font-size: 44px;
    font-weight: 500;  /* Medium, no Bold */
    letter-spacing: -0.5px;  /* -0.02em */
    color: #f8fafc;
}

QLabel#section_title {
    font-family: "Segoe UI";
    font-size: 28px;
    font-weight: 600;  /* Semi-Bold */
    color: #f8fafc;
}

QLabel#table_header {
    font-size: 11px;
    font-weight: 700;  /* Bold */
    text-transform: uppercase;
    letter-spacing: 0.5px;  /* +0.05em */
    color: #94a3b8;
}
```

---

### 3. ELEVACIÓN Y PROFUNDIDAD

| Aspecto | TuCajero Actual | Sovereign Analyst | Brecha |
|---------|-----------------|-------------------|--------|
| **Estrategia** | Bordes + sombras | Tonal layering (sin bordes) | 🔴 Crítico |
| **Cards** | Borde 1px visible | Sin borde, solo background shift | 🔴 Cambiar |
| **Sidebar** | Borde derecho visible | Tonal shift puro | 🔴 Cambiar |
| **Shadows** | Genéricas | Ambientales (8% opacity, 40px blur) | ⚠️ Ajustar |
| **Glassmorphism** | 85% opacity + borde | 70% opacity + 20px blur | ⚠️ Ajustar |

#### 🎯 Acciones Requeridas

```python
# tucajero/app/ui/theme/theme.py - ELEVACIÓN
# ==========================================

# NIVELES DE SUPERFICIE (Bottom to Top)
# Level 0: Base canvas
SURFACE_LEVEL_0 = "#0b1326"  # Fondo principal

# Level 1: Secciones grandes (sidebar, footer)
SURFACE_LEVEL_1 = "#131b2e"  # Surface container low

# Level 2: Cards de contenido
SURFACE_LEVEL_2 = "#171f33"  # Surface container

# Level 3: Interactive (hover, active)
SURFACE_LEVEL_3 = "#222a3d"  # Surface container high

# Level 4: Floating (modals, dropdowns)
SURFACE_LEVEL_4 = "#334155"  # Surface container highest

# Ghost Border (15% opacity máximo)
GHOST_BORDER = "rgba(66, 71, 84, 0.15)"  # outline_variant al 15%

# Ambient Shadow (solo para floating elements)
AMBIENT_SHADOW = "rgba(0, 0, 0, 0.08)"  # 8% opacity
AMBIENT_SHADOW_BLUR = "40px"
```

```css
/* Card sin bordes - SOVEREIGN ANALYST */
QFrame#card {
    background-color: #171f33;  /* Surface container */
    border: none;               /* SIN BORDES */
    border-radius: 12px;
    padding: 24px;              /* spacing-6 */
}

/* Sidebar sin borde derecho */
QWidget#sidebar {
    background-color: #131b2e;  /* Surface container low */
    border: none;               /* SIN BORDE */
}

/* Input fields - "Recessed Field" */
QLineEdit {
    background-color: #060e20;  /* Surface container lowest */
    border: 2px solid transparent;
    border-bottom: 2px solid #3b82f6;  /* Solo bottom accent */
    border-radius: 8px;
    padding: 12px 16px;
}
QLineEdit:focus {
    border-bottom-color: #3b82f6;  /* Primary en focus */
}

/* Glassmorphism para modals/overlays */
QDialog#glass {
    background: rgba(23, 31, 51, 0.7);  /* 70% opacity */
    border: none;
    border-radius: 16px;
    /* backdrop-filter: blur(20px); - No disponible en Qt */
}
```

---

### 4. COMPONENTES

#### 4.1 Botones

| Aspecto | TuCajero Actual | Sovereign Analyst | Acción |
|---------|-----------------|-------------------|--------|
| **Primary Fill** | Gradiente Purple→Pink | Gradiente Blue→Blue Container | 🔴 Cambiar |
| **Border Radius** | 10px | 8px (DEFAULT) | ⚠️ Ajustar |
| **Hover State** | Opacity 0.9 | Surface bright inner glow | 🔴 Cambiar |
| **Secondary** | Borde visible | Ghost (20% opacity) | 🔴 Cambiar |

```python
# tucajero/app/ui/theme/theme.py - BOTONES
# ========================================

def button_primary():
    """Primary Button - Gradiente Ejecutivo"""
    return """
        QPushButton {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #3b82f6,      /* Primary */
                stop:1 #1e293b       /* Primary Container */
            );
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #60a5fa,      /* Primary más claro */
                stop:1 #334155       /* Surface bright */
            );
        }
        QPushButton:pressed {
            background: #2563eb;
        }
    """

def button_secondary():
    """Secondary Button - Ghost Style"""
    return """
        QPushButton {
            background: transparent;
            color: #f8fafc;
            border: 1px solid rgba(66, 71, 84, 0.2);  /* 20% opacity */
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 500;
            font-size: 14px;
        }
        QPushButton:hover {
            background: rgba(51, 57, 77, 0.5);  /* Surface bright */
            border-color: rgba(66, 71, 84, 0.4);
        }
    """

def button_sidebar():
    """Sidebar Navigation - Pill Indicator"""
    return """
        QPushButton {
            background: transparent;
            color: #94a3b8;  /* Secondary text */
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            text-align: left;
            font-weight: 500;
        }
        QPushButton:hover {
            color: #f8fafc;
            background: rgba(255, 255, 255, 0.05);
        }
        QPushButton:checked {
            color: #f8fafc;
            background: transparent;
            border-left: 3px solid #3b82f6;  /* Pill indicator */
            padding-left: 13px;  /* Compensar border */
        }
    """
```

#### 4.2 KPI Cards

| Aspecto | TuCajero Actual | Sovereign Analyst | Acción |
|---------|-----------------|-------------------|--------|
| **Layout** | Gradiente full | Surface + Icon + Sparkline | 🔴 Rediseñar |
| **Icon** | Integrado en gradiente | Pill background (10% opacity) | 🔴 Cambiar |
| **Trend** | No tiene | +12% con ícono trending | 🔴 Agregar |
| **Border** | 1px visible | Sin borde | 🔴 Eliminar |

```python
# tucajero/ui/components/kpi_card.py - VERSIÓN SOVEREIGN
# ======================================================

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class KPICardSovereign(QWidget):
    """KPI Card estilo Sovereign Analyst"""
    
    def __init__(self, title, value, icon="payments", trend=None, trend_value=None, parent=None):
        super().__init__(parent)
        self.setup_ui(title, value, icon, trend, trend_value)
    
    def setup_ui(self, title, value, icon, trend, trend_value):
        # Determinar colores según trend
        if trend == "up":
            trend_color = "#4edea3"  # Emerald
            trend_bg = "rgba(78, 222, 163, 0.1)"
        elif trend == "down":
            trend_color = "#ef4444"  # Red
            trend_bg = "rgba(239, 68, 68, 0.1)"
        else:
            trend_color = "#94a3b8"
            trend_bg = "transparent"
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #171f33;  /* Surface container */
                border: none;
                border-radius: 12px;
                padding: 24px;
            }}
            QWidget:hover {{
                background-color: #222a3d;  /* Surface container high */
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header: Icon + Trend
        header = QHBoxLayout()
        
        # Icon pill
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(59, 130, 246, 0.1);  /* Primary 10% */
                color: #60a5fa;
                border-radius: 8px;
                padding: 8px;
                font-size: 20px;
            }}
        """)
        header.addWidget(icon_label)
        
        header.addStretch()
        
        # Trend indicator
        if trend:
            trend_label = QLabel(f"{'↑' if trend == 'up' else '↓'} {trend_value}")
            trend_label.setStyleSheet(f"""
                QLabel {{
                    color: {trend_color};
                    font-size: 12px;
                    font-weight: 700;
                    background-color: {trend_bg};
                    padding: 4px 8px;
                    border-radius: 4px;
                }}
            """)
            header.addWidget(trend_label)
        
        layout.addLayout(header)
        
        # Title
        title_label = QLabel(title.upper())
        title_label.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #f8fafc;
                font-size: 36px;
                font-weight: 500;
                letter-spacing: -0.5px;
            }
        """)
        layout.addWidget(value_label)
```

#### 4.3 Tablas de Datos

| Aspecto | TuCajero Actual | Sovereign Analyst | Acción |
|---------|-----------------|-------------------|--------|
| **Headers** | 12px, background | 11px Bold Uppercase +0.05em | ⚠️ Ajustar |
| **Dividers** | 1px visible | Sin dividers (spacing + zebra) | 🔴 Cambiar |
| **Row Hover** | Purple 20% | Surface bright 40% | ⚠️ Ajustar |
| **Zebra** | 2% opacity | 2% opacity (OK) | ✅ OK |
| **Padding** | 12px | 16px (spacing-4) | ⚠️ Ajustar |

```css
/* Tabla Sovereign Analyst */
QTableWidget#sovereign_table {
    background: transparent;
    color: #f8fafc;
    border: none;
    gridline-color: transparent;  /* SIN GRID LINES */
    alternate-background-color: rgba(255, 255, 255, 0.02);  /* 2% zebra */
}

QTableWidget#sovereign_table::item {
    padding: 16px;  /* spacing-4 */
    border-bottom: none;  /* SIN DIVISORES */
}

QTableWidget#sovereign_table::item:hover {
    background: rgba(51, 57, 77, 0.4);  /* Surface bright 40% */
}

QHeaderView::section {
    background: rgba(15, 23, 42, 0.5);  /* Surface dim */
    color: #94a3b8;
    padding: 16px;
    border: none;  /* SIN BORDES */
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;  /* +0.05em */
}
```

---

### 5. SPACING & LAYOUT

| Aspecto | TuCajero Actual | Sovereign Analyst | Acción |
|---------|-----------------|-------------------|--------|
| **Base Scale** | Inconsistente | 4px grid | ⚠️ Estandarizar |
| **Section Gap** | 20px | 32px (spacing-8) | 🔴 Aumentar |
| **Card Padding** | 16px | 24px (spacing-6) | 🔴 Aumentar |
| **KPI Gap** | 20px | 24px (spacing-6) | ⚠️ Ajustar |
| **Whitespace** | Mínimo | Generoso (32-48px) | 🔴 Aumentar |

```python
# tucajero/app/ui/theme/theme.py - SPACING SCALE
# ==============================================

# Base: 4px grid
SPACING_XS = 4    # 0.25rem - Micro spacing
SPACING_SM = 8    # 0.5rem - Small gaps
SPACING_MD = 16   # 1rem - Standard gap
SPACING_LG = 24   # 1.5rem - Section gaps
SPACING_XL = 32   # 2rem - Large sections
SPACING_2XL = 48  # 3rem - Hero sections
SPACING_3XL = 64  # 4rem - Page margins

# Border Radius
RADIUS_SM = 4     # Buttons, small elements
RADIUS_MD = 8     # Cards, inputs (DEFAULT)
RADIUS_LG = 12    # Large cards, modals
RADIUS_XL = 16    # Feature cards
RADIUS_FULL = 9999 # Pills, avatars
```

---

### 6. SIDEBAR DE NAVEGACIÓN

| Aspecto | TuCajero Actual | Sovereign Analyst | Acción |
|---------|-----------------|-------------------|--------|
| **Width** | ~240px | 256px (w-64) | ⚠️ Ajustar |
| **Background** | `#0F172A` 95% | `#1E293B` puro | ⚠️ Ajustar |
| **Active State** | Background full | Pill indicator izquierdo | 🔴 Cambiar |
| **Icon + Text** | OK | OK | ✅ OK |
| **CTA Button** | No tiene | Gradiente "New Sale" | 🔴 Agregar |
| **Logo Area** | OK | + "Terminal 01" subtitle | ⚠️ Agregar |

```python
# tucajero/ui/main_window.py - SIDEBAR SOVEREIGN
# ===============================================

def _build_sidebar_sovereign(self):
    """Sidebar estilo Sovereign Analyst"""
    sidebar = QFrame()
    sidebar.setFixedWidth(256)  # w-64
    sidebar.setStyleSheet("""
        QFrame {
            background-color: #1E293B;  /* Surface container low */
            border: none;
        }
    """)
    
    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(0, 24, 0, 24)
    layout.setSpacing(8)
    
    # Logo Area
    logo_container = QWidget()
    logo_layout = QVBoxLayout(logo_container)
    logo_layout.setContentsMargins(24, 0, 24, 24)
    logo_layout.setSpacing(4)
    
    logo_label = QLabel("TuCajero POS")
    logo_label.setStyleSheet("""
        QLabel {
            color: #f8fafc;
            font-size: 16px;
            font-weight: 800;  /* Black */
            letter-spacing: -0.3px;
        }
    """)
    
    terminal_label = QLabel("TERMINAL 01")
    terminal_label.setStyleSheet("""
        QLabel {
            color: #64748b;  /* Muted */
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    """)
    
    logo_layout.addWidget(logo_label)
    logo_layout.addWidget(terminal_label)
    layout.addWidget(logo_container)
    
    # Navigation Items
    nav_container = QWidget()
    nav_layout = QVBoxLayout(nav_container)
    nav_layout.setContentsMargins(8, 0, 8, 0)
    nav_layout.setSpacing(4)
    
    nav_items = [
        ("dashboard", "Dashboard", "dashboard"),
        ("ventas", "Punto de Venta", "point_of_sale"),
        ("inventario", "Inventario", "inventory_2"),
        ("clientes", "Clientes", "group"),
        ("reportes", "Reportes", "analytics"),
    ]
    
    for view_id, label, icon in nav_items:
        btn = QPushButton(f"  {icon}  {label}")
        btn.setFixedHeight(48)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(self._btn_sidebar_style())
        btn.clicked.connect(lambda checked, v=view_id: self.show_view(v))
        self._nav_buttons[view_id] = btn
        nav_layout.addWidget(btn)
    
    layout.addWidget(nav_container)
    layout.addStretch()
    
    # CTA Button - "New Sale"
    cta_btn = QPushButton("💰 Nueva Venta")
    cta_btn.setFixedHeight(48)
    cta_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    cta_btn.setStyleSheet("""
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #3b82f6, stop:1 #1e40af);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 700;
            font-size: 14px;
            margin: 16px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #60a5fa, stop:1 #3b82f6);
        }
    """)
    layout.addWidget(cta_btn)
    
    # Bottom Links (Support, Logout)
    bottom_container = QWidget()
    bottom_layout = QVBoxLayout(bottom_container)
    bottom_layout.setContentsMargins(16, 16, 16, 0)
    bottom_layout.setSpacing(8)
    
    support_btn = QPushButton("  ❓  Soporte")
    support_btn.setFixedHeight(40)
    support_btn.setStyleSheet(self._btn_sidebar_bottom_style())
    
    logout_btn = QPushButton("  🚪  Salir")
    logout_btn.setFixedHeight(40)
    logout_btn.setStyleSheet(self._btn_sidebar_bottom_style())
    
    bottom_layout.addWidget(support_btn)
    bottom_layout.addWidget(logout_btn)
    layout.addWidget(bottom_container)
    
    return sidebar

def _btn_sidebar_style(self):
    return """
        QPushButton {
            background: transparent;
            color: #94a3b8;
            border: none;
            border-radius: 8px;
            padding: 12px 16px;
            font-size: 14px;
            font-weight: 500;
            text-align: left;
        }
        QPushButton:hover {
            color: #f8fafc;
            background: rgba(255, 255, 255, 0.05);
        }
        QPushButton:checked {
            color: #f8fafc;
            background: rgba(59, 130, 246, 0.15);
            border-left: 3px solid #3b82f6;
            padding-left: 13px;
        }
    """

def _btn_sidebar_bottom_style(self):
    return """
        QPushButton {
            background: transparent;
            color: #64748b;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 13px;
            text-align: left;
        }
        QPushButton:hover {
            color: #94a3b8;
            background: rgba(255, 255, 255, 0.03);
        }
    """
```

---

## 📊 MATRIZ DE PRIORIZACIÓN

| Prioridad | Componente | Impacto Visual | Esfuerzo | ROI |
|-----------|------------|----------------|----------|-----|
| **P0** | Eliminar bordes visibles | Alto | Bajo | Alto |
| **P0** | Cambiar Primary Purple → Blue | Alto | Medio | Alto |
| **P0** | Ajustar spacing (20px → 32px) | Alto | Bajo | Alto |
| **P1** | Nueva tipografía (tamaños) | Medio | Bajo | Medio |
| **P1** | Rediseñar KPI Cards | Alto | Medio | Alto |
| **P1** | Sidebar sin bordes + pill indicator | Medio | Medio | Medio |
| **P2** | Tablas sin dividers | Medio | Bajo | Medio |
| **P2** | Botones con gradientes blue | Bajo | Bajo | Bajo |
| **P3** | Agregar sparklines a KPIs | Bajo | Alto | Bajo |
| **P3** | Actividad reciente widget | Bajo | Alto | Bajo |

---

## 🗺️ PLAN DE IMPLEMENTACIÓN

### Fase 1: Cimientos (Día 1)
1. Actualizar `theme.py` con nueva paleta de colores
2. Eliminar todos los bordes visibles de cards y sidebar
3. Ajustar spacing global (20px → 24-32px)
4. Cambiar primary de purple a blue

### Fase 2: Tipografía y Componentes (Día 2)
1. Ajustar tamaños de fuente (KPIs: 36px → 44px)
2. Implementar letter-spacing (-0.02em display, +0.05em labels)
3. Rediseñar KPICard con icon pill + trend indicator
4. Actualizar botones (gradiente blue, ghost secondary)

### Fase 3: Navegación y Tablas (Día 3)
1. Rediseñar sidebar (pill indicator, CTA button)
2. Eliminar dividers de tablas
3. Ajustar padding de celdas (12px → 16px)
4. Implementar zebra striping sutil (2%)

### Fase 4: Pulido Final (Día 4)
1. Agregar widgets de "Actividad Reciente"
2. Implementar sparklines en KPIs (opcional)
3. Ajustar glassmorphism (70% opacity)
4. QA visual comparativo con referencia

---

## 📁 ARCHIVOS A MODIFICAR

| Archivo | Cambios | Prioridad |
|---------|---------|-----------|
| `tucajero/app/ui/theme/theme.py` | Paleta completa, spacing, radius | P0 |
| `tucajero/ui/main_window.py` | Sidebar sin bordes, pill indicator | P1 |
| `tucajero/ui/components/kpi_card.py` | Rediseño completo | P1 |
| `tucajero/app/ui/views/dashboard/dashboard_view.py` | Ajustar spacing, eliminar bordes | P0 |
| `tucajero/ui/views/dashboard/dashboard_clean.py` | Ajustar spacing, eliminar bordes | P0 |
| `tucajero/ui/ventas_view.py` | Ajustar colores, eliminar bordes | P2 |
| `tucajero/ui/components/data_table.py` | Sin dividers, padding 16px | P2 |

---

## ✅ CHECKLIST DE VALIDACIÓN

### Color System
- [ ] Background base es `#0b1326` (Obsidian)
- [ ] Primary es azul (`#3b82f6`), NO purple
- [ ] Success es esmeralda (`#4edea3`), NO green estándar
- [ ] Text primary tiene tinte azul (`#f8fafc`), NO blanco puro
- [ ] Bordes visibles eliminados (usar tonal shifts)

### Typography
- [ ] KPIs usan 44px Medium (no 36px Bold)
- [ ] Títulos de sección usan 28px Semi-Bold
- [ ] Labels de tabla usan 11px Bold Uppercase +0.05em
- [ ] Display tiene letter-spacing -0.02em

### Elevation
- [ ] Cards NO tienen bordes visibles
- [ ] Sidebar NO tiene borde derecho
- [ ] Shadows solo en modals (8% opacity, 40px blur)
- [ ] Superficies usan 5-tier nesting

### Components
- [ ] Botones primarios: gradiente blue (no purple)
- [ ] Botones secundarios: ghost style (20% border)
- [ ] KPI Cards: icon pill + trend indicator
- [ ] Sidebar: pill indicator izquierdo (no background full)
- [ ] Tablas: sin dividers, zebra 2%

### Spacing
- [ ] Gap entre secciones: 32px mínimo
- [ ] Padding de cards: 24px
- [ ] Padding de celdas: 16px
- [ ] Whitespace generoso (no crowding)

---

## 🎯 MÉTRICAS DE ÉXITO

1. **Test de los 5 segundos:** Un usuario nuevo debe poder identificar:
   - Ventas del día (KPI principal)
   - Dónde hacer una nueva venta
   - Estado del inventario
   
2. **Test de coherencia:** Cerrar los ojos y abrir la app. ¿Se siente como un "centro de comando ejecutivo" o como una "tienda colorida"?

3. **Test de accesibilidad:** Todos los textos deben tener contraste ≥ 4.5:1 (WCAG AA)

4. **Test de performance:** La UI debe mantener 60fps con el nuevo diseño

---

## 📌 NOTAS FINALES

### Lo que NO cambiar
- Funcionalidad core (ventas, inventario, clientes)
- Estructura de base de datos
- Servicios y lógica de negocio
- Atajos de teclado existentes

### Lo que SÍ cambia
- **Look & Feel:** De "Dark Mode Template" a "Executive Dashboard"
- **Percepción de valor:** Un diseño premium justifica un precio premium
- **Fatiga visual:** Menos contraste agresivo = menos cansancio en turnos largos
- **Identidad de marca:** TuCajero se ve como software empresarial, no como app genérica

### Principio Rector
> "El diseño no es solo cómo se ve, es cómo funciona. Un POS ejecutivo debe hacer que el cajero se sienta como un analista financiero, no como un despachador."

---

*Documento creado: 30 de Marzo 2026*  
*Basado en: DESIGN.md (Sovereign Analyst Specification)*  
*Referencia visual: stitch_interfaz_pos.zip (screen.png, code.html)*
