# 🎯 GUÍA MAESTRA: Transformación UI Premium con Qwen/Antigravity
## Instrucciones paso a paso SIN MARGEN DE ERROR

---

## 📂 ARCHIVOS QUE TIENES

1. **PLAN_UI_PREMIUM_EXACTO.md** - Sistema de diseño base (HACER PRIMERO)
2. **PLAN_DASHBOARD_MAXTON_EXACTO.md** - Dashboard estilo Maxton (HACER SEGUNDO)
3. **PLAN_UI_PREMIUM_COMPLETO_PARTE2.md** - Todas las demás vistas (HACER AL FINAL)

---

## 🚀 FASE 1: Sistema de Diseño Base (CRÍTICO - HACER PRIMERO)

### Agente 1: "Sistema de Diseño"

**Prompt para Qwen:**

```
TAREA: Implementar sistema de diseño premium

ARCHIVOS A CREAR (en este orden exacto):

1. tucajero/ui/design_tokens.py
   - Copia EXACTAMENTE el código del PASO 1 de PLAN_UI_PREMIUM_EXACTO.md
   - NO cambies NINGÚN valor
   - NO agregues comentarios adicionales
   - Verifica que todos los colores están EXACTAMENTE como se especifica

2. tucajero/ui/components_premium.py
   - Copia EXACTAMENTE el código del PASO 2 de PLAN_UI_PREMIUM_EXACTO.md
   - Incluye TODAS las clases: MetricCardPremium, CardPremium, ButtonPremium, SectionHeaderPremium, InputPremium, TABLE_STYLE_PREMIUM
   - NO modifiques la lógica de paintEvent
   - NO cambies los valores de spacing o colores

VERIFICACIÓN:
- Ambos archivos se crean sin errores
- No hay warnings de imports
- La app NO debe crashear al importar estos módulos

IMPORTANTE: NO continúes con otros pasos hasta que estos 2 archivos estén creados y funcionando.
```

**Duración estimada:** 30 minutos

**Verificar antes de continuar:**
- [ ] `/tucajero/ui/design_tokens.py` existe y tiene la clase Colors completa
- [ ] `/tucajero/ui/components_premium.py` existe con todas las clases
- [ ] No hay errores de sintaxis
- [ ] App arranca sin errores

---

## 🚀 FASE 2: Dashboard Estilo Maxton (HACER DESPUÉS DE FASE 1)

### Agente 2: "Dashboard Premium"

**Prompt para Qwen:**

```
PREREQUISITO: Fase 1 debe estar completada (design_tokens.py y components_premium.py existen)

TAREA: Rediseñar dashboard_view.py estilo Maxton

ARCHIVO A MODIFICAR: tucajero/ui/dashboard_view.py

PASO 1: Agregar MetricCardMaxton a components_premium.py
- Abre: tucajero/ui/components_premium.py
- Ve al FINAL del archivo
- Copia EXACTAMENTE el código de MetricCardMaxton del PASO 2 de PLAN_DASHBOARD_MAXTON_EXACTO.md
- Guarda el archivo

PASO 2: Agregar ChartCardMaxton a components_premium.py
- En el MISMO archivo (components_premium.py)
- Ve al FINAL (después de MetricCardMaxton)
- Copia EXACTAMENTE el código de ChartCardMaxton del PASO 3 de PLAN_DASHBOARD_MAXTON_EXACTO.md
- Guarda el archivo

PASO 3: Actualizar colores en design_tokens.py
- Abre: tucajero/ui/design_tokens.py
- REEMPLAZA la clase Colors COMPLETA con el código del PASO 1 de PLAN_DASHBOARD_MAXTON_EXACTO.md
- NO toques las otras clases (Typography, Spacing, etc.)
- Guarda el archivo

PASO 4: Rediseñar dashboard_view.py
- Abre: tucajero/ui/dashboard_view.py
- REEMPLAZA el método init_ui() COMPLETO con el código del PASO 4 de PLAN_DASHBOARD_MAXTON_EXACTO.md
- REEMPLAZA el método create_header() con el código del PASO 5
- AGREGA el método crear_grafico_barras_ventas() del PASO 6 al FINAL de la clase
- REEMPLAZA el método actualizar_metricas() con el código del PASO 7
- Guarda el archivo

PASO 5: Actualizar main_window.py
- Abre: tucajero/ui/main_window.py
- Busca el método __init__
- AGREGA al INICIO (después de super().__init__()) el código del PASO 8 de PLAN_DASHBOARD_MAXTON_EXACTO.md
- Guarda el archivo

VERIFICACIÓN:
- Dashboard se ve con fondo ultra oscuro (#0f1320)
- Aparecen 4 metric cards con gradientes
- Las cards están en un grid 2x2
- Hay un gráfico de barras (puede estar vacío si no hay datos)
- NO hay errores en consola

IMPORTANTE: Si hay algún error, NO intentes arreglarlo tú. Reporta el error exacto.
```

**Duración estimada:** 1-2 horas

**Verificar antes de continuar:**
- [ ] Dashboard tiene fondo ultra oscuro
- [ ] Se ven 4 metric cards con colores vibrantes
- [ ] Layout es limpio (grid 2x2 + fila de 3 cards)
- [ ] No hay errores de imports
- [ ] Los valores se actualizan (aunque sean $0)

---

## 🚀 FASE 3: Vista de Ventas (POS)

### Agente 3: "Vista de Ventas Premium"

**Prompt para Qwen:**

```
PREREQUISITO: Fases 1 y 2 completadas

TAREA: Rediseñar vista de ventas (POS)

ARCHIVO A MODIFICAR: tucajero/ui/ventas_view.py

INSTRUCCIONES:
1. Abre el archivo ventas_view.py
2. En el método __init__, AGREGA esta línea después de super().__init__():
   self.setStyleSheet(f"background: {Colors.BG_APP};")
3. Importa los componentes premium al inicio del archivo:
   from ui.design_tokens import Colors, Typography, Spacing, BorderRadius
   from ui.components_premium import CardPremium, ButtonPremium, TABLE_STYLE_PREMIUM

4. ENCUENTRA el input de búsqueda (QLineEdit) y REEMPLAZA su styleSheet con:
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

5. ENCUENTRA la tabla del carrito (self.tabla_carrito) y REEMPLAZA su styleSheet con:
   self.tabla_carrito.setStyleSheet(TABLE_STYLE_PREMIUM)

6. ENCUENTRA TODOS los botones que usan btn_primary(), btn_success(), btn_danger(), btn_secondary()
   Y REEMPLÁZALOS por ButtonPremium:
   - btn_primary() → ButtonPremium("Texto", style="primary")
   - btn_success() → ButtonPremium("Texto", style="success")
   - btn_danger() → ButtonPremium("Texto", style="danger")
   - btn_secondary() → ButtonPremium("Texto", style="secondary")

7. El botón CONFIRMAR VENTA debe ser GRANDE:
   btn_confirmar = ButtonPremium("✓ CONFIRMAR VENTA", style="success")
   btn_confirmar.setMinimumHeight(70)

VERIFICACIÓN:
- Fondo oscuro
- Input de búsqueda grande con borde azul al hacer focus
- Tabla del carrito con estilo premium
- Botones con colores correctos
- Botón confirmar es GRANDE y verde

NO modifiques la lógica de ventas, SOLO los estilos visuales.
```

**Duración estimada:** 1 hora

---

## 🚀 FASE 4: Vista de Productos

### Agente 4: "Vista de Productos Premium"

**Prompt para Qwen:**

```
PREREQUISITO: Fases 1, 2 y 3 completadas

TAREA: Actualizar vista de productos

ARCHIVO: tucajero/ui/productos_view.py

INSTRUCCIONES:
1. Importa componentes premium:
   from ui.design_tokens import Colors, Typography, Spacing
   from ui.components_premium import ButtonPremium, TABLE_STYLE_PREMIUM

2. En __init__, agrega fondo oscuro:
   self.setStyleSheet(f"background: {Colors.BG_APP};")

3. ENCUENTRA el título "Gestión de Productos" y cambia su estilo:
   title.setStyleSheet(f"""
       color: {Colors.TEXT_PRIMARY};
       font-size: {Typography.H2}px;
       font-weight: {Typography.BOLD};
   """)

4. ENCUENTRA la tabla de productos y cambia:
   self.tabla_productos.setStyleSheet(TABLE_STYLE_PREMIUM)

5. REEMPLAZA TODOS los botones por ButtonPremium (igual que en ventas)

VERIFICACIÓN:
- Fondo oscuro
- Título grande y claro
- Tabla con nuevo estilo
- Botones con colores correctos
```

**Duración estimada:** 30-45 minutos

---

## 🚀 FASE 5: Sidebar Premium

### Agente 5: "Sidebar Premium"

**Prompt para Qwen:**

```
PREREQUISITO: Todas las fases anteriores completadas

TAREA: Actualizar sidebar de main_window.py

ARCHIVO: tucajero/ui/main_window.py

INSTRUCCIONES:
1. Busca el método create_sidebar() o donde se crea el sidebar
2. El sidebar debe tener este estilo:
   sidebar.setStyleSheet(f"""
       QWidget {{
           background: {Colors.BG_PANEL};
           border-right: 1px solid {Colors.BORDER_SUBTLE};
       }}
   """)

3. CADA botón del menú debe tener este estilo:
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

4. El logo debe tener este estilo:
   logo_label.setStyleSheet(f"""
       color: {Colors.TEXT_PRIMARY};
       font-size: {Typography.H3}px;
       font-weight: {Typography.BOLD};
       padding: {Spacing.XXL}px;
   """)

VERIFICACIÓN:
- Sidebar oscuro (#151825)
- Botones cambian de color al hover
- Botón activo es azul
- Borde derecho sutil
```

**Duración estimada:** 30 minutos

---

## 📋 CHECKLIST COMPLETO

### Sistema base
- [ ] design_tokens.py creado
- [ ] components_premium.py creado
- [ ] App arranca sin errores

### Dashboard
- [ ] MetricCardMaxton funciona
- [ ] ChartCardMaxton funciona
- [ ] Dashboard tiene layout 2x2
- [ ] Gradientes se ven vibrantes
- [ ] Gráfico de barras funciona
- [ ] Valores se actualizan

### Ventas
- [ ] Fondo oscuro
- [ ] Input de búsqueda grande
- [ ] Tabla premium
- [ ] Botón confirmar GRANDE
- [ ] Lógica de ventas NO se rompió

### Productos
- [ ] Fondo oscuro
- [ ] Tabla premium
- [ ] Botones correctos

### Sidebar
- [ ] Fondo oscuro
- [ ] Hover states funcionan
- [ ] Active state es azul

### General
- [ ] NO hay errores en consola
- [ ] NO hay warnings de imports
- [ ] La app NO crashea
- [ ] TODOS los textos son legibles
- [ ] Espaciado es uniforme

---

## ⚠️ REGLAS CRÍTICAS PARA QWEN

1. **NUNCA** modifiques valores numéricos (colores, tamaños, spacing)
2. **NUNCA** agregues features no solicitadas
3. **NUNCA** cambies la lógica de negocio
4. **SOLO** modifica estilos visuales (colores, tamaños, fonts)
5. **SI HAY ERROR:** Reporta el error EXACTO, NO intentes arreglarlo
6. **COPIA EXACTAMENTE** el código de los planes
7. **NO IMPROVISES** nombres de variables o estructuras

---

## 🚨 SI ALGO SALE MAL

### Error: ModuleNotFoundError
```
SOLUCIÓN: Verifica que los archivos están en las rutas correctas
- tucajero/ui/design_tokens.py
- tucajero/ui/components_premium.py
```

### Error: paintEvent no dibuja gradientes
```
SOLUCIÓN: Verifica que super().paintEvent(event) está al FINAL del método
```

### Error: Cards no se ven
```
SOLUCIÓN: Verifica que agregaste las cards al layout con addWidget()
```

### La app crashea al iniciar
```
SOLUCIÓN: Revierte los cambios y aplica paso a paso
```

---

## 📊 ORDEN DE EJECUCIÓN RECOMENDADO

```
DÍA 1 (2-3 horas):
├─ Fase 1: Sistema de diseño (30 min)
├─ Fase 2: Dashboard (1-2 horas)
└─ Verificar y testear

DÍA 2 (2-3 horas):
├─ Fase 3: Vista de Ventas (1 hora)
├─ Fase 4: Vista de Productos (45 min)
├─ Fase 5: Sidebar (30 min)
└─ Testing completo

DÍA 3 (opcional):
└─ Aplicar a vistas restantes usando PLAN_UI_PREMIUM_COMPLETO_PARTE2.md
```

---

## ✅ RESULTADO FINAL ESPERADO

Al completar TODAS las fases:

1. **Dashboard** con gradientes vibrantes estilo Maxton
2. **Vista de Ventas** con diseño premium y botones grandes
3. **Vista de Productos** limpia y profesional
4. **Sidebar** oscuro con estados hover/active
5. **Colores consistentes** en toda la app
6. **Tipografía clara** y legible
7. **Espaciado uniforme** (sistema de 8px)
8. **Sin errores** en consola
9. **Funcionalidad intacta** (no se rompió nada)

---

**IMPORTANTE:** Ejecuta fase por fase, verificando cada una antes de continuar.

**NO** intentes hacer todo de una vez.

**SÍ** haz commits de git después de cada fase exitosa.
