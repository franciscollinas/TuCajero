# 🎯 PLAN EXACTO: Dashboard Premium Estilo Maxton
## Instrucciones PIXEL-PERFECT para Qwen/Antigravity

**REGLA DE ORO:** COPIA EXACTAMENTE. NO IMPROVISES. NO USES TU CRITERIO.

---

## 📊 ANÁLISIS DEL DISEÑO DE REFERENCIA (Maxton)

### Layout Structure (medidas exactas)

```
┌─────────────────────────────────────────────────────────────┐
│ HEADER (height: 60px)                                       │
│ - Logo izquierda                                            │
│ - Search bar centro (width: 600px)                          │
│ - Icons derecha (spacing: 16px)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ WELCOME BANNER (height: 200px)                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Avatar + Welcome + Metrics + Illustration            │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ GRID DE MÉTRICAS (2 filas × 2 columnas, gap: 24px)        │
│ ┌──────────────┐ ┌──────────────┐                         │
│ │ Metric Card  │ │ Chart Card   │                         │
│ │ 160px height │ │ 300px height │                         │
│ └──────────────┘ └──────────────┘                         │
│ ┌──────────────┐ ┌──────────────┐                         │
│ │ Donut Chart  │ │ Metric Card  │                         │
│ │ 300px height │ │ 160px height │                         │
│ └──────────────┘ └──────────────┘                         │
│                                                             │
│ BOTTOM CARDS (height: auto)                                │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Line chart + metrics                                 │   │
│ └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Colores Exactos (extraídos de la imagen)

```python
COLORS_MAXTON = {
    # Fondos
    "bg_app": "#0f1320",           # Fondo principal
    "bg_sidebar": "#151825",       # Sidebar
    "bg_card": "#1a1d2e",          # Cards
    "bg_card_hover": "#1f2333",    # Card hover
    
    # Gradientes de las metric cards
    "gradient_cyan_start": "#00d4ff",
    "gradient_cyan_end": "#00a3cc",
    "gradient_green_start": "#00ff88",
    "gradient_green_end": "#00cc66",
    "gradient_pink_start": "#ff0080",
    "gradient_pink_end": "#cc0066",
    "gradient_purple_start": "#a855f7",
    "gradient_purple_end": "#7c3aed",
    
    # Gráficos
    "chart_cyan": "#00d4ff",
    "chart_green": "#00ff88",
    "chart_orange": "#ff8c00",
    "chart_pink": "#ff0080",
    "chart_purple": "#a855f7",
    
    # Texto
    "text_primary": "#ffffff",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    
    # Acentos
    "accent_blue": "#3b82f6",
    "success": "#00ff88",
    "warning": "#fbbf24",
    "danger": "#ff0080",
}
```

---

## 🎨 PASO 1: Actualizar design_tokens.py

**Archivo:** `tucajero/ui/design_tokens.py`

**INSTRUCCIÓN:** REEMPLAZA la clase Colors COMPLETA con esto:

```python
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
```

**VERIFICACIÓN:**
- [ ] Colores EXACTAMENTE como arriba
- [ ] NO cambiaste ningún valor
- [ ] Archivo guarda sin errores

---

## 🎨 PASO 2: Crear MetricCardMaxton

**Archivo:** `tucajero/ui/components_premium.py`

**INSTRUCCIÓN:** AGREGA esta clase COMPLETA al final del archivo:

```python
class MetricCardMaxton(QFrame):
    """
    Metric card estilo Maxton con gradiente y sombra glow
    
    USO EXACTO:
    card = MetricCardMaxton(
        value="$262,226",
        label="Ventas hoy",
        gradient_colors=("cyan", None)  # cyan, green, pink, purple, blue, orange
    )
    """
    
    def __init__(self, value, label, gradient_colors="cyan", icon=None, change=None, parent=None):
        super().__init__(parent)
        
        self.gradient_type = gradient_colors
        self.setMinimumHeight(140)
        self.setMinimumWidth(280)
        
        # Aplicar sombra glow según gradiente
        if gradient_colors == "cyan":
            shadow = Colors.SHADOW_GLOW_CYAN
        elif gradient_colors == "green":
            shadow = Colors.SHADOW_GLOW_GREEN
        elif gradient_colors == "pink":
            shadow = Colors.SHADOW_GLOW_PINK
        else:
            shadow = Colors.SHADOW_MD
        
        self.setStyleSheet(f"""
            QFrame {{
                border-radius: {BorderRadius.XL}px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)
        
        # Label (arriba, pequeño)
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            QLabel {{
                color: rgba(255, 255, 255, 0.7);
                font-size: {Typography.CAPTION}px;
                font-weight: {Typography.MEDIUM};
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        """)
        layout.addWidget(label_widget)
        
        # Valor (grande, bold)
        value_widget = QLabel(value)
        value_widget.setStyleSheet(f"""
            QLabel {{
                color: rgb(255, 255, 255);
                font-size: {Typography.H1}px;
                font-weight: {Typography.EXTRABOLD};
                background: transparent;
                letter-spacing: -1px;
            }}
        """)
        layout.addWidget(value_widget)
        
        # Cambio/indicador (si existe)
        if change:
            change_widget = QLabel(change)
            change_widget.setStyleSheet(f"""
                QLabel {{
                    color: rgba(255, 255, 255, 0.6);
                    font-size: {Typography.CAPTION}px;
                    background: transparent;
                }}
            """)
            layout.addWidget(change_widget)
        
        layout.addStretch()
    
    def paintEvent(self, event):
        """Dibuja gradiente de fondo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Crear gradiente según tipo
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        
        if self.gradient_type == "cyan":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_CYAN_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_CYAN_END))
        elif self.gradient_type == "green":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_GREEN_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_GREEN_END))
        elif self.gradient_type == "pink":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_PINK_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_PINK_END))
        elif self.gradient_type == "purple":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_PURPLE_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_PURPLE_END))
        elif self.gradient_type == "blue":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_BLUE_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_BLUE_END))
        elif self.gradient_type == "orange":
            gradient.setColorAt(0, QColor(Colors.GRADIENT_ORANGE_START))
            gradient.setColorAt(1, QColor(Colors.GRADIENT_ORANGE_END))
        else:
            # Gradiente por defecto
            gradient.setColorAt(0, QColor(Colors.PRIMARY))
            gradient.setColorAt(1, QColor("#1e40af"))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), BorderRadius.XL, BorderRadius.XL)
        
        super().paintEvent(event)
```

**VERIFICACIÓN:**
- [ ] Clase agregada al final de components_premium.py
- [ ] NO modificaste otras clases
- [ ] Imports están correctos

---

## 🎨 PASO 3: Crear ChartCardMaxton

**INSTRUCCIÓN:** AGREGA al final de `components_premium.py`:

```python
class ChartCardMaxton(QFrame):
    """
    Card con gráfico estilo Maxton
    
    USO:
    card = ChartCardMaxton(title="Ventas últimos 7 días")
    """
    
    def __init__(self, title, subtitle=None, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: {BorderRadius.XL}px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H4}px;
                font-weight: {Typography.SEMIBOLD};
            }}
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Botón options (3 puntos)
        btn_options = QPushButton("⋮")
        btn_options.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_TERTIARY};
                border: none;
                font-size: {Typography.H3}px;
                padding: 0;
                max-width: 24px;
            }}
            QPushButton:hover {{
                color: {Colors.TEXT_PRIMARY};
            }}
        """)
        header_layout.addWidget(btn_options)
        
        layout.addLayout(header_layout)
        
        # Subtitle (si existe)
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"""
                QLabel {{
                    color: {Colors.TEXT_TERTIARY};
                    font-size: {Typography.CAPTION}px;
                }}
            """)
            layout.addWidget(subtitle_label)
        
        # Espacio para contenido del gráfico
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
```

**VERIFICACIÓN:**
- [ ] Clase agregada
- [ ] Estilos correctos

---

## 🎨 PASO 4: Dashboard Layout EXACTO

**Archivo:** `tucajero/ui/dashboard_view.py`

**INSTRUCCIÓN:** REEMPLAZA el método `init_ui()` COMPLETO:

```python
def init_ui(self):
    """Layout principal del dashboard"""
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(32, 24, 32, 32)  # Márgenes exactos
    main_layout.setSpacing(24)  # Spacing exacto
    
    # HEADER (título + fecha + botón)
    header = self.create_header()
    main_layout.addWidget(header)
    
    # GRID PRINCIPAL (2x2)
    grid = QGridLayout()
    grid.setSpacing(24)  # Gap exacto de 24px
    
    # FILA 1
    # Card 1: Ventas hoy (arriba izquierda)
    self.card_ventas_hoy = MetricCardMaxton(
        value="$0",
        label="Ventas hoy",
        gradient_colors="green"
    )
    self.card_ventas_hoy.setMinimumHeight(160)
    grid.addWidget(self.card_ventas_hoy, 0, 0)
    
    # Card 2: Gráfico de barras (arriba derecha)
    self.card_chart_ventas = ChartCardMaxton(
        title="Ventas últimos 7 días",
        subtitle="Comparación diaria"
    )
    self.card_chart_ventas.setMinimumHeight(320)
    grid.addWidget(self.card_chart_ventas, 0, 1, 2, 1)  # Ocupa 2 filas
    
    # FILA 2
    # Card 3: Gráfico de dona (abajo izquierda)
    self.card_metodos_pago = ChartCardMaxton(
        title="Métodos de pago"
    )
    self.card_metodos_pago.setMinimumHeight(320)
    grid.addWidget(self.card_metodos_pago, 1, 0)
    
    main_layout.addLayout(grid)
    
    # FILA 3: Cards de métricas pequeñas (horizontal)
    metrics_row = QHBoxLayout()
    metrics_row.setSpacing(24)
    
    self.card_ventas_mes = MetricCardMaxton(
        value="$0",
        label="Ventas mes",
        gradient_colors="blue"
    )
    self.card_ventas_mes.setMinimumHeight(140)
    metrics_row.addWidget(self.card_ventas_mes)
    
    self.card_ticket = MetricCardMaxton(
        value="$0",
        label="Ticket promedio",
        gradient_colors="cyan"
    )
    self.card_ticket.setMinimumHeight(140)
    metrics_row.addWidget(self.card_ticket)
    
    self.card_num_ventas = MetricCardMaxton(
        value="0",
        label="Nº ventas",
        gradient_colors="purple"
    )
    self.card_num_ventas.setMinimumHeight(140)
    metrics_row.addWidget(self.card_num_ventas)
    
    main_layout.addLayout(metrics_row)
    
    # FILA 4: Tabla de ventas recientes
    table_card = ChartCardMaxton(title="Ventas recientes")
    table_card.setMinimumHeight(400)
    
    # Tabla dentro de la card
    self.tabla_ventas = QTableWidget()
    self.tabla_ventas.setColumnCount(5)
    self.tabla_ventas.setHorizontalHeaderLabels([
        "Fecha", "Cliente", "Total", "Método", "Productos"
    ])
    self.tabla_ventas.setStyleSheet(TABLE_STYLE_PREMIUM)
    self.tabla_ventas.setShowGrid(False)
    self.tabla_ventas.verticalHeader().setVisible(False)
    self.tabla_ventas.horizontalHeader().setStretchLastSection(True)
    
    table_card.content_layout.addWidget(self.tabla_ventas)
    
    main_layout.addWidget(table_card)
    
    main_layout.addStretch()
```

**VERIFICACIÓN:**
- [ ] Layout es EXACTAMENTE como se especificó
- [ ] Grid 2x2 con spacing de 24px
- [ ] Cards con alturas correctas
- [ ] NO cambiaste la estructura

---

## 🎨 PASO 5: Actualizar Header

**INSTRUCCIÓN:** REEMPLAZA el método `create_header()`:

```python
def create_header(self):
    """Header con título y controles"""
    header = QWidget()
    header.setStyleSheet("background: transparent;")
    header_layout = QHBoxLayout(header)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(16)
    
    # Título
    title = QLabel("Dashboard")
    title.setStyleSheet(f"""
        QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.H1}px;
            font-weight: {Typography.BOLD};
        }}
    """)
    header_layout.addWidget(title)
    
    # Fecha actual
    from datetime import datetime
    now = datetime.now()
    fecha = QLabel(now.strftime("%A, %d de %B %Y"))
    fecha.setStyleSheet(f"""
        QLabel {{
            color: {Colors.TEXT_TERTIARY};
            font-size: {Typography.BODY}px;
        }}
    """)
    header_layout.addWidget(fecha)
    
    header_layout.addStretch()
    
    # Botón settings (opcional)
    btn_settings = QPushButton("⚙")
    btn_settings.setStyleSheet(f"""
        QPushButton {{
            background: {Colors.BG_CARD};
            color: {Colors.TEXT_SECONDARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {BorderRadius.MD}px;
            padding: 10px;
            font-size: {Typography.H4}px;
            min-width: 40px;
            max-width: 40px;
            min-height: 40px;
            max-height: 40px;
        }}
        QPushButton:hover {{
            background: {Colors.BG_HOVER};
            color: {Colors.TEXT_PRIMARY};
        }}
    """)
    header_layout.addWidget(btn_settings)
    
    # Botón refresh
    btn_refresh = ButtonPremium("🔄", style="secondary")
    btn_refresh.clicked.connect(self.refresh_data)
    btn_refresh.setMinimumWidth(40)
    btn_refresh.setMaximumWidth(40)
    header_layout.addWidget(btn_refresh)
    
    return header
```

**VERIFICACIÓN:**
- [ ] Header tiene todos los elementos
- [ ] Estilos son exactos

---

## 🎨 PASO 6: Implementar gráfico de barras

**INSTRUCCIÓN:** AGREGA este método a dashboard_view.py:

```python
def crear_grafico_barras_ventas(self):
    """Crea gráfico de barras para ventas últimos 7 días"""
    from PySide6.QtWidgets import QWidget
    from PySide6.QtGui import QPainter, QColor, QPen
    from PySide6.QtCore import Qt
    from datetime import datetime, timedelta
    
    class GraficoBarras(QWidget):
        def __init__(self, datos, parent=None):
            super().__init__(parent)
            self.datos = datos  # Lista de tuplas (label, valor)
            self.setMinimumHeight(240)
        
        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Configuración
            width = self.width()
            height = self.height()
            margin = 40
            chart_width = width - 2 * margin
            chart_height = height - 2 * margin
            
            # Encontrar valor máximo
            max_val = max([v for _, v in self.datos]) if self.datos else 1
            
            # Dibujar barras
            bar_width = chart_width / len(self.datos) * 0.7
            spacing = chart_width / len(self.datos) * 0.3
            
            for i, (label, valor) in enumerate(self.datos):
                # Calcular altura de la barra
                bar_height = (valor / max_val) * chart_height if max_val > 0 else 0
                
                # Posición X
                x = margin + i * (bar_width + spacing)
                # Posición Y (desde abajo)
                y = height - margin - bar_height
                
                # Gradiente para la barra
                gradient = QLinearGradient(x, y, x, y + bar_height)
                gradient.setColorAt(0, QColor(Colors.GRADIENT_GREEN_START))
                gradient.setColorAt(1, QColor(Colors.GRADIENT_GREEN_END))
                
                painter.setBrush(gradient)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_height), 6, 6)
                
                # Dibujar label
                painter.setPen(QColor(Colors.TEXT_TERTIARY))
                painter.drawText(
                    int(x), 
                    height - margin + 20,
                    int(bar_width),
                    20,
                    Qt.AlignmentFlag.AlignCenter,
                    label
                )
                
                # Dibujar valor arriba de la barra
                painter.setPen(QColor(Colors.TEXT_PRIMARY))
                from utils.format import formato_moneda
                valor_text = formato_moneda(valor)
                painter.drawText(
                    int(x),
                    int(y - 10),
                    int(bar_width),
                    20,
                    Qt.AlignmentFlag.AlignCenter,
                    valor_text
                )
    
    # Obtener datos de ventas últimos 7 días
    hoy = datetime.now().date()
    datos = []
    
    for i in range(6, -1, -1):  # 7 días atrás hasta hoy
        fecha = hoy - timedelta(days=i)
        
        ventas_dia = self.session.query(Venta).filter(
            and_(
                func.date(Venta.fecha) == fecha,
                Venta.anulada == False
            )
        ).all()
        
        total = sum(v.total for v in ventas_dia)
        label = fecha.strftime("%d/%m")
        datos.append((label, total))
    
    # Crear widget de gráfico
    grafico = GraficoBarras(datos)
    
    # Agregar al content_layout de la card
    self.card_chart_ventas.content_layout.addWidget(grafico)
```

**LUEGO:** Llama este método al final de `init_ui()`:

```python
# Al final de init_ui(), ANTES de main_layout.addStretch()
self.crear_grafico_barras_ventas()
```

**VERIFICACIÓN:**
- [ ] Gráfico se dibuja correctamente
- [ ] Barras tienen gradiente verde
- [ ] Labels y valores se muestran

---

## 🎨 PASO 7: Actualizar valores de las métricas

**INSTRUCCIÓN:** REEMPLAZA el método `actualizar_metricas()`:

```python
def actualizar_metricas(self):
    """Actualiza valores de las metric cards"""
    from datetime import datetime
    from utils.format import formato_moneda
    
    hoy = datetime.now().date()
    inicio_mes = datetime.now().replace(day=1).date()
    
    # Ventas de hoy
    ventas_hoy = self.session.query(Venta).filter(
        and_(
            func.date(Venta.fecha) == hoy,
            Venta.anulada == False
        )
    ).all()
    
    total_hoy = sum(v.total for v in ventas_hoy)
    num_ventas_hoy = len(ventas_hoy)
    
    # Ventas del mes
    ventas_mes = self.session.query(Venta).filter(
        and_(
            func.date(Venta.fecha) >= inicio_mes,
            Venta.anulada == False
        )
    ).all()
    
    total_mes = sum(v.total for v in ventas_mes)
    
    # Ticket promedio
    ticket_prom = total_hoy / num_ventas_hoy if num_ventas_hoy > 0 else 0
    
    # Actualizar cards (buscar el QLabel dentro de cada card)
    # Card ventas hoy
    for child in self.card_ventas_hoy.children():
        if isinstance(child, QLabel) and "font-size: 36px" in child.styleSheet():
            child.setText(formato_moneda(total_hoy))
            break
    
    # Card ventas mes
    for child in self.card_ventas_mes.children():
        if isinstance(child, QLabel) and "font-size: 36px" in child.styleSheet():
            child.setText(formato_moneda(total_mes))
            break
    
    # Card ticket promedio
    for child in self.card_ticket.children():
        if isinstance(child, QLabel) and "font-size: 36px" in child.styleSheet():
            child.setText(formato_moneda(ticket_prom))
            break
    
    # Card número de ventas
    for child in self.card_num_ventas.children():
        if isinstance(child, QLabel) and "font-size: 36px" in child.styleSheet():
            child.setText(str(num_ventas_hoy))
            break
```

**VERIFICACIÓN:**
- [ ] Los valores se actualizan correctamente
- [ ] Formato de moneda es correcto

---

## 🎨 PASO 8: Fondo de la ventana principal

**Archivo:** `tucajero/ui/main_window.py`

**INSTRUCCIÓN:** Busca el método `__init__` y AGREGA al inicio:

```python
def __init__(self):
    super().__init__()
    
    # AGREGAR ESTAS LÍNEAS:
    from ui.design_tokens import Colors
    self.setStyleSheet(f"""
        QMainWindow {{
            background: {Colors.BG_APP};
        }}
        QWidget {{
            background: {Colors.BG_APP};
        }}
    """)
    
    # ... resto del código existente
```

**VERIFICACIÓN:**
- [ ] Fondo es #0f1320 (muy oscuro)
- [ ] No hay parches blancos

---

## 📋 CHECKLIST FINAL

### Archivos modificados
- [ ] `tucajero/ui/design_tokens.py` - Nuevos colores
- [ ] `tucajero/ui/components_premium.py` - MetricCardMaxton y ChartCardMaxton
- [ ] `tucajero/ui/dashboard_view.py` - Layout completo
- [ ] `tucajero/ui/main_window.py` - Fondo oscuro

### Verificación visual
- [ ] Fondo es ultra oscuro (#0f1320)
- [ ] Cards tienen gradientes vibrantes
- [ ] Espaciado es uniforme (24px entre cards)
- [ ] Gráfico de barras se dibuja correctamente
- [ ] Texto es legible (blanco sobre oscuro)
- [ ] No hay errores en consola
- [ ] Los valores se actualizan al hacer refresh

### Comparación con referencia
- [ ] Layout es similar a Maxton
- [ ] Gradientes son vibrantes como Maxton
- [ ] Tipografía es clara y grande
- [ ] Cards tienen bordes sutiles
- [ ] Espaciado se ve profesional

---

## 🚨 TROUBLESHOOTING

**Si los gradientes no se ven:**
```python
# Verifica que paintEvent se está ejecutando
def paintEvent(self, event):
    print("Dibujando gradiente...")  # Debug
    # ... resto del código
```

**Si los valores no se actualizan:**
```python
# Verifica que refresh_data se llama
def refresh_data(self):
    print("Actualizando datos...")  # Debug
    self.actualizar_metricas()
```

**Si el layout se ve mal:**
```python
# Verifica los margins y spacing
main_layout.setContentsMargins(32, 24, 32, 32)
main_layout.setSpacing(24)
grid.setSpacing(24)
```

---

## 🎯 RESULTADO ESPERADO

Después de aplicar TODOS estos pasos:

1. Dashboard con fondo ultra oscuro (#0f1320)
2. 4 metric cards con gradientes vibrantes
3. Gráfico de barras funcionando
4. Tabla de ventas recientes
5. Layout limpio y profesional
6. Espaciado uniforme (24px)
7. Tipografía clara y legible

**TIEMPO ESTIMADO:** 2-3 horas aplicando paso a paso

**NO SALTARSE NINGÚN PASO**
**NO IMPROVISAR**
**COPIAR EXACTAMENTE**
