from core.models import Clientes
from core.repositories.clientes_repository import ClientesRepository


class ClientesService:
    """
    Servicio equivalente a ClientesService de Spring Boot.
    Gestiona la lógica de negocio relacionada con los clientes.
    """

    def __init__(self):
        self.repository = ClientesRepository()

    def find_all(self):
        """Obtiene todos los clientes."""
        return self.repository.get_all()

    def find_by_id(self, cliente_id):
        """Obtiene un cliente por su ID."""
        return self.repository.get_by_id(cliente_id)

    def save(self, data):
        """
        Crea o actualiza un cliente.
        Si existe el ID, actualiza; si no, crea uno nuevo.
        """
        cliente_id = data.get("id")
        if cliente_id:
            cliente = self.repository.get_by_id(cliente_id)
            if cliente:
                for key, value in data.items():
                    setattr(cliente, key, value)
                cliente.save()
                return cliente
        return self.repository.create(data)

    def delete(self, cliente_id):
        """Elimina un cliente por su ID."""
        return self.repository.delete(cliente_id)
