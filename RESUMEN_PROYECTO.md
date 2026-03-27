# TuCajero POS - Resumen del Proyecto

**Última actualización:** 26 de Marzo 2026  
**Versión:** 2.1.0  
**Estado:** ✅ Producción

---

## 📌 Descripción

**TuCajero POS** es un sistema de punto de venta para pequeños negocios. Desarrollado en Python con PySide6, ofrece una interfaz moderna y funcional para gestionar ventas, inventario, clientes y reportes.

---

## 🎯 Estado Actual - Marzo 2026

### ✅ Sistema Estable
- **Inicio:** Sin errores de imports
- **Gráficos:** Nativos Qt (sin matplotlib)
- **Dashboard:** Funcional con tabla de productos
- **Validaciones:** Stock, fechas, descuentos activos
- **Persistencia:** Carrito se recupera tras crashes

---

## 📊 Características Principales

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| **Ventas POS** | ✅ Completo | Búsqueda, carrito, múltiples pagos, descuentos |
| **Productos** | ✅ Completo | CRUD, categorías, stock, vencimientos |
| **Inventario** | ✅ Unificado | Entradas, salidas, desempaque, alertas |
| **Dashboard** | ✅ Mejorado | Gráficos Qt, KPIs, tabla con productos |
| **Corte de Caja** | ✅ Validado | Diferencias, sobrantes/faltantes |
| **Clientes** | ✅ Completo | Historial, crédito, búsqueda |
| **Proveedores** | ✅ Completo | Órdenes de compra, recepción |
| **Cotizaciones** | ✅ Funcional | Crear y convertir a ventas |
| **Historial** | ✅ Completo | Búsqueda, filtros, exportación |
| **Licencias** | ✅ Activo | Machine ID, activación única |

---

## 🛠️ Arquitectura Técnica

### Frontend
- **Framework:** PySide6 (Qt 6.5+)
- **Gráficos:** QPainter (nativo, sin matplotlib)
- **Tema:** Personalizado con colores configurables

### Backend
- **Lenguaje:** Python 3.12+
- **ORM:** SQLAlchemy 2.0
- **Database:** SQLite (WAL mode)

### Infraestructura
- **Build:** PyInstaller 6.0
- **Tamaño EXE:** ~65 MB
- **RAM:** ~150MB en ejecución

---

## 📁 Estructura de Archivos

```
TuCajeroPOS/
├── tucajero/
│   ├── main.py                 # Punto de entrada
│   ├── TuCajero.spec           # Config PyInstaller
│   │
│   ├── ui/                     # Interfaces gráficas
│   │   ├── main_window.py      # Ventana principal
│   │   ├── ventas_view.py      # POS (ventas)
│   │   ├── productos_view.py   # Productos + inventario
│   │   ├── dashboard_view.py   # Dashboard con gráficos
│   │   ├── escritorio_view.py  # Vista simple
│   │   ├── corte_view.py       # Corte de caja
│   │   ├── clientes_view.py    # Clientes
│   │   ├── proveedores_view.py # Proveedores
│   │   ├── cotizaciones_view.py# Cotizaciones
│   │   ├── historial_view.py   # Historial
│   │   ├── cajeros_view.py     # Cajeros
│   │   ├── login_cajero.py     # Login
│   │   ├── buscador_productos.py
│   │   ├── selector_cliente.py
│   │   ├── descuento_dialog.py
│   │   ├── activate_view.py    # Licencias
│   │   ├── setup_view.py       # Setup inicial
│   │   ├── config_view.py      # Configuración
│   │   └── about_view.py       # Acerca de
│   │
│   ├── models/                 # Modelos DB
│   │   ├── producto.py         # Producto, Venta, Categoria
│   │   ├── cliente.py          # Cliente
│   │   ├── cajero.py           # Cajero
│   │   ├── cotizacion.py       # Cotizacion
│   │   └── proveedor.py        # Proveedor, OrdenCompra
│   │
│   ├── services/               # Lógica de negocio
│   │   ├── producto_service.py
│   │   ├── venta_service.py
│   │   ├── cliente_service.py
│   │   ├── cajero_service.py
│   │   ├── corte_service.py
│   │   ├── cotizacion_service.py
│   │   ├── proveedor_service.py
│   │   ├── categoria_service.py
│   │   ├── historial_service.py
│   │   └── fraccion_service.py
│   │
│   ├── repositories/           # Acceso a datos
│   │   ├── producto_repo.py
│   │   ├── venta_repo.py
│   │   ├── cliente_repo.py
│   │   └── inventario_repo.py
│   │
│   ├── config/                 # Configuración
│   │   ├── database.py         # DB SQLite
│   │   └── app_config.py       # Constantes
│   │
│   ├── security/               # Seguridad
│   │   └── license_manager.py  # Licencias
│   │
│   └── utils/                  # Utilidades
│       ├── ticket.py           # Tickets
│       ├── store_config.py     # Config tienda
│       ├── backup.py           # Backups
│       ├── logging_config.py   # Logs
│       ├── formato.py          # Formato moneda
│       ├── theme.py            # Temas UI
│       ├── impresora.py        # Impresión
│       ├── excel_exporter.py   # Excel
│       └── factura_diaria.py   # PDF facturas
│
├── dist/                       # Ejecutable
├── build/                      # Build temporal
├── requirements.txt            # Dependencias
├── build_exe.bat              # Script build
└── run.bat                     # Ejecutar
```

---

## 🔧 Correcciones Implementadas

### 26 de Marzo 2026

| # | Problema | Solución | Estado |
|---|----------|----------|--------|
| 1 | `Index is not defined` | Agregar imports en modelos | ✅ |
| 2 | Gráficos no disponibles | Reemplazar matplotlib con Qt | ✅ |
| 3 | Tabla sin productos | Agregar columna detalle | ✅ |
| 4 | Stock negativo | Validación en repo/service | ✅ |
| 5 | Fechas en pasado | Bloqueo en UI y service | ✅ |
| 6 | Descuentos ilimitados | Límite 50% en dialog | ✅ |
| 7 | Carrito se perdía | Persistencia JSON | ✅ |
| 8 | DB lenta | 14 índices nuevos | ✅ |
| 9 | Comprobante no validado | Input en pagos electrónicos | ✅ |
| 10 | Corte sin validación | Diferencias en corte_view | ✅ |

---

## 📈 Métricas del Sistema

### Rendimiento
- **Inicio:** < 3 segundos
- **Venta:** < 1 segundo
- **Dashboard refresh:** 30 segundos (auto)
- **Backup:** ~5 segundos

### Base de Datos
- **Tablas:** 12
- **Índices:** 16
- **Reglas típicas:** 1,000-10,000 ventas
- **Tamaño DB:** 10-100 MB

### Usuario
- **Cajeros simultáneos:** 1 (monousuario)
- **Productos soportados:** Ilimitados
- **Ventas por día:** 100-500

---

## 🔐 Seguridad

### Implementado
- ✅ Hash SHA256 para PINs de cajeros
- ✅ Licencias por machine ID
- ✅ Logs de auditoría
- ✅ Validación de permisos por rol
- ✅ Backup automático

### En Progreso
- 🔄 Autenticación de dos factores
- 🔄 Encriptación de base de datos
- 🔄 Exportación de logs remota

---

## 📚 Documentación

| Documento | Propósito | Ubicación |
|-----------|-----------|-----------|
| `README.md` | Información general | Root |
| `MAPA_PROYECTO.md` | Estructura detallada | Root |
| `CAMBIOS_2026-03-25.md` | Cambios 25 Mar | Root |
| `CAMBIOS_2026-03-26.md` | Cambios 26 Mar | Root |
| `CODIGO_COMPLETO.md` | Código completo | Root |
| `database/README.md` | Info base de datos | tucajero/database |

---

## 🚀 Comandos Útiles

### Ejecutar en desarrollo
```bash
cd TuCajeroPOS
venv\Scripts\python.exe tucajero\main.py
```

### Compilar
```bash
rmdir /s /q build dist
pyinstaller --noconfirm TuCajero.spec
```

### Ejecutar EXE
```bash
dist\TuCajero.exe
```

### Ver logs
```bash
type %LOCALAPPDATA%\TuCajero\logs\app.log
```

### Limpiar caché
```bash
del /s /q tucajero\**\__pycache__
del /s /q tucajero\**\*.pyc
```

---

## 📞 Soporte

**Desarrollador:** Francisco Collinas  
**Email:** [Contacto en configuración]  
**Documentación:** Archivos .md en root del proyecto

---

## 📝 Licencia

Este proyecto es **propietario**. Todos los derechos reservados.

---

*Documento generado el 26 de Marzo 2026*  
*Próxima revisión: 1 de Abril 2026*
