# TuCajero - Sistema de Punto de Venta (POS)

## Descripción General

**TuCajero** es un sistema de caja registradora para pequeños negocios (farmacias, tiendas, minimarkets). Permite gestionar ventas, productos, inventario, clientes, proveedores, cortes de caja y más. Desarrollado en Python con interfaz gráfica usando PySide6.

## Tech Stack

| Tecnología | Propósito |
|------------|-----------|
| **Python 3.12+** | Lenguaje de programación |
| **PySide6** | Framework de interfaz gráfica (Qt) |
| **SQLAlchemy 2.0** | ORM para base de datos |
| **SQLite** | Base de datos embebida (WAL mode) |
| **reportlab** | Generación de PDFs (facturas) |
| **openpyxl** | Exportación a Excel |
| **python-escpos** | Impresión de tickets |
| **matplotlib** | Gráficos en dashboard |
| **pyinstaller** | Compilación a ejecutable .exe |

---

## Estructura del Proyecto

```
TuCajeroPOS/
├── tucajero/                    # Código principal
│   ├── main.py                  # Punto de entrada
│   ├── TuCajero.spec            # Configuración PyInstaller
│   │
│   ├── ui/                      # Vistas/Interfaces (PySide6)
│   │   ├── main_window.py       # Ventana principal con sidebar
│   │   ├── ventas_view.py      # Vista de ventas (POS)
│   │   ├── productos_view.py    # CRUD de productos
│   │   ├── inventario_view.py   # Entrada/salida de inventario
│   │   ├── corte_view.py       # Corte de caja
│   │   ├── clientes_view.py    # Gestión de clientes
│   │   ├── proveedores_view.py # Gestión de proveedores
│   │   ├── cotizaciones_view.py# Cotizaciones
│   │   ├── historial_view.py   # Historial de ventas
│   │   ├── dashboard_view.py  # Panel de control
│   │   ├── setup_view.py       # Configuración inicial
│   │   ├── activate_view.py    # Activación de licencias
│   │   ├── config_view.py      # Configuración de tienda
│   │   ├── cajeros_view.py     # Gestión de cajeros
│   │   ├── login_cajero.py     # Login de cajeros
│   │   ├── buscador_productos.py
│   │   ├── selector_cliente.py
│   │   ├── descuento_dialog.py
│   │   └── about_view.py
│   │
│   ├── models/                  # Modelos de datos (SQLAlchemy)
│   │   ├── producto.py         # Producto, Categoria
│   │   ├── cliente.py          # Cliente
│   │   ├── cajero.py           # Cajero
│   │   ├── cotizacion.py       # Cotizacion, CotizacionItem
│   │   └── proveedor.py        # Proveedor, OrdenCompra
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── producto_service.py # ProductoService, CategoriaService
│   │   ├── venta_service.py    # VentaService
│   │   ├── cliente_service.py  # ClienteService
│   │   ├── cajero_service.py   # CajeroService
│   │   ├── corte_service.py    # CorteCajaService
│   │   ├── cotizacion_service.py
│   │   ├── proveedor_service.py
│   │   ├── categoria_service.py
│   │   ├── historial_service.py
│   │   └── fraccion_service.py
│   │
│   ├── repositories/            # Acceso a datos
│   │   ├── producto_repo.py
│   │   ├── venta_repo.py       # VentaRepository, InventarioRepository
│   │   └── cliente_repo.py
│   │
│   ├── config/                  # Configuración
│   │   ├── database.py         # Inicialización DB, conexión SQLite
│   │   └── app_config.py       # Constantes
│   │
│   ├── security/                # Seguridad
│   │   └── license_manager.py # Sistema de licencias
│   │
│   ├── utils/                   # Utilidades
│   │   ├── ticket.py           # Generador de tickets
│   │   ├── store_config.py     # Configuración de tienda
│   │   ├── backup.py           # Backup de base de datos
│   │   ├── logging_config.py  # Configuración de logs
│   │   ├── error_handler.py   # Manejo de errores
│   │   ├── format.py           # Formato de moneda
│   │   ├── theme.py            # Temas de la UI
│   │   ├── impresora.py        # Impresión ESC/POS
│   │   ├── excel_exporter.py   # Exportación Excel
│   │   ├── factura_diaria.py   # Generación PDF
│   │   └── importador.py       # Importar productos
│   │
│   ├── database/                # Base de datos (dev)
│   │   └── pos.db              # SQLite
│   │
│   └── assets/                  # Recursos
│       ├── icons/              # Iconos
│       └── store/              # Logo de tienda
│
├── build/                      # Archivos de compilación PyInstaller
├── dist/                       # Ejecutable final (56MB)
├── installer/                  # Instaladores
├── venv/                       # Entorno virtual
├── requirements.txt            # Dependencias
├── TuCajero.spec              # Config PyInstaller
├── build_exe.bat              # Script compilación
└── run.bat                    # Ejecutar app
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
| aplica_iva | Boolean | Aplica IVA |
| activo | Boolean | Borrado lógico |
| categoria_id | Integer | FK -> Categoria |
| stock_minimo | Integer | Alerta de stock bajo |
| es_fraccion | Boolean | Producto fraccionable |
| unidades_por_empaque | Integer | Cantidad por empaque |

### Venta
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| fecha | DateTime | Fecha y hora |
| total | Float | Total de la venta |
| metodo_pago | String | Efectivo, Nequi, etc. |
| cliente_id | Integer | FK -> Cliente |
| es_credito | Boolean | Venta a crédito/fiado |
| descuento_tipo | String | %, fijo |
| descuento_valor | Float | Valor del descuento |
| descuento_total | Float | Descuento aplicado |
| cajero_id | Integer | FK -> Cajero |

### VentaItem
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| venta_id | Integer | FK -> Venta |
| producto_id | Integer | FK -> Producto |
| cantidad | Integer | Cantidad |
| precio | Float | Precio unitario |

### Cliente
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| nombre | String(100) | Nombre |
| telefono | String(20) | Teléfono |
| email | String(100) | Email |
| nit | String(20) | NIT |
| activo | Boolean | Estado |

### Cajero
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| nombre | String(100) | Nombre |
| pin | String(4) | PIN de 4 dígitos |
| rol | String | admin, cajero |
| activo | Boolean | Estado |

### CorteCaja
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| fecha_apertura | DateTime | Apertura de caja |
| fecha_cierre | DateTime | Cierre (null si abierta) |
| total_ventas | Float | Total vendido |
| efectivo_inicial | Float | Efectivo al abrir |
| efectivo_final | Float | Efectivo al cerrar |
| numero_ventas | Integer | Cantidad de ventas |
| cajero_id | Integer | FK -> Cajero |

### Cotizacion
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| fecha | DateTime | Fecha |
| cliente_id | Integer | FK -> Cliente |
| notas | String | Notas |
|total | Float | Total |

### Proveedor
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | PK |
| nombre | String(100) | Nombre |
| telefono | String(20) | Teléfono |
| email | String(100) | Email |
| direccion | String | Dirección |
| activo | Boolean | Estado |

---

## Hardening Implementado

### 1. Manejo de Excepciones Global (main.py)
- `sys.excepthook` para capturar excepciones no controladas
- Logging de errores críticos
- Mensaje amigable al usuario

### 2. Base de Datos (database.py)
- Timeout de 30 segundos
- WAL mode activo
- pool_pre_ping=True
- Retry automático para "database is locked"
- Transacciones con rollback seguro

### 3. UI (ventas_view.py)
- Flags de control: `_initialized`, `_loading`, `_procesando_pago`
- Protección en métodos principales
- Anti-doble-click en botones críticos

### 4. Logging (logging_config.py)
- Logs en `%LOCALAPPDATA%\TuCajero\logs\app.log`
- Rotación automática (1MB por archivo, 3 backups)
- Consola solo en desarrollo

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
5. Si no hay setup -> Ventana de configuración inicial
6. Inicializar base de datos (crear tablas si no existen)
7. Login de cajero
8. Abrir caja automáticamente
9. Crear vistas y mostrarlas
```

### 2. Sistema de Licencias
- **Machine ID**: UUID del hardware + nombre PC + procesador
- **Licencia**: SHA256(machine_id + secret) -> 16 caracteres
- **Activación**: Guarda en `%LOCALAPPDATA%\TuCajero\config\license.json`

### 3. Ventas (ventas_view.py)
```
1. Input código producto o clic en "Buscar"
2. Si existe y hay stock -> Agregar al carrito
3. Modificar cantidad (+/-), eliminar items
4. Aplicar descuento opcional
5. Seleccionar cliente (opcional)
6. Click "COBRAR" -> Panel de cobro
7. Seleccionar método de pago
8. Calcular cambio, confirmar
9. Registrar venta en DB (descuenta stock)
10. Generar ticket/imprimir
11. Recargar productos (actualizar stock)
```

---

## Rutas y Archivos

### Producción (Windows)
- Base de datos: `%LOCALAPPDATA%\TuCajero\database\pos.db`
- Logs: `%LOCALAPPDATA%\TuCajero\logs\app.log`
- Backups: `%LOCALAPPDATA%\TuCajero\database\backups\`
- Config: `%LOCALAPPDATA%\TuCajero\config\`

### Desarrollo
- Base de datos: `tucajero/database/pos.db`
- Logs: `%LOCALAPPDATA%\TuCajero\logs\app.log`

---

## Comandos

### Ejecutar en desarrollo
```bash
cd TuCajeroPOS
venv\Scripts\python.exe tucajero\main.py
```

### Compilar ejecutable
```bash
python -m PyInstaller --noconfirm --clean TuCajero.spec
```

### Ejecutar exe
```bash
dist\TuCajero.exe
```

---

## Dependencias (requirements.txt)
```
PySide6>=6.5.0
SQLAlchemy>=2.0.0
reportlab
python-dateutil
pyinstaller
openpyxl>=3.1.0
python-escpos>=3.0.0
matplotlib>=3.7.0
```

---

## Características del Sistema

### Módulos principales:
- **Ventas**: POS con búsqueda, carrito, múltiples métodos de pago, descuentos
- **Productos**: CRUD completo con categorías, códigos de barras, stock mínimo
- **Inventario**: Entradas/salidas, alertas de stock bajo
- **Clientes**: Registro, historial de compras, crédito/fiado
- **Proveedores**: Órdenes de compra, recepción
- **Corte de Caja**: Apertura/cierre, estadísticas, backup automático
- **Cotizaciones**: Crear y convertir en ventas
- **Historial**: Búsqueda, filtros, exportación Excel
- **Dashboard**: Gráficos de ventas, métricas en tiempo real
- **Cajeros**: Gestión de usuarios con PIN de 4 dígitos
- **Configuración**: Datos del negocio, impresora, backup

### Sistema de backup:
- Backup manual desde dashboard
- Backup automático semanal (lunes)
- Restaurar backup desde archivo
- Exportar backup a USB/carpeta externa
- Mantiene últimos 4 backups

### Hardening implementado:
- Manejo global de excepciones
- Base de datos con WAL mode y retry
- UI con flags de inicialización
- Logging en %LOCALAPPDATA%\TuCajero\logs\
- Validación de funciones críticas con try/except

---

## Características

1. **Ventas**: POS con búsqueda, carrito, múltiples métodos de pago
2. **Productos**: CRUD completo con categorías, códigos de barras
3. **Inventario**: Entradas/salidas, stock mínimo, alertas
4. **Clientes**: Registro, historial de compras, crédito/fiado
5. **Proveedores**: Órdenes de compra, recepción
6. **Corte de Caja**: Apertura/cierre, estadísticas, backup
7. **Cotizaciones**: Crear y convertir en ventas
8. **Historial**: Búsqueda, filtros, exportación Excel
9. **Dashboard**: Estadísticas en tiempo real
10. **Impresión**: Tickets ESC/POS (USB, red, serial)
11. **Licencias**: Sistema de activación por machine ID

---

## Notas Importantes

1. **Licencia obligatoria**: El sistema no funciona sin licencia válida
2. **Caja requerida**: No se pueden hacer ventas si la caja está cerrada
3. **Stock automático**: Las ventas-descuentan stock automáticamente
4. **Backup automático**: Se crea backup al cerrar caja
5. **Identificador único**: Cada PC tiene un machine ID único para licencias
6. **Ejecutable**: 56MB (comprimido con UPX)