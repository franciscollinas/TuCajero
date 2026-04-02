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
from tucajero.utils.formato import fmt_moneda
from tucajero.utils.theme import btn_primary, btn_secondary, get_colors
c = get_colors()

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
        from tucajero.utils.theme import get_colors
        c = get_colors()
        self.setStyleSheet(f"QDialog {{ background-color: {c['bg_app']}; }}")
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        titulo = QLabel("Buscar Producto")
        titulo.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {c['text_primary']}; padding-bottom: 4px;")
        layout.addWidget(titulo)

        search_layout = QHBoxLayout()
        self.buscador_input = QLineEdit()
        self.buscador_input.setPlaceholderText(
            "Buscar por código o nombre del producto..."
        )
        self.buscador_input.setStyleSheet(f"padding: 10px; font-size: 14px; background-color: {c['bg_input']}; color: {c['text_primary']}; border: 1.5px solid {c['border']}; border-radius: 8px;")
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
        self.lbl_resultados.setStyleSheet(f"color: {c['text_secondary']};")
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
        lbl_cat.setStyleSheet(f"color: {c['text_secondary']}; font-size: 12px; padding: 2px;")
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
        btn_seleccionar.setStyleSheet(btn_primary())
        btn_seleccionar.clicked.connect(self.seleccionar_producto)
        btn_layout.addWidget(btn_seleccionar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet(btn_secondary())
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
                stock_item.setForeground(QColor(c["danger"]))
            elif p.stock < 5:
                stock_item.setForeground(QColor(c["warning"]))
            tabla.setItem(i, 2, stock_item)
            tabla.setItem(i, 3, QTableWidgetItem(fmt_moneda(p.precio)))

    def _cargar_categorias(self):
        """Carga los botones de categorías"""
        try:
            from tucajero.models.producto import Categoria

            if self.session:
                categorias = (
                    self.session.query(Categoria).order_by(Categoria.nombre.asc()).all()
                )
            else:
                categoria_nombres = set()
                for p in self.productos:
                    if hasattr(p, "categoria") and p.categoria:
                        categoria_nombres.add(p.categoria)
                categorias = []
                for i, nombre in enumerate(sorted(categoria_nombres)):

                    class FakeCategoria:
                        def __init__(self, id, nombre, color):
                            self.id = id
                            self.nombre = nombre
                            self.color = color

                    categorias.append(
                        FakeCategoria(
                            id=i + 1,
                            nombre=nombre,
                            color=COLORES_CATEGORIA[i % len(COLORES_CATEGORIA)],
                        )
                    )

            while self.cat_buttons_layout.count():
                item = self.cat_buttons_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            btn_todos = QPushButton("Todos")
            btn_todos.setStyleSheet(btn_secondary())
            btn_todos.clicked.connect(
                lambda: self.llenar_tabla(self.productos, self.tabla_cat)
            )
            self.cat_buttons_layout.addWidget(btn_todos)

            for i, cat in enumerate(categorias):
                color = cat.color or COLORES_CATEGORIA[i % len(COLORES_CATEGORIA)]
                btn = QPushButton(f"🏷 {cat.nombre}")
                btn.setStyleSheet(btn_secondary())
                btn.clicked.connect(
                    lambda checked, c=cat: self._filtrar_por_categoria(c)
                )
                self.cat_buttons_layout.addWidget(btn)
        except Exception as e:
            print(f"[WARN] No se pudieron cargar categorías: {e}")

    def _filtrar_por_categoria(self, categoria):
        """Filtra productos por categoría"""
        try:
            if self.session:
                from tucajero.repositories.producto_repo import ProductoRepository

                repo = ProductoRepository(self.session)
                productos = repo.search_por_categoria(categoria.id)
            else:
                productos = [
                    p
                    for p in self.productos
                    if hasattr(p, "categoria") and p.categoria == categoria.nombre
                ]
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
                    from tucajero.repositories.producto_repo import ProductoRepository

                    repo = ProductoRepository(self.session)
                    p = repo.get_by_codigo(codigo)
                    if p:
                        self.producto_seleccionado = p
                        self.accept()
