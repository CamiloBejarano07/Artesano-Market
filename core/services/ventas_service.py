from core.models import Ventas
from django.shortcuts import get_object_or_404


class VentasService:
    """
    Servicio equivalente a VentasService de Spring Boot.
    Gestiona las operaciones CRUD para la entidad Ventas.
    """

    @staticmethod
    def find_all():
        """Obtiene todas las ventas."""
        return Ventas.objects.all()

    @staticmethod
    def find_by_id(id):
        """Obtiene una venta por su ID."""
        return Ventas.objects.filter(id=id).first()

    @staticmethod
    def save(data):
        """
        Guarda una nueva venta o actualiza una existente.
        'data' puede ser un diccionario o una instancia del modelo Ventas.
        """
        if isinstance(data, Ventas):
            data.save()
            return data
        else:
            obj, created = Ventas.objects.update_or_create(
                id=data.get("id"),
                defaults=data
            )
            return obj

    @staticmethod
    def delete(id):
        """Elimina una venta por su ID."""
        obj = get_object_or_404(Ventas, id=id)
        obj.delete()
