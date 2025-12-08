from core.models import Vendedores


class VendedoresRepository:
    """
    Repositorio equivalente a VendedoresRepository de Spring Boot.
    Gestiona operaciones CRUD sobre la entidad Vendedores.
    """

    # ====== CRUD ======

    @staticmethod
    def get_all():
        """Obtiene todos los vendedores."""
        return Vendedores.objects.all()

    @staticmethod
    def get_by_id(vendedor_id):
        """Obtiene un vendedor por su ID."""
        return Vendedores.objects.filter(id=vendedor_id).first()

    @staticmethod
    def create(data):
        """Crea un nuevo vendedor."""
        return Vendedores.objects.create(**data)

    @staticmethod
    def update(vendedor_id, data):
        """Actualiza los datos de un vendedor existente."""
        vendedor = VendedoresRepository.get_by_id(vendedor_id)
        if vendedor:
            for key, value in data.items():
                setattr(vendedor, key, value)
            vendedor.save()
            return vendedor
        return None

    @staticmethod
    def delete(vendedor_id):
        """Elimina un vendedor por su ID."""
        vendedor = VendedoresRepository.get_by_id(vendedor_id)
        if vendedor:
            vendedor.delete()
            return True
        return False
