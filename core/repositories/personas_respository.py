from core.models import Personas


class PersonasRepository:
    """
    Repositorio para manejar las operaciones CRUD y búsquedas
    de la entidad Personas (equivalente al PersonasRepository de Spring Boot).
    """

    # ===== CRUD =====
    @staticmethod
    def get_all():
        """Obtiene todas las personas."""
        return Personas.objects.all()

    @staticmethod
    def get_by_id(persona_id):
        """Obtiene una persona por su ID."""
        return Personas.objects.filter(id=persona_id).first()

    @staticmethod
    def create(data):
        """Crea una nueva persona."""
        return Personas.objects.create(**data)

    @staticmethod
    def update(persona_id, data):
        """Actualiza una persona existente."""
        persona = PersonasRepository.get_by_id(persona_id)
        if persona:
            for key, value in data.items():
                setattr(persona, key, value)
            persona.save()
            return persona
        return None

    @staticmethod
    def delete(persona_id):
        """Elimina una persona por su ID."""
        persona = PersonasRepository.get_by_id(persona_id)
        if persona:
            persona.delete()
            return True
        return False

    # ===== Consultas personalizadas =====
    @staticmethod
    def find_by_nombre(nombre):
        """Busca personas por nombre (sin importar mayúsculas/minúsculas)."""
        return Personas.objects.filter(nombre_persona__icontains=nombre)

    @staticmethod
    def find_by_apellido(apellido):
        """Busca personas por apellido (sin importar mayúsculas/minúsculas)."""
        return Personas.objects.filter(apellido_persona__icontains=apellido)

    @staticmethod
    def find_by_correo(correo):
        """Busca personas por correo (sin importar mayúsculas/minúsculas)."""
        return Personas.objects.filter(correo_persona__icontains=correo)

    @staticmethod
    def find_by_telefono(telefono):
        """Busca personas por número de teléfono."""
        return Personas.objects.filter(telefono__icontains=telefono)

    @staticmethod
    def find_one_by_correo(correo):
        """Obtiene una sola persona por correo exacto."""
        return Personas.objects.filter(correo_persona=correo).first()
