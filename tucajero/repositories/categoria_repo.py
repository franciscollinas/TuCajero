from tucajero.models.producto import Categoria
import logging


class CategoriaRepository:
    """Repositorio para acceso a datos de categorías"""

    def __init__(self, session):
        self.session = session

    def get_all(self):
        """Retorna todas las categorías"""
        return self.session.query(Categoria).order_by(Categoria.nombre).all()

    def get_by_id(self, categoria_id):
        """Retorna una categoría por su ID"""
        return (
            self.session.query(Categoria).filter(Categoria.id == categoria_id).first()
        )

    def get_by_nombre(self, nombre):
        """Retorna una categoría por su nombre"""
        return self.session.query(Categoria).filter(Categoria.nombre == nombre).first()

    def create(self, nombre, descripcion="", color="#3498db"):
        """Crea una nueva categoría"""
        categoria = Categoria(
            nombre=nombre,
            descripcion=descripcion,
            color=color,
        )
        try:
            self.session.add(categoria)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error creando categoría: {e}", exc_info=True)
            raise
        return categoria

    def update(self, categoria_id, **kwargs):
        """Actualiza una categoría"""
        categoria = self.get_by_id(categoria_id)
        if categoria:
            for key, value in kwargs.items():
                setattr(categoria, key, value)
            try:
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                logging.error(f"Error actualizando categoría: {e}", exc_info=True)
                raise
        return categoria

    def delete(self, categoria_id):
        """Elimina una categoría"""
        categoria = self.get_by_id(categoria_id)
        if categoria:
            try:
                self.session.delete(categoria)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                logging.error(f"Error eliminando categoría: {e}", exc_info=True)
                raise
        return categoria
