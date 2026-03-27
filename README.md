# TuCajero - Sistema de Punto de Venta (POS)

**TuCajero** es un sistema de caja registradora para pequeños negocios (farmacias, tiendas, minimarkets). Permite gestionar ventas, productos, inventario, clientes, proveedores y cortes de caja con dashboard en tiempo real.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![PySide6](https://img.shields.io/badge/PySide6-Qt-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![License](https://img.shields.io/badge/License-Propietary-red)

---

## ✨ Características Principales

- **🛒 Ventas POS**: Interfaz intuitiva con búsqueda por código de barras, carrito de compras y múltiples métodos de pago
- **📦 Gestión de Productos**: CRUD completo con categorías, control de stock, fechas de vencimiento y productos fraccionables
- **📊 Dashboard en Tiempo Real**: Gráficos nativos de ventas, métricas KPI y tabla de facturas del día con detalle de productos
- **📈 Inventario Unificado**: Entradas, salidas, desempaque de productos y alertas de stock bajo/crítico
- **💰 Corte de Caja**: Apertura y cierre con validación de diferencias (sobrantes/faltantes)
- **👥 Clientes y Proveedores**: Gestión completa con historial de compras y órdenes de compra
- **📋 Cotizaciones**: Crear presupuestos y convertirlos en ventas
- **🔐 Sistema de Licencias**: Activación por máquina para evitar uso no autorizado
- **🖨️ Tickets y Reportes**: Generación de tickets ESC/POS y facturas diarias en PDF
- **💾 Backup Automático**: Respaldo de base de datos semanal y manual
- **💳 Múltiples Pagos**: Efectivo, Nequi, Daviplata, transferencia, tarjetas y crédito

---

## 🚀 Novedades - Marzo 2026

### ✅ Correcciones Recientes
- **Gráficos Nativos Qt**: Reemplazo de matplotlib por gráficos dibujados con QPainter (más rápidos y estables)
- **Tabla de Facturas Mejorada**: Ahora muestra productos vendidos por factura
- **Validación de Stock**: Bloqueo de stock negativo en ventas y movimientos
- **Fechas de Vencimiento**: Bloqueo de fechas en el pasado
- **Límite de Descuentos**: Máximo 50% para cajeros normales
- **Persistencia de Carrito**: Recuperación automática después de crashes
- **14 Índices Nuevos**: Optimización de consultas de base de datos

---

## 🛠️ Tech Stack

| Tecnología | Propósito | Versión |
|------------|-----------|---------|
| **Python** | Lenguaje de programación | 3.12+ |
| **PySide6** | Interfaz gráfica (Qt) | 6.5.0+ |
| **SQLAlchemy** | ORM para base de datos | 2.0.0+ |
| **SQLite** | Base de datos embebida (WAL mode) | 3.40+ |
| **python-dateutil** | Manejo de fechas | 2.9.0+ |
| **pyinstaller** | Compilación a ejecutable | 6.0+ |

**Opcionales (no incluidos en EXE):**
- `openpyxl` - Exportación a Excel
- `reportlab` - Generación de PDFs
- `python-escpos` - Impresión de tickets

---

## 📋 Requisitos

**Mínimos:**
- Windows 10/11
- 2GB RAM
- 200MB disco duro
- .NET Framework 4.7+

**Recomendados:**
- Windows 11
- 4GB RAM
- SSD
- Impresora térmica ESC/POS (opcional)

---

## Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/franciscollinas/TuCajero.git
cd TuCajero
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Ejecutar la aplicación
```bash
python tucajero/main.py
```

---

## Compilación a .exe

### Windows
```bash
# Usando el script incluido
build_exe.bat

# O manualmente con PyInstaller
pyinstaller tucajero/TuCajero.spec --onefile
```

El ejecutable se generará en la carpeta `dist/`.

---

## Estructura del Proyecto

```
TuCajero/
├── tucajero/                    # Código principal
│   ├── main.py                  # Punto de entrada
│   ├── ui/                      # Interfaces gráficas (PySide6)
│   │   ├── ventas_view.py       # Vista de ventas POS
│   │   ├── productos_view.py    # CRUD de productos
│   │   ├── inventario_view.py   # Control de inventario
│   │   ├── corte_view.py        # Corte de caja
│   │   └── activate_view.py     # Activación de licencias
│   ├── models/                  # Modelos de datos
│   ├── services/                # Lógica de negocio
│   ├── repositories/           # Acceso a datos
│   ├── security/                # Sistema de licencias
│   ├── utils/                   # Utilidades
│   └── config/                  # Configuración
├── dist/                        # Ejecutable compilado
├── requirements.txt             # Dependencias
└── build_exe.bat               # Script de compilación
```

---

## Modelos de Datos

### Producto
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | Integer | Identificador único |
| codigo | String | Código de barras |
| nombre | String | Nombre del producto |
| precio | Float | Precio de venta |
| costo | Float | Costo de compra |
| stock | Integer | Cantidad en inventario |

### Venta
Registro de cada transacción realizada con fecha y total.

### CorteCaja
Control de apertura y cierre de caja con estadísticas.

---

## Sistema de Licencias

El sistema requiere activación:
1. Genera un Machine ID único basado en el hardware
2. Calcula la licencia basada en el Machine ID
3. El administrador proporciona la licencia de activación

---

## Rutas de Datos (Windows)

- Base de datos: `%LOCALAPPDATA%\TuCajero\database\pos.db`
- Logs: `%LOCALAPPDATA%\TuCajero\logs\app.log`
- Backups: `%LOCALAPPDATA%\TuCajero\database\backups\`

---

## Configuración de Tienda

Edita `tucajero/config/store_config.json`:

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

## Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcion`)
3. Commit tus cambios (`git commit -m 'Agregar nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abre un Pull Request

---

## Licencia

Este proyecto es propietario. Todos los derechos reservados.

---

**Desarrollado por Francisco Collinas**
