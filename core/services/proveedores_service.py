from core.models import Proveedores
from django.shortcuts import get_object_or_404


class ProveedoresService:
    """
    Servicio equivalente a ProveedoresService de Spring Boot.
    Gestiona las operaciones CRUD para la entidad Proveedores.
    """

    @staticmethod
    def find_all():
        """Obtiene todos los proveedores."""
        return Proveedores.objects.all()

    @staticmethod
    def find_by_id(id):
        """Obtiene un proveedor por su ID."""
        return Proveedores.objects.filter(id=id).first()

    @staticmethod
    def save(data):
        """
        Guarda un proveedor nuevo o actualiza uno existente.
        'data' puede ser un diccionario o una instancia de Proveedores.
        """
        if isinstance(data, Proveedores):
            data.save()
            return data
        else:
            obj, created = Proveedores.objects.update_or_create(
                id=data.get("id"),
                defaults=data
            )
            return obj

    @staticmethod
    def delete(id):
        """Elimina un proveedor por su ID."""
        obj = get_object_or_404(Proveedores, id=id)
        obj.delete()
