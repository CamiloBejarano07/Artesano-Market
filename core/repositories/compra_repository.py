from core.models import Compra


class CompraRepository:
    """
    Repositorio para manejar las operaciones CRUD de la entidad Compra.
    Equivalente al CompraRepository de Spring Boot.
    """

    @staticmethod
    def get_all():
        """Obtiene todas las compras."""
        return Compra.objects.all()

    @staticmethod
    def get_by_id(compra_id):
        """Obtiene una compra por su ID."""
        return Compra.objects.filter(id=compra_id).first()

    @staticmethod
    def create(data):
        """Crea una nueva compra."""
        return Compra.objects.create(**data)

    @staticmethod
    def update(compra_id, data):
        """Actualiza una compra existente."""
        compra = CompraRepository.get_by_id(compra_id)
        if compra:
            for key, value in data.items():
                setattr(compra, key, value)
            compra.save()
            return compra
        return None

    @staticmethod
    def delete(compra_id):
        """Elimina una compra por su ID."""
        compra = CompraRepository.get_by_id(compra_id)
        if compra:
            compra.delete()
            return True
        return False
