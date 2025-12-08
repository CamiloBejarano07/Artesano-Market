from core.models import Clientes


class ClientesRepository:
    """
    Repositorio para manejar operaciones CRUD del modelo Clientes.
    Equivalente al ClientesRepository de Spring Boot.
    """

    @staticmethod
    def get_all():
        """Obtiene todos los clientes."""
        return Clientes.objects.all()

    @staticmethod
    def get_by_id(id):
        """Obtiene un cliente por su ID."""
        return Clientes.objects.filter(id=id).first()

    @staticmethod
    def create(data):
        """Crea un nuevo cliente."""
        return Clientes.objects.create(**data)

    @staticmethod
    def update(id, data):
        """Actualiza un cliente existente."""
        cliente = ClientesRepository.get_by_id(id)
        if cliente:
            for key, value in data.items():
                setattr(cliente, key, value)
            cliente.save()
            return cliente
        return None

    @staticmethod
    def delete(id):
        """Elimina un cliente por su ID."""
        cliente = ClientesRepository.get_by_id(id)
        if cliente:
            cliente.delete()
            return True
        return False
