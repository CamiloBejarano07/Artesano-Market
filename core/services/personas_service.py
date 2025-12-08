from core.models import Personas
from django.shortcuts import get_object_or_404


class PersonasService:
    """
    Servicio equivalente a PersonasService de Spring Boot.
    Maneja las operaciones CRUD para el modelo Personas.
    """

    @staticmethod
    def find_all():
        """Obtiene todas las personas."""
        return Personas.objects.all()

    @staticmethod
    def find_by_id(id):
        """Obtiene una persona por su ID o devuelve None si no existe."""
        return Personas.objects.filter(id=id).first()

    @staticmethod
    def save(data):
        """
        Guarda una persona (crear o actualizar).
        'data' puede ser un diccionario o una instancia del modelo Personas.
        """
        if isinstance(data, Personas):
            data.save()
            return data
        else:
            persona = Personas(**data)
            persona.save()
            return persona

    @staticmethod
    def delete(id):
        """Elimina una persona por su ID."""
        persona = get_object_or_404(Personas, id=id)
        persona.delete()
