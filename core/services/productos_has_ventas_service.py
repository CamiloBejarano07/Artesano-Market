from core.models import ProductosHasVentas
from django.shortcuts import get_object_or_404


class ProductosHasVentasService:
    """
    Servicio equivalente a ProductoshasventasService de Spring Boot.
    Gestiona las operaciones CRUD para la relación ProductosHasVentas.
    """

    @staticmethod
    def find_all():
        """Obtiene todas las relaciones producto-venta."""
        return ProductosHasVentas.objects.all()

    @staticmethod
    def find_by_id(venta_id, producto_id):
        """
        Obtiene una relación ProductosHasVentas por su clave compuesta.
        """
        return ProductosHasVentas.objects.filter(venta_id=venta_id, producto_id=producto_id).first()

    @staticmethod
    def save(data):
        """
        Guarda una relación producto-venta.
        'data' puede ser un diccionario o una instancia de ProductosHasVentas.
        """
        if isinstance(data, ProductosHasVentas):
            data.save()
            return data
        else:
            obj = ProductosHasVentas(**data)
            obj.save()
            return obj

    @staticmethod
    def delete(venta_id, producto_id):
        """Elimina una relación producto-venta por su clave compuesta."""
        obj = get_object_or_404(ProductosHasVentas, venta_id=venta_id, producto_id=producto_id)
        obj.delete()
