# TuCajero POS - Documentación Completa del Proyecto

## Descripción General del Proyecto

**TuCajero** es un sistema de Punto de Venta (POS) completo desarrollado en Python con PySide6 para pequeños negocios como farmacias, tiendas y minimarkets. El sistema permite gestionar ventas, productos, inventario, clientes, proveedores, cotizaciones y cortes de caja.

### Tecnología Principal
- **Python 3.14** - Lenguaje de programación
- **PySide6** - Framework de interfaz gráfica (Qt)
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos embebida
- **ReportLab** - Generación de documentos PDF

---

## Estructura del Proyecto

```
TuCajeroPOS/
├── tucajero/
│   ├── main.py                    # Punto de entrada de la aplicación
│   ├── config/
│   │   ├── database.py            # Configuración de base de datos SQLAlchemy
│   │   └── app_config.py          # Configuración de la aplicación
│   ├── models/
│   │   ├── producto.py            # Modelos: Producto, Venta, VentaItem, Categoria
│   │   ├── cliente.py            # Modelo de Cliente
│   │   ├── cajero.py              # Modelo de Cajero
│   │   ├── cotizacion.py          # Modelo de Cotización
│   │   └── proveedor.py          # Modelo de Proveedor y Orden de Compra
│   ├── repositories/
│   │   ├── producto_repo.py       # Repositorio de Productos
│   │   ├── venta_repo.py          # Repositorio de Ventas e Inventario
│   │   └── cliente_repo.py        # Repositorio de Clientes
│   ├── services/
│   │   ├── producto_service.py   # Lógica de negocio de productos
│   │   ├── cliente_service.py     # Lógica de clientes
│   │   ├── proveedor_service.py   # Lógica de proveedores
│   │   ├── cotizacion_service.py # Lógica de cotizaciones
│   │   ├── cajero_service.py      # Lógica de cajeros
│   │   ├── corte_service.py       # Lógica de corte de caja
│   │   ├── fraccion_service.py    # Lógica de fraccionamiento
│   │   └── categoria_service.py   # Lógica de categorías
│   ├── ui/
│   │   ├── main_window.py         # Ventana principal
│   │   ├── ventas_view.py         # Vista de ventas POS
│   │   ├── productos_view.py     # CRUD de productos
│   │   ├── dashboard_view.py      # Dashboard con métricas
│   │   ├── clientes_view.py       # Gestión de clientes
│   │   ├── proveedores_view.py    # Gestión de proveedores
│   │   ├── cotizaciones_view.py   # Gestión de cotizaciones
│   │   ├── historial_view.py      # Historial de ventas
│   │   ├── corte_view.py          # Corte de caja
│   │   ├── login_cajero.py        # Login de cajero
│   │   ├── activate_view.py       # Activación de licencias
│   │   ├── setup_view.py          # Configuración inicial
│   │   └── chart_widget.py        # Widget de gráficos
│   ├── utils/
│   │   ├── theme.py               # Temas y estilos de la UI
│   │   ├── formato.py             # Formato de moneda y fechas
│   │   ├── ticket.py              # Generación de tickets
│   │   ├── backup.py              # Respaldo de base de datos
│   │   ├── store_config.py        # Configuración de la tienda
│   │   └── importador.py         # Importación de productos
│   └── security/
│       └── license_manager.py     # Sistema de licencias
```

---

## Modelos de Datos (SQLAlchemy)

### producto.py - Modelos Principales

**Categoria:**
```python
class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(200), default="")
    color = Column(String(7), default="#3498db")
    productos = relationship("Producto", back_populates="categoria")
```

**Producto:**
```python
class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    costo = Column(Float, default=0)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    aplica_iva = Column(Boolean, default=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    unidades_por_empaque = Column(Integer, nullable=True)
    producto_fraccion_id = Column(Integer, ForeignKey("productos.id"), nullable=True)
    es_fraccion = Column(Boolean, default=False)
    stock_minimo = Column(Integer, default=0, nullable=True)
    fecha_vencimiento = Column(DateTime, nullable=True)
    
    producto_fraccion = relationship("Producto", foreign_keys=[producto_fraccion_id], uselist=False)
    categoria = relationship("Categoria", back_populates="productos")
    venta_items = relationship("VentaItem", back_populates="producto")
    movimientos = relationship("MovimientoInventario", back_populates="producto")
```

**Venta:**
```python
class Venta(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)
    anulada = Column(Boolean, default=False)
    metodo_pago = Column(String(50), nullable=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    es_credito = Column(Boolean, default=False)
    descuento_tipo = Column(String(20), nullable=True)
    descuento_valor = Column(Float, default=0)
    descuento_total = Column(Float, default=0)
    cajero_id = Column(Integer, ForeignKey("cajeros.id"), nullable=True)
    items = relationship("VentaItem", back_populates="venta", cascade="all, delete-orphan")
```

**VentaItem:**
```python
class VentaItem(Base):
    __tablename__ = "venta_items"
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    iva_monto = Column(Float, default=0)
    venta = relationship("Venta", back_populates="items")
    producto = relationship("Producto", back_populates="venta_items")
```

**MovimientoInventario:**
```python
class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String(10), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.now)
```

### cliente.py
```python
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), default="")
    email = Column(String(100), default="")
    direccion = Column(String(200), default="")
    nit = Column(String(20), default="")
    fecha_registro = Column(DateTime, default=datetime.now)
    activo = Column(Boolean, default=True)
```

### cajero.py
```python
class Cajero(Base):
    __tablename__ = "cajeros"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    pin = Column(String(4), nullable=False)
    es_admin = Column(Boolean, default=False)
    activo = Column(Boolean, default=True)
    ultimo_login = Column(DateTime, nullable=True)
```

### cotizacion.py
```python
class Cotizacion(Base):
    __tablename__ = "cotizaciones"
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.now)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    total = Column(Float, nullable=False)
    estado = Column(String(20), default="pendiente")
    notas = Column(String(500), default="")
    items = relationship("CotizacionItem", back_populates="cotizacion")

class CotizacionItem(Base):
    __tablename__ = "cotizacion_items"
    id = Column(Integer, primary_key=True)
    cotizacion_id = Column(Integer, ForeignKey("cotizaciones.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    iva_monto = Column(Float, default=0)
```

### proveedor.py
```python
class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), default="")
    email = Column(String(100), default="")
    direccion = Column(String(200), default="")
    nit = Column(String(20), default="")
    activo = Column(Boolean, default=True)

class OrdenCompra(Base):
    __tablename__ = "ordenes_compra"
    id = Column(Integer, primary_key=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    fecha = Column(DateTime, default=datetime.now)
    total = Column(Float, default=0)
    estado = Column(String(20), default="pendiente")
    notas = Column(String(500), default="")
    proveedor = relationship("Proveedor")
    items = relationship("OrdenCompraItem", back_populates="orden")

class OrdenCompraItem(Base):
    __tablename__ = "orden_compra_items"
    id = Column(Integer, primary_key=True)
    orden_id = Column(Integer, ForeignKey("ordenes_compra.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    precio_compra = Column(Float, nullable=False)
```

---

## Base de Datos (database.py)

```python
Base = declarative_base()
_engine = None

def get_data_dir():
    """Retorna directorio de datos"""
    if sys.platform == "win32":
        return os.path.join(os.environ.get("LOCALAPPDATA", os.environ["APPDATA"]), "TuCajero")
    else:
        return os.path.join(os.path.expanduser("~"), ".tucajero")

def get_db_path():
    """Ruta de la base de datos"""
    return os.path.join(get_data_dir(), "database", "pos.db")

def get_engine():
    """Crea el engine de SQLite con WAL mode"""
    global _engine
    if _engine is None:
        db_path = get_db_path()
        _engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False, "timeout": 30},
            pool_pre_ping=True,
        )
        # PRAGMAS
        with _engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA foreign_keys=ON"))
            conn.commit()
    return _engine

def get_session():
    """Crea sesión de base de datos"""
    engine = get_engine()
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return Session()

def init_db():
    """Inicializa la base de datos"""
    crear_carpetas()
    Base.metadata.create_all(engine)
    agregar_columnas_si_existen(engine)

def agregar_columnas_si_existen(engine):
    """Migration de columnas nuevas"""
    columnas = [
        ("productos", "unidades_por_empaque", "INTEGER"),
        ("productos", "producto_fraccion_id", "INTEGER"),
        ("productos", "es_fraccion", "BOOLEAN DEFAULT 0"),
        ("productos", "stock_minimo", "INTEGER DEFAULT 0"),
        ("ventas", "cliente_id", "INTEGER"),
        ("ventas", "es_credito", "INTEGER DEFAULT 0"),
        ("ventas", "descuento_tipo", "VARCHAR(20)"),
        ("ventas", "descuento_valor", "FLOAT DEFAULT 0"),
        ("ventas", "descuento_total", "FLOAT DEFAULT 0"),
        ("ventas", "cajero_id", "INTEGER"),
        ("cortes_caja", "cajero_id", "INTEGER"),
        ("productos", "fecha_vencimiento", "DATETIME"),
    ]
```

---

## Servicios de Lógica de Negocio

### producto_service.py

```python
class ProductoService:
    def __init__(self, session):
        self.session = session
        self.repo = ProductoRepository(session)

    def get_all_productos(self):
        return self.repo.get_all()

    def get_producto_by_id(self, producto_id):
        return self.repo.get_by_id(producto_id)

    def get_producto_by_codigo(self, codigo):
        return self.repo.get_by_codigo(codigo)

    def create_producto(self, codigo, nombre, precio, costo=0, stock=0,
                        aplica_iva=True, categoria_id=None, stock_minimo=0, fecha_vencimiento=None):
        self.validar_codigo(codigo)
        return self.repo.create(...)

    def update_producto(self, producto_id, **kwargs):
        return self.repo.update(producto_id, **kwargs)

    def delete_producto(self, producto_id):
        return self.repo.delete(producto_id)

    def get_productos_stock_bajo(self):
        return [p for p in self.repo.get_all() if p.stock_minimo and p.stock_minimo > 0 and p.stock <= p.stock_minimo]

    def get_productos_stock_critico(self):
        return [p for p in self.repo.get_all() if p.stock <= 0]

    def get_productos_proximos_vencimiento(self, dias=30):
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() + timedelta(days=dias)
        return [p for p in self.repo.get_all() if p.fecha_vencimiento and p.fecha_vencimiento <= fecha_limite]

class CategoriaService:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Categoria).order_by(Categoria.nombre).all()

    def create(self, nombre, descripcion=""):
        # Crear categoría
        pass

    def delete(self, categoria_id):
        # Eliminar categoría
        pass
```

---

## Repositorios

### producto_repo.py

```python
class ProductoRepository:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Producto).filter(Producto.activo == True).all()

    def get_by_id(self, producto_id):
        return self.session.query(Producto).filter(Producto.id == producto_id).first()

    def get_by_codigo(self, codigo):
        return self.session.query(Producto).filter(
            and_(Producto.codigo == codigo, Producto.activo == True)
        ).first()

    def create(self, codigo, nombre, precio, costo=0, stock=0, aplica_iva=True,
               categoria_id=None, stock_minimo=0, fecha_vencimiento=None):
        producto = Producto(...)
        self.session.add(producto)
        self.session.commit()
        return producto

    def update(self, producto_id, **kwargs):
        producto = self.get_by_id(producto_id)
        if producto:
            for key, value in kwargs.items():
                if key == "categoria_id" and value is None:
                    setattr(producto, key, None)
                elif value is not None:
                    setattr(producto, key, value)
            self.session.commit()
        return producto

    def delete(self, producto_id):
        producto = self.get_by_id(producto_id)
        if producto:
            producto.activo = False
            self.session.commit()
        return producto
```

---

## Interfaz de Usuario

### main.py - Punto de Entrada

```python
def main():
    crear_carpetas()
    configurar_logging()
    load_store_config()
    backup_semanal()
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(get_stylesheet())
    app.setWindowIcon(QIcon(ICON_PATH))
    
    # Validar licencia
    while not validar_licencia():
        dialog = ActivationDialog()
        dialog.exec()
        if not dialog.activation_success:
            sys.exit(0)
    
    # Setup inicial
    if not is_setup_complete():
        setup = SetupDialog()
        setup.exec()
    
    init_db()
    session = get_session()
    
    # Login cajero
    login = LoginCajeroDialog(session)
    result = login.exec()
    if result != QDialog.DialogCode.Accepted:
        sys.exit(0)
    cajero_activo = login.cajero_seleccionado
    
    # Abrir caja
    service = CorteCajaService(session)
    service.abrir_caja()
    
    # Crear ventana y vistas
    window = MainWindow()
    window.session = session
    
    dashboard_view = DashboardView(session)
    window.add_view(dashboard_view, "dashboard")
    
    ventas_view = VentasView(session, cajero_activo=cajero_activo)
    window.add_view(ventas_view, "ventas")
    ventas_view.sale_completed.connect(dashboard_view.refresh)
    
    window.set_cajero_activo(cajero_activo)
    window.switch_view_by_name("dashboard")
    window.switch_to_ventas()
    window.show()
    
    sys.exit(app.exec())
```

### theme.py - Estilos

```python
def get_colors():
    return {
        "bg_app": "#0f172a",
        "bg_sidebar": "#1e293b",
        "bg_card": "#334155",
        "bg_input": "#475569",
        "accent": "#3b82f6",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "info": "#06b6d4",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "text_muted": "#64748b",
        "border": "#475569",
    }

def btn_primary():
    return """
        QPushButton {
            background-color: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #2563eb; }
    """

def btn_secondary():
    return """
        QPushButton {
            background-color: #475569;
            color: #f8fafc;
            border: 1px solid #64748b;
            border-radius: 6px;
            padding: 8px 16px;
        }
        QPushButton:hover { background-color: #64748b; }
    """

def btn_danger():
    return """
        QPushButton {
            background-color: #ef4444;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }
        QPushButton:hover { background-color: #dc2626; }
    """
```

### ventas_view.py - Vista de Ventas POS

Estructura principal:
- Campo de búsqueda por código
- Carrito de compras (tabla)
- Panel de totales
- Panel de métodos de pago

Carrito:
```python
self.carrito = []  # [{"producto": prod, "cantidad": n, "precio": p, "iva": i, "subtotal": s}]

def agregar_al_carrito(producto, cantidad=1):
    for item in self.carrito:
        if item["producto"].id == producto.id:
            item["cantidad"] += cantidad
            return
    precio = producto.precio
    iva = producto.precio * 0.19 if producto.aplica_iva else 0
    self.carrito.append({
        "producto": producto,
        "cantidad": cantidad,
        "precio": precio,
        "iva": iva,
        "subtotal": (precio + iva) * cantidad
    })
```

### productos_view.py - Gestión de Productos

Diálogo de producto incluye:
- Código, Nombre, Precio, Costo, Stock, Stock mínimo
- Checkbox IVA (19%)
- **Fecha de vencimiento** (QDateEdit) - campo agregado recientemente
- Fraccionamiento (unidades por empaque)
- Categoría

### dashboard_view.py - Dashboard

Muestra:
- Ventas del día/semana
- Productos con stock bajo
- **Productos próximos a vencer** (nuevo)
- Gráficos de ventas (matplotlib)
- Tabla de últimas facturas del día

---

## Sistema de Licencias

```python
def get_machine_id():
    """Genera ID único basado en hardware"""
    # Obtiene información de red, placa base, CPU
    return hash(...)

def validar_licencia():
    """Valida licencia contra archivo license.dat"""
    license_data = obtener_licencia_archiva()
    if not license_data:
        return False
    machine_id = get_machine_id()
    return license_data.get("machine_id") == machine_id

def activar_licencia(clave):
    """Activa con clave proporcionada"""
    # Valida clave y guarda license.dat
```

---

## Rutas de Archivos

| Ubicación | Descripción |
|-----------|-------------|
| `%LOCALAPPDATA%\TuCajero\database\pos.db` | Base de datos SQLite |
| `%LOCALAPPDATA%\TuCajero\database\backups\` | Backups automáticos |
| `%LOCALAPPDATA%\TuCajero\logs\app.log` | Logs |
| `%LOCALAPPDATA%\TuCajero\store_config.json` | Config de tienda |
| `%LOCALAPPDATA%\TuCajero\license.dat` | Archivo de licencia |

---

## Características Principales

1. **Ventas POS** - Interfaz con código de barras
2. **Gestión de Productos** - CRUD, categorías, fraccionamiento
3. **Inventario** - Entradas, salidas, desempacar, alertas stock
4. **Dashboard** - Métricas y gráficos
5. **Corte de Caja** - Apertura/cierre con estadísticas
6. **Sistema de Licencias** - Activación por máquina
7. **Tickets PDF** - Generación con ReportLab
8. **Backup Automático** - Respaldo al cerrar
9. **Múltiples Métodos de Pago** - Efectivo, Nequi, Daviplata
10. **Clientes y Proveedores** - Gestión completa
11. **Cotizaciones** - Crear y convertir en ventas
12. **Historial** - Búsqueda, filtros, exportar Excel
13. **Importar Productos** - Desde Excel/CSV
14. **Fecha de Vencimiento** - Alertas de productos próximos a vencer

---

## Errores Recientes Corregidos

1. **Errores theme key**: `cotizaciones_view.py` y `proveedores_view.py` - corregidos keys inexistentes (`primary`, `secondary_text`)
2. **Fecha de vencimiento**: Agregado en `productos_view.py` con `QDateEdit` y método `get_productos_proximos_vencimiento()` en servicio
3. **Colores sidebar**: Restaurados estilos originales con `btn_secondary()`
4. **Botones cantidad**: Restaurados a tamaño 24x24

---

## Notas para IA

- SQLAlchemy 2.0 con declaraciones de columnas individuales
- Relaciones con back_populates para bidireccionalidad
- Sesión con autoflush=False, autocommit=False
- PySide6 estilo "Fusion" con hoja de estilos personalizada
- Errores LSP locales no afectan ejecución real
- Manejo de errores globales con sys.excepthook
- El proyecto usa Widgets de Qt con Signal/Slot

---

*Documento generado: 25 de marzo de 2026*