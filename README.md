# TuCajero - Sistema de Punto de Venta (POS)

**TuCajero** es un sistema de caja registradora para pequeños negocios (farmacias, tiendas, minimarkets). Permite gestionar ventas, productos, inventario y cortes de caja.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![PySide6](https://img.shields.io/badge/PySide6-Qt-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![License](https://img.shields.io/badge/License-Propietary-red)

---

## Características

- **Ventas POS**: Interfaz intuitiva para registrar ventas con código de barras
- **Gestión de Productos**: CRUD completo con código, nombre, precio y stock
- **Control de Inventario**: Entradas y salidas con historial de movimientos
- **Corte de Caja**: Apertura y cierre de caja con estadísticas diarias
- **Sistema de Licencias**: Activación por máquina para evitar uso no autorizado
- **Tickets y Reportes**: Generación de tickets en PDF
- **Backup Automático**: Respaldo de base de datos al cerrar caja

---

## Tech Stack

| Tecnología | Propósito |
|------------|-----------|
| Python 3.14 | Lenguaje de programación |
| PySide6 | Interfaz gráfica (Qt) |
| SQLAlchemy | ORM para base de datos |
| SQLite | Base de datos embebida |
| ReportLab | Generación de documentos PDF |
| PyInstaller | Compilación a ejecutable .exe |

---

## Requisitos

```
PySide6>=6.5.0
SQLAlchemy>=2.0.0
reportlab
python-dateutil
pyinstaller
openpyxl>=3.1.0
```

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
