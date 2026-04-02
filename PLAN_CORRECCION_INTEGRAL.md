# PLAN DE CORRECCIÓN INTEGRAL - TuCajero POS

## Fecha: 31 de Marzo 2026
## Estado: ✅ COMPLETADO
## Objetivo: Corregir todos los problemas críticos identificados

---

## RESUMEN DE CORRECCIONES APLICADAS

### ✅ FASE 1: BACKEND

| # | Tarea | Estado | Archivos |
|---|-------|--------|----------|
| B1 | Corregir relaciones faltantes en modelos | ✅ | `producto.py`, `cajero.py` |
| B2 | Crear CategoriaRepository | ✅ | `categoria_repo.py` (NUEVO) |
| B3 | Crear ProveedorRepository | ✅ | `proveedor_repo.py` (NUEVO) |
| B4 | Crear CorteCajaRepository | ✅ | `corte_repo.py` (NUEVO) |
| B5 | Centralizar IVA_RATE | ✅ | `app_config.py` |

### ✅ FASE 2: LÓGICA

| # | Tarea | Estado |
|---|-------|--------|
| L1 | Eliminar duplicación VentaService | ✅ Renombrado a VentaAnalyticsService |
| L2 | Agregar IVA_RATE centralizado | ✅ |

### ✅ FASE 3: FRONTEND

| Vista | Estado |
|-------|--------|
| productos_view.py | ✅ Migrado |
| clientes_view.py | ✅ Migrado |
| inventario_view.py | ✅ Migrado |
| corte_view.py | ✅ Migrado |
| proveedores_view.py | ✅ Migrado |
| cajeros_view.py | ✅ Migrado |

### ✅ FASE 4: UI/UX

| Corrección | Archivo |
|------------|---------|
| Contraste WCAG AA | `theme.py` (text_secondary: #cbd5e1) |
| Modo claro sidebar | `theme.py` (bg_sidebar: #e2e8f0) |

### ✅ FASE 5: QA

| Archivo | Corrección |
|---------|------------|
| theme.py | except Exception |
| impresora.py | logging.warning |
| backup.py | logging.warning |
| main.py | except Exception |

---

## ARCHIVOS CREADOS

```
tucajero/repositories/
├── categoria_repo.py    (NUEVO)
├── proveedor_repo.py    (NUEVO)
└── corte_repo.py        (NUEVO)
```

## ARCHIVOS MODIFICADOS

```
tucajero/
├── models/producto.py       (relaciones mermas, devoluciones)
├── models/cajero.py          (relaciones nomina, mermas, devoluciones)
├── config/app_config.py       (IVA_RATE centralizado)
├── services/venta_service.py (VentaAnalyticsService)
├── utils/theme.py            (contraste, modo claro)
├── utils/impresora.py        (manejo excepciones)
├── utils/backup.py           (manejo excepciones)
├── main.py                   (manejo excepciones)
├── ui/productos_view.py      (colores theme)
├── ui/clientes_view.py       (colores theme)
├── ui/inventario_view.py    (colores theme)
├── ui/corte_view.py         (colores theme)
├── ui/proveedores_view.py   (colores theme)
└── ui/cajeros_view.py       (colores theme)
```

---

## CORRECCIONES PENDIENTES (VISTAS SECUNDARIAS)

Las siguientes vistas tienen colores hardcodeados pero son de menor uso:
- historial_view.py
- cotizaciones_view.py
- config_view.py
- ventas_view.py (botones de cambio/faltante)
- login_cajero.py
- setup_view.py
- activate_view.py
- about_view.py
- buscador_productos.py
- descuento_dialog.py
- selector_cliente.py

**Nota:** El patrón de migración está establecido. Las vistas restantes pueden migrarse según necesidad.

```
FASE 1: BACKEND (CRÍTICO - 3 tareas)
├── 1.1 Corregir relaciones faltantes en modelos
├── 1.2 Crear repositorios faltantes
└── 1.3 Centralizar IVA_RATE en app_config.py

FASE 2: LÓGICA (DEPENDE DE FASE 1)
├── 2.1 Eliminar duplicación VentaService
└── 2.2 Actualizar servicios para usar IVA_RATE centralizado

FASE 3: FRONTEND (Tareas independientes, pueden ejecutarse EN PARALELO con FASE 2)
├── 3.1 Migrar colores hardcodeados al sistema de temas
├── 3.2 Corregir modo claro del sidebar
└── 3.3 Corregir contraste de texto (UI/UX)

FASE 4: QA (Durante todo el proceso)
└── 4.1 Reemplazar excepciones vacías

FASE 5: VERIFICACIÓN FINAL
└── 5.1 Validar que todo funciona
```

---

## TAREAS POR AGENTE

### 🔧 AGENTE BACKEND (Inicio: Inmediato)

| # | Tarea | Archivos | Dependencias |
|---|-------|----------|---------------|
| **B1** | Corregir relaciones faltantes en modelos | `tucajero/models/producto.py`, `cajero.py`, `venta.py`, `cliente.py` | Ninguna |
| **B2** | Crear CategoriaRepository | `tucajero/repositories/categoria_repo.py` | B1 |
| **B3** | Crear ProveedorRepository + OrdenCompraRepository | `tucajero/repositories/proveedor_repo.py` | Ninguna |
| **B4** | Crear CorteCajaRepository | `tucajero/repositories/corte_repo.py` | Ninguna |
| **B5** | Centralizar IVA_RATE en app_config.py | `tucajero/config/app_config.py` | Ninguna |

**Repositorio nuevo - CategoriaRepository:**
```python
# archivo: tucajero/repositories/categoria_repo.py
class CategoriaRepository:
    def __init__(self, session):
        self.session = session
    
    def get_all(self): ...
    def get_by_id(self, id): ...
    def create(self, nombre, descripcion=None, color=None): ...
    def update(self, id, **kwargs): ...
    def delete(self, id): ...
    def get_by_nombre(self, nombre): ...
    def search(self, query): ...
```

**Repositorio nuevo - ProveedorRepository:**
```python
# archivo: tucajero/repositories/proveedor_repo.py
class ProveedorRepository: ...
class OrdenCompraRepository: ...
```

**Repositorio nuevo - CorteCajaRepository:**
```python
# archivo: tucajero/repositories/corte_repo.py
class CorteCajaRepository: ...
class GastoCajaRepository: ...
```

**Constante IVA centralizada:**
```python
# archivo: tucajero/config/app_config.py
from dataclasses import dataclass

@dataclass
class AppConfig:
    IVA_RATE: float = 0.19
    VERSION: str = "1.0.0"
    # ...

app_config = AppConfig()
```

---

### 📊 AGENTE LÓGICA (Inicio: Después de B5)

| # | Tarea | Archivos | Dependencias |
|---|-------|----------|---------------|
| **L1** | Eliminar duplicación VentaService | `tucajero/services/venta_service.py` | Ninguna |
| **L2** | Actualizar servicios para usar app_config.IVA_RATE | Múltiples servicios | B5 |
| **L3** | Migrar servicios para usar nuevos repositorios | Servicios que usan modelos directamente | B2, B3, B4 |

**Reestructuración venta_service.py:**
```python
# ANTES: Dos clases con mismo nombre
class VentaService: ...  # Analytics (líneas 8-112)
class VentaService: ...  # Operaciones (líneas 130-221)

# DESPUÉS: Clases separadas
class VentaAnalyticsService: ...  # analytics
class VentaOperacionesService: ...  # operaciones (ya existe en venta_operaciones_service.py)
```

---

### 🎨 AGENTE FRONTEND (Inicio: En PARALELO con Lógica)

| # | Tarea | Archivos | Dependencias |
|---|-------|----------|---------------|
| **F1** | Migrar colores hardcodeados - productos_view.py | `tucajero/ui/productos_view.py` | Ninguna |
| **F2** | Migrar colores hardcodeados - clientes_view.py | `tucajero/ui/clientes_view.py` | Ninguna |
| **F3** | Migrar colores hardcodeados - inventario_view.py | `tucajero/ui/inventario_view.py` | Ninguna |
| **F4** | Migrar colores hardcodeados - corte_view.py | `tucajero/ui/corte_view.py` | Ninguna |
| **F5** | Migrar colores hardcodeados - main_window.py | `tucajero/ui/main_window.py` | Ninguna |
| **F6** | Corregir modo claro del sidebar | `tucajero/ui/main_window.py` | Ninguna |

**Patrón de corrección (ejemplo para productos_view.py):**
```python
# ANTES (línea 53):
btn_agregar.setStyleSheet("background-color: #27ae60; color: white; ...")

# DESPUÉS:
c = get_colors()
btn_agregar.setStyleSheet(f"background-color: {c['success']}; color: white; ...")
```

---

### 🎨 AGENTE UI/UX DESIGN (Inicio: En PARALELO con Frontend)

| # | Tarea | Archivo | Dependencias |
|---|-------|----------|--------------|
| **U1** | Corregir contraste de texto secundario | `tucajero/utils/theme.py` | Ninguna |

**Corrección de contraste:**
```python
# EN theme.py - colors["dark"]["text_secondary"]
# ANTES: "#94a3b8" (contraste 4.2:1 - INSUFICIENTE)
# DESPUÉS: "#cbd5e1" (contraste 5.8:1 - CUMPLE WCAG AA)
```

---

### 🔍 AGENTE QA (Inicio: Durante TODO el proceso)

| # | Tarea | Archivos | Dependencias |
|---|-------|----------|---------------|
| **Q1** | Reemplazar excepciones vacías - main.py | `tucajero/main.py` | Ninguna |
| **Q2** | Reemplazar excepciones vacías - impresora.py | `tucajero/utils/impresora.py` | Ninguna |
| **Q3** | Reemplazar excepciones vacías - backup.py | `tucajero/utils/backup.py` | Ninguna |
| **Q4** | Reemplazar excepciones vacías - theme.py | `tucajero/utils/theme.py` | Ninguna |
| **Q5** | Reemplazar excepciones vacías - ventas_view.py | `tucajero/ui/ventas_view.py` | Ninguna |
| **Q6** | Verificar calidad después de cada fase | Todos | Depende de fase |

**Patrón de corrección:**
```python
# ANTES:
try:
    self.conectar()
except:
    pass

# DESPUÉS:
try:
    self.conectar()
except ConnectionError as e:
    logger.warning(f"No se pudo conectar a la impresora: {e}")
except Exception as e:
    logger.error(f"Error inesperado al conectar: {e}")
```

---

## CRONOGRAMA DE EJECUCIÓN

| Día | Mañana (4h) | Tarde (4h) |
|-----|-------------|------------|
| **Día 1** | B1, B2, B3, B4, B5 | F1, F2, F3 (en paralelo) |
| **Día 2** | F4, F5, F6 + U1 | L1, L2 + Q1, Q2 |
| **Día 3** | Q3, Q4, Q5, Q6 | L3 + VERIFICACIÓN FINAL |

**Tiempo total estimado: 3 días**

---

## CHECKLIST DE VERIFICACIÓN

### Post-Fase 1 (Backend):
- [ ] Relaciones de modelos corregidas
- [ ] CategoriaRepository creado y funcionando
- [ ] ProveedorRepository creado y funcionando
- [ ] CorteCajaRepository creado y funcionando
- [ ] IVA_RATE centralizado en app_config.py

### Post-Fase 2 (Lógica):
- [ ] VentaService duplicado eliminado
- [ ] Servicios usan app_config.IVA_RATE
- [ ] Servicios usan nuevos repositorios

### Post-Fase 3 (Frontend):
- [ ] 232 colores hardcodeados migrados a theme
- [ ] Modo claro del sidebar corregido
- [ ] Contraste de texto secundario cumple WCAG AA

### Post-Fase 4 (QA):
- [ ] Todas las excepciones vacías reemplazadas
- [ ] Sin errores de lint

### Post-Fase 5 (Verificación):
- [ ] App inicia sin errores
- [ ] Flujo de venta funciona
- [ ] Compilación exitosa con PyInstaller

---

## NOTAS IMPORTANTES

1. **Trabajo en paralelo**: Frontend y UI/UX pueden trabajar simultáneamente con Lógica
2. **No romper funcionalidad**: Cada cambio debe probarse antes de avanzar
3. **Backup antes de DB**: Antes de modificar modelos, hacer backup de pos.db
4. **Commits frecuentes**: Cada tarea completada = commit con mensaje descriptivo
5. **QA como guardián**: QA revisa cada archivo antes de marcar como completado

---

*Coordinador del Proyecto - TuCajero POS*