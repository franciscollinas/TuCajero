# TuCajero - Código Completo del Proyecto

> **Versión:** 1.0  
> **Framework:** PySide6 + SQLAlchemy + SQLite  
> **Última actualización:** 2026-03-18  

---

## Tabla de Contenidos

1. [## 1. main.py — Punto de Entrada](###-1-mainpy)
2. [## 2. config/database.py — Base de Datos](###-2-config/databasepy)
3. [## 3. config/app_config.py](###-3-config/app_configpy)
4. [## 4. models/producto.py — Modelos](###-4-models/productopy)
5. [## 5. utils/store_config.py — Configuración de Tienda](###-5-utils/store_configpy)
6. [## 6. repositories/producto_repo.py](###-6-repositories/producto_repopy)
7. [## 7. repositories/venta_repo.py](###-7-repositories/venta_repopy)
8. [## 8. services/producto_service.py](###-8-services/producto_servicepy)
9. [## 9. services/corte_service.py](###-9-services/corte_servicepy)
10. [## 10. services/historial_service.py](###-10-services/historial_servicepy)
11. [## 11. services/categoria_service.py](###-11-services/categoria_servicepy)
12. [## 12. security/license_manager.py](###-12-security/license_managerpy)
13. [## 13. ui/main_window.py — Ventana Principal](###-13-ui/main_windowpy)
14. [## 14. ui/setup_view.py — Configuración Inicial](###-14-ui/setup_viewpy)
15. [## 15. ui/ventas_view.py — Ventas](###-15-ui/ventas_viewpy)
16. [## 16. ui/productos_view.py — Productos](###-16-ui/productos_viewpy)
17. [## 17. ui/corte_view.py — Corte de Caja](###-17-ui/corte_viewpy)
18. [## 18. ui/historial_view.py — Historial](###-18-ui/historial_viewpy)
19. [## 19. ui/inventario_view.py — Inventario](###-19-ui/inventario_viewpy)
20. [## 20. ui/buscador_productos.py](###-20-ui/buscador_productospy)
21. [## 21. ui/activate_view.py](###-21-ui/activate_viewpy)
22. [## 22. ui/about_view.py](###-22-ui/about_viewpy)
23. [## 23. ui/config_view.py](###-23-ui/config_viewpy)
24. [## 24. utils/ticket.py](###-24-utils/ticketpy)
25. [## 25. utils/factura_diaria.py](###-25-utils/factura_diariapy)
26. [## 26. utils/backup.py](###-26-utils/backuppy)
27. [## 27. utils/excel_exporter.py](###-27-utils/excel_exporterpy)
28. [## 28. tools/license_generator.py](###-28-tools/license_generatorpy)
29. [## 29. verificar_iva.py](###-29-verificar_ivapy)
30. [## 30. migrar_iva.py](###-30-migrar_ivapy)

---

## 1. main.py — Punto de Entrada

```python
"""
TuCajero
Sistema simple de caja registradora para pequeños negocios.
"""

import sys
import logging
import os
from logging.handlers import RotatingFileHandler
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
from config.database import init_db, get_session, crear_carpetas
from services.corte_service import CorteCajaService
from ui.main_window import MainWindow
from ui.ventas_view import VentasView
from ui.productos_view import ProductosView
from ui.inventario_view import InventarioView
from ui.corte_view import CorteView
from ui.historial_view import HistorialView
from ui.activate_view import ActivationDialog
from security.license_manager import validar_licencia, crear_license_default
from utils.store_config import load_store_config, is_setup_complete
from ui.setup_view import SetupDialog


def configurar_logging():
    """Configura el logging global con rotación"""
    from config.database import get_log_file, crear_carpetas

    crear_carpetas()
    log_file = get_log_file()

    handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=3)

    logging.basicConfig(
        handlers=[handler],
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )


def mostrar_activacion():
    """Muestra la ventana de activación"""
    dialog = ActivationDialog()
    return dialog.exec() == QDialog.DialogCode.Accepted and dialog.activation_success


def main():
    """Función principal de la aplicación"""
    crear_carpetas()
    configurar_logging()
    load_store_config()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ICON_PATH = os.path.join(BASE_DIR, "assets", "icons", "logo.png")

    print(f"[INFO] Icono cargado desde: {ICON_PATH}")
    print(f"[INFO] Archivo existe: {os.path.exists(ICON_PATH)}")

    try:
        crear_license_default()
    except Exception as e:
        logging.error(f"Error al crear licencia: {e}")

    if not validar_licencia():
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setWindowIcon(QIcon(ICON_PATH))

        while True:
            result = mostrar_activacion()
            if not result:
                QMessageBox.critical(
                    None,
                    "Sistema Bloqueado",
                    "El sistema requiere activación para funcionar.\n\nEl programa se cerrará.",
                )
                sys.exit(1)
            elif validar_licencia():
                break
    else:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setWindowIcon(QIcon(ICON_PATH))

    if not is_setup_complete():
        setup = SetupDialog()
        if setup.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)
        load_store_config()

    try:
        init_db()
    except Exception as e:
        logging.error(f"Error al inicializar base de datos: {e}")
        QMessageBox.critical(
            None, "Error", f"Error al inicializar la base de datos:\n{str(e)}"
        )
        sys.exit(1)

    session = get_session()

    try:
        service = CorteCajaService(session)
        service.abrir_caja()
    except Exception as e:
        logging.error(f"Error al abrir caja: {e}")

    window = MainWindow()
    window.setWindowIcon(QIcon(ICON_PATH))

    try:
        ventas_view = VentasView(session)
        productos_view = ProductosView(session)
        inventario_view = InventarioView(session)
        corte_view = CorteView(session)
        historial_view = HistorialView(session)

        ventas_view.sale_completed.connect(productos_view.recargar_productos)
        ventas_view.sale_completed.connect(inventario_view.recargar_inventario)
        ventas_view.sale_completed.connect(corte_view.cargar_estadisticas)

        window.add_view(ventas_view, "ventas")
        window.add_view(productos_view, "productos")
        window.add_view(inventario_view, "inventario")
        window.add_view(corte_view, "corte")
        window.add_view(historial_view, "historial")

        try:
            from ui.setup_view import SetupView

            config_view = SetupView(session, parent=window)
            window.add_view(config_view, "config")
        except Exception as e:
            logging.error(f"Error al crear vista de config: {e}")

    except Exception as e:
        logging.error(f"Error al crear vistas: {e}")
        QMessageBox.critical(None, "Error", f"Error al cargar las vistas:\n{str(e)}")
        sys.exit(1)

    window.switch_to_ventas()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Error crítico no manejado: {e}")
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox

            app = QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Error crítico",
                f"Ha ocurrido un error inesperado:\n\n{str(e)}\n\nRevise logs/app.log",
            )
        except:
            print(f"Error crítico: {e}")
        sys.exit(1)

```

---

## 2. config/database.py — Base de Datos

```python
import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
_engine = None


def get_data_dir():
    """Returns the data directory for the application.

    Uses %LOCALAPPDATA%/TuCajero for Windows.
    Falls back to user home directory for other platforms.
    """
    if sys.platform == "win32":
        return os.path.join(
            os.environ.get("LOCALAPPDATA", os.environ["APPDATA"]), "TuCajero"
        )
    else:
        return os.path.join(os.path.expanduser("~"), ".tucajero")


def get_base_dir():
    """Returns the base directory of the application"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def crear_carpetas():
    """Creates necessary folders if they don't exist"""
    data_dir = get_data_dir()

    db_dir = os.path.join(data_dir, "database")
    os.makedirs(db_dir, exist_ok=True)

    backups_dir = os.path.join(db_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)

    logs_dir = os.path.join(data_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)


def get_db_path():
    """Returns the database path - always uses %LOCALAPPDATA%"""
    data_dir = get_data_dir()
    db_dir = os.path.join(data_dir, "database")
    return os.path.join(db_dir, "pos.db")


def get_logs_dir():
    """Returns the logs directory"""
    data_dir = get_data_dir()
    return os.path.join(data_dir, "logs")


def get_log_file():
    """Returns the full path to the log file"""
    return os.path.join(get_logs_dir(), "app.log")


def get_engine():
    """Creates and returns the database engine with production config"""
    global _engine
    if _engine is None:
        db_path = get_db_path()
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        _engine = create_engine(
            f"sqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )

        with _engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA foreign_keys=ON"))

    return _engine


def get_session():
    """Creates and returns a database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initializes the database creating all tables"""
    crear_carpetas()

    from models.producto import Producto

    engine = get_engine()
    Base.metadata.create_all(engine)


def close_db():
    """Cierra la base de datos correctamente con WAL checkpoint"""
    global _engine
    try:
        if _engine:
            with _engine.connect() as conn:
                conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
    except Exception as e:
        logging.error(f"WAL checkpoint error: {e}")
    finally:
        try:
            if _engine:
                _engine.dispose()
                _engine = None
        except Exception as e:
            logging.error(f"Engine dispose error: {e}")

```

---

## 3. config/app_config.py

```python
APP_NAME = "TuCajero"
VERSION = "1.0"
AUTHOR = "TuCajero"

```

---

## 4. models/producto.py — Modelos

```python
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from config.database import Base
from datetime import datetime


class Categoria(Base):
    """Modelo de Categoría de producto"""

    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(200), default="")
    color = Column(String(7), default="#3498db")

    productos = relationship("Producto", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria {self.nombre}>"


class Producto(Base):
    """Modelo de Producto"""

    __tablename__ = "productos"
    __table_args__ = (
        Index("idx_producto_codigo", "codigo"),
        Index("idx_producto_nombre", "nombre"),
    )

    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
    costo = Column(Float, default=0)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    aplica_iva = Column(Boolean, default=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)

    venta_items = relationship("VentaItem", back_populates="producto")
    movimientos = relationship("MovimientoInventario", back_populates="producto")
    categoria = relationship("Categoria", back_populates="productos")

    def __repr__(self):
        return f"<Producto {self.nombre}>"


class Venta(Base):
    """Modelo de Venta"""

    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.now)
    total = Column(Float, nullable=False)
    anulada = Column(Boolean, default=False)
    metodo_pago = Column(String(50), nullable=True)

    items = relationship(
        "VentaItem", back_populates="venta", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Venta {self.id} - {self.total}>"


class VentaItem(Base):
    """Modelo de Item de Venta"""

    __tablename__ = "venta_items"

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    iva_monto = Column(Float, default=0)

    venta = relationship("Venta", back_populates="items")
    producto = relationship("Producto", back_populates="venta_items")

    @property
    def subtotal(self):
        return self.cantidad * self.precio

    def __repr__(self):
        return f"<VentaItem {self.producto_id} x {self.cantidad}>"


class MovimientoInventario(Base):
    """Modelo de Movimiento de Inventario"""

    __tablename__ = "movimientos_inventario"

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String(10), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    producto = relationship("Producto", back_populates="movimientos")

    def __repr__(self):
        return f"<Movimiento {self.tipo} - {self.cantidad}>"


class CorteCaja(Base):
    """Modelo de Corte de Caja"""

    __tablename__ = "cortes_caja"

    id = Column(Integer, primary_key=True)
    fecha_apertura = Column(DateTime, default=datetime.now)
    fecha_cierre = Column(DateTime, nullable=True)
    total_ventas = Column(Float, default=0)
    numero_ventas = Column(Integer, default=0)
    total_gastos = Column(Float, default=0)
    ganancia_neta = Column(Float, default=0)

    gastos = relationship("GastoCaja", backref="corte", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CorteCaja {self.id}>"


class GastoCaja(Base):
    """Modelo de Gasto de Caja"""

    __tablename__ = "gastos_caja"

    id = Column(Integer, primary_key=True)
    corte_id = Column(Integer, ForeignKey("cortes_caja.id"), nullable=False)
    concepto = Column(String(200), nullable=False)
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<GastoCaja {self.concepto} - {self.monto}>"

```

---

## 5. utils/store_config.py — Configuración de Tienda

```python
import json
import os
import sys

DEFAULT_CONFIG = {
    "store_name": "",
    "logo_path": "",
    "address": "",
    "phone": "",
    "email": "",
    "nit": "",
    "setup_complete": False,
}

_store_config = None


def get_config_dir():
    """Retorna el directorio de configuración en %LOCALAPPDATA%"""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        return os.path.join(base, "TuCajero", "config")
    return os.path.join(os.path.expanduser("~"), ".tucajero", "config")


def _get_config_path():
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "store_config.json")


def config_exists():
    """Retorna True si ya existe configuración guardada"""
    path = _get_config_path()
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return bool(data.get("store_name", "").strip())
    except Exception:
        return False


def load_store_config():
    global _store_config
    config_path = _get_config_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                _store_config = json.load(f)
        else:
            _store_config = DEFAULT_CONFIG.copy()
    except (json.JSONDecodeError, IOError):
        _store_config = DEFAULT_CONFIG.copy()
    return _store_config


def save_store_config(config_data):
    config_path = _get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        global _store_config
        _store_config = config_data
        return True
    except IOError:
        return False


def get_store_name():
    if _store_config is None:
        load_store_config()
    return _store_config.get("store_name", "")


def _get_default_logo():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo = os.path.join(base, "assets", "icons", "logo.png")
    if os.path.exists(logo):
        return logo
    return ""


def get_logo_path():
    if _store_config is None:
        load_store_config()
    logo = _store_config.get("logo_path", "")
    if logo and os.path.exists(logo):
        return logo
    return _get_default_logo()


def get_address():
    if _store_config is None:
        load_store_config()
    return _store_config.get("address", "")


def get_phone():
    if _store_config is None:
        load_store_config()
    return _store_config.get("phone", "")


def get_email():
    if _store_config is None:
        load_store_config()
    return _store_config.get("email", "")


def get_nit():
    if _store_config is None:
        load_store_config()
    return _store_config.get("nit", "")


def is_setup_complete():
    if _store_config is None:
        load_store_config()
    return _store_config.get("setup_complete", False)

```

---

## 6. repositories/producto_repo.py

```python
from models.producto import Producto
from sqlalchemy import and_


class ProductoRepository:
    """Repositorio para acceso a datos de productos"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todos los productos activos"""
        return self.session.query(Producto).filter(Producto.activo == True).all()

    def get_by_id(self, producto_id):
        """Retorna un producto por su ID"""
        return self.session.query(Producto).filter(Producto.id == producto_id).first()

    def get_by_codigo(self, codigo):
        """Retorna un producto por su código de barras"""
        return (
            self.session.query(Producto)
            .filter(and_(Producto.codigo == codigo, Producto.activo == True))
            .first()
        )

    def existe_codigo(self, codigo, exclude_id=None):
        """Verifica si existe un código (excluyendo un ID opcional)"""
        query = self.session.query(Producto).filter(Producto.codigo == codigo)
        if exclude_id:
            query = query.filter(Producto.id != exclude_id)
        return query.filter(Producto.activo == True).first() is not None

    def create(
        self,
        codigo,
        nombre,
        precio,
        costo=0,
        stock=0,
        aplica_iva=True,
        categoria_id=None,
    ):
        """Crea un nuevo producto"""
        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            precio=precio,
            costo=costo,
            stock=stock,
            aplica_iva=aplica_iva,
            categoria_id=categoria_id,
        )
        self.session.add(producto)
        self.session.commit()
        return producto

    def update(self, producto_id, **kwargs):
        """Actualiza un producto"""
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
        """Elimina (desactiva) un producto"""
        producto = self.get_by_id(producto_id)
        if producto:
            producto.activo = False
            self.session.commit()
        return producto

    def update_stock(self, producto_id, cantidad):
        """Actualiza el stock de un producto"""
        producto = self.get_by_id(producto_id)
        if producto:
            producto.stock += cantidad
            self.session.commit()
        return producto

    def search(self, query):
        """Busca productos por código, nombre o parte del nombre"""
        search_term = f"%{query}%"
        return (
            self.session.query(Producto)
            .filter(
                and_(
                    Producto.activo == True,
                    (
                        Producto.codigo.ilike(search_term)
                        | Producto.nombre.ilike(search_term)
                    ),
                )
            )
            .all()
        )

    def search_por_nombre(self, nombre):
        """Busca productos por nombre parcial"""
        search_term = f"%{nombre}%"
        return (
            self.session.query(Producto)
            .filter(
                and_(
                    Producto.activo == True,
                    Producto.nombre.ilike(search_term),
                )
            )
            .all()
        )

```

---

## 7. repositories/venta_repo.py

```python
from models.producto import Venta, VentaItem, MovimientoInventario
from sqlalchemy import and_
from datetime import datetime, timedelta

IVA_RATE = 0.19


class VentaRepository:
    """Repositorio para acceso a datos de ventas"""

    def __init__(self, session):
        self.session = session

    def create_venta(self, items, metodo_pago=None):
        """Crea una venta con sus items (incluye IVA)"""
        total = 0
        for item in items:
            subtotal = item["cantidad"] * item["precio"]
            if item.get("aplica_iva", True):
                iva = round(subtotal * IVA_RATE, 2)
            else:
                iva = 0
            total += subtotal + iva

        venta = Venta(
            total=round(total, 2), fecha=datetime.now(), metodo_pago=metodo_pago
        )
        self.session.add(venta)
        self.session.flush()

        for item in items:
            subtotal = item["cantidad"] * item["precio"]
            if item.get("aplica_iva", True):
                iva_monto = round(subtotal * IVA_RATE, 2)
            else:
                iva_monto = 0
            venta_item = VentaItem(
                venta_id=venta.id,
                producto_id=item["producto_id"],
                cantidad=item["cantidad"],
                precio=item["precio"],
                iva_monto=iva_monto,
            )
            self.session.add(venta_item)

        self.session.commit()
        return venta

    def get_ventas_hoy(self, incluir_anuladas=False):
        """Retorna las ventas de hoy"""
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        fin_dia = datetime.combine(hoy, datetime.max.time())

        query = self.session.query(Venta).filter(
            and_(Venta.fecha >= inicio_dia, Venta.fecha <= fin_dia)
        )
        if not incluir_anuladas:
            query = query.filter(Venta.anulada == False)
        return query.all()

    def get_total_hoy(self):
        """Retorna el total de ventas de hoy"""
        ventas = self.get_ventas_hoy()
        return sum(v.total for v in ventas)

    def get_count_hoy(self):
        """Retorna el número de ventas de hoy"""
        return len(self.get_ventas_hoy())

    def get_venta_by_id(self, venta_id):
        """Retorna una venta por su ID"""
        return self.session.query(Venta).filter(Venta.id == venta_id).first()

    def anular_venta(self, venta_id):
        """Anula una venta y la marca como cancelada"""
        venta = self.get_venta_by_id(venta_id)
        if not venta:
            raise ValueError(f"Venta #{venta_id} no encontrada")
        if venta.anulada:
            raise ValueError(f"Venta #{venta_id} ya está anulada")
        venta.anulada = True
        self.session.commit()
        return venta

    def get_all(self, incluir_anuladas=False):
        """Retorna todas las ventas"""
        query = self.session.query(Venta)
        if not incluir_anuladas:
            query = query.filter(Venta.anulada == False)
        return query.order_by(Venta.fecha.desc()).all()


class InventarioRepository:
    """Repositorio para acceso a datos de inventario"""

    def __init__(self, session):
        self.session = session

    def create_movimiento(self, producto_id, tipo, cantidad):
        """Crea un movimiento de inventario"""
        movimiento = MovimientoInventario(
            producto_id=producto_id, tipo=tipo, cantidad=cantidad, fecha=datetime.now()
        )
        self.session.add(movimiento)
        self.session.commit()
        return movimiento

    def get_movimientos_producto(self, producto_id):
        """Retorna los movimientos de un producto"""
        return (
            self.session.query(MovimientoInventario)
            .filter(MovimientoInventario.producto_id == producto_id)
            .order_by(MovimientoInventario.fecha.desc())
            .all()
        )

    def get_movimientos_hoy(self):
        """Retorna los movimientos de hoy"""
        hoy = datetime.now().date()
        inicio_dia = datetime.combine(hoy, datetime.min.time())
        fin_dia = datetime.combine(hoy, datetime.max.time())

        return (
            self.session.query(MovimientoInventario)
            .filter(
                and_(
                    MovimientoInventario.fecha >= inicio_dia,
                    MovimientoInventario.fecha <= fin_dia,
                )
            )
            .all()
        )

```

---

## 8. services/producto_service.py

```python
from repositories.producto_repo import ProductoRepository
from repositories.venta_repo import VentaRepository, InventarioRepository
from models.producto import Categoria


class ProductoService:
    """Servicio para lógica de negocio de productos"""

    def __init__(self, session):
        self.session = session
        self.repo = ProductoRepository(session)

    def validar_codigo(self, codigo, exclude_id=None):
        """Valida que el código no esté repetido"""
        if self.repo.existe_codigo(codigo, exclude_id):
            raise ValueError(f"El código '{codigo}' ya está en uso")

    def get_all_productos(self):
        """Retorna todos los productos"""
        return self.repo.get_all()

    def get_producto_by_id(self, producto_id):
        """Retorna un producto por ID"""
        return self.repo.get_by_id(producto_id)

    def get_producto_by_codigo(self, codigo):
        """Retorna un producto por código"""
        return self.repo.get_by_codigo(codigo)

    def get_producto_by_nombre(self, nombre):
        """Busca productos por nombre parcial"""
        return self.repo.search_por_nombre(nombre)

    def create_producto(
        self,
        codigo,
        nombre,
        precio,
        costo=0,
        stock=0,
        aplica_iva=True,
        categoria_id=None,
    ):
        """Crea un nuevo producto"""
        self.validar_codigo(codigo)
        return self.repo.create(
            codigo, nombre, precio, costo, stock, aplica_iva, categoria_id
        )

    def update_producto(self, producto_id, **kwargs):
        """Actualiza un producto"""
        if "codigo" in kwargs:
            self.validar_codigo(kwargs["codigo"], exclude_id=producto_id)
        return self.repo.update(producto_id, **kwargs)

    def delete_producto(self, producto_id):
        """Elimina un producto"""
        return self.repo.delete(producto_id)

    def search_productos(self, query):
        """Busca productos"""
        return self.repo.search(query)


class CategoriaService:
    """Servicio para gestión de categorías"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todas las categorías ordenadas"""
        return self.session.query(Categoria).order_by(Categoria.nombre).all()

    def get_by_id(self, categoria_id):
        """Retorna una categoría por ID"""
        return (
            self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        )

    def create(self, nombre, descripcion=""):
        """Crea una nueva categoría"""
        if self.session.query(Categoria).filter(Categoria.nombre == nombre).first():
            raise ValueError(f"La categoría '{nombre}' ya existe")
        c = Categoria(nombre=nombre, descripcion=descripcion)
        self.session.add(c)
        self.session.commit()
        return c

    def update(self, categoria_id, nombre, descripcion=""):
        """Actualiza una categoría"""
        c = self.get_by_id(categoria_id)
        if not c:
            raise ValueError("Categoría no encontrada")
        if nombre != c.nombre:
            existente = (
                self.session.query(Categoria).filter(Categoria.nombre == nombre).first()
            )
            if existente:
                raise ValueError(f"La categoría '{nombre}' ya existe")
        c.nombre = nombre
        c.descripcion = descripcion
        self.session.commit()
        return c

    def delete(self, categoria_id):
        """Elimina una categoría (solo si no tiene productos)"""
        c = self.get_by_id(categoria_id)
        if not c:
            raise ValueError("Categoría no encontrada")
        if c.productos and len([p for p in c.productos if p.activo]) > 0:
            raise ValueError("No se puede eliminar: hay productos en esta categoría")
        self.session.delete(c)
        self.session.commit()


class VentaService:
    """Servicio para lógica de negocio de ventas"""

    def __init__(self, session):
        self.session = session
        self.venta_repo = VentaRepository(session)
        self.producto_repo = ProductoRepository(session)
        self.inventario_repo = InventarioRepository(session)
        from services.corte_service import CorteCajaService

        self.corte_service = CorteCajaService(session)

    def registrar_venta(self, items, metodo_pago=None):
        """Registra una venta y descuenta inventario"""
        if not self.corte_service.esta_caja_abierta():
            raise Exception(
                "No se puede registrar la venta porque la caja está cerrada."
            )

        for item in items:
            producto = self.producto_repo.get_by_id(item["producto_id"])
            if producto.stock < item["cantidad"]:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

        venta = self.venta_repo.create_venta(items, metodo_pago=metodo_pago)

        for item in items:
            self.producto_repo.update_stock(item["producto_id"], -item["cantidad"])
            self.inventario_repo.create_movimiento(
                item["producto_id"], "salida", item["cantidad"]
            )

        return venta

    def anular_venta(self, venta_id):
        """Anula una venta y restaura el stock"""
        venta = self.venta_repo.get_venta_by_id(venta_id)
        if not venta:
            raise ValueError(f"Venta #{venta_id} no encontrada")
        if venta.anulada:
            raise ValueError(f"Venta #{venta_id} ya está anulada")

        for item in venta.items:
            self.producto_repo.update_stock(item.producto_id, item.cantidad)
            self.inventario_repo.create_movimiento(
                item.producto_id, "entrada", item.cantidad
            )

        self.venta_repo.anular_venta(venta_id)
        return venta

    def get_ventas_hoy(self):
        """Retorna las ventas de hoy"""
        return self.venta_repo.get_ventas_hoy()

    def get_total_hoy(self):
        """Retorna el total de ventas de hoy"""
        return self.venta_repo.get_total_hoy()

    def get_count_hoy(self):
        """Retorna el número de ventas de hoy"""
        return self.venta_repo.get_count_hoy()


class InventarioService:
    """Servicio para lógica de negocio de inventario"""

    def __init__(self, session):
        self.session = session
        self.producto_repo = ProductoRepository(session)
        self.inventario_repo = InventarioRepository(session)

    def entrada_inventario(self, producto_id, cantidad):
        """Registra entrada de inventario"""
        self.producto_repo.update_stock(producto_id, cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "entrada", cantidad)

    def salida_inventario(self, producto_id, cantidad):
        """Registra salida manual de inventario"""
        producto = self.producto_repo.get_by_id(producto_id)
        if producto.stock < cantidad:
            raise ValueError("Stock insuficiente")
        self.producto_repo.update_stock(producto_id, -cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "salida", cantidad)

    def descontar_por_venta(self, producto_id, cantidad):
        """Descuenta inventario por venta (usado desde ventas)"""
        producto = self.producto_repo.get_by_id(producto_id)
        if producto.stock < cantidad:
            raise ValueError(f"Stock insuficiente para {producto.nombre}")
        self.producto_repo.update_stock(producto_id, -cantidad)
        return self.inventario_repo.create_movimiento(producto_id, "salida", cantidad)

    def obtener_stock(self, producto_id):
        """Obtiene el stock actual de un producto"""
        producto = self.producto_repo.get_by_id(producto_id)
        return producto.stock if producto else 0

    def get_movimientos_producto(self, producto_id):
        """Retorna los movimientos de un producto"""
        return self.inventario_repo.get_movimientos_producto(producto_id)

    def get_all_productos(self):
        """Retorna todos los productos con su stock"""
        return self.producto_repo.get_all()

```

---

## 9. services/corte_service.py

```python
from models.producto import CorteCaja, GastoCaja
from repositories.venta_repo import VentaRepository
from datetime import datetime


class CorteCajaService:
    """Servicio para lógica de negocio de corte de caja"""

    def __init__(self, session):
        self.session = session
        self.venta_repo = VentaRepository(session)

    def get_corte_actual(self):
        """Retorna el corte de caja del día"""
        return (
            self.session.query(CorteCaja)
            .filter(CorteCaja.fecha_cierre.is_(None))
            .first()
        )

    def abrir_caja(self):
        """Abre la caja creando un nuevo corte"""
        corte_existente = self.get_corte_actual()
        if corte_existente:
            return corte_existente

        corte = CorteCaja(fecha_apertura=datetime.now(), total_ventas=0)
        self.session.add(corte)
        self.session.commit()
        return corte

    def registrar_gasto(self, concepto, monto):
        """Registra un gasto de caja en el corte actual"""
        corte = self.get_corte_actual()
        if not corte:
            raise Exception("No hay caja abierta")
        gasto = GastoCaja(corte_id=corte.id, concepto=concepto, monto=monto)
        self.session.add(gasto)
        self.session.commit()
        return gasto

    def get_gastos_hoy(self):
        """Retorna los gastos del corte actual"""
        corte = self.get_corte_actual()
        if not corte:
            return []
        return (
            self.session.query(GastoCaja).filter(GastoCaja.corte_id == corte.id).all()
        )

    def get_total_gastos_hoy(self):
        """Retorna el total de gastos de hoy"""
        return sum(g.monto for g in self.get_gastos_hoy())

    def cerrar_caja(self):
        """Cierra la caja actual"""
        corte = self.get_corte_actual()
        if not corte:
            return None

        total = self.venta_repo.get_total_hoy()
        num_ventas = self.venta_repo.get_count_hoy()
        total_gastos = self.get_total_gastos_hoy()
        corte.fecha_cierre = datetime.now()
        corte.total_ventas = total
        corte.numero_ventas = num_ventas
        corte.total_gastos = total_gastos
        corte.ganancia_neta = total - total_gastos
        self.session.commit()

        try:
            from utils.backup import backup_database

            backup_database()
        except Exception as e:
            print(f"Error al crear backup: {e}")

        return corte

    def obtener_total_vendido(self):
        """Retorna el total vendido hoy"""
        return self.venta_repo.get_total_hoy()

    def obtener_numero_ventas(self):
        """Retorna el número de ventas hoy"""
        return self.venta_repo.get_count_hoy()

    def esta_caja_abierta(self):
        """Retorna True si la caja está abierta"""
        return self.get_corte_actual() is not None

    def get_estadisticas_hoy(self):
        """Retorna las estadísticas de ventas de hoy"""
        gastos = self.get_gastos_hoy()
        total_gastos = sum(g.monto for g in gastos)
        total_ventas = self.venta_repo.get_total_hoy()
        return {
            "total": total_ventas,
            "num_ventas": self.venta_repo.get_count_hoy(),
            "ventas": self.venta_repo.get_ventas_hoy(),
            "gastos": gastos,
            "total_gastos": total_gastos,
            "ganancia_neta": total_ventas - total_gastos,
        }

    def get_historial_cortes(self):
        """Retorna el historial de cortes de caja"""
        return (
            self.session.query(CorteCaja)
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )

```

---

## 10. services/historial_service.py

```python
from models.producto import CorteCaja, Venta, VentaItem, Producto, GastoCaja
from sqlalchemy import and_, func
from datetime import datetime


class HistorialService:
    def __init__(self, session):
        self.session = session

    def get_cierres(self, fecha_desde=None, fecha_hasta=None):
        """Retorna cierres cerrados con filtro opcional de fechas"""
        query = self.session.query(CorteCaja).filter(CorteCaja.fecha_cierre.isnot(None))
        if fecha_desde:
            query = query.filter(CorteCaja.fecha_apertura >= fecha_desde)
        if fecha_hasta:
            query = query.filter(CorteCaja.fecha_apertura <= fecha_hasta)
        return query.order_by(CorteCaja.fecha_apertura.desc()).all()

    def get_ventas_del_cierre(self, corte_id):
        """Retorna las ventas de un corte específico"""
        corte = self.session.query(CorteCaja).filter(CorteCaja.id == corte_id).first()
        if not corte:
            return []
        return (
            self.session.query(Venta)
            .filter(
                and_(
                    Venta.fecha >= corte.fecha_apertura,
                    Venta.fecha <= corte.fecha_cierre,
                )
            )
            .order_by(Venta.fecha.asc())
            .all()
        )

    def get_ranking_productos(self, fecha_desde=None, fecha_hasta=None):
        """Retorna ranking de productos más y menos vendidos"""
        query = (
            self.session.query(
                Producto.codigo,
                Producto.nombre,
                func.sum(VentaItem.cantidad).label("total_vendido"),
                func.sum(VentaItem.cantidad * VentaItem.precio).label("total_ingresos"),
            )
            .join(VentaItem, Producto.id == VentaItem.producto_id)
            .join(Venta, VentaItem.venta_id == Venta.id)
        )
        if fecha_desde:
            query = query.filter(Venta.fecha >= fecha_desde)
        if fecha_hasta:
            query = query.filter(Venta.fecha <= fecha_hasta)
        return (
            query.group_by(Producto.id)
            .order_by(func.sum(VentaItem.cantidad).desc())
            .all()
        )

    def get_resumen_periodo(self, fecha_desde=None, fecha_hasta=None):
        """Retorna totales consolidados del período"""
        cierres = self.get_cierres(fecha_desde, fecha_hasta)
        return {
            "total_ventas": sum(c.total_ventas for c in cierres),
            "total_gastos": sum(c.total_gastos or 0 for c in cierres),
            "ganancia_neta": sum(c.ganancia_neta or 0 for c in cierres),
            "num_cierres": len(cierres),
            "num_ventas": sum(c.numero_ventas for c in cierres),
        }

```

---

## 11. services/categoria_service.py

```python
from models.producto import Categoria, Producto
from sqlalchemy.exc import IntegrityError

COLORES_DEFAULT = [
    "#3498db",
    "#27ae60",
    "#e67e22",
    "#8e44ad",
    "#e74c3c",
    "#16a085",
    "#d35400",
    "#2980b9",
    "#1abc9c",
    "#f39c12",
]


class CategoriaService:
    def __init__(self, session):
        self.session = session

    def get_all(self):
        return self.session.query(Categoria).order_by(Categoria.nombre.asc()).all()

    def crear(self, nombre, color=None):
        nombre = nombre.strip()
        if not nombre:
            raise ValueError("El nombre de la categoría es obligatorio")
        if not color:
            total = self.session.query(Categoria).count()
            color = COLORES_DEFAULT[total % len(COLORES_DEFAULT)]
        cat = Categoria(nombre=nombre, color=color)
        self.session.add(cat)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise ValueError(f"La categoría '{nombre}' ya existe")
        return cat

    def renombrar(self, categoria_id, nuevo_nombre):
        cat = self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        if not cat:
            raise ValueError("Categoría no encontrada")
        cat.nombre = nuevo_nombre.strip()
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise ValueError(f"Ya existe una categoría con ese nombre")
        return cat

    def eliminar(self, categoria_id):
        cat = self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        if cat:
            self.session.delete(cat)
            self.session.commit()

    def asignar_a_producto(self, producto_id, categoria_ids):
        """Reemplaza las categorías de un producto con la lista dada"""
        producto = (
            self.session.query(Producto).filter(Producto.id == producto_id).first()
        )
        if not producto:
            raise ValueError("Producto no encontrado")
        categorias = (
            self.session.query(Categoria).filter(Categoria.id.in_(categoria_ids)).all()
        )
        producto.categorias = categorias
        self.session.commit()
        return producto

    def get_productos_de_categoria(self, categoria_id):
        cat = self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        if not cat:
            return []
        return [p for p in cat.productos if p.activo]

```

---

## 12. security/license_manager.py

```python
import uuid
import hashlib
import json
import os
import sys
import platform

SECRET = "tito_castilla_pos_secret"


def get_config_dir():
    """Retorna el directorio de configuración en %LOCALAPPDATA%"""
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ""))
        return os.path.join(base, "TuCajero", "config")
    return os.path.join(os.path.expanduser("~"), ".tucajero", "config")


def get_machine_id():
    """Obtiene un identificador único robusto de la computadora"""
    components = [
        str(uuid.getnode()),
        platform.node(),
        platform.processor() or "unknown",
        platform.machine() or "unknown",
    ]
    combined = "|".join(components)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def generar_licencia(machine_id):
    """Genera una licencia basada en el machine_id"""
    licencia = hashlib.sha256((machine_id + SECRET).encode()).hexdigest()[:16]
    return licencia.upper()


def get_license_path():
    """Retorna la ruta del archivo de licencia en %LOCALAPPDATA%"""
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "license.json")


def cargar_licencia():
    """Carga la configuración de licencia"""
    license_path = get_license_path()
    if not os.path.exists(license_path):
        return {"activated": False, "license_key": ""}

    try:
        with open(license_path, "r") as f:
            return json.load(f)
    except:
        return {"activated": False, "license_key": ""}


def guardar_licencia(license_key):
    """Guarda la licencia en el archivo"""
    license_path = get_license_path()
    data = {"activated": True, "license_key": license_key.upper()}
    with open(license_path, "w") as f:
        json.dump(data, f, indent=4)
    return True


def validar_licencia():
    """Valida si la licencia es correcta"""
    licencia_data = cargar_licencia()

    if not licencia_data.get("activated", False):
        return False

    machine_id = get_machine_id()
    licencia_correcta = generar_licencia(machine_id)

    return licencia_data.get("license_key", "").upper() == licencia_correcta


def crear_license_default():
    """Crea el archivo de licencia por defecto"""
    license_path = get_license_path()
    if not os.path.exists(license_path):
        data = {"activated": False, "license_key": ""}
        with open(license_path, "w") as f:
            json.dump(data, f, indent=4)

```

---

## 13. ui/main_window.py — Ventana Principal

```python
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QStackedWidget,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from utils.store_config import (
    get_store_name,
    get_logo_path,
    get_nit,
    get_phone,
    get_email,
    get_address,
)
import os


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self):
        super().__init__()
        store_name = get_store_name()
        self.setWindowTitle(f"TuCajero POS - {store_name}")
        self.setMinimumSize(1024, 768)
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.sidebar = self.crear_sidebar()
        main_layout.addWidget(self.sidebar)

        content_area = QWidget()
        content_layout = QVBoxLayout()
        content_area.setLayout(content_layout)

        header = self.crear_header()
        content_layout.addWidget(header)

        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack, 1)

        main_layout.addWidget(content_area, 1)

    def crear_header(self):
        """Crea el encabezado con logo, nombre e info de tienda"""
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50;")
        header.setFixedHeight(80)

        layout = QHBoxLayout()
        header.setLayout(layout)

        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    60,
                    60,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label, 0)

        store_name = get_store_name()
        nit = get_nit()
        phone = get_phone()
        email = get_email()
        address = get_address()

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        title_label = QLabel(f"TuCajero POS")
        title_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        info_layout.addWidget(title_label)

        if store_name:
            store_label = QLabel(store_name)
            store_label.setStyleSheet(
                "color: #3498db; font-size: 14px; font-weight: bold;"
            )
            info_layout.addWidget(store_label)

        contact_parts = []
        if nit:
            contact_parts.append(f"NIT: {nit}")
        if phone:
            contact_parts.append(f"Tel: {phone}")
        if email:
            contact_parts.append(email)
        if contact_parts:
            contact_label = QLabel("  |  ".join(contact_parts))
            contact_label.setStyleSheet("color: #bdc3c7; font-size: 11px;")
            info_layout.addWidget(contact_label)

        if address:
            addr_label = QLabel(address)
            addr_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
            info_layout.addWidget(addr_label)

        layout.addLayout(info_layout, 1)

        return header

    def crear_sidebar(self):
        """Crea el menú lateral"""
        sidebar = QWidget()
        layout = QVBoxLayout()
        sidebar.setLayout(layout)
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #34495e;")

        title = QLabel("TuCajero")
        title.setStyleSheet(
            "color: white; font-size: 20px; font-weight: bold; padding: 15px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.btn_ventas = self.crear_boton("Ventas", self.switch_to_ventas)
        self.btn_productos = self.crear_boton("Productos", self.switch_to_productos)
        self.btn_inventario = self.crear_boton("Inventario", self.switch_to_inventario)
        self.btn_corte = self.crear_boton("Corte de Caja", self.switch_to_corte)
        self.btn_historial = self.crear_boton("Historial", self.switch_to_historial)
        self.btn_config = self.crear_boton("Config", self.switch_to_config)

        layout.addWidget(self.btn_ventas)
        layout.addWidget(self.btn_productos)
        layout.addWidget(self.btn_inventario)
        layout.addWidget(self.btn_corte)
        layout.addWidget(self.btn_historial)
        layout.addWidget(self.btn_config)

        layout.addStretch()

        btn_acerca = QPushButton("Acerca de")
        btn_acerca.setFixedHeight(40)
        btn_acerca.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #95a5a6;
                border: none;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        btn_acerca.clicked.connect(self.mostrar_acerca)
        layout.addWidget(btn_acerca)

        copyright_label = QLabel("© Ing. Francisco Llinas P.")
        copyright_label.setStyleSheet("color: #7f8c8d; font-size: 10px; padding: 10px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(copyright_label)

        return sidebar

    def mostrar_acerca(self):
        """Muestra la ventana Acerca de"""
        from ui.about_view import AboutView

        dialog = AboutView(self)
        dialog.exec()

    def crear_boton(self, texto, callback):
        """Crea un botón del menú"""
        btn = QPushButton(texto)
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        btn.clicked.connect(callback)
        return btn

    def add_view(self, widget, name):
        """Agrega una vista al stack"""
        self.content_stack.addWidget(widget)
        return self.content_stack.count() - 1

    def switch_view(self, index):
        """Cambia a una vista específica"""
        self.content_stack.setCurrentIndex(index)

    def switch_to_ventas(self):
        self.switch_view(0)

    def switch_to_productos(self):
        self.switch_view(1)

    def switch_to_inventario(self):
        self.switch_view(2)

    def switch_to_corte(self):
        self.switch_view(3)

    def switch_to_historial(self):
        self.switch_view(4)

    def switch_to_config(self):
        self.switch_view(5)

    def closeEvent(self, event):
        """Cierra la aplicación correctamente"""
        try:
            from config.database import close_db

            close_db()
        except Exception as e:
            import logging

            logging.error(f"closeEvent error: {e}")
        event.accept()

```

---

## 14. ui/setup_view.py — Configuración Inicial

```python
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QFormLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from utils.store_config import (
    save_store_config,
    load_store_config,
    get_store_name,
    get_address,
    get_phone,
    get_email,
    get_nit,
    get_logo_path,
)


class SetupDialog(QDialog):
    """Pantalla de configuración inicial — aparece solo la primera vez"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logo_path = ""
        self.setWindowTitle("Bienvenido")
        self.setFixedSize(600, 550)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50;")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)
        header_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Bienvenido a TuCajero")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Configura tu negocio para comenzar")
        subtitle.setStyleSheet("color: #bdc3c7; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_widget.setLayout(form_layout)
        form_layout.setContentsMargins(40, 30, 40, 20)
        form_layout.setSpacing(15)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Droguería CruzMedic")
        self.nombre_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        form_layout.addWidget(QLabel("Nombre del negocio *"))
        form_layout.addWidget(self.nombre_input)

        nit_layout = QHBoxLayout()
        nit_layout.setSpacing(15)
        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("123456789-0")
        self.nit_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        nit_layout.addWidget(QLabel("NIT"))
        nit_layout.addWidget(self.nit_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("300 123 4567")
        self.telefono_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        nit_layout.addWidget(QLabel("Teléfono"))
        nit_layout.addWidget(self.telefono_input)

        form_layout.addLayout(nit_layout)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("info@ejemplo.com")
        self.email_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        form_layout.addWidget(QLabel("Correo electrónico"))
        form_layout.addWidget(self.email_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Calle 123 #45-67, Ciudad")
        self.direccion_input.setStyleSheet(
            "padding: 12px; font-size: 14px; border: 1px solid #bdc3c7; border-radius: 4px;"
        )
        form_layout.addWidget(QLabel("Dirección"))
        form_layout.addWidget(self.direccion_input)

        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(15)

        self.btn_logo = QPushButton("Seleccionar imagen...")
        self.btn_logo.setStyleSheet("padding: 12px; font-size: 14px;")
        self.btn_logo.clicked.connect(self.seleccionar_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setStyleSheet(
            "border: 1px solid #bdc3c7; border-radius: 4px; background-color: #f8f9fa;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(QLabel("Logo:"))
        logo_layout.addWidget(self.btn_logo)
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addStretch()

        form_layout.addLayout(logo_layout)

        main_layout.addWidget(form_widget)

        footer = QWidget()
        footer_layout = QVBoxLayout()
        footer.setLayout(footer_layout)
        footer_layout.setContentsMargins(40, 0, 40, 20)
        footer_layout.setSpacing(10)

        nota = QLabel("* Campo requerido")
        nota.setStyleSheet("color: #95a5a6; font-size: 12px;")
        footer_layout.addWidget(nota)

        self.btn_comenzar = QPushButton("COMENZAR")
        self.btn_comenzar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_comenzar.clicked.connect(self.guardar)
        footer_layout.addWidget(self.btn_comenzar)

        main_layout.addWidget(footer)

        self.nombre_input.setFocus()

    def seleccionar_logo(self):
        """Abre dialogo para seleccionar logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.ico *.bmp);;Todos los archivos (*)",
        )
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
            self.btn_logo.setText("Cambiar imagen...")

    def guardar(self):
        """Guarda la configuracion"""
        nombre = self.nombre_input.text().strip()
        if not nombre:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.warning(
                self, "Campo requerido", "El nombre del negocio es requerido"
            )
            self.nombre_input.setFocus()
            return

        config_data = {
            "store_name": nombre,
            "nit": self.nit_input.text().strip(),
            "phone": self.telefono_input.text().strip(),
            "email": self.email_input.text().strip(),
            "address": self.direccion_input.text().strip(),
            "logo_path": self.logo_path,
            "setup_complete": True,
        }

        if save_store_config(config_data):
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")


class SetupView(QWidget):
    """Panel de configuración — accesible desde el menú lateral"""

    config_saved = Signal()

    def __init__(self, session=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.logo_path = get_logo_path()
        self.init_ui()
        self.cargar_config()

    def init_ui(self):
        """Inicializa la interfaz del panel de configuración"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Configuración del Negocio")
        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold; padding-bottom: 10px;"
        )
        layout.addWidget(titulo)

        info_group = QGroupBox("Información del Negocio")
        info_layout = QFormLayout()
        info_group.setLayout(info_layout)
        info_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del negocio")
        self.nombre_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("Nombre:", self.nombre_input)

        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("NIT")
        self.nit_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("NIT:", self.nit_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Teléfono")
        self.telefono_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("Teléfono:", self.telefono_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        self.email_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("Email:", self.email_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Dirección")
        self.direccion_input.setStyleSheet("padding: 10px; font-size: 14px;")
        info_layout.addRow("Dirección:", self.direccion_input)

        layout.addWidget(info_group)

        logo_group = QGroupBox("Logo")
        logo_layout = QHBoxLayout()
        logo_group.setLayout(logo_layout)

        self.btn_logo = QPushButton("Seleccionar imagen...")
        self.btn_logo.setStyleSheet("padding: 10px; font-size: 14px;")
        self.btn_logo.clicked.connect(self.seleccionar_logo)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setStyleSheet(
            "border: 1px solid #bdc3c7; border-radius: 4px; background-color: #f8f9fa;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.logo_path and __import__("os").path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
                self.btn_logo.setText("Cambiar imagen...")

        logo_layout.addWidget(QLabel("Logo:"))
        logo_layout.addWidget(self.btn_logo)
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addStretch()

        layout.addWidget(logo_group)

        layout.addStretch()

        self.btn_guardar = QPushButton("GUARDAR CONFIGURACIÓN")
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(self.btn_guardar)

    def cargar_config(self):
        """Carga la configuración actual"""
        self.nombre_input.setText(get_store_name())
        self.nit_input.setText(get_nit())
        self.telefono_input.setText(get_phone())
        self.email_input.setText(get_email())
        self.direccion_input.setText(get_address())

    def seleccionar_logo(self):
        """Abre diálogo para seleccionar logo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.ico *.bmp);;Todos los archivos (*)",
        )
        if file_path:
            self.logo_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    80,
                    80,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.logo_preview.setPixmap(scaled)
            self.btn_logo.setText("Cambiar imagen...")

    def guardar(self):
        """Guarda la configuración"""
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(
                self, "Campo requerido", "El nombre del negocio es requerido"
            )
            self.nombre_input.setFocus()
            return

        config_data = {
            "store_name": nombre,
            "nit": self.nit_input.text().strip(),
            "phone": self.telefono_input.text().strip(),
            "email": self.email_input.text().strip(),
            "address": self.direccion_input.text().strip(),
            "logo_path": self.logo_path,
            "setup_complete": True,
        }

        if save_store_config(config_data):
            load_store_config()
            QMessageBox.information(
                self, "Éxito", "Configuración guardada correctamente"
            )
            self.config_saved.emit()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")

```

---

## 15. ui/ventas_view.py — Ventas

```python
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDoubleSpinBox,
    QHeaderView,
    QDialog,
    QDialogButtonBox,
    QButtonGroup,
    QRadioButton,
)
from PySide6.QtCore import Qt, Signal

IVA_RATE = 0.19


class PaymentDialog(QDialog):
    """Dialog for payment with multiple payment methods"""

    def __init__(self, subtotal, iva, total, parent=None):
        super().__init__(parent)
        self.subtotal = subtotal
        self.iva = iva
        self.total = total
        self.payment_amount = 0
        self.metodo_pago = "Efectivo"
        self.init_ui()

    def init_ui(self):
        """Initialize the payment dialog UI"""
        self.setWindowTitle("Cobro")
        self.setFixedSize(400, 480)

        layout = QVBoxLayout()
        self.setLayout(layout)

        from utils.store_config import get_store_name

        store_name_label = QLabel(get_store_name())
        store_name_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50;"
        )
        store_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(store_name_label)

        total_label = QLabel("TOTAL A PAGAR")
        total_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(total_label)

        self.lbl_total = QLabel(f"${self.total:.2f}")
        self.lbl_total.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: #27ae60;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_total)

        metodo_label = QLabel("Método de pago:")
        metodo_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(metodo_label)

        self.metodo_group = QButtonGroup()
        metodos = [
            ("Efectivo", "Efectivo"),
            ("Nequi", "Nequi"),
            ("Daviplata", "Daviplata"),
            ("Transferencia", "Transferencia"),
        ]
        for texto, valor in metodos:
            radio = QRadioButton(texto)
            radio.setStyleSheet("padding: 6px; font-size: 14px;")
            self.metodo_group.addButton(radio)
            self.metodo_group.setId(radio, len(self.metodo_group.buttons()))
            radio.metodo_valor = valor
            radio.toggled.connect(self.on_metodo_changed)
            layout.addWidget(radio)

        self.metodo_group.buttons()[0].setChecked(True)

        self.efectivo_container = QWidget()
        efectivo_layout = QVBoxLayout()
        self.efectivo_container.setLayout(efectivo_layout)

        pago_label = QLabel("Monto recibido:")
        pago_label.setStyleSheet("font-size: 14px;")
        efectivo_layout.addWidget(pago_label)

        self.pago_input = QDoubleSpinBox()
        self.pago_input.setRange(0, 999999999)
        self.pago_input.setDecimals(2)
        self.pago_input.setStyleSheet("font-size: 24px; padding: 10px;")
        self.pago_input.setFocus()
        self.pago_input.valueChanged.connect(self.calcular_cambio)
        efectivo_layout.addWidget(self.pago_input)

        self.lbl_cambio = QLabel("Cambio: $0.00")
        self.lbl_cambio.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #3498db;"
        )
        self.lbl_cambio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        efectivo_layout.addWidget(self.lbl_cambio)

        layout.addWidget(self.efectivo_container)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("CONFIRMAR PAGO")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("CANCELAR")
        layout.addWidget(buttons)

    def on_metodo_changed(self):
        """Handle payment method change"""
        for radio in self.metodo_group.buttons():
            if radio.isChecked():
                self.metodo_pago = radio.metodo_valor
                break
        if self.metodo_pago == "Efectivo":
            self.efectivo_container.setVisible(True)
        else:
            self.efectivo_container.setVisible(False)

    def calcular_cambio(self):
        """Calculate change from payment"""
        pago = self.pago_input.value()
        cambio = pago - self.total
        if cambio >= 0:
            self.lbl_cambio.setText(f"Cambio: ${cambio:.2f}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #27ae60;"
            )
            self.payment_amount = pago
        else:
            self.lbl_cambio.setText(f"Faltan: ${abs(cambio):.2f}")
            self.lbl_cambio.setStyleSheet(
                "font-size: 24px; font-weight: bold; color: #e74c3c;"
            )
            self.payment_amount = 0

    def accept(self):
        """Handle dialog acceptance"""
        if self.metodo_pago == "Efectivo" and self.pago_input.value() < self.total:
            QMessageBox.warning(
                self, "Pago insuficiente", "El monto recibido es menor al total"
            )
            return
        super().accept()


class VentasView(QWidget):
    """Sales view with auto-refresh support"""

    sale_completed = Signal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.carrito = []
        self.productos = []
        self.init_ui()
        self.cargar_productos()
        self.codigo_input.setFocus()

    def init_ui(self):
        """Initialize the interface"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        from utils.store_config import get_store_name, get_address, get_phone

        store_name = get_store_name()
        address = get_address()
        phone = get_phone()

        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #2c3e50; padding: 10px;")
        header_layout = QVBoxLayout()
        header_widget.setLayout(header_layout)

        title = QLabel(f"Nueva Venta - {store_name}")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        header_layout.addWidget(title)

        if address:
            addr_label = QLabel(address)
            addr_label.setStyleSheet("font-size: 12px; color: #bdc3c7;")
            header_layout.addWidget(addr_label)

        if phone:
            phone_label = QLabel(f"Tel: {phone}")
            phone_label.setStyleSheet("font-size: 12px; color: #bdc3c7;")
            header_layout.addWidget(phone_label)

        layout.addWidget(header_widget)

        input_layout = QHBoxLayout()
        layout.addLayout(input_layout)

        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código o nombre de producto")
        self.codigo_input.setStyleSheet("padding: 10px; font-size: 16px;")
        self.codigo_input.returnPressed.connect(self.buscar_producto)
        input_layout.addWidget(self.codigo_input)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.setFixedWidth(100)
        btn_buscar.setStyleSheet(
            "padding: 10px; background-color: #3498db; color: white;"
        )
        btn_buscar.clicked.connect(self.mostrar_buscador)
        input_layout.addWidget(btn_buscar)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["Código", "Producto", "Cantidad", "Precio", "IVA", "Subtotal"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setStyleSheet("font-size: 14px;")
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()

        self.btn_menos = QPushButton("-")
        self.btn_menos.setFixedWidth(50)
        self.btn_menos.clicked.connect(self.disminuir_cantidad)
        btn_layout.addWidget(self.btn_menos)

        self.btn_mas = QPushButton("+")
        self.btn_mas.setFixedWidth(50)
        self.btn_mas.clicked.connect(self.aumentar_cantidad)
        btn_layout.addWidget(self.btn_mas)

        btn_layout.addStretch()

        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px;"
        )
        self.btn_eliminar.clicked.connect(self.eliminar_item)
        btn_layout.addWidget(self.btn_eliminar)

        layout.addLayout(btn_layout)

        resumen_layout = QVBoxLayout()

        self.lbl_subtotal = QLabel("Subtotal: $0.00")
        self.lbl_subtotal.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        self.lbl_subtotal.setAlignment(Qt.AlignmentFlag.AlignRight)
        resumen_layout.addWidget(self.lbl_subtotal)

        self.lbl_iva = QLabel("IVA (19%): $0.00")
        self.lbl_iva.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        self.lbl_iva.setAlignment(Qt.AlignmentFlag.AlignRight)
        resumen_layout.addWidget(self.lbl_iva)

        self.lbl_total = QLabel("TOTAL: $0.00")
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; padding: 15px; color: #27ae60;"
        )
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        resumen_layout.addWidget(self.lbl_total)

        layout.addLayout(resumen_layout)

        botones_layout = QHBoxLayout()

        self.btn_cancelar = QPushButton("CANCELAR")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_cancelar.clicked.connect(self.cancelar_venta)
        botones_layout.addWidget(self.btn_cancelar)

        self.btn_cobrar = QPushButton("COBRAR")
        self.btn_cobrar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_cobrar.clicked.connect(self.cobrar)
        botones_layout.addWidget(self.btn_cobrar)

        layout.addLayout(botones_layout)

    def cargar_productos(self):
        """Load all products for the search"""
        from services.producto_service import ProductoService

        service = ProductoService(self.session)
        self.productos = service.get_all_productos()

    def recargar_productos(self):
        """Reload products (called after sale)"""
        self.session.commit()
        self.cargar_productos()

    def buscar_producto(self):
        """Search product by code or name"""
        from services.producto_service import ProductoService

        texto = self.codigo_input.text().strip()
        if not texto:
            return

        service = ProductoService(self.session)

        producto = service.get_producto_by_codigo(texto)
        if producto and producto.stock > 0:
            self.agregar_al_carrito(producto)
            self.codigo_input.clear()
            self.codigo_input.setFocus()
            return

        productos = service.get_producto_by_nombre(texto)
        if len(productos) == 1:
            producto = productos[0]
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.codigo_input.clear()
                self.codigo_input.setFocus()
                return
        elif len(productos) > 1:
            self.codigo_input.clear()
            self.mostrar_buscador_productos(productos)
            return

        QMessageBox.warning(self, "No encontrado", f"No se encontró '{texto}'")
        self.codigo_input.selectAll()
        self.codigo_input.setFocus()

    def mostrar_buscador(self):
        """Show product search dialog"""
        from ui.buscador_productos import BuscadorProductosDialog

        dialog = BuscadorProductosDialog(self.productos, self)
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.producto_seleccionado
        ):
            producto = dialog.producto_seleccionado
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.codigo_input.setFocus()

    def mostrar_buscador_productos(self, productos):
        """Show custom product list when multiple matches"""
        from ui.buscador_productos import BuscadorProductosDialog

        dialog = BuscadorProductosDialog(productos, self)
        if (
            dialog.exec() == QDialog.DialogCode.Accepted
            and dialog.producto_seleccionado
        ):
            producto = dialog.producto_seleccionado
            if producto.stock > 0:
                self.agregar_al_carrito(producto)
                self.codigo_input.setFocus()

    def agregar_al_carrito(self, producto):
        """Add product to cart"""
        for item in self.carrito:
            if item["producto_id"] == producto.id:
                item["cantidad"] += 1
                self.actualizar_tabla()
                return

        self.carrito.append(
            {
                "producto_id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "precio": producto.precio,
                "cantidad": 1,
                "aplica_iva": getattr(producto, "aplica_iva", True),
            }
        )
        self.actualizar_tabla()

    def actualizar_tabla(self):
        """Update cart table"""
        self.tabla.setRowCount(len(self.carrito))

        subtotal_total = 0
        iva_total = 0

        for i, item in enumerate(self.carrito):
            cantidad = item["cantidad"]
            precio = item["precio"]
            aplica_iva = item.get("aplica_iva", True)

            subtotal = cantidad * precio
            iva = round(subtotal * IVA_RATE, 2) if aplica_iva else 0
            total_item = subtotal + iva

            subtotal_total += subtotal
            iva_total += iva

            self.tabla.setItem(i, 0, QTableWidgetItem(item["codigo"]))
            self.tabla.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            self.tabla.setItem(i, 2, QTableWidgetItem(str(cantidad)))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"${precio:.2f}"))
            self.tabla.setItem(
                i, 4, QTableWidgetItem(f"${iva:.2f}" if aplica_iva else "—")
            )
            self.tabla.setItem(i, 5, QTableWidgetItem(f"${total_item:.2f}"))

        total_final = subtotal_total + iva_total

        self.lbl_subtotal.setText(f"Subtotal: ${subtotal_total:.2f}")
        self.lbl_iva.setText(f"IVA (19%): ${iva_total:.2f}")
        self.lbl_total.setText(f"TOTAL: ${total_final:.2f}")

    def aumentar_cantidad(self):
        """Increase quantity of selected product"""
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.carrito):
            self.carrito[row]["cantidad"] += 1
            self.actualizar_tabla()

    def disminuir_cantidad(self):
        """Decrease quantity of selected product"""
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.carrito):
            if self.carrito[row]["cantidad"] > 1:
                self.carrito[row]["cantidad"] -= 1
            else:
                self.carrito.pop(row)
            self.actualizar_tabla()

    def eliminar_item(self):
        """Remove item from cart"""
        row = self.tabla.currentRow()
        if row >= 0 and row < len(self.carrito):
            self.carrito.pop(row)
            self.actualizar_tabla()

    def cancelar_venta(self):
        """Cancel current sale"""
        if not self.carrito:
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Cancelar la venta actual?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.carrito = []
            self.actualizar_tabla()
            self.codigo_input.setFocus()

    def cobrar(self):
        """Process sale payment"""
        if not self.carrito:
            QMessageBox.warning(self, "Error", "El carrito está vacío")
            return

        from services.producto_service import VentaService
        from utils.ticket import GeneradorTicket

        subtotal = sum(item["cantidad"] * item["precio"] for item in self.carrito)
        iva = 0
        for item in self.carrito:
            if item.get("aplica_iva", True):
                iva += round(item["cantidad"] * item["precio"] * IVA_RATE, 2)
        total = subtotal + iva

        dialog = PaymentDialog(subtotal, iva, total, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            service = VentaService(self.session)
            venta = service.registrar_venta(
                self.carrito, metodo_pago=dialog.metodo_pago
            )

            generador = GeneradorTicket()
            generador.imprimir(venta, venta.items)

            cambio = dialog.payment_amount - total
            QMessageBox.information(
                self,
                "Venta Registrada",
                f"Venta #{venta.id}\n"
                f"Subtotal: ${subtotal:.2f}\n"
                f"IVA: ${iva:.2f}\n"
                f"Total: ${total:.2f}\n"
                f"Pago: ${dialog.payment_amount:.2f}\n"
                f"Cambio: ${cambio:.2f}\n\n"
                f"¡Gracias por su compra!",
            )

            self.carrito = []
            self.actualizar_tabla()

            self.recargar_productos()
            self.sale_completed.emit()

            self.codigo_input.setFocus()

        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar venta: {str(e)}")

```

---

## 16. ui/productos_view.py — Productos

```python
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QHeaderView,
    QCheckBox,
    QComboBox,
    QInputDialog,
)
from PySide6.QtCore import Qt


class ProductosView(QWidget):
    """Vista de gestión de productos"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_productos()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Productos")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_agregar = QPushButton("+ Agregar Producto")
        btn_agregar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 10px;"
        )
        btn_agregar.clicked.connect(self.abrir_dialogo_agregar)
        btn_layout.addWidget(btn_agregar)

        btn_editar = QPushButton("Editar")
        btn_editar.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px;"
        )
        btn_editar.clicked.connect(self.editar_producto)
        btn_layout.addWidget(btn_editar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 10px;"
        )
        btn_eliminar.clicked.connect(self.eliminar_producto)
        btn_layout.addWidget(btn_eliminar)

        btn_categorias = QPushButton("Categorías")
        btn_categorias.setStyleSheet(
            "background-color: #9b59b6; color: white; padding: 10px;"
        )
        btn_categorias.clicked.connect(self.abrir_gestor_categorias)
        btn_layout.addWidget(btn_categorias)

        layout.addLayout(btn_layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Código", "Nombre", "Precio", "Stock", "Categoría"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.tabla)

    def cargar_productos(self):
        """Carga los productos desde la base de datos"""
        from services.producto_service import ProductoService

        service = ProductoService(self.session)
        productos = service.get_all_productos()

        self.tabla.setRowCount(len(productos))

        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 2, QTableWidgetItem(p.nombre))
            self.tabla.setItem(i, 3, QTableWidgetItem(f"${p.precio:.2f}"))
            self.tabla.setItem(i, 4, QTableWidgetItem(str(p.stock)))
            cat_nombre = p.categoria.nombre if p.categoria else "—"
            self.tabla.setItem(i, 5, QTableWidgetItem(cat_nombre))

    def recargar_productos(self):
        """Recarga los productos (para auto-actualizacion despues de venta)"""
        self.cargar_productos()

    def obtener_producto_seleccionado(self):
        """Retorna el ID del producto seleccionado"""
        row = self.tabla.currentRow()
        if row >= 0:
            item = self.tabla.item(row, 0)
            if item is not None:
                try:
                    return int(item.text())
                except (ValueError, TypeError):
                    return None
        return None

    def abrir_dialogo_agregar(self):
        """Abre el diálogo para agregar un producto"""
        dialog = ProductoDialog(self.session, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_productos()

    def editar_producto(self):
        """Abre el diálogo para editar un producto"""
        producto_id = self.obtener_producto_seleccionado()
        if not producto_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        dialog = ProductoDialog(self.session, self, producto_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_productos()

    def eliminar_producto(self):
        """Elimina el producto seleccionado"""
        producto_id = self.obtener_producto_seleccionado()
        if not producto_id:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de eliminar este producto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            from services.producto_service import ProductoService

            service = ProductoService(self.session)
            service.delete_producto(producto_id)
            self.cargar_productos()

    def abrir_gestor_categorias(self):
        """Abre el diálogo de gestión de categorías"""
        dialog = CategoriaDialog(self.session, self)
        dialog.exec()
        self.cargar_productos()


class ProductoDialog(QDialog):
    """Diálogo para agregar/editar productos"""

    def __init__(self, session, parent=None, producto_id=None):
        super().__init__(parent)
        self.session = session
        self.producto_id = producto_id
        self.setWindowTitle(
            "Agregar Producto" if not producto_id else "Editar Producto"
        )
        self.setMinimumWidth(450)
        self.init_ui()

        if producto_id:
            self.cargar_producto()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QFormLayout()
        self.setLayout(layout)

        self.codigo_input = QLineEdit()
        layout.addRow("Código:", self.codigo_input)

        self.nombre_input = QLineEdit()
        layout.addRow("Nombre:", self.nombre_input)

        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0, 999999)
        self.precio_input.setDecimals(2)
        layout.addRow("Precio:", self.precio_input)

        self.costo_input = QDoubleSpinBox()
        self.costo_input.setRange(0, 999999)
        self.costo_input.setDecimals(2)
        layout.addRow("Costo:", self.costo_input)

        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 999999)
        layout.addRow("Stock:", self.stock_input)

        cat_layout = QHBoxLayout()
        self.cat_combo = QComboBox()
        self.cat_combo.addItem("Sin categoría", None)
        self._cargar_categorias()
        cat_layout.addWidget(self.cat_combo)

        btn_nueva_cat = QPushButton("+")
        btn_nueva_cat.setFixedWidth(40)
        btn_nueva_cat.setToolTip("Crear nueva categoría")
        btn_nueva_cat.clicked.connect(self._crear_categoria_rapida)
        cat_layout.addWidget(btn_nueva_cat)

        layout.addRow("Categoría:", cat_layout)

        self.aplica_iva = QCheckBox("Aplica IVA (19%)")
        self.aplica_iva.setChecked(True)
        layout.addRow("", self.aplica_iva)

        btn_layout = QHBoxLayout()

        btn_guardar = QPushButton("Guardar")
        btn_guardar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 10px;"
        )
        btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_guardar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(
            "background-color: #95a5a6; color: white; padding: 10px;"
        )
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        layout.addRow("", btn_layout)

    def _cargar_categorias(self):
        """Carga las categorías en el combo"""
        self.cat_combo.clear()
        self.cat_combo.addItem("Sin categoría", None)
        from services.producto_service import CategoriaService

        service = CategoriaService(self.session)
        cats = service.get_all()
        for cat in cats:
            self.cat_combo.addItem(cat.nombre, cat.id)

    def _crear_categoria_rapida(self):
        """Crea una categoría rápida"""
        nombre, ok = QInputDialog.getText(
            self, "Nueva Categoría", "Nombre de la categoría:"
        )
        if ok and nombre.strip():
            try:
                from services.producto_service import CategoriaService

                service = CategoriaService(self.session)
                service.create(nombre.strip())
                self._cargar_categorias()
                for i in range(self.cat_combo.count()):
                    if self.cat_combo.itemText(i) == nombre.strip():
                        self.cat_combo.setCurrentIndex(i)
                        break
                QMessageBox.information(self, "Éxito", f"Categoría '{nombre}' creada")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))

    def cargar_producto(self):
        """Carga los datos del producto a editar"""
        from services.producto_service import ProductoService

        service = ProductoService(self.session)
        producto = service.get_producto_by_id(self.producto_id)

        if producto:
            self.codigo_input.setText(producto.codigo)
            self.nombre_input.setText(producto.nombre)
            self.precio_input.setValue(producto.precio)
            self.costo_input.setValue(producto.costo)
            self.stock_input.setValue(producto.stock)
            self.aplica_iva.setChecked(producto.aplica_iva)

            if producto.categoria_id:
                for i in range(self.cat_combo.count()):
                    if self.cat_combo.currentData() == producto.categoria_id:
                        self.cat_combo.setCurrentIndex(i)
                        break

    def guardar(self):
        """Guarda el producto"""
        from services.producto_service import ProductoService

        codigo = self.codigo_input.text().strip()
        nombre = self.nombre_input.text().strip()
        precio = self.precio_input.value()
        costo = self.costo_input.value()
        stock = self.stock_input.value()
        aplica_iva = self.aplica_iva.isChecked()
        categoria_id = self.cat_combo.currentData()

        if not codigo or not nombre:
            QMessageBox.warning(self, "Error", "Código y nombre son requeridos")
            return

        service = ProductoService(self.session)

        try:
            if self.producto_id:
                service.update_producto(
                    self.producto_id,
                    codigo=codigo,
                    nombre=nombre,
                    precio=precio,
                    costo=costo,
                    stock=stock,
                    aplica_iva=aplica_iva,
                    categoria_id=categoria_id,
                )
            else:
                service.create_producto(
                    codigo, nombre, precio, costo, stock, aplica_iva, categoria_id
                )

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")


class CategoriaDialog(QDialog):
    """Diálogo para gestionar categorías"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Gestión de Categorías")
        self.setMinimumWidth(500)
        self.init_ui()
        self.cargar_categorias()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()

        btn_agregar = QPushButton("+ Agregar")
        btn_agregar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px;"
        )
        btn_agregar.clicked.connect(self.agregar_categoria)
        btn_layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 8px;"
        )
        btn_eliminar.clicked.connect(self.eliminar_categoria)
        btn_layout.addWidget(btn_eliminar)

        btn_layout.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)

    def cargar_categorias(self):
        """Carga las categorías"""
        from services.producto_service import CategoriaService

        service = CategoriaService(self.session)
        cats = service.get_all()

        self.tabla.setRowCount(len(cats))
        for i, cat in enumerate(cats):
            self.tabla.setItem(i, 0, QTableWidgetItem(str(cat.id)))
            self.tabla.setItem(i, 1, QTableWidgetItem(cat.nombre))
            self.tabla.setItem(i, 2, QTableWidgetItem(cat.descripcion or ""))

    def agregar_categoria(self):
        """Agrega una nueva categoría"""
        nombre, ok1 = QInputDialog.getText(self, "Nueva Categoría", "Nombre:")
        if not ok1 or not nombre.strip():
            return

        desc, ok2 = QInputDialog.getText(
            self, "Nueva Categoría", "Descripción (opcional):"
        )
        desc = desc.strip() if ok2 else ""

        try:
            from services.producto_service import CategoriaService

            service = CategoriaService(self.session)
            service.create(nombre.strip(), desc)
            self.cargar_categorias()
            QMessageBox.information(self, "Éxito", "Categoría creada")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def eliminar_categoria(self):
        """Elimina la categoría seleccionada"""
        row = self.tabla.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccione una categoría")
            return

        cat_id = int(self.tabla.item(row, 0).text())
        cat_nombre = self.tabla.item(row, 1).text()

        resp = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar la categoría '{cat_nombre}'?"
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        try:
            from services.producto_service import CategoriaService

            service = CategoriaService(self.session)
            service.delete(cat_id)
            self.cargar_categorias()
            QMessageBox.information(self, "Éxito", "Categoría eliminada")
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

```

---

## 17. ui/corte_view.py — Corte de Caja

```python
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt
from datetime import datetime


class CorteView(QWidget):
    """Vista de corte de caja"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_estadisticas()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Corte de Caja")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        self.info_widget = QWidget()
        self.info_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout()
        self.info_widget.setLayout(info_layout)

        self.lbl_fecha = QLabel(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        self.lbl_fecha.setStyleSheet("font-size: 18px;")
        info_layout.addWidget(self.lbl_fecha)

        self.lbl_estado = QLabel("Caja: ABIERTA")
        self.lbl_estado.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #27ae60;"
        )
        info_layout.addWidget(self.lbl_estado)

        self.lbl_total = QLabel("Total vendido: $0.00")
        self.lbl_total.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #27ae60;"
        )
        info_layout.addWidget(self.lbl_total)

        self.lbl_num_ventas = QLabel("Número de ventas: 0")
        self.lbl_num_ventas.setStyleSheet("font-size: 18px;")
        info_layout.addWidget(self.lbl_num_ventas)

        layout.addWidget(self.info_widget)

        botones_layout = QHBoxLayout()

        self.btn_abrir = QPushButton("ABRIR CAJA")
        self.btn_abrir.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_abrir.clicked.connect(self.abrir_caja)
        botones_layout.addWidget(self.btn_abrir)

        self.btn_cerrar = QPushButton("CERRAR CAJA")
        self.btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_cerrar.clicked.connect(self.cerrar_caja)
        botones_layout.addWidget(self.btn_cerrar)

        layout.addLayout(botones_layout)

        self.btn_gasto = QPushButton("Registrar Gasto de Caja")
        self.btn_gasto.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_gasto.clicked.connect(self.registrar_gasto)
        layout.addWidget(self.btn_gasto)

        self.btn_anular = QPushButton("Anular Venta")
        self.btn_anular.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.btn_anular.clicked.connect(self.anular_venta)
        layout.addWidget(self.btn_anular)

        self.btn_facturas = QPushButton("Ver Facturas del Día")
        self.btn_facturas.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.btn_facturas.clicked.connect(self.ver_facturas_dia)
        layout.addWidget(self.btn_facturas)

        self.lbl_ganancia = QLabel("Ganancia neta: $0.00")
        self.lbl_ganancia.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #8e44ad; padding: 8px;"
        )
        layout.addWidget(self.lbl_ganancia)

        historial_label = QLabel("Ventas del día")
        historial_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 20px;"
        )
        layout.addWidget(historial_label)

        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(3)
        self.tabla_ventas.setHorizontalHeaderLabels(["ID", "Hora", "Total"])
        self.tabla_ventas.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_ventas.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.tabla_ventas)

        gastos_label = QLabel("Gastos del día")
        gastos_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-top: 15px;"
        )
        layout.addWidget(gastos_label)

        self.tabla_gastos = QTableWidget()
        self.tabla_gastos.setColumnCount(3)
        self.tabla_gastos.setHorizontalHeaderLabels(["Hora", "Concepto", "Monto"])
        self.tabla_gastos.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_gastos.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.tabla_gastos)

    def cargar_estadisticas(self):
        """Carga las estadísticas del día"""
        from services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        caja_abierta = service.esta_caja_abierta()

        if caja_abierta:
            self.lbl_estado.setText("Caja: ABIERTA")
            self.lbl_estado.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #27ae60;"
            )
            self.btn_abrir.setEnabled(False)
            self.btn_cerrar.setEnabled(True)
            self.btn_gasto.setEnabled(True)
            self.btn_anular.setEnabled(True)
        else:
            self.lbl_estado.setText("Caja: CERRADA")
            self.lbl_estado.setStyleSheet(
                "font-size: 18px; font-weight: bold; color: #e74c3c;"
            )
            self.btn_abrir.setEnabled(True)
            self.btn_cerrar.setEnabled(False)
            self.btn_gasto.setEnabled(False)
            self.btn_anular.setEnabled(False)

        self.lbl_total.setText(f"Total vendido: ${stats['total']:.2f}")
        self.lbl_num_ventas.setText(f"Número de ventas: {stats['num_ventas']}")
        self.lbl_ganancia.setText(
            f"Ganancia neta: ${stats['ganancia_neta']:.2f} "
            f"(Gastos: ${stats['total_gastos']:.2f})"
        )

        ventas = stats["ventas"]
        self.tabla_ventas.setRowCount(len(ventas))

        for i, venta in enumerate(ventas):
            self.tabla_ventas.setItem(i, 0, QTableWidgetItem(str(venta.id)))
            self.tabla_ventas.setItem(
                i, 1, QTableWidgetItem(venta.fecha.strftime("%H:%M:%S"))
            )
            self.tabla_ventas.setItem(i, 2, QTableWidgetItem(f"${venta.total:.2f}"))

        gastos = stats["gastos"]
        self.tabla_gastos.setRowCount(len(gastos))

        for i, gasto in enumerate(gastos):
            self.tabla_gastos.setItem(
                i, 0, QTableWidgetItem(gasto.fecha.strftime("%H:%M"))
            )
            self.tabla_gastos.setItem(i, 1, QTableWidgetItem(gasto.concepto))
            self.tabla_gastos.setItem(i, 2, QTableWidgetItem(f"${gasto.monto:.2f}"))

    def abrir_caja(self):
        """Abre la caja"""
        from services.corte_service import CorteCajaService

        service = CorteCajaService(self.session)
        service.abrir_caja()

        QMessageBox.information(
            self,
            "Caja Abierta",
            "La caja ha sido abierta correctamente.\n\nYa puedes comenzar a registrar ventas.",
        )

        self.cargar_estadisticas()

    def registrar_gasto(self):
        """Abre diálogo para registrar gasto"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Registrar Gasto de Caja")
        dialog.setMinimumWidth(380)
        layout = QFormLayout()
        dialog.setLayout(layout)

        info = QLabel("El monto será descontado de la ganancia del día.")
        info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addRow("", info)

        concepto_input = QLineEdit()
        concepto_input.setPlaceholderText("Ej: Compra de bolsas, Pasaje, Luz...")
        concepto_input.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addRow("Concepto:", concepto_input)

        monto_input = QDoubleSpinBox()
        monto_input.setRange(0.01, 999999)
        monto_input.setDecimals(2)
        monto_input.setStyleSheet("padding: 8px; font-size: 16px;")
        layout.addRow("Monto:", monto_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("REGISTRAR")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(
            "background-color: #e67e22; color: white; padding: 8px 16px;"
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow("", buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            concepto = concepto_input.text().strip()
            monto = monto_input.value()
            if not concepto:
                QMessageBox.warning(self, "Error", "El concepto es obligatorio")
                return
            if monto <= 0:
                QMessageBox.warning(self, "Error", "El monto debe ser mayor a cero")
                return
            try:
                from services.corte_service import CorteCajaService

                service = CorteCajaService(self.session)
                service.registrar_gasto(concepto, monto)
                self.cargar_estadisticas()
                QMessageBox.information(
                    self,
                    "Gasto Registrado",
                    f"Gasto registrado:\n{concepto}: ${monto:.2f}",
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def cerrar_caja(self):
        """Cierra la caja"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de cerrar la caja?\nSe registrará el corte del día.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            from services.corte_service import CorteCajaService

            service = CorteCajaService(self.session)
            stats = service.get_estadisticas_hoy()

            corte = service.cerrar_caja()

            if corte:
                QMessageBox.information(
                    self,
                    "Corte de Caja",
                    f"Corte de caja cerrado!\n\n"
                    f"Total vendido: ${corte.total_ventas:.2f}\n"
                    f"Gastos: ${stats['total_gastos']:.2f}\n"
                    f"Ganancia neta: ${stats['ganancia_neta']:.2f}\n\n"
                    f"Ventas: {stats['num_ventas']}",
                )
            else:
                QMessageBox.warning(self, "Error", "No hay caja abierta")

            self.cargar_estadisticas()

    def anular_venta(self):
        """Anula una venta del día"""
        from services.corte_service import CorteCajaService
        from services.producto_service import VentaService
        from ui.ventas_view import VentasView

        service = CorteCajaService(self.session)
        stats = service.get_estadisticas_hoy()
        ventas = stats["ventas"]

        if not ventas:
            QMessageBox.warning(self, "Sin ventas", "No hay ventas registradas hoy")
            return

        from PySide6.QtWidgets import QInputDialog

        venta_ids = [str(v.id) for v in ventas]
        venta_id_str, ok = QInputDialog.getItem(
            self,
            "Anular Venta",
            "Seleccione la venta a anular:",
            venta_ids,
            0,
            False,
        )

        if not ok or not venta_id_str:
            return

        venta_id = int(venta_id_str)

        respuesta = QMessageBox.question(
            self,
            "Confirmar Anulación",
            f"¿Está seguro de anular la venta #{venta_id}?\n"
            "El stock de los productos será restaurado.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:
            venta_service = VentaService(self.session)
            venta_service.anular_venta(venta_id)
            QMessageBox.information(
                self,
                "Venta Anulada",
                f"Venta #{venta_id} ha sido anulada.\nEl stock ha sido restaurado.",
            )
            self.cargar_estadisticas()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al anular venta: {str(e)}")

    def ver_facturas_dia(self):
        """Abre o genera el PDF de facturas del día"""
        from utils.factura_diaria import get_factura_diaria_path
        import subprocess
        import os

        pdf_path = get_factura_diaria_path()
        if not os.path.exists(pdf_path):
            QMessageBox.information(
                self,
                "Sin facturas",
                "No hay facturas registradas para el día de hoy.",
            )
            return

        try:
            if os.name == "nt":
                os.startfile(pdf_path)
            else:
                subprocess.run(["xdg-open", pdf_path])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

```

---

## 18. ui/historial_view.py — Historial

```python
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDateEdit,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt, QDate
from datetime import datetime, timedelta
import os


class HistorialView(QWidget):
    """Vista de historial de cierres y ranking de productos"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_historial()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Historial de Cierres")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        filtros_layout = QHBoxLayout()

        filtros_layout.addWidget(QLabel("Desde:"))
        self.desde_edit = QDateEdit()
        self.desde_edit.setCalendarPopup(True)
        self.desde_edit.setDate(QDate.currentDate().addDays(-30))
        filtros_layout.addWidget(self.desde_edit)

        filtros_layout.addWidget(QLabel("Hasta:"))
        self.hasta_edit = QDateEdit()
        self.hasta_edit.setCalendarPopup(True)
        self.hasta_edit.setDate(QDate.currentDate())
        filtros_layout.addWidget(self.hasta_edit)

        self.filtro_rapido = QComboBox()
        self.filtro_rapido.addItems(
            [
                "Filtro rápido...",
                "Este mes",
                "Mes anterior",
                "Últimos 3 meses",
                "Este año",
            ]
        )
        self.filtro_rapido.currentTextChanged.connect(self.on_filtro_rapido_changed)
        filtros_layout.addWidget(self.filtro_rapido)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px 16px;"
        )
        btn_filtrar.clicked.connect(self.cargar_historial)
        filtros_layout.addWidget(btn_filtrar)

        btn_exportar = QPushButton("Exportar Excel")
        btn_exportar.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 8px 16px;"
        )
        btn_exportar.clicked.connect(self.exportar_excel)
        filtros_layout.addWidget(btn_exportar)

        filtros_layout.addStretch()
        layout.addLayout(filtros_layout)

        self.resumen_widget = QWidget()
        self.resumen_widget.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        resumen_layout = QHBoxLayout()
        self.resumen_widget.setLayout(resumen_layout)

        self.lbl_ventas = QLabel("Ventas brutas: $0.00")
        self.lbl_ventas.setStyleSheet(
            "color: white; font-size: 16px; font-weight: bold;"
        )
        resumen_layout.addWidget(self.lbl_ventas)

        self.lbl_gastos = QLabel("Gastos: $0.00")
        self.lbl_gastos.setStyleSheet(
            "color: #e74c3c; font-size: 16px; font-weight: bold;"
        )
        resumen_layout.addWidget(self.lbl_gastos)

        self.lbl_ganancia = QLabel("Ganancia neta: $0.00")
        self.lbl_ganancia.setStyleSheet(
            "color: #2ecc71; font-size: 16px; font-weight: bold;"
        )
        resumen_layout.addWidget(self.lbl_ganancia)

        resumen_layout.addStretch()

        self.lbl_resumen_datos = QLabel("Cierres: 0 | Ventas: 0")
        self.lbl_resumen_datos.setStyleSheet("color: #bdc3c7; font-size: 14px;")
        resumen_layout.addWidget(self.lbl_resumen_datos)

        layout.addWidget(self.resumen_widget)

        cierres_label = QLabel("Cierres del período")
        cierres_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 15px;"
        )
        layout.addWidget(cierres_label)

        self.tabla_cierres = QTableWidget()
        self.tabla_cierres.setColumnCount(5)
        self.tabla_cierres.setHorizontalHeaderLabels(
            ["ID", "Apertura", "Cierre", "Ventas brutas", "Ganancia neta"]
        )
        self.tabla_cierres.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_cierres.setStyleSheet("font-size: 14px;")
        self.tabla_cierres.setMinimumHeight(200)
        layout.addWidget(self.tabla_cierres)

        ranking_label = QLabel("Ranking de productos")
        ranking_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin-top: 15px;"
        )
        layout.addWidget(ranking_label)

        self.tabla_ranking = QTableWidget()
        self.tabla_ranking.setColumnCount(4)
        self.tabla_ranking.setHorizontalHeaderLabels(
            ["#", "Producto", "Unidades vendidas", "Ingresos"]
        )
        self.tabla_ranking.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_ranking.setStyleSheet("font-size: 14px;")
        self.tabla_ranking.setMaximumHeight(250)
        layout.addWidget(self.tabla_ranking)

    def on_filtro_rapido_changed(self, text):
        """Aplica filtro rápido"""
        today = QDate.currentDate()
        if text == "Este mes":
            self.desde_edit.setDate(QDate(today.year(), today.month(), 1))
            self.hasta_edit.setDate(today)
        elif text == "Mes anterior":
            first_this_month = QDate(today.year(), today.month(), 1)
            last_prev_month = first_this_month.addDays(-1)
            first_prev_month = QDate(last_prev_month.year(), last_prev_month.month(), 1)
            self.desde_edit.setDate(first_prev_month)
            self.hasta_edit.setDate(last_prev_month)
        elif text == "Últimos 3 meses":
            self.desde_edit.setDate(today.addDays(-90))
            self.hasta_edit.setDate(today)
        elif text == "Este año":
            self.desde_edit.setDate(QDate(today.year(), 1, 1))
            self.hasta_edit.setDate(today)

    def cargar_historial(self):
        """Carga el historial de cierres"""
        desde = self.desde_edit.date().toPython()
        hasta = self.hasta_edit.date().toPython()
        hasta = datetime.combine(hasta, datetime.max.time())

        from models.producto import CorteCaja, VentaItem, Venta, Producto
        from sqlalchemy import and_

        cierres = (
            self.session.query(CorteCaja)
            .filter(
                CorteCaja.fecha_cierre.isnot(None),
                CorteCaja.fecha_apertura
                >= datetime.combine(desde, datetime.min.time()),
                CorteCaja.fecha_apertura <= hasta,
            )
            .order_by(CorteCaja.fecha_apertura.desc())
            .all()
        )

        self.tabla_cierres.setRowCount(len(cierres))

        total_ventas = 0
        total_gastos = 0
        total_cierres = len(cierres)
        total_num_ventas = 0

        for i, corte in enumerate(cierres):
            self.tabla_cierres.setItem(i, 0, QTableWidgetItem(str(corte.id)))
            self.tabla_cierres.setItem(
                i, 1, QTableWidgetItem(corte.fecha_apertura.strftime("%d/%m/%Y %H:%M"))
            )
            self.tabla_cierres.setItem(
                i,
                2,
                QTableWidgetItem(corte.fecha_cierre.strftime("%d/%m/%Y %H:%M"))
                if corte.fecha_cierre
                else QTableWidgetItem("—"),
            )
            self.tabla_cierres.setItem(
                i, 3, QTableWidgetItem(f"${corte.total_ventas:.2f}")
            )
            ganancia = getattr(corte, "ganancia_neta", corte.total_ventas)
            self.tabla_cierres.setItem(i, 4, QTableWidgetItem(f"${ganancia:.2f}"))

            total_ventas += corte.total_ventas
            total_gastos += getattr(corte, "total_gastos", 0)
            total_num_ventas += corte.numero_ventas

        self.lbl_ventas.setText(f"Ventas brutas: ${total_ventas:.2f}")
        self.lbl_gastos.setText(f"Gastos: ${total_gastos:.2f}")
        self.lbl_ganancia.setText(f"Ganancia neta: ${total_ventas - total_gastos:.2f}")
        self.lbl_resumen_datos.setText(
            f"Cierres: {total_cierres} | Ventas: {total_num_ventas}"
        )

        self.cargar_ranking(desde, hasta)

    def cargar_ranking(self, desde, hasta):
        """Carga el ranking de productos"""
        desde_dt = datetime.combine(desde, datetime.min.time())
        hasta_dt = datetime.combine(hasta, datetime.max.time())

        from models.producto import VentaItem, Venta, Producto
        from sqlalchemy import func

        ranking = (
            self.session.query(
                Producto.nombre,
                func.sum(VentaItem.cantidad).label("unidades"),
                func.sum(VentaItem.cantidad * VentaItem.precio).label("ingresos"),
            )
            .join(VentaItem, VentaItem.producto_id == Producto.id)
            .join(Venta, Venta.id == VentaItem.venta_id)
            .filter(
                Venta.fecha >= desde_dt,
                Venta.fecha <= hasta_dt,
                Venta.anulada == False,
            )
            .group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(VentaItem.cantidad * VentaItem.precio).desc())
            .limit(50)
            .all()
        )

        self.tabla_ranking.setRowCount(len(ranking))

        for i, item in enumerate(ranking):
            self.tabla_ranking.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.tabla_ranking.setItem(i, 1, QTableWidgetItem(item.nombre))
            self.tabla_ranking.setItem(i, 2, QTableWidgetItem(str(int(item.unidades))))
            self.tabla_ranking.setItem(i, 3, QTableWidgetItem(f"${item.ingresos:.2f}"))

    def exportar_excel(self):
        """Exporta el historial a Excel"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill

            wb = Workbook()

            desde = self.desde_edit.date().toPython()
            hasta = self.hasta_edit.date().toPython()
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")

            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            filename = os.path.join(downloads, f"TuCajero_Historial_{fecha_str}.xlsx")

            ws_cierres = wb.active
            ws_cierres.title = "Cierres"

            headers = [
                "ID",
                "Apertura",
                "Cierre",
                "Ventas brutas",
                "Gastos",
                "Ganancia neta",
                "N° Ventas",
            ]
            ws_cierres.append(headers)

            for cell in ws_cierres[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    start_color="3498db", end_color="3498db", fill_type="solid"
                )
                cell.alignment = Alignment(horizontal="center")

            for row in range(self.tabla_cierres.rowCount()):
                row_data = []
                for col in range(self.tabla_cierres.columnCount()):
                    item = self.tabla_cierres.item(row, col)
                    row_data.append(item.text() if item else "")
                total = (
                    self.tabla_cierres.item(row, 3).text()
                    if self.tabla_cierres.item(row, 3)
                    else "$0.00"
                )
                row_data.extend(["$0.00", "$0.00", "0"])
                ws_cierres.append(row_data)

            ws_ranking = wb.create_sheet("Ranking")
            ranking_headers = ["#", "Producto", "Unidades vendidas", "Ingresos"]
            ws_ranking.append(ranking_headers)

            for cell in ws_ranking[1]:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    start_color="27ae60", end_color="27ae60", fill_type="solid"
                )

            for row in range(self.tabla_ranking.rowCount()):
                row_data = []
                for col in range(self.tabla_ranking.columnCount()):
                    item = self.tabla_ranking.item(row, col)
                    row_data.append(item.text() if item else "")
                ws_ranking.append(row_data)

            for ws in [ws_cierres, ws_ranking]:
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    ws.column_dimensions[column_letter].width = min(max_length + 2, 50)

            wb.save(filename)
            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"Archivo exportado a:\n{filename}",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error al exportar",
                f"No se pudo exportar el archivo:\n{str(e)}",
            )

```

---

## 19. ui/inventario_view.py — Inventario

```python
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QDialog,
    QFormLayout,
    QSpinBox,
    QHeaderView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class InventarioView(QWidget):
    """Vista de inventario"""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.init_ui()
        self.cargar_inventario()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Inventario")
        titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(titulo)

        info_label = QLabel("Seleccione un producto y elija Entrada o Salida")
        info_label.setStyleSheet("color: #7f8c8d; padding-bottom: 10px;")
        layout.addWidget(info_label)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Código", "Producto", "Stock", "Precio"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setStyleSheet("font-size: 14px;")
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()

        btn_entrada = QPushButton("+ Entrada")
        btn_entrada.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 12px; font-weight: bold;"
        )
        btn_entrada.clicked.connect(lambda: self.movimiento_inventario("entrada"))
        btn_layout.addWidget(btn_entrada)

        btn_salida = QPushButton("- Salida")
        btn_salida.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 12px; font-weight: bold;"
        )
        btn_salida.clicked.connect(lambda: self.movimiento_inventario("salida"))
        btn_layout.addWidget(btn_salida)

        btn_layout.addStretch()

        btn_actualizar = QPushButton("Actualizar")
        btn_actualizar.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px;"
        )
        btn_actualizar.clicked.connect(self.cargar_inventario)
        btn_layout.addWidget(btn_actualizar)

        layout.addLayout(btn_layout)

    def cargar_inventario(self):
        """Carga el inventario desde la base de datos"""
        from services.producto_service import InventarioService

        service = InventarioService(self.session)
        productos = service.get_all_productos()

        self.tabla.setRowCount(len(productos))

        for i, p in enumerate(productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.nombre))

            stock_item = QTableWidgetItem(str(p.stock))
            if p.stock <= 0:
                stock_item.setBackground(QColor("#ffcccc"))
            elif p.stock < 5:
                stock_item.setBackground(QColor("#fff3cd"))
            self.tabla.setItem(i, 2, stock_item)

            self.tabla.setItem(i, 3, QTableWidgetItem(f"${p.precio:.2f}"))

    def recargar_inventario(self):
        """Recarga el inventario (para auto-actualizacion despues de venta)"""
        self.cargar_inventario()

    def obtener_producto_seleccionado(self):
        """Retorna el ID del producto seleccionado"""
        row = self.tabla.currentRow()
        if row >= 0:
            item = self.tabla.item(row, 0)
            if item is not None:
                codigo = item.text()
                from services.producto_service import ProductoService

                service = ProductoService(self.session)
                producto = service.get_producto_by_codigo(codigo)
                return producto
        return None

    def movimiento_inventario(self, tipo):
        """Abre el diálogo para registrar movimiento"""
        producto = self.obtener_producto_seleccionado()
        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return

        dialog = MovimientoDialog(self.session, producto, tipo, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cargar_inventario()


class MovimientoDialog(QDialog):
    """Diálogo para registrar movimientos de inventario"""

    def __init__(self, session, producto, tipo, parent=None):
        super().__init__(parent)
        self.session = session
        self.producto = producto
        self.tipo = tipo
        color = "#27ae60" if tipo == "entrada" else "#e74c3c"
        self.setWindowTitle(
            f"{'Entrada' if tipo == 'entrada' else 'Salida'} de Inventario"
        )
        self.setMinimumWidth(350)
        self.init_ui(color)

    def init_ui(self, color):
        """Inicializa la interfaz"""
        layout = QFormLayout()
        self.setLayout(layout)

        info_box = QWidget()
        info_box.setStyleSheet(
            f"background-color: #f8f9fa; padding: 10px; border-radius: 5px;"
        )
        info_layout = QVBoxLayout()
        info_box.setLayout(info_layout)

        info_layout.addWidget(QLabel(f"<b>Producto:</b> {self.producto.nombre}"))
        info_layout.addWidget(QLabel(f"<b>Código:</b> {self.producto.codigo}"))
        info_layout.addWidget(QLabel(f"<b>Stock actual:</b> {self.producto.stock}"))

        layout.addRow("", info_box)

        self.cantidad_input = QSpinBox()
        self.cantidad_input.setRange(1, 999999)
        self.cantidad_input.setStyleSheet("padding: 8px; font-size: 16px;")
        self.cantidad_input.setFocus()
        layout.addRow("Cantidad:", self.cantidad_input)

        btn_layout = QHBoxLayout()

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet(
            f"background-color: {color}; color: white; padding: 12px; font-weight: bold;"
        )
        btn_aceptar.clicked.connect(self.aceptar)
        btn_layout.addWidget(btn_aceptar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(
            "background-color: #95a5a6; color: white; padding: 12px;"
        )
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        layout.addRow("", btn_layout)

    def aceptar(self):
        """Registra el movimiento"""
        from services.producto_service import InventarioService

        cantidad = self.cantidad_input.value()

        if cantidad <= 0:
            QMessageBox.warning(self, "Error", "Cantidad inválida")
            return

        try:
            service = InventarioService(self.session)
            if self.tipo == "entrada":
                service.entrada_inventario(self.producto.id, cantidad)
            else:
                service.salida_inventario(self.producto.id, cantidad)

            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

```

---

## 20. ui/buscador_productos.py

```python
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QTabWidget,
    QWidget,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor

COLORES_CATEGORIA = [
    "#3498db",
    "#27ae60",
    "#e67e22",
    "#8e44ad",
    "#e74c3c",
    "#16a085",
    "#d35400",
    "#2980b9",
    "#1abc9c",
    "#f39c12",
]


class BuscadorProductosDialog(QDialog):
    """Diálogo de búsqueda con 3 modos: código, nombre y categoría"""

    def __init__(self, productos, session=None, parent=None):
        super().__init__(parent)
        self.productos = productos
        self.session = session
        self.producto_seleccionado = None
        self.setWindowTitle("Buscar Producto")
        self.setMinimumSize(620, 500)
        self.init_ui()
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._filtrar_debounced)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Buscar Producto")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; padding-bottom: 4px;")
        layout.addWidget(titulo)

        search_layout = QHBoxLayout()
        self.buscador_input = QLineEdit()
        self.buscador_input.setPlaceholderText(
            "Buscar por código o nombre del producto..."
        )
        self.buscador_input.setStyleSheet("padding: 10px; font-size: 14px;")
        self.buscador_input.textChanged.connect(self._on_text_changed)
        self.buscador_input.returnPressed.connect(self._seleccionar_primero)
        search_layout.addWidget(self.buscador_input)
        layout.addLayout(search_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.tabs)

        tab_resultados = QWidget()
        tab_resultados_layout = QVBoxLayout()
        tab_resultados.setLayout(tab_resultados_layout)

        self.lbl_resultados = QLabel("Mostrando todos los productos")
        self.lbl_resultados.setStyleSheet(
            "color: #7f8c8d; font-size: 12px; padding: 2px;"
        )
        tab_resultados_layout.addWidget(self.lbl_resultados)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Código", "Nombre", "Stock", "Precio"])
        self.tabla.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.doubleClicked.connect(self.seleccionar_producto)
        self.tabla.setStyleSheet("font-size: 13px;")
        tab_resultados_layout.addWidget(self.tabla)
        self.tabs.addTab(tab_resultados, "🔍  Búsqueda")

        tab_categorias = QWidget()
        tab_cat_layout = QVBoxLayout()
        tab_categorias.setLayout(tab_cat_layout)

        lbl_cat = QLabel("Selecciona una categoría para filtrar productos:")
        lbl_cat.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 2px;")
        tab_cat_layout.addWidget(lbl_cat)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(120)
        scroll.setStyleSheet("border: none;")
        self.cat_buttons_widget = QWidget()
        self.cat_buttons_layout = QHBoxLayout()
        self.cat_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.cat_buttons_widget.setLayout(self.cat_buttons_layout)
        scroll.setWidget(self.cat_buttons_widget)
        tab_cat_layout.addWidget(scroll)

        self.tabla_cat = QTableWidget()
        self.tabla_cat.setColumnCount(4)
        self.tabla_cat.setHorizontalHeaderLabels(
            ["Código", "Nombre", "Stock", "Precio"]
        )
        self.tabla_cat.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.tabla_cat.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_cat.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_cat.doubleClicked.connect(self._seleccionar_de_cat)
        self.tabla_cat.setStyleSheet("font-size: 13px;")
        tab_cat_layout.addWidget(self.tabla_cat)
        self.tabs.addTab(tab_categorias, "🏷️  Categorías")

        btn_layout = QHBoxLayout()
        btn_seleccionar = QPushButton("Seleccionar")
        btn_seleccionar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_seleccionar.clicked.connect(self.seleccionar_producto)
        btn_layout.addWidget(btn_seleccionar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)

        self.llenar_tabla(self.productos, self.tabla)
        self._cargar_categorias()
        self.buscador_input.setFocus()

    def _on_text_changed(self):
        self._timer.start(200)

    def _filtrar_debounced(self):
        texto = self.buscador_input.text().strip().lower()
        if not texto:
            productos_filtrados = self.productos
            self.lbl_resultados.setText(
                f"Mostrando todos los productos ({len(self.productos)})"
            )
        else:
            productos_filtrados = [
                p
                for p in self.productos
                if texto in p.codigo.lower() or texto in p.nombre.lower()
            ]
            self.lbl_resultados.setText(
                f'{len(productos_filtrados)} resultado(s) para "{texto}"'
            )
        self.llenar_tabla(productos_filtrados, self.tabla)
        if productos_filtrados:
            self.tabla.selectRow(0)

    def _seleccionar_primero(self):
        """Al presionar Enter selecciona el primer resultado"""
        if self.tabla.rowCount() > 0:
            self.tabla.selectRow(0)
            self.seleccionar_producto()

    def llenar_tabla(self, productos, tabla):
        tabla.setRowCount(len(productos))
        for i, p in enumerate(productos):
            tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            tabla.setItem(i, 1, QTableWidgetItem(p.nombre))
            stock_item = QTableWidgetItem(str(p.stock))
            if p.stock <= 0:
                stock_item.setForeground(QColor("#e74c3c"))
            elif p.stock < 5:
                stock_item.setForeground(QColor("#e67e22"))
            tabla.setItem(i, 2, stock_item)
            tabla.setItem(i, 3, QTableWidgetItem(f"${p.precio:,.2f}"))

    def _cargar_categorias(self):
        """Carga los botones de categorías"""
        if not self.session:
            return
        try:
            from models.producto import Categoria

            categorias = (
                self.session.query(Categoria).order_by(Categoria.nombre.asc()).all()
            )
            while self.cat_buttons_layout.count():
                item = self.cat_buttons_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            btn_todos = QPushButton("Todos")
            btn_todos.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 16px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #34495e; }
            """)
            btn_todos.clicked.connect(
                lambda: self.llenar_tabla(self.productos, self.tabla_cat)
            )
            self.cat_buttons_layout.addWidget(btn_todos)

            for i, cat in enumerate(categorias):
                color = cat.color or COLORES_CATEGORIA[i % len(COLORES_CATEGORIA)]
                btn = QPushButton(f"🏷 {cat.nombre}")
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        padding: 8px 16px;
                        border-radius: 16px;
                        font-size: 12px;
                    }}
                    QPushButton:hover {{ opacity: 0.85; }}
                """)
                btn.clicked.connect(
                    lambda checked, c=cat: self._filtrar_por_categoria(c)
                )
                self.cat_buttons_layout.addWidget(btn)
        except Exception as e:
            print(f"[WARN] No se pudieron cargar categorías: {e}")

    def _filtrar_por_categoria(self, categoria):
        """Filtra productos por categoría"""
        if not self.session:
            return
        try:
            from repositories.producto_repo import ProductoRepository

            repo = ProductoRepository(self.session)
            productos = repo.search_por_categoria(categoria.id)
            self.llenar_tabla(productos, self.tabla_cat)
        except Exception as e:
            print(f"[WARN] Error filtrando por categoría: {e}")

    def seleccionar_producto(self):
        """Selecciona de la tab activa"""
        tab_actual = self.tabs.currentIndex()
        if tab_actual == 0:
            self._seleccionar_de_tabla(self.tabla)
        else:
            self._seleccionar_de_cat()

    def _seleccionar_de_cat(self):
        self._seleccionar_de_tabla(self.tabla_cat)

    def _seleccionar_de_tabla(self, tabla):
        row = tabla.currentRow()
        if row >= 0:
            item = tabla.item(row, 0)
            if item is not None:
                codigo = item.text()
                for p in self.productos:
                    if p.codigo == codigo:
                        self.producto_seleccionado = p
                        self.accept()
                        return
                if self.session:
                    from repositories.producto_repo import ProductoRepository

                    repo = ProductoRepository(self.session)
                    p = repo.get_by_codigo(codigo)
                    if p:
                        self.producto_seleccionado = p
                        self.accept()

```

---

## 21. ui/activate_view.py

```python
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QDialog,
)
from PySide6.QtCore import Qt
from security.license_manager import (
    get_machine_id,
    generar_licencia,
    guardar_licencia,
    validar_licencia,
)
from utils.store_config import get_store_name


class ActivateView(QWidget):
    """Vista de activación del sistema"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activation_success = False
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        store_name = get_store_name()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(400, 300)
        self.setWindowTitle(f"Activación - {store_name}")

        titulo = QLabel(f"Activación de {store_name}")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setStyleSheet("color: #7f8c8d; padding-bottom: 20px;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()
        machine_label = QLabel(f"Machine ID:")
        machine_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(machine_label)

        self.machine_id_display = QLabel(machine_id)
        self.machine_id_display.setStyleSheet(
            "background-color: #ecf0f1; padding: 10px; font-family: monospace; font-size: 14px;"
        )
        self.machine_id_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.machine_id_display)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 8px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Ingrese su licencia")
        self.licencia_input.setStyleSheet("padding: 10px; font-size: 16px;")
        self.licencia_input.setMaxLength(16)
        layout.addWidget(self.licencia_input)

        btn_layout = QHBoxLayout()

        self.btn_activar = QPushButton("ACTIVAR")
        self.btn_activar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_activar.clicked.connect(self.activar)
        btn_layout.addWidget(self.btn_activar)

        layout.addLayout(btn_layout)

    def activar(self):
        """Activa el sistema con la licencia"""
        licencia = self.licencia_input.text().strip().upper()

        if not licencia:
            QMessageBox.warning(self, "Error", "Ingrese una licencia")
            return

        machine_id = get_machine_id()
        licencia_correcta = generar_licencia(machine_id)

        if licencia == licencia_correcta:
            guardar_licencia(licencia)
            QMessageBox.information(
                self,
                "Sistema Activado",
                f"{get_store_name()} ha sido activado correctamente.\n\nEl sistema se cerrará. Vuelve a abrirlo.",
            )
            self.activation_success = True
            self.close()
        else:
            QMessageBox.critical(
                self,
                "Licencia Inválida",
                "La licencia ingresada no es válida para esta computadora.",
            )
            self.licencia_input.clear()


class ActivationDialog(QDialog):
    """Diálogo de activación"""

    def __init__(self, parent=None):
        super().__init__(parent)
        store_name = get_store_name()
        self.setWindowTitle(f"Activación - {store_name}")
        self.setModal(True)
        self.activation_success = False

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setFixedSize(450, 380)

        titulo = QLabel(f"Activación de {store_name}")
        titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        subtitulo = QLabel("Ingrese su licencia para activar el sistema")
        subtitulo.setStyleSheet("color: #7f8c8d; padding-bottom: 10px;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitulo)

        machine_id = get_machine_id()

        machine_label = QLabel("Machine ID de esta computadora:")
        machine_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(machine_label)

        self.machine_id_display = QLabel(machine_id)
        self.machine_id_display.setStyleSheet(
            "background-color: #ecf0f1; padding: 10px; font-family: monospace; font-size: 12px;"
        )
        self.machine_id_display.setWordWrap(True)
        layout.addWidget(self.machine_id_display)

        info_label = QLabel(
            "Envía tu Machine ID al administrador\npara recibir tu licencia de activación."
        )
        info_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 8px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        self.licencia_input = QLineEdit()
        self.licencia_input.setPlaceholderText("Ingrese su licencia de 16 caracteres")
        self.licencia_input.setStyleSheet("padding: 10px; font-size: 14px;")
        self.licencia_input.setMaxLength(16)
        layout.addWidget(self.licencia_input)

        btn_activar = QPushButton("ACTIVAR SISTEMA")
        btn_activar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        btn_activar.clicked.connect(self.activar)
        layout.addWidget(btn_activar)

    def activar(self):
        """Activa el sistema"""
        licencia = self.licencia_input.text().strip().upper()

        if not licencia:
            QMessageBox.warning(self, "Error", "Ingrese una licencia")
            return

        if len(licencia) != 16:
            QMessageBox.warning(self, "Error", "La licencia debe tener 16 caracteres")
            return

        machine_id = get_machine_id()
        licencia_correcta = generar_licencia(machine_id)

        if licencia == licencia_correcta:
            guardar_licencia(licencia)
            QMessageBox.information(
                self,
                "Sistema Activado",
                f"{get_store_name()} ha sido activado correctamente.\n\nEl sistema se cerrará. Vuélvelo a abrir.",
            )
            self.activation_success = True
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Licencia Inválida",
                "La licencia ingresada no es válida para esta computadora.",
            )
            self.licencia_input.clear()

```

---

## 22. ui/about_view.py

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDialog
from PySide6.QtCore import Qt
from utils.store_config import get_store_name, get_address, get_phone, get_nit


class AboutView(QDialog):
    """Ventana Acerca de"""

    def __init__(self, parent=None):
        super().__init__(parent)
        store_name = get_store_name()
        self.setWindowTitle(f"Acerca de {store_name}")
        self.setFixedSize(400, 350)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel(get_store_name())
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        descripcion = QLabel("Sistema de ventas para pequeños negocios")
        descripcion.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(descripcion)

        version = QLabel("Versión 1.0")
        version.setStyleSheet(
            "font-size: 16px; color: #27ae60; font-weight: bold; margin-top: 20px;"
        )
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        address = get_address()
        if address:
            addr_label = QLabel(address)
            addr_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
            addr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(addr_label)

        phone = get_phone()
        if phone:
            phone_label = QLabel(f"Tel: {phone}")
            phone_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
            phone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(phone_label)

        nit = get_nit()
        if nit:
            nit_label = QLabel(f"NIT: {nit}")
            nit_label.setStyleSheet("font-size: 12px; color: #7f8c8d;")
            nit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(nit_label)

        separator = QLabel("")
        separator.setFixedHeight(20)
        layout.addWidget(separator)

        desarrollado = QLabel("Desarrollado por:")
        desarrollado.setStyleSheet("font-size: 12px; color: #95a5a6;")
        desarrollado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desarrollado)

        autor = QLabel("Ingeniero Francisco Llinas P.")
        autor.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        autor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(autor)

        layout.addStretch()

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 30px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)

```

---

## 23. ui/config_view.py

```python
import os
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QFormLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ConfigNegocioDialog(QDialog):
    def __init__(self, parent=None, primera_vez=False):
        super().__init__(parent)
        self.primera_vez = primera_vez
        self.logo_path_seleccionado = ""
        self.setWindowTitle("Configuración del Negocio")
        self.setMinimumWidth(480)
        self.setMinimumHeight(500)
        if primera_vez:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint
            )
        self.init_ui()
        self.cargar_datos_existentes()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        header = QWidget()
        header.setStyleSheet(
            "background-color: #1a252f; border-radius: 8px; padding: 16px;"
        )
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        if self.primera_vez:
            titulo = QLabel("¡Bienvenido a TuCajero!")
            titulo.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
            subtitulo = QLabel("Configura los datos de tu negocio antes de comenzar.")
            subtitulo.setStyleSheet("color: #a0b0c0; font-size: 13px;")
            header_layout.addWidget(titulo)
            header_layout.addWidget(subtitulo)
        else:
            titulo = QLabel("Configuración del Negocio")
            titulo.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
            header_layout.addWidget(titulo)

        layout.addWidget(header)

        form_widget = QWidget()
        form = QFormLayout()
        form.setSpacing(12)
        form_widget.setLayout(form)

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Droguería El Carmen")
        self.nombre_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Nombre del negocio *:", self.nombre_input)

        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Ej: Calle 10 # 5-20")
        self.direccion_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Dirección:", self.direccion_input)

        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Ej: 3001234567")
        self.telefono_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Teléfono:", self.telefono_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Ej: minegocio@gmail.com")
        self.email_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("Email:", self.email_input)

        self.nit_input = QLineEdit()
        self.nit_input.setPlaceholderText("Ej: 900123456-1")
        self.nit_input.setStyleSheet("padding: 8px; font-size: 14px;")
        form.addRow("NIT:", self.nit_input)

        logo_widget = QWidget()
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_widget.setLayout(logo_layout)

        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(80, 80)
        self.logo_preview.setStyleSheet(
            "border: 2px dashed #bdc3c7; border-radius: 8px;background: #f8f9fa;"
        )
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setText("Sin logo")
        logo_layout.addWidget(self.logo_preview)

        logo_btn_layout = QVBoxLayout()
        btn_seleccionar_logo = QPushButton("Seleccionar logo...")
        btn_seleccionar_logo.setStyleSheet(
            "background-color: #3498db; color: white; padding: 8px 16px;"
        )
        btn_seleccionar_logo.clicked.connect(self.seleccionar_logo)
        logo_btn_layout.addWidget(btn_seleccionar_logo)

        self.lbl_logo_path = QLabel("Ningún archivo seleccionado")
        self.lbl_logo_path.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        self.lbl_logo_path.setWordWrap(True)
        logo_btn_layout.addWidget(self.lbl_logo_path)
        logo_btn_layout.addStretch()
        logo_layout.addLayout(logo_btn_layout)

        form.addRow("Logo del negocio:", logo_widget)
        layout.addWidget(form_widget)

        nota = QLabel("* Campo obligatorio")
        nota.setStyleSheet("color: #e74c3c; font-size: 11px;")
        layout.addWidget(nota)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton(
            "GUARDAR Y CONTINUAR" if self.primera_vez else "GUARDAR"
        )
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_guardar.clicked.connect(self.guardar)
        btn_layout.addWidget(btn_guardar)

        if not self.primera_vez:
            btn_cancelar = QPushButton("Cancelar")
            btn_cancelar.setStyleSheet(
                "background-color: #95a5a6; color: white; padding: 12px 24px;"
            )
            btn_cancelar.clicked.connect(self.reject)
            btn_layout.addWidget(btn_cancelar)

        layout.addLayout(btn_layout)

    def cargar_datos_existentes(self):
        from utils.store_config import (
            load_store_config,
            get_store_name,
            get_address,
            get_phone,
            get_email,
            get_nit,
            get_logo_path,
        )

        load_store_config()
        self.nombre_input.setText(get_store_name())
        self.direccion_input.setText(get_address())
        self.telefono_input.setText(get_phone())
        self.email_input.setText(get_email())
        self.nit_input.setText(get_nit())
        logo = get_logo_path()
        if logo and os.path.exists(logo):
            self.logo_path_seleccionado = logo
            self._mostrar_preview_logo(logo)
            self.lbl_logo_path.setText(os.path.basename(logo))

    def seleccionar_logo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar logo del negocio",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.ico)",
        )
        if archivo:
            self.logo_path_seleccionado = archivo
            self._mostrar_preview_logo(archivo)
            self.lbl_logo_path.setText(os.path.basename(archivo))

    def _mostrar_preview_logo(self, path):
        pm = QPixmap(path)
        if not pm.isNull():
            scaled = pm.scaled(
                76,
                76,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.logo_preview.setPixmap(scaled)
            self.logo_preview.setText("")

    def guardar(self):
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(
                self, "Campo requerido", "El nombre del negocio es obligatorio."
            )
            self.nombre_input.setFocus()
            return

        logo_guardado = ""
        if self.logo_path_seleccionado:
            try:
                import shutil
                from utils.store_config import get_config_dir

                assets_dir = os.path.join(os.path.dirname(get_config_dir()), "assets")
                os.makedirs(assets_dir, exist_ok=True)
                ext = os.path.splitext(self.logo_path_seleccionado)[1]
                destino = os.path.join(assets_dir, f"logo{ext}")
                shutil.copy2(self.logo_path_seleccionado, destino)
                logo_guardado = destino
            except Exception as e:
                print(f"[WARN] No se pudo copiar el logo: {e}")
                logo_guardado = self.logo_path_seleccionado

        config = {
            "store_name": nombre,
            "logo_path": logo_guardado,
            "address": self.direccion_input.text().strip(),
            "phone": self.telefono_input.text().strip(),
            "email": self.email_input.text().strip(),
            "nit": self.nit_input.text().strip(),
        }

        from utils.store_config import save_store_config

        if save_store_config(config):
            if not self.primera_vez:
                QMessageBox.information(
                    self,
                    "Guardado",
                    "Configuración guardada.\n"
                    "Reinicia la aplicación para ver los cambios en el header.",
                )
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la configuración.")

```

---

## 24. utils/ticket.py

```python
import os
from datetime import datetime
from utils.store_config import (
    get_store_name,
    get_address,
    get_phone,
    get_nit,
    get_email,
    get_logo_path,
)


class GeneradorTicket:
    WIDTH = 40

    def __init__(self, nombre_tienda=None):
        self.nombre_tienda = nombre_tienda or get_store_name()

    def generar(self, venta, items):
        """Genera el texto del ticket"""
        IVA_RATE = 0.19
        lines = []
        lines.append("=" * self.WIDTH)
        store_name = get_store_name()
        if store_name:
            lines.append(f"{store_name.upper():^{self.WIDTH}}")
        address = get_address()
        if address:
            lines.append(f"{address:^{self.WIDTH}}")
        phone = get_phone()
        if phone:
            lines.append(f"Tel: {phone}")
        email = get_email()
        if email:
            lines.append(f"Email: {email}")
        nit = get_nit()
        if nit:
            lines.append(f"NIT: {nit}")
        lines.append("=" * self.WIDTH)
        lines.append(f"Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M')}")
        lines.append(f"Ticket #: {venta.id}")
        if getattr(venta, "metodo_pago", None):
            lines.append(f"Método: {venta.metodo_pago}")
        lines.append("-" * self.WIDTH)
        subtotal_total = 0
        iva_total = 0
        for item in items:
            producto = item.producto
            cantidad = item.cantidad
            precio = item.precio
            subtotal = cantidad * precio
            iva = round(subtotal * IVA_RATE, 2)
            total_item = round(subtotal + iva, 2)
            subtotal_total += subtotal
            iva_total += iva
            lines.append(f"{producto.nombre[:20]:<20} x{cantidad}")
            lines.append(
                f"Base:${precio:.2f} IVA:${iva / cantidad:.2f} Total:${total_item:.2f}"
            )
        subtotal_total = round(subtotal_total, 2)
        iva_total = round(iva_total, 2)
        total_final = round(subtotal_total + iva_total, 2)
        lines.append("-" * self.WIDTH)
        lines.append(f"{'Subtotal:':<20} ${subtotal_total:.2f}")
        lines.append(f"{'IVA 19%:':<20} ${iva_total:.2f}")
        lines.append(f"{'TOTAL:':<20} ${total_final:.2f}")
        lines.append("=" * self.WIDTH)
        lines.append("Gracias por su compra!")
        lines.append("")
        return "\n".join(lines)

    def generar_html(self, venta, items):
        """Genera el ticket en formato HTML para impresión"""
        store_name = get_store_name()
        address = get_address()
        phone = get_phone()
        nit = get_nit()
        email = get_email()

        logo_path = get_logo_path()
        logo_img = ""
        if logo_path and os.path.exists(logo_path):
            logo_img = (
                f'<img src="{logo_path}" width="100" style="margin-bottom: 10px;"><br>'
            )

        items_html = ""
        IVA_RATE = 0.19
        subtotal_total = 0
        iva_total = 0
        for item in items:
            producto = item.producto
            cantidad = item.cantidad
            precio = item.precio
            subtotal = cantidad * precio
            iva = round(subtotal * IVA_RATE, 2)
            total_item = round(subtotal + iva, 2)
            subtotal_total += subtotal
            iva_total += iva
            items_html += f"""
            <tr>
                <td>{producto.nombre}</td>
                <td style="text-align:center">{cantidad}</td>
                <td style="text-align:right">${precio:.2f}</td>
                <td style="text-align:right">${iva:.2f}</td>
                <td style="text-align:right">${total_item:.2f}</td>
            </tr>
            """
        subtotal_total = round(subtotal_total, 2)
        iva_total = round(iva_total, 2)
        total_final = round(subtotal_total + iva_total, 2)

        metodo_pago = getattr(venta, "metodo_pago", None)
        html = f"""
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            width: 300px;
            margin: 0 auto;
            color: #2c3e50;
        }}
        .header {{
            text-align: center;
            margin-bottom: 16px;
            padding: 12px 0;
            border-bottom: 2px solid #2c3e50;
        }}
        .store-name {{
            font-size: 20px;
            font-weight: bold;
            color: #1a252f;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }}
        .store-type {{
            font-size: 11px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }}
        .info {{
            font-size: 11px;
            color: #555;
            line-height: 1.6;
        }}
        .nit {{
            font-size: 11px;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 10px;
        }}
        th {{
            border-bottom: 1px solid #bdc3c7;
            padding: 4px;
            text-align: left;
            font-size: 11px;
            color: #7f8c8d;
        }}
        td {{ padding: 4px; text-align: left; }}
        .total-row {{
            border-top: 2px solid #2c3e50;
            font-weight: bold;
            font-size: 14px;
            margin-top: 8px;
            padding-top: 8px;
        }}
        .footer {{
            text-align: center;
            margin-top: 16px;
            font-size: 10px;
            color: #95a5a6;
            border-top: 1px solid #ecf0f1;
            padding-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        {logo_img}
        <div class="store-name">{store_name}</div>
        {f'<div class="info">{address}</div>' if address else ""}
        {f'<div class="info">Tel: {phone}</div>' if phone else ""}
        {f'<div class="info">{email}</div>' if email else ""}
        {f'<div class="nit">NIT: {nit}</div>' if nit else ""}
    </div>
    <div class="info">
        Fecha: {venta.fecha.strftime("%d/%m/%Y %H:%M")}&nbsp;&nbsp;
        Ticket #: {venta.id}
        {f"<br>Método: {metodo_pago}" if metodo_pago else ""}
    </div>
    <table>
        <thead>
            <tr>
                <th>Producto</th>
                <th>Cant</th>
                <th>Precio</th>
                <th>IVA</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {items_html}
        </tbody>
    </table>
    <div class="total-row">
        Subtotal: ${subtotal_total:.2f}<br>
        IVA 19%: ${iva_total:.2f}<br>
        <strong>TOTAL: ${total_final:.2f}</strong>
    </div>
    <div class="footer">
        <p>¡Gracias por su compra!</p>
        <p>{store_name} — {email}</p>
    </div>
</body>
</html>
"""
        return html

    def imprimir(self, venta, items):
        """Imprime el ticket en consola y guarda en PDF diario"""
        ticket = self.generar(venta, items)
        print(ticket)
        try:
            from utils.factura_diaria import agregar_ticket_a_pdf_diario

            agregar_ticket_a_pdf_diario(venta, items)
        except Exception as e:
            print(f"[WARN] No se pudo guardar en PDF diario: {e}")
        return ticket

    def imprimir_html(self, venta, items):
        """Genera ticket en HTML para impresión"""
        return self.generar_html(venta, items)


def generar_facturas_dia(fecha=None):
    """
    Genera el PDF de facturas para un día específico.
    Si fecha es None, usa la fecha actual.
    Retorna la ruta del PDF generado.
    """
    from utils.factura_diaria import (
        get_factura_diaria_path,
        get_facturas_dir,
        _generar_pdf_diario,
    )
    from utils.store_config import (
        get_store_name,
        get_address,
        get_phone,
        get_email,
        get_nit,
    )
    import json
    import os

    if fecha is None:
        from datetime import datetime

        fecha = datetime.now().date()

    json_path = os.path.join(
        get_facturas_dir(), f"facturas_{fecha.strftime('%Y-%m-%d')}_data.json"
    )
    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            tickets = json.load(f)
    except Exception:
        return None

    if not tickets:
        return None

    pdf_path = get_factura_diaria_path(fecha)
    _generar_pdf_diario(
        pdf_path,
        tickets,
        get_store_name(),
        get_address(),
        get_phone(),
        get_email(),
        get_nit(),
    )
    return pdf_path

```

---

## 25. utils/factura_diaria.py

```python
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def get_facturas_dir():
    """Retorna el directorio de facturas diarias"""
    from config.database import get_data_dir

    facturas_dir = os.path.join(get_data_dir(), "facturas")
    os.makedirs(facturas_dir, exist_ok=True)
    return facturas_dir


def get_factura_diaria_path(fecha=None):
    """Retorna la ruta del PDF del día"""
    if fecha is None:
        fecha = datetime.now().date()
    facturas_dir = get_facturas_dir()
    nombre = f"facturas_{fecha.strftime('%Y-%m-%d')}.pdf"
    return os.path.join(facturas_dir, nombre)


def agregar_ticket_a_pdf_diario(venta, items):
    """
    Agrega el ticket de una venta al PDF diario acumulativo.
    Si el PDF del día no existe lo crea.
    Si ya existe agrega la nueva factura al final.
    """
    from utils.store_config import (
        get_store_name,
        get_address,
        get_phone,
        get_email,
        get_nit,
    )

    pdf_path = get_factura_diaria_path()

    tickets_existentes = []
    if os.path.exists(pdf_path):
        try:
            import json

            json_path = pdf_path.replace(".pdf", "_data.json")
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    tickets_existentes = json.load(f)
        except Exception:
            tickets_existentes = []

    ticket_data = {
        "venta_id": venta.id,
        "fecha": venta.fecha.strftime("%d/%m/%Y %H:%M:%S"),
        "total": venta.total,
        "metodo_pago": getattr(venta, "metodo_pago", "efectivo") or "efectivo",
        "items": [
            {
                "nombre": item.producto.nombre,
                "cantidad": item.cantidad,
                "precio": item.precio,
                "subtotal": item.cantidad * item.precio,
            }
            for item in items
        ],
    }
    tickets_existentes.append(ticket_data)

    import json

    json_path = pdf_path.replace(".pdf", "_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(tickets_existentes, f, ensure_ascii=False, indent=2)

    _generar_pdf_diario(
        pdf_path,
        tickets_existentes,
        get_store_name(),
        get_address(),
        get_phone(),
        get_email(),
        get_nit(),
    )

    return pdf_path


def _generar_pdf_diario(pdf_path, tickets, store_name, address, phone, email, nit):
    """Genera el PDF con todos los tickets del día"""
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    style_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Normal"],
        fontSize=16,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    style_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        alignment=TA_CENTER,
        textColor=colors.HexColor("#555555"),
        spaceAfter=2,
    )
    style_ticket_header = ParagraphStyle(
        "TicketHeader",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        spaceAfter=4,
        spaceBefore=12,
    )
    style_normal = ParagraphStyle(
        "Normal2",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        spaceAfter=2,
    )

    story = []

    story.append(Paragraph(store_name.upper(), style_titulo))
    if address:
        story.append(Paragraph(address, style_subtitulo))
    if phone:
        story.append(Paragraph(f"Tel: {phone}", style_subtitulo))
    if email:
        story.append(Paragraph(email, style_subtitulo))
    if nit:
        story.append(Paragraph(f"NIT: {nit}", style_subtitulo))

    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            f"FACTURAS DEL DÍA — {fecha_hoy}  |  Total ventas: {len(tickets)}",
            ParagraphStyle(
                "dia",
                parent=styles["Normal"],
                fontSize=10,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                textColor=colors.HexColor("#2c3e50"),
            ),
        )
    )
    story.append(
        HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2c3e50"))
    )
    story.append(Spacer(1, 0.3 * cm))

    metodos_label = {
        "efectivo": "Efectivo",
        "nequi": "Nequi",
        "daviplata": "Daviplata",
        "transferencia": "Transferencia",
        "mixto": "Mixto",
    }

    for ticket in tickets:
        story.append(
            Paragraph(
                f"Ticket #{ticket['venta_id']}  —  {ticket['fecha']}  —  "
                f"Método: {metodos_label.get(ticket['metodo_pago'], ticket['metodo_pago'])}",
                style_ticket_header,
            )
        )

        data = [["Producto", "Cant.", "Precio unit.", "Subtotal"]]
        for item in ticket["items"]:
            data.append(
                [
                    item["nombre"],
                    str(item["cantidad"]),
                    f"${item['precio']:,.2f}",
                    f"${item['subtotal']:,.2f}",
                ]
            )

        tabla = Table(data, colWidths=[9 * cm, 2 * cm, 3 * cm, 3 * cm])
        tabla.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f8f9fa")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(tabla)

        total_data = [["", "", "TOTAL:", f"${ticket['total']:,.2f}"]]
        total_tabla = Table(total_data, colWidths=[9 * cm, 2 * cm, 3 * cm, 3 * cm])
        total_tabla.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LINEABOVE", (2, 0), (-1, -1), 1, colors.HexColor("#2c3e50")),
                ]
            )
        )
        story.append(total_tabla)
        story.append(
            HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dee2e6"))
        )

    if tickets:
        story.append(Spacer(1, 0.5 * cm))
        total_dia = sum(t["total"] for t in tickets)
        story.append(
            HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2c3e50"))
        )
        story.append(
            Paragraph(
                f"TOTAL DEL DÍA: ${total_dia:,.2f}  |  "
                f"Ventas registradas: {len(tickets)}",
                ParagraphStyle(
                    "resumen",
                    parent=styles["Normal"],
                    fontSize=12,
                    fontName="Helvetica-Bold",
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#27ae60"),
                    spaceBefore=8,
                ),
            )
        )

    doc.build(story)


def limpiar_datos_dia_anterior():
    """Elimina el JSON auxiliar de días anteriores (limpieza opcional)"""
    import json
    from datetime import date, timedelta

    ayer = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    json_path = os.path.join(get_facturas_dir(), f"facturas_{ayer}_data.json")
    if os.path.exists(json_path):
        try:
            os.remove(json_path)
        except Exception:
            pass

```

---

## 26. utils/backup.py

```python
import shutil
import datetime
import os
import sys


def get_backups_dir():
    """Retorna el directorio de backups"""
    from config.database import get_data_dir

    data_dir = get_data_dir()
    backups_dir = os.path.join(data_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)
    return backups_dir


def backup_database():
    """Crea un backup de la base de datos"""
    from config.database import get_db_path

    db_path = get_db_path()

    if not os.path.exists(db_path):
        return None

    now = datetime.datetime.now()
    filename = f"pos_backup_{now.strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(get_backups_dir(), filename)

    try:
        shutil.copy2(db_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Error al crear backup: {e}")
        return None


def cleanup_old_backups(keep_days=7):
    """Elimina backups mayores a keep_days"""
    backups_dir = get_backups_dir()
    now = datetime.datetime.now()

    for filename in os.listdir(backups_dir):
        if filename.startswith("pos_backup_") and filename.endswith(".db"):
            filepath = os.path.join(backups_dir, filename)
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
            if (now - file_time).days > keep_days:
                try:
                    os.remove(filepath)
                except:
                    pass

```

---

## 27. utils/excel_exporter.py

```python
import os
from datetime import datetime


def exportar_historial_excel(
    cierres, ventas_por_cierre, ranking, resumen, ruta_destino=None
):
    """Exporta historial a Excel con 3 hojas"""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        raise ImportError("openpyxl no está instalado. Ejecuta: pip install openpyxl")

    wb = openpyxl.Workbook()

    ws1 = wb.active
    ws1.title = "Cierres"
    headers1 = [
        "ID",
        "Fecha apertura",
        "Fecha cierre",
        "Ventas brutas",
        "IVA recaudado",
        "Efectivo",
        "Transferencias",
        "Gastos",
        "Ganancia neta",
        "Núm. ventas",
    ]
    ws1.append(headers1)
    for cell in ws1[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="2C3E50")
        cell.font = Font(bold=True, color="FFFFFF")
    for c in cierres:
        ws1.append(
            [
                c.id,
                c.fecha_apertura.strftime("%d/%m/%Y %H:%M") if c.fecha_apertura else "",
                c.fecha_cierre.strftime("%d/%m/%Y %H:%M") if c.fecha_cierre else "",
                round(c.total_ventas or 0, 2),
                round(c.total_iva or 0, 2),
                round(c.total_efectivo or 0, 2),
                round(c.total_transferencias or 0, 2),
                round(c.total_gastos or 0, 2),
                round(c.ganancia_neta or 0, 2),
                c.numero_ventas or 0,
            ]
        )
    ws1.append(
        [
            "TOTALES",
            "",
            "",
            round(resumen["total_ventas"], 2),
            round(sum(c.total_iva or 0 for c in cierres), 2),
            round(sum(c.total_efectivo or 0 for c in cierres), 2),
            round(sum(c.total_transferencias or 0 for c in cierres), 2),
            round(resumen["total_gastos"], 2),
            round(resumen["ganancia_neta"], 2),
            resumen["num_ventas"],
        ]
    )
    for cell in ws1[ws1.max_row]:
        cell.font = Font(bold=True)

    ws2 = wb.create_sheet("Detalle ventas")
    headers2 = [
        "Cierre ID",
        "Venta ID",
        "Fecha",
        "Subtotal base",
        "IVA 19%",
        "Total",
        "Método de pago",
        "Estado",
        "Motivo anulación",
    ]
    ws2.append(headers2)
    for cell in ws2[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="27AE60")
        cell.font = Font(bold=True, color="FFFFFF")
    IVA_RATE = 0.19
    for corte_id, ventas in ventas_por_cierre.items():
        for v in ventas:
            subtotal = round(v.total / 1.19, 2)
            iva = round(v.total - subtotal, 2)
            ws2.append(
                [
                    corte_id,
                    v.id,
                    v.fecha.strftime("%d/%m/%Y %H:%M:%S"),
                    subtotal,
                    iva,
                    round(v.total, 2),
                    v.metodo_pago or "efectivo",
                    "Anulada" if v.anulada else "Válida",
                    v.motivo_anulacion or "",
                ]
            )

    ws3 = wb.create_sheet("Ranking productos")
    headers3 = [
        "Posición",
        "Código",
        "Producto",
        "Unidades vendidas",
        "Ingresos totales",
    ]
    ws3.append(headers3)
    for cell in ws3[1]:
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="8E44AD")
        cell.font = Font(bold=True, color="FFFFFF")
    for i, r in enumerate(ranking, 1):
        ws3.append(
            [
                i,
                r.codigo,
                r.nombre,
                int(r.total_vendido or 0),
                round(float(r.total_ingresos or 0), 2),
            ]
        )

    for ws in [ws1, ws2, ws3]:
        for col in ws.columns:
            max_len = max(
                (len(str(cell.value)) for cell in col if cell.value), default=10
            )
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    if not ruta_destino:
        from config.database import get_data_dir

        exports_dir = os.path.join(get_data_dir(), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_destino = os.path.join(exports_dir, f"historial_{timestamp}.xlsx")

    wb.save(ruta_destino)
    return ruta_destino

```

---

## 28. tools/license_generator.py

```python
"""
TuCajero - Generador de Licencias
Herramienta para generar licencias para clientes.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.license_manager import get_machine_id, generar_licencia
from utils.store_config import get_store_name


def main():
    """Función principal"""
    store_name = get_store_name()
    print()
    print("=" * 30)
    print(f"{store_name.upper()}")
    print("GENERADOR DE LICENCIAS")
    print("=" * 30)
    print()

    print("Opciones:")
    print("1. Generar licencia para esta computadora")
    print("2. Generar licencia con Machine ID personalizado")
    print()

    opcion = input("Seleccione una opcion (1/2): ").strip()

    print()

    if opcion == "1":
        machine_id = get_machine_id()
        print(f"Machine ID de esta computadora:")
        print(f"  {machine_id}")
    elif opcion == "2":
        machine_id = input("Ingresar Machine ID: ").strip()
        if not machine_id:
            print("Error: Debe ingresar un Machine ID")
            return
    else:
        print("Opcion invalida")
        return

    licencia = generar_licencia(machine_id)

    print()
    print("-" * 30)
    print("RESULTADO:")
    print("-" * 30)
    print()
    print(f"Machine ID: {machine_id}")
    print(f"Licencia:   {licencia}")
    print()
    print("=" * 30)
    print()
    print("Instrucciones:")
    print("1. Copie la licencia generada")
    print("2. En el sistema del cliente, vaya a Activacion")
    print("3. Ingrese la licencia")
    print("4. El sistema se activara automaticamente")
    print()


if __name__ == "__main__":
    main()

```

---

## 29. verificar_iva.py

```python
import sys

sys.path.insert(0, "tucajero")
from config.database import init_db, get_session

init_db()
session = get_session()

from sqlalchemy import inspect

cols_items = [c["name"] for c in inspect(session.bind).get_columns("venta_items")]
cols_corte = [c["name"] for c in inspect(session.bind).get_columns("cortes_caja")]
print(f"Columnas venta_items: {cols_items}")
print(f"Columnas cortes_caja: {cols_corte}")

assert "iva_monto" in cols_items, "Falta iva_monto en venta_items"
assert "total_iva" in cols_corte, "Falta total_iva en cortes_caja"
print("Columnas verificadas OK")

from services.corte_service import CorteCajaService
from services.producto_service import ProductoService, VentaService

cs = CorteCajaService(session)
if not cs.esta_caja_abierta():
    cs.abrir_caja()
    print("Caja abierta")

ps = ProductoService(session)
p = ps.create_producto("TESTIVA", "Producto IVA Test", 10000.0, 5000.0, 10)
print(f"Producto creado: {p.nombre}")

vs = VentaService(session)
venta = vs.registrar_venta([{"producto_id": p.id, "cantidad": 2, "precio": 10000.0}])
session.expire_all()

print(f"\n--- VERIFICACIÓN IVA ---")
print(f"Venta #{venta.id}")
print(f"Base: 2 x $10,000 = $20,000.00")
iva_item = venta.items[0].iva_monto
print(f"IVA 19%: ${iva_item:,.2f}")
print(f"Total: ${venta.total:,.2f}")

assert abs(venta.total - 23800.0) < 0.01, (
    f"Total esperado $23.800, obtenido ${venta.total}"
)
assert abs(iva_item - 3800.0) < 0.01, f"IVA esperado $3.800, obtenido ${iva_item}"

total_iva_hoy = vs.venta_repo.get_total_iva_hoy()
print(f"\nTotal IVA hoy: ${total_iva_hoy:,.2f}")
assert total_iva_hoy >= 3800.0

ps.delete_producto(p.id)
print("\nVERIFICACIÓN IVA OK - TODO CORRECTO")

```

---

## 30. migrar_iva.py

```python
import sys

sys.path.insert(0, "tucajero")
from config.database import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    migraciones = [
        "ALTER TABLE venta_items ADD COLUMN iva_monto REAL DEFAULT 0",
        "ALTER TABLE cortes_caja ADD COLUMN total_iva REAL DEFAULT 0",
    ]
    for sql in migraciones:
        try:
            conn.execute(text(sql))
            print(f"OK: {sql[:50]}...")
        except Exception as e:
            print(f"Ya existe o error: {e}")
    conn.commit()
print("Migración OK")

```

---

