# TuCajero - Sistema de Punto de Venta (POS)

## Descripción General

**TuCajero** es un sistema de caja registradora para pequeños negocios (farmacias, tiendas, minimarkets). Permite gestionar ventas, productos, inventario y cortes de caja. Desarrollado en Python con interfaz gráfica usando PySide6.

## Tech Stack

| Tecnología | Propósito |
|------------|-----------|
| **Python 3.14** | Lenguaje de programación |
| **PySide6** | Framework de interfaz gráfica (Qt) |
| **SQLAlchemy** | ORM para base de datos |
| **SQLite** | Base de datos embebida |
| **reportlab** | Generación de documentos |
| **pyinstaller** | Compilación a ejecutable .exe |

---

## Estructura del Proyecto

```
tito castilla/
├── tucajero/                    # Código principal
│   ├── main.py                  # Punto de entrada de la app
│   ├── TuCajero.spec            # Configuración PyInstaller
│   │
│   ├── ui/                      # Vistas/Interfaces (PySide6)
│   │   ├── main_window.py       # Ventana principal con sidebar
│   │   ├── ventas_view.py       # Vista de ventas (POS)
│   │   ├── productos_view.py    # CRUD de productos
│   │   ├── inventario_view.py   # Entrada/salida de inventario
│   │   ├── corte_view.py        # Corte de caja
│   │   ├── activate_view.py     # Activación de licencias
│   │   ├── about_view.py        # Acerca de
│   │   └── buscador_productos.py
│   │
│   ├── models/                  # Modelos de datos (SQLAlchemy)
│   │   └── producto.py          # Producto, Venta, VentaItem, MovimientoInventario, CorteCaja
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── producto_service.py # ProductoService, VentaService, InventarioService
│   │   └── corte_service.py    # CorteCajaService
│   │
│   ├── repositories/            # Acceso a datos
│   │   ├── producto_repo.py    # ProductoRepository
│   │   └── venta_repo.py       # VentaRepository, InventarioRepository
│   │
│   ├── config/                 # Configuración
│   │   ├── database.py         # Inicialización DB, conexión SQLite
│   │   ├── app_config.py       # Constantes (nombre, versión)
│   │   └── store_config.json   # Configuración de la tienda
│   │
│   ├── security/                # Seguridad
│   │   └── license_manager.py  # Sistema de licencias (machine ID)
│   │
│   ├── utils/                   # Utilidades
│   │   ├── ticket.py           # Generador de tickets
│   │   ├── store_config.py     # Cargar/configurar tienda
│   │   ├── backup.py           # Backup de base de datos
│   │   └── ...
│   │
│   ├── database/                # Base de datos
│   │   └── pos.db              # SQLite (se genera automáticamente)
│   │
│   └── assets/                  # Recursos
│       └── icons/               # Iconos
│
├── build/                       # Archivos de compilación PyInstaller
├── dist/                        # Ejecutable final
├── venv/                        # Entorno virtual
├── requirements.txt             # Dependencias
├── build_exe.bat               # Script compilación
└── run.bat                     # Ejecutar app
```

---

## Modelos de Base de Datos

### Producto
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| codigo | String(50) | Código de barras (único) |
| nombre | String(100) | Nombre del producto |
| precio | Float | Precio de venta |
| costo | Float | Costo de compra |
| stock | Integer | Cantidad en inventario |
| activo | Boolean | Si está activo (borrado lógico) |

### Venta
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| fecha | DateTime | Fecha y hora |
| total | Float | Total de la venta |

### VentaItem
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| venta_id | Integer | FK -> Venta |
| producto_id | Integer | FK -> Producto |
| cantidad | Integer | Cantidad |
| precio | Float | Precio unitario |

### MovimientoInventario
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| producto_id | Integer | FK -> Producto |
| tipo | String | 'entrada' o 'salida' |
| cantidad | Integer | Cantidad |
| fecha | DateTime | Fecha |

### CorteCaja
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| fecha_apertura | DateTime | Cuándo se abrió la caja |
| fecha_cierre | DateTime | Cuándo se cerró (null si abierta) |
| total_ventas | Float | Total vendido |
| numero_ventas | Integer | Cantidad de ventas |

---

## Flujo de la Aplicación

### 1. Inicio (main.py)
```
1. Configurar logging (logs/app.log)
2. Crear carpetas necesarias
3. Cargar configuración de tienda
4. Validar licencia
   - Si no activada -> Mostrar ventana activación
   - Esperar hasta que se active
5. Inicializar base de datos (crear tablas si no existen)
6. Abrir caja automáticamente
7. Crear vistas y mostrarlas
```

### 2. Sistema de Licencias
- **Machine ID**: Se genera usando UUID del hardware + nombre PC + procesador
- **Licencia**: SHA256(machine_id + "tito_castilla_pos_secret") -> 16 caracteres
- **Activación**: Guarda en `config/license.json`
- **Validación**: Compara licencia guardada vs calculada

### 3. Ventas (ventas_view.py)
```
1. Input código producto o clic en "Buscar"
2. Si existe y hay stock -> Agregar al carrito
3. Modificar cantidad (+/-), eliminar items
4. Click "COBRAR" -> Dialog pago en efectivo
5. Calcular cambio, confirmar
6. Registrar venta en DB (descuenta stock)
7. Generar ticket
8. Recargar productos (para actualizar stock)
```

### 4. Productos (productos_view.py)
- CRUD completo: Crear, Leer, Actualizar, Eliminar (borrado lógico)
- Campos: código, nombre, precio, costo, stock

### 5. Inventario (inventario_view.py)
- Entrada: Aumentar stock (compras, devoluciones)
- Salida: Disminuir stock (pérdidas, ajustes)
- Historial de movimientos

### 6. Corte de Caja (corte_view.py)
- Abrir caja: Crea registro CorteCaja
- Cerrar caja: Finaliza corte, suma ventas del día, crea backup
- Ver estadísticas del día

---

## Configuración de la Tienda

Archivo: `config/store_config.json`
```json
{
  "store_name": "Mi Tienda",
  "logo_path": "",
  "address": "",
  "phone": "",
  "nit": ""
}
```

---

## Rutas y Archivos

### Datos (Windows)
- Base de datos: `%LOCALAPPDATA%\TuCajero\database\pos.db`
- Logs: `%LOCALAPPDATA%\TuCajero\logs\app.log`
- Backups: `%LOCALAPPDATA%\TuCajero\database\backups\`

### Desarrollo
- Base de datos: `tucajero/database/pos.db`
- Logs: `logs/app.log`

---

## Comandos

### Ejecutar en desarrollo
```bash
cd tito castilla
venv\Scripts\python.exe tucajero\main.py
```

### Compilar ejecutable
```bash
pyinstaller tucajero\TuCajero.spec --onefile
```

---

## Dependencias (requirements.txt)
```
PySide6>=6.5.0
SQLAlchemy>=2.0.0
reportlab
python-dateutil
pyinstaller
```

---

## Notas Importantes

1. **Licencia obligatoria**: El sistema no funciona sin licencia válida
2. **Caja requerida**: No se pueden hacer ventas si la caja está cerrada
3. **Stock automático**: Las ventas descuentan stock automáticamente
4. **Backup automático**: Se crea backup al cerrar caja
5. **Identificador único**: Cada PC tiene un machine ID único para licencias
