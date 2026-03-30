# TuCajero - Base de Datos

## Desarrollo (local)
- Ubicación: `tucajero/database/pos.db`
- SQLite con WAL mode

## Producción (Windows)
- Ubicación: `%LOCALAPPDATA%\TuCajero\database\pos.db`
- Ubicación logs: `%LOCALAPPDATA%\TuCajero\logs\`
- Ubicación backups: `%LOCALAPPDATA%\TuCajero\database\backups\`

## Tablas principales
- producto, categoria, venta, venta_item, cliente, cajero, corte_caja, cotizacion, cotizacion_item, proveedor, orden_compra

## Notas
- WAL mode activo para mejor concurrencia
- Retry automático para "database is locked"
