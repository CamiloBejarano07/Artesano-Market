from core.models import CarritoCompras
from core.repositories.carrito_compras_repository import CarritoComprasRepository


class CarritoComprasService:
    """
    Servicio equivalente a CarritocomprasService de Spring Boot.
    Contiene la lógica de negocio para la gestión del carrito de compras.
    """

    def __init__(self):
        self.repository = CarritoComprasRepository()

    def find_all(self):
        """Obtiene todos los carritos de compras."""
        return self.repository.get_all()

    def find_by_id(self, carrito_id):
        """Busca un carrito por su ID."""
        return self.repository.get_by_id(carrito_id)

    def save(self, data):
        """
        Crea o actualiza un carrito.
        Si incluye 'id', intenta actualizarlo; de lo contrario, crea uno nuevo.
        """
        carrito_id = data.get("id")
        if carrito_id:
            carrito = self.repository.get_by_id(carrito_id)
            if carrito:
                for key, value in data.items():
                    setattr(carrito, key, value)
                carrito.save()
                return carrito
        return self.repository.create(data)

    def delete(self, carrito_id):
        """Elimina un carrito de compras por su ID."""
        return self.repository.delete(carrito_id)
