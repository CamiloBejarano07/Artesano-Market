from core.models import Ventas


class VentasRepository:
    """
    Repositorio equivalente a VentasRepository de Spring Boot.
    Gestiona las operaciones CRUD sobre la entidad Ventas.
    """

    # ====== CRUD ======

    @staticmethod
    def get_all():
        """Obtiene todas las ventas."""
        return Ventas.objects.all()

    @staticmethod
    def get_by_id(venta_id):
        """Obtiene una venta por su ID."""
        return Ventas.objects.filter(id=venta_id).first()

    @staticmethod
    def create(data):
        """Crea una nueva venta."""
        return Ventas.objects.create(**data)

    @staticmethod
    def update(venta_id, data):
        """Actualiza una venta existente."""
        venta = VentasRepository.get_by_id(venta_id)
        if venta:
            for key, value in data.items():
                setattr(venta, key, value)
            venta.save()
            return venta
        return None

    @staticmethod
    def delete(venta_id):
        """Elimina una venta por su ID."""
        venta = VentasRepository.get_by_id(venta_id)
        if venta:
            venta.delete()
            return True
        return False
