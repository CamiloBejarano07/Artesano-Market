from core.models import Compra
from core.repositories.compra_repository import CompraRepository


class CompraService:
    """
    Servicio equivalente a CompraService de Spring Boot.
    Se encarga de la lógica de negocio para las compras.
    """

    def __init__(self):
        self.repository = CompraRepository()

    def find_all(self):
        """Obtiene todas las compras."""
        return self.repository.get_all()

    def find_by_id(self, id):
        """Busca una compra por su ID."""
        return self.repository.get_by_id(id)

    def save(self, data):
        """
        Crea o actualiza una compra.
        Si existe, actualiza los datos; si no, la crea.
        """
        compra = self.repository.get_by_id(data.get("id"))
        if compra:
            for key, value in data.items():
                setattr(compra, key, value)
            compra.save()
            return compra
        else:
            return self.repository.create(data)

    def delete(self, id):
        """Elimina una compra por su ID."""
        return self.repository.delete(id)
