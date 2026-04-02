# 🎨 PLAN COMPLETO UI PREMIUM - TODAS LAS VISTAS
## Instrucciones EXACTAS para Qwen - PARTE 2

**PREREQUISITO:** Completar PLAN_UI_PREMIUM_EXACTO.md primero

---

# VISTA: PUNTO DE VENTA (ventas_view.py)

## REEMPLAZAR COMPLETAMENTE el archivo

```python
"""Vista de ventas premium - NO MODIFICAR"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QFrame, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.design_tokens import Colors, Typography, Spacing, BorderRadius
from ui.components_premium import (
    CardPremium, ButtonPremium, InputPremium, TABLE_STYLE_PREMIUM
)
from models.producto import Producto
from utils.format import formato_moneda


class VentasView(QWidget):
    """Vista de punto de venta premium"""
    
    def __init__(self, session, cajero_activo=None):
        super().__init__()
        self.session = session
        self.cajero_activo = cajero_activo
        self.carrito = []
        
        self.setStyleSheet(f"background: {Colors.BG_APP};")
        self.init_ui()
    
    def init_ui(self):
        """Inicializa interfaz"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            Spacing.XXXL, Spacing.XXL, Spacing.XXXL, Spacing.XXL
        )
        layout.setSpacing(Spacing.XXL)
        
        # COLUMNA IZQUIERDA: Búsqueda y carrito (60%)
        left_col = self.create_left_column()
        layout.addWidget(left_col, 60)
        
        # COLUMNA DERECHA: Resumen y pago (40%)
        right_col = self.create_right_column()
        layout.addWidget(right_col, 40)
    
    def create_left_column(self):
        """Columna de búsqueda y carrito"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.XL)
        
        # HEADER: Nueva Venta
        header = QLabel("Nueva Venta")
        header.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H2}px;
                font-weight: {Typography.BOLD};
            }}
        """)
        layout.addWidget(header)
        
        # BÚSQUEDA
        search_card = CardPremium(padding=Spacing.LG)
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(Spacing.MD)
        
        # Input de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por código, nombre o escanear...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 2px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.LG}px;
                padding: {Spacing.LG}px {Spacing.XL}px;
                font-size: {Typography.H4}px;
                min-height: 30px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.PRIMARY};
                background: {Colors.BG_ELEVATED};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_MUTED};
            }}
        """)
        search_layout.addWidget(self.search_input, 1)
        
        # Botón buscar
        btn_buscar = ButtonPremium("Buscar", style="primary")
        btn_buscar.setMinimumWidth(120)
        search_layout.addWidget(btn_buscar)
        
        layout.addWidget(search_card)
        
        # CARRITO
        carrito_card = CardPremium(padding=Spacing.LG)
        carrito_layout = QVBoxLayout(carrito_card)
        carrito_layout.setContentsMargins(0, 0, 0, 0)
        carrito_layout.setSpacing(Spacing.MD)
        
        # Header del carrito
        carrito_header = QLabel("🛒 Carrito de Compra")
        carrito_header.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H4}px;
                font-weight: {Typography.SEMIBOLD};
            }}
        """)
        carrito_layout.addWidget(carrito_header)
        
        # Tabla del carrito
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(6)
        self.tabla_carrito.setHorizontalHeaderLabels([
            "PRODUCTO", "PRECIO", "CANT.", "-", "+", "SUBTOTAL"
        ])
        self.tabla_carrito.setStyleSheet(TABLE_STYLE_PREMIUM)
        self.tabla_carrito.horizontalHeader().setStretchLastSection(True)
        self.tabla_carrito.setMinimumHeight(400)
        self.tabla_carrito.setShowGrid(False)
        self.tabla_carrito.verticalHeader().setVisible(False)
        carrito_layout.addWidget(self.tabla_carrito)
        
        # Botones de acción del carrito
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.MD)
        
        btn_limpiar = ButtonPremium("🗑️ Limpiar", style="danger")
        btn_layout.addWidget(btn_limpiar)
        
        btn_descuento = ButtonPremium("% Descuento", style="secondary")
        btn_layout.addWidget(btn_descuento)
        
        btn_cliente = ButtonPremium("👤 Cliente", style="secondary")
        btn_layout.addWidget(btn_cliente)
        
        carrito_layout.addLayout(btn_layout)
        
        layout.addWidget(carrito_card)
        
        return container
    
    def create_right_column(self):
        """Columna de resumen y pago"""
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Spacing.XL)
        
        # RESUMEN
        resumen_card = CardPremium(padding=Spacing.XXL)
        resumen_layout = QVBoxLayout(resumen_card)
        resumen_layout.setContentsMargins(0, 0, 0, 0)
        resumen_layout.setSpacing(Spacing.LG)
        
        # Título
        resumen_title = QLabel("Resumen de Compra")
        resumen_title.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H3}px;
                font-weight: {Typography.BOLD};
            }}
        """)
        resumen_layout.addWidget(resumen_title)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet(f"background: {Colors.BORDER_DEFAULT};")
        separador.setFixedHeight(1)
        resumen_layout.addWidget(separador)
        
        # Subtotal
        subtotal_layout = QHBoxLayout()
        subtotal_label = QLabel("Subtotal:")
        subtotal_label.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.BODY}px;
        """)
        self.subtotal_value = QLabel("$0.00")
        self.subtotal_value.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.BODY}px;
            font-weight: {Typography.MEDIUM};
        """)
        subtotal_layout.addWidget(subtotal_label)
        subtotal_layout.addStretch()
        subtotal_layout.addWidget(self.subtotal_value)
        resumen_layout.addLayout(subtotal_layout)
        
        # IVA
        iva_layout = QHBoxLayout()
        iva_label = QLabel("IVA (19%):")
        iva_label.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.BODY}px;
        """)
        self.iva_value = QLabel("$0.00")
        self.iva_value.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.BODY}px;
            font-weight: {Typography.MEDIUM};
        """)
        iva_layout.addWidget(iva_label)
        iva_layout.addStretch()
        iva_layout.addWidget(self.iva_value)
        resumen_layout.addLayout(iva_layout)
        
        # Descuento
        desc_layout = QHBoxLayout()
        desc_label = QLabel("Descuento:")
        desc_label.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.BODY}px;
        """)
        self.desc_value = QLabel("$0.00")
        self.desc_value.setStyleSheet(f"""
            color: {Colors.SUCCESS};
            font-size: {Typography.BODY}px;
            font-weight: {Typography.MEDIUM};
        """)
        desc_layout.addWidget(desc_label)
        desc_layout.addStretch()
        desc_layout.addWidget(self.desc_value)
        resumen_layout.addLayout(desc_layout)
        
        # Separador grueso
        separador2 = QFrame()
        separador2.setFrameShape(QFrame.Shape.HLine)
        separador2.setStyleSheet(f"background: {Colors.BORDER_STRONG};")
        separador2.setFixedHeight(2)
        resumen_layout.addWidget(separador2)
        
        # TOTAL (destacado)
        total_layout = QHBoxLayout()
        total_label = QLabel("TOTAL A PAGAR:")
        total_label.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.H4}px;
            font-weight: {Typography.BOLD};
        """)
        self.total_value = QLabel("$0.00")
        self.total_value.setStyleSheet(f"""
            color: {Colors.PRIMARY_LIGHT};
            font-size: {Typography.H2}px;
            font-weight: {Typography.EXTRABOLD};
        """)
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_value)
        resumen_layout.addLayout(total_layout)
        
        layout.addWidget(resumen_card)
        
        # MÉTODOS DE PAGO
        pago_card = CardPremium(padding=Spacing.XL)
        pago_layout = QVBoxLayout(pago_card)
        pago_layout.setContentsMargins(0, 0, 0, 0)
        pago_layout.setSpacing(Spacing.LG)
        
        # Título
        pago_title = QLabel("Método de Pago")
        pago_title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.H4}px;
            font-weight: {Typography.SEMIBOLD};
        """)
        pago_layout.addWidget(pago_title)
        
        # Grid de botones de pago
        metodos_grid = QGridLayout()
        metodos_grid.setSpacing(Spacing.MD)
        
        metodos = [
            ("💵 Efectivo", 0, 0),
            ("💳 Tarjeta", 0, 1),
            ("📱 Nequi", 1, 0),
            ("💸 Daviplata", 1, 1),
            ("🏦 Transferencia", 2, 0),
            ("🔄 Mixto", 2, 1),
        ]
        
        for texto, row, col in metodos:
            btn = ButtonPremium(texto, style="secondary")
            btn.setMinimumHeight(50)
            metodos_grid.addWidget(btn, row, col)
        
        pago_layout.addLayout(metodos_grid)
        
        layout.addWidget(pago_card)
        
        # BOTÓN CONFIRMAR (grande y verde)
        btn_confirmar = ButtonPremium("✓ CONFIRMAR VENTA", style="success")
        btn_confirmar.setMinimumHeight(70)
        btn_confirmar.setStyleSheet(f"""
            QPushButton {{
                background: {Colors.SUCCESS};
                color: white;
                border: none;
                border-radius: {BorderRadius.XL}px;
                padding: {Spacing.XL}px;
                font-size: {Typography.H3}px;
                font-weight: {Typography.BOLD};
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: {Colors.SUCCESS_DARK};
            }}
            QPushButton:pressed {{
                background: {Colors.SUCCESS_LIGHT};
            }}
        """)
        layout.addWidget(btn_confirmar)
        
        layout.addStretch()
        
        return container
```

**VERIFICACIÓN:**
- ✅ ventas_view.py COMPLETAMENTE reemplazado
- ✅ Layout 60/40 (carrito/resumen)
- ✅ Búsqueda grande y prominente
- ✅ Tabla de carrito premium
- ✅ Resumen con tipografía clara
- ✅ Botones de método de pago en grid
- ✅ Botón confirmar GIGANTE y verde

---

# VISTA: PRODUCTOS (productos_view.py)

## INSTRUCCIÓN: Reemplazar layout y estilos

**Header:**
```python
# Al inicio del init_ui()
header_layout = QHBoxLayout()
header_layout.setSpacing(Spacing.LG)

title = QLabel("📦 Gestión de Productos")
title.setStyleSheet(f"""
    color: {Colors.TEXT_PRIMARY};
    font-size: {Typography.H2}px;
    font-weight: {Typography.BOLD};
""")
header_layout.addWidget(title)
header_layout.addStretch()

btn_agregar = ButtonPremium("+ Nuevo Producto", style="primary")
header_layout.addWidget(btn_agregar)

btn_importar = ButtonPremium("📥 Importar", style="secondary")
header_layout.addWidget(btn_importar)
```

**Tabla de productos:**
```python
self.tabla_productos.setStyleSheet(TABLE_STYLE_PREMIUM)
self.tabla_productos.setMinimumHeight(500)
```

**Botones de acción:**
```python
# En vez de botones simples, usar ButtonPremium:
btn_entrada = ButtonPremium("📥 Entrada", style="success")
btn_salida = ButtonPremium("📤 Salida", style="danger")
btn_editar = ButtonPremium("✏️ Editar", style="secondary")
```

---

# VISTA: CLIENTES (clientes_view.py)

## INSTRUCCIÓN: Actualizar a diseño premium

```python
# Header
header = QLabel("👥 Gestión de Clientes")
header.setStyleSheet(f"""
    color: {Colors.TEXT_PRIMARY};
    font-size: {Typography.H2}px;
    font-weight: {Typography.BOLD};
""")

# Búsqueda con input premium
search_input = QLineEdit()
search_input.setPlaceholderText("🔍 Buscar cliente por nombre, teléfono o NIT...")
search_input.setStyleSheet(f"""
    QLineEdit {{
        background: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 2px solid {Colors.BORDER_DEFAULT};
        border-radius: {BorderRadius.MD}px;
        padding: {Spacing.MD}px {Spacing.LG}px;
        font-size: {Typography.BODY}px;
        min-height: 25px;
    }}
    QLineEdit:focus {{
        border-color: {Colors.PRIMARY};
    }}
""")

# Tabla
self.tabla_clientes.setStyleSheet(TABLE_STYLE_PREMIUM)

# Botones
btn_nuevo = ButtonPremium("+ Nuevo Cliente", style="primary")
btn_editar = ButtonPremium("✏️ Editar", style="secondary")
btn_historial = ButtonPremium("📊 Historial", style="secondary")
```

---

# VISTA: CORTE DE CAJA (corte_view.py)

## Card de estado de caja

```python
# Si caja abierta:
estado_card = MetricCardPremium(
    title="Estado de Caja",
    value="ABIERTA",
    gradient_type="green",
    icon="🔓"
)

# Si caja cerrada:
estado_card = MetricCardPremium(
    title="Estado de Caja",
    value="CERRADA",
    gradient_type="danger",
    icon="🔒"
)
```

## Grid de métricas de corte

```python
grid = QGridLayout()
grid.setSpacing(Spacing.XL)

# Card efectivo inicial
card_inicial = MetricCardPremium(
    title="Efectivo Inicial",
    value=formato_moneda(efectivo_inicial),
    gradient_type="blue"
)
grid.addWidget(card_inicial, 0, 0)

# Card ventas del día
card_ventas = MetricCardPremium(
    title="Total Ventas",
    value=formato_moneda(total_ventas),
    change=f"+{num_ventas} ventas",
    gradient_type="green"
)
grid.addWidget(card_ventas, 0, 1)

# Card efectivo esperado
card_esperado = MetricCardPremium(
    title="Efectivo Esperado",
    value=formato_moneda(efectivo_esperado),
    gradient_type="cyan"
)
grid.addWidget(card_esperado, 1, 0)

# Card diferencia
diferencia_positiva = diferencia >= 0
card_diferencia = MetricCardPremium(
    title="Diferencia",
    value=formato_moneda(abs(diferencia)),
    gradient_type="green" if diferencia_positiva else "orange"
)
grid.addWidget(card_diferencia, 1, 1)
```

---

# VISTA: HISTORIAL (historial_view.py)

## Filtros en cards

```python
filtros_card = CardPremium(padding=Spacing.XL)
filtros_layout = QHBoxLayout(filtros_card)

# Label
label = QLabel("Filtrar por fecha:")
label.setStyleSheet(f"""
    color: {Colors.TEXT_SECONDARY};
    font-size: {Typography.BODY}px;
    font-weight: {Typography.MEDIUM};
""")
filtros_layout.addWidget(label)

# Date desde
desde_input = QDateEdit()
desde_input.setCalendarPopup(True)
desde_input.setStyleSheet(f"""
    QDateEdit {{
        background: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_DEFAULT};
        border-radius: {BorderRadius.MD}px;
        padding: {Spacing.SM}px {Spacing.MD}px;
    }}
    QDateEdit:focus {{
        border-color: {Colors.PRIMARY};
    }}
""")
filtros_layout.addWidget(desde_input)

# Date hasta
hasta_input = QDateEdit()
# ... mismo estilo
filtros_layout.addWidget(hasta_input)

# Botón filtrar
btn_filtrar = ButtonPremium("🔍 Filtrar", style="primary")
filtros_layout.addWidget(btn_filtrar)
```

## Tabla de historial

```python
self.tabla_historial.setStyleSheet(TABLE_STYLE_PREMIUM)
self.tabla_historial.setAlternatingRowColors(False)
self.tabla_historial.setMinimumHeight(600)
```

---

# SIDEBAR (main_window.py)

## Actualizar estilos del sidebar

```python
# En main_window.py, método create_sidebar():

sidebar.setStyleSheet(f"""
    QWidget {{
        background: {Colors.BG_PANEL};
        border-right: 1px solid {Colors.BORDER_SUBTLE};
    }}
""")

# Logo
logo_label = QLabel("🏪 TuCajero")
logo_label.setStyleSheet(f"""
    QLabel {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Typography.H3}px;
        font-weight: {Typography.BOLD};
        padding: {Spacing.XXL}px {Spacing.XL}px;
        background: transparent;
    }}
""")

# Botones del menú
for nombre, icono in menu_items:
    btn = QPushButton(f"{icono} {nombre}")
    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            color: {Colors.TEXT_SECONDARY};
            border: none;
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.LG}px {Spacing.XL}px;
            text-align: left;
            font-size: {Typography.BODY}px;
            font-weight: {Typography.MEDIUM};
        }}
        QPushButton:hover {{
            background: {Colors.BG_HOVER};
            color: {Colors.TEXT_PRIMARY};
        }}
        QPushButton:checked {{
            background: {Colors.PRIMARY};
            color: white;
            font-weight: {Typography.SEMIBOLD};
        }}
    """)
    btn.setCheckable(True)
    btn.setMinimumHeight(48)
```

## Info de usuario (footer del sidebar)

```python
user_info = QWidget()
user_info.setStyleSheet(f"""
    QWidget {{
        background: {Colors.BG_ELEVATED};
        border-top: 1px solid {Colors.BORDER_SUBTLE};
        padding: {Spacing.LG}px;
    }}
""")

user_layout = QHBoxLayout(user_info)

# Avatar
avatar = QLabel("👤")
avatar.setStyleSheet(f"""
    QLabel {{
        font-size: {IconSize.XL}px;
        background: {Colors.BG_INPUT};
        border-radius: {BorderRadius.FULL}px;
        padding: {Spacing.SM}px;
    }}
""")
user_layout.addWidget(avatar)

# Nombre
nombre_label = QLabel(cajero.nombre)
nombre_label.setStyleSheet(f"""
    QLabel {{
        color: {Colors.TEXT_PRIMARY};
        font-size: {Typography.BODY_SM}px;
        font-weight: {Typography.SEMIBOLD};
    }}
""")

# Rol
rol_label = QLabel("Administrador" if cajero.es_admin else "Cajero")
rol_label.setStyleSheet(f"""
    QLabel {{
        color: {Colors.TEXT_TERTIARY};
        font-size: {Typography.CAPTION}px;
    }}
""")

user_text_layout = QVBoxLayout()
user_text_layout.addWidget(nombre_label)
user_text_layout.addWidget(rol_label)
user_layout.addLayout(user_text_layout)
```

---

# DIÁLOGOS

## Modal genérico premium

```python
class DialogPremium(QDialog):
    """Diálogo base premium"""
    
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: {BorderRadius.XL}px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL
        )
        layout.setSpacing(Spacing.XL)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Colors.TEXT_PRIMARY};
                font-size: {Typography.H3}px;
                font-weight: {Typography.BOLD};
            }}
        """)
        layout.addWidget(title_label)
        
        # Contenido (override en subclases)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(Spacing.MD)
        
        btn_cancelar = ButtonPremium("Cancelar", style="secondary")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        btn_aceptar = ButtonPremium("Aceptar", style="primary")
        btn_aceptar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_aceptar)
        
        layout.addLayout(btn_layout)
```

---

# MENSAJES DE ALERTA

## QMessageBox premium

```python
def mostrar_alerta_premium(parent, tipo, titulo, mensaje):
    """
    Muestra alerta con diseño premium
    tipo: 'success', 'warning', 'error', 'info'
    """
    msg = QMessageBox(parent)
    msg.setWindowTitle(titulo)
    msg.setText(mensaje)
    
    # Iconos según tipo
    iconos = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️'
    }
    
    colores = {
        'success': Colors.SUCCESS,
        'warning': Colors.WARNING,
        'error': Colors.DANGER,
        'info': Colors.INFO
    }
    
    msg.setStyleSheet(f"""
        QMessageBox {{
            background: {Colors.BG_CARD};
        }}
        QMessageBox QLabel {{
            color: {Colors.TEXT_PRIMARY};
            font-size: {Typography.BODY}px;
            padding: {Spacing.LG}px;
        }}
        QPushButton {{
            background: {colores[tipo]};
            color: white;
            border: none;
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MD}px {Spacing.XXL}px;
            font-weight: {Typography.SEMIBOLD};
            min-width: 100px;
        }}
        QPushButton:hover {{
            background: {Colors.PRIMARY_DARK if tipo == 'info' else colores[tipo]};
            opacity: 0.9;
        }}
    """)
    
    return msg.exec()
```

---

# INPUTS Y FORMULARIOS

## ComboBox premium

```python
def estilo_combobox_premium():
    return f"""
        QComboBox {{
            background: {Colors.BG_INPUT};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MD}px {Spacing.LG}px;
            font-size: {Typography.BODY}px;
            min-height: 25px;
        }}
        QComboBox:hover {{
            border-color: {Colors.BORDER_STRONG};
        }}
        QComboBox:focus {{
            border-color: {Colors.PRIMARY};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {Colors.TEXT_SECONDARY};
        }}
        QComboBox QAbstractItemView {{
            background: {Colors.BG_CARD};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {BorderRadius.MD}px;
            selection-background-color: {Colors.PRIMARY};
            selection-color: white;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: {Spacing.MD}px;
            border: none;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background: {Colors.BG_HOVER};
        }}
    """
```

## SpinBox / DoubleSpinBox premium

```python
def estilo_spinbox_premium():
    return f"""
        QSpinBox, QDoubleSpinBox {{
            background: {Colors.BG_INPUT};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MD}px {Spacing.LG}px;
            font-size: {Typography.BODY}px;
            min-height: 25px;
        }}
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {Colors.BORDER_STRONG};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {Colors.PRIMARY};
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            background: {Colors.BG_ELEVATED};
            border-left: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: 0 {BorderRadius.MD}px 0 0;
        }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
            background: {Colors.BG_HOVER};
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background: {Colors.BG_ELEVATED};
            border-left: 1px solid {Colors.BORDER_DEFAULT};
            border-radius: 0 0 {BorderRadius.MD}px 0;
        }}
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background: {Colors.BG_HOVER};
        }}
    """
```

---

# CHECKLIST COMPLETO

## Archivos principales
- [ ] design_tokens.py creado
- [ ] components_premium.py creado
- [ ] dashboard_view.py rediseñado
- [ ] ventas_view.py rediseñado
- [ ] productos_view.py actualizado
- [ ] clientes_view.py actualizado
- [ ] corte_view.py actualizado
- [ ] historial_view.py actualizado
- [ ] main_window.py con sidebar premium

## Componentes
- [ ] MetricCardPremium funciona
- [ ] CardPremium funciona
- [ ] ButtonPremium con 4 estilos
- [ ] SectionHeaderPremium funciona
- [ ] TABLE_STYLE_PREMIUM aplicado en todas las tablas

## Diálogos y mensajes
- [ ] DialogPremium base creado
- [ ] QMessageBox con estilo premium
- [ ] Todos los inputs tienen estilo consistente

## Colores y espaciado
- [ ] Fondo ultra oscuro (#0a0e1a)
- [ ] Jerarquía de texto clara (4 niveles)
- [ ] Espaciado uniforme (sistema de 8px)
- [ ] Bordes sutiles pero visibles

## Tipografía
- [ ] Tamaños consistentes (12-36px)
- [ ] Pesos correctos (400, 500, 600, 700)
- [ ] Altura de línea adecuada

## UX
- [ ] Focus states visibles (borde azul)
- [ ] Hover states suaves
- [ ] Botones con cursor pointer
- [ ] Transiciones suaves
- [ ] Sin texto cortado
- [ ] Sin elementos superpuestos

---

**FIN PLAN COMPLETO - APLICAR EN ORDEN**
