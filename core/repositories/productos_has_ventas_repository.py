from core.models import ProductosHasVentas


class ProductosHasVentasRepository:
    """
    Repositorio equivalente a ProductosHasVentasRepository de Spring Boot.
    Maneja la relación entre productos y ventas.
    """

    # ===== CRUD =====
    @staticmethod
    def get_all():
        """Obtiene todos los registros de productos y ventas."""
        return ProductosHasVentas.objects.all()

    @staticmethod
    def get_by_id(venta_id, producto_id):
        """Obtiene un registro por su clave compuesta (venta_id y producto_id)."""
        return ProductosHasVentas.objects.filter(venta_id=venta_id, producto_id=producto_id).first()

    @staticmethod
    def create(data):
        """Crea un nuevo registro de producto-venta."""
        return ProductosHasVentas.objects.create(**data)

    @staticmethod
    def update(venta_id, producto_id, data):
        """Actualiza un registro de producto-venta existente."""
        registro = ProductosHasVentasRepository.get_by_id(venta_id, producto_id)
        if registro:
            for key, value in data.items():
                setattr(registro, key, value)
            registro.save()
            return registro
        return None

    @staticmethod
    def delete(venta_id, producto_id):
        """Elimina un registro de producto-venta por su clave compuesta."""
        registro = ProductosHasVentasRepository.get_by_id(venta_id, producto_id)
        if registro:
            registro.delete()
            return True
        return False
