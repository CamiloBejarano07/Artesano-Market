from core.models import Categoria
from core.repositories.categoria_repository import CategoriaRepository


class CategoriaService:
    """
    Servicio equivalente a CategoriaService de Spring Boot.
    Maneja la lógica de negocio para las categorías.
    """

    def __init__(self):
        self.repository = CategoriaRepository()

    def find_all(self):
        """Obtiene todas las categorías."""
        return self.repository.get_all()

    def find_by_id(self, categoria_id):
        """Obtiene una categoría por su ID."""
        return self.repository.get_by_id(categoria_id)

    def save(self, data):
        """
        Crea o actualiza una categoría.
        Si existe el ID, actualiza; si no, crea una nueva.
        """
        categoria_id = data.get("id")
        if categoria_id:
            categoria = self.repository.get_by_id(categoria_id)
            if categoria:
                for key, value in data.items():
                    setattr(categoria, key, value)
                categoria.save()
                return categoria
        return self.repository.create(data)

    def delete(self, categoria_id):
        """Elimina una categoría por su ID."""
        return self.repository.delete(categoria_id)
