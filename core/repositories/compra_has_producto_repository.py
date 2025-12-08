from core.models import CompraHasProducto


class CompraHasProductoRepository:
    """
    Repositorio para manejar las relaciones entre Compra y Producto.
    Equivalente al CompraHasProductoRepository de Spring Boot.
    """

    @staticmethod
    def get_all():
        """Obtiene todas las relaciones compra-producto."""
        return CompraHasProducto.objects.all()

    @staticmethod
    def get_by_id(compra_id, producto_id):
        """Obtiene una relación específica por su clave compuesta."""
        return CompraHasProducto.objects.filter(
            compra_id=compra_id,
            producto_id=producto_id
        ).first()

    @staticmethod
    def create(data):
        """Crea una nueva relación compra-producto."""
        return CompraHasProducto.objects.create(**data)

    @staticmethod
    def update(compra_id, producto_id, data):
        """Actualiza una relación compra-producto existente."""
        relation = CompraHasProductoRepository.get_by_id(compra_id, producto_id)
        if relation:
            for key, value in data.items():
                setattr(relation, key, value)
            relation.save()
            return relation
        return None

    @staticmethod
    def delete(compra_id, producto_id):
        """Elimina una relación compra-producto por su clave compuesta."""
        relation = CompraHasProductoRepository.get_by_id(compra_id, producto_id)
        if relation:
            relation.delete()
            return True
        return False
