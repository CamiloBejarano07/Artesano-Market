from core.models import Marcas
from django.shortcuts import get_object_or_404


class MarcasService:
    """
    Servicio equivalente a MarcasService de Spring Boot.
    Gestiona las operaciones CRUD sobre el modelo Marcas.
    """

    @staticmethod
    def find_all():
        """Obtiene todas las marcas."""
        return Marcas.objects.all()

    @staticmethod
    def find_by_id(id):
        """Busca una marca por su ID o devuelve None si no existe."""
        return Marcas.objects.filter(id=id).first()

    @staticmethod
    def save(data):
        """
        Guarda una nueva marca o actualiza una existente.
        data puede ser un diccionario o una instancia del modelo.
        """
        if isinstance(data, Marcas):
            data.save()
            return data
        else:
            marca = Marcas(**data)
            marca.save()
            return marca

    @staticmethod
    def delete(id):
        """Elimina una marca por su ID."""
        marca = get_object_or_404(Marcas, id=id)
        marca.delete()
