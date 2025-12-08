from core.models import Marcas


class MarcasRepository:
    """
    Repositorio para manejar las operaciones CRUD de la entidad Marcas.
    Equivalente al MarcasRepository de Spring Boot.
    """

    @staticmethod
    def get_all():
        """Obtiene todas las marcas."""
        return Marcas.objects.all()

    @staticmethod
    def get_by_id(marca_id):
        """Obtiene una marca por su ID."""
        return Marcas.objects.filter(id=marca_id).first()

    @staticmethod
    def create(data):
        """Crea una nueva marca."""
        return Marcas.objects.create(**data)

    @staticmethod
    def update(marca_id, data):
        """Actualiza una marca existente."""
        marca = MarcasRepository.get_by_id(marca_id)
        if marca:
            for key, value in data.items():
                setattr(marca, key, value)
            marca.save()
            return marca
        return None

    @staticmethod
    def delete(marca_id):
        """Elimina una marca por su ID."""
        marca = MarcasRepository.get_by_id(marca_id)
        if marca:
            marca.delete()
            return True
        return False
