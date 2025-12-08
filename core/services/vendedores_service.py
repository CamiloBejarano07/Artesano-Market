from core.models import Vendedores
from django.shortcuts import get_object_or_404


class VendedoresService:
    """
    Servicio equivalente a VendedoresService de Spring Boot.
    Gestiona las operaciones CRUD para la entidad Vendedores.
    """

    @staticmethod
    def find_all():
        """Obtiene todos los vendedores."""
        return Vendedores.objects.all()

    @staticmethod
    def find_by_id(id):
        """Obtiene un vendedor por su ID."""
        return Vendedores.objects.filter(id=id).first()

    @staticmethod
    def save(data):
        """
        Guarda un vendedor nuevo o actualiza uno existente.
        'data' puede ser un diccionario o una instancia del modelo Vendedores.
        """
        if isinstance(data, Vendedores):
            data.save()
            return data
        else:
            obj, created = Vendedores.objects.update_or_create(
                id=data.get("id"),
                defaults=data
            )
            return obj

    @staticmethod
    def delete(id):
        """Elimina un vendedor por su ID."""
        obj = get_object_or_404(Vendedores, id=id)
        obj.delete()
