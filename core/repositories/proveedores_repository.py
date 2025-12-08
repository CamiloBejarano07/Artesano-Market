from core.models import Proveedores


class ProveedoresRepository:
    """
    Repositorio equivalente a ProveedoresRepository de Spring Boot.
    Gestiona operaciones CRUD sobre la entidad Proveedores.
    """

    # ====== CRUD ======

    @staticmethod
    def get_all():
        """Obtiene todos los proveedores."""
        return Proveedores.objects.all()

    @staticmethod
    def get_by_id(proveedor_id):
        """Obtiene un proveedor por su ID."""
        return Proveedores.objects.filter(id=proveedor_id).first()

    @staticmethod
    def create(data):
        """Crea un nuevo proveedor."""
        return Proveedores.objects.create(**data)

    @staticmethod
    def update(proveedor_id, data):
        """Actualiza los datos de un proveedor existente."""
        proveedor = ProveedoresRepository.get_by_id(proveedor_id)
        if proveedor:
            for key, value in data.items():
                setattr(proveedor, key, value)
            proveedor.save()
            return proveedor
        return None

    @staticmethod
    def delete(proveedor_id):
        """Elimina un proveedor por su ID."""
        proveedor = ProveedoresRepository.get_by_id(proveedor_id)
        if proveedor:
            proveedor.delete()
            return True
        return False
