from core.models import Producto
from django.shortcuts import get_object_or_404


class ProductoService:
    """
    Servicio equivalente a ProductoService de Spring Boot.
    Gestiona las operaciones CRUD del modelo Producto.
    """

    @staticmethod
    def find_all():
        """Obtiene todos los productos."""
        return Producto.objects.all()

    @staticmethod
    def find_by_id(id):
        """Obtiene un producto por su ID o devuelve None si no existe."""
        return Producto.objects.filter(id=id).first()

    @staticmethod
    def save(data):
        """
        Guarda un producto (crear o actualizar).
        'data' puede ser un diccionario o una instancia de Producto.
        """
        if isinstance(data, Producto):
            data.save()
            return data
        else:
            producto = Producto(**data)
            producto.save()
            return producto

    @staticmethod
    def delete(id):
        """Elimina un producto por su ID."""
        producto = get_object_or_404(Producto, id=id)
        producto.delete()
