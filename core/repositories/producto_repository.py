from core.models import Producto


class ProductoRepository:
    """
    Repositorio para la entidad Producto.
    Equivalente a ProductoRepository de Spring Boot.
    """

    # ===== CRUD =====
    @staticmethod
    def get_all():
        """Obtiene todos los productos."""
        return Producto.objects.all()

    @staticmethod
    def get_by_id(producto_id):
        """Obtiene un producto por su ID."""
        return Producto.objects.filter(id=producto_id).first()

    @staticmethod
    def create(data):
        """Crea un nuevo producto."""
        return Producto.objects.create(**data)

    @staticmethod
    def update(producto_id, data):
        """Actualiza un producto existente."""
        producto = ProductoRepository.get_by_id(producto_id)
        if producto:
            for key, value in data.items():
                setattr(producto, key, value)
            producto.save()
            return producto
        return None

    @staticmethod
    def delete(producto_id):
        """Elimina un producto por su ID."""
        producto = ProductoRepository.get_by_id(producto_id)
        if producto:
            producto.delete()
            return True
        return False

    # ===== Consultas personalizadas =====
    @staticmethod
    def find_by_nombre(nombre):
        """Busca productos cuyo nombre contenga una cadena (ignorando mayúsculas/minúsculas)."""
        return Producto.objects.filter(nombre__icontains=nombre)

    @staticmethod
    def find_by_precio(precio):
        """Busca productos por precio exacto."""
        return Producto.objects.filter(precio=precio)

    @staticmethod
    def find_by_cantidad_existente(cantidad):
        """Busca productos por cantidad existente exacta."""
        return Producto.objects.filter(cantidad_existente=cantidad)
