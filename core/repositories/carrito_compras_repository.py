from core.models import CarritoCompras


class CarritoComprasRepository:
    """
    Repositorio para manejar las operaciones CRUD del modelo CarritoCompras.
    Equivalente al CarritoComprasRepository de Spring Boot.
    """

    @staticmethod
    def get_all():
        """Obtiene todos los carritos de compras."""
        return CarritoCompras.objects.all()

    @staticmethod
    def get_by_id(id):
        """Busca un carrito por su ID."""
        return CarritoCompras.objects.filter(id=id).first()

    @staticmethod
    def create(data):
        """Crea un nuevo carrito de compras."""
        return CarritoCompras.objects.create(**data)

    @staticmethod
    def update(id, data):
        """Actualiza un carrito existente."""
        carrito = CarritoComprasRepository.get_by_id(id)
        if carrito:
            for key, value in data.items():
                setattr(carrito, key, value)
            carrito.save()
            return carrito
        return None

    @staticmethod
    def delete(id):
        """Elimina un carrito por su ID."""
        carrito = CarritoComprasRepository.get_by_id(id)
        if carrito:
            carrito.delete()
            return True
        return False
