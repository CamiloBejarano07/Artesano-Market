from core.models import CompraHasProducto
from core.repositories.compra_has_producto_repository import CompraHasProductoRepository


class CompraHasProductoService:
    """
    Servicio equivalente a ComprahasproductoService de Spring Boot.
    Gestiona la lógica de negocio para la relación entre Compras y Productos.
    """

    def __init__(self):
        self.repository = CompraHasProductoRepository()

    def find_all(self):
        """Obtiene todos los registros CompraHasProducto."""
        return self.repository.get_all()

    def find_by_id(self, compra_id, producto_id):
        """
        Busca una relación específica entre una compra y un producto.
        """
        return self.repository.get_by_id(compra_id, producto_id)

    def save(self, data):
        """
        Crea o actualiza una relación compra-producto.
        data debe contener 'compra_id' y 'producto_id'.
        """
        compra_id = data.get("compra_id")
        producto_id = data.get("producto_id")

        existing = self.repository.get_by_id(compra_id, producto_id)
        if existing:
            # Si ya existe, actualiza los campos
            for key, value in data.items():
                setattr(existing, key, value)
            existing.save()
            return existing
        else:
            # Si no existe, crea uno nuevo
            return self.repository.create(data)

    def delete(self, compra_id, producto_id):
        """Elimina la relación entre una compra y un producto."""
        return self.repository.delete(compra_id, producto_id)
