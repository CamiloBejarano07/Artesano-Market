from core.models import Categoria


class CategoriaRepository:
    """
    Repositorio para manejar operaciones CRUD del modelo Categoria.
    Equivalente al CategoriaRepository de Spring Boot.
    """

    @staticmethod
    def get_all():
        """Obtiene todas las categorías."""
        return Categoria.objects.all()

    @staticmethod
    def get_by_id(id):
        """Obtiene una categoría por su ID."""
        return Categoria.objects.filter(id=id).first()

    @staticmethod
    def create(data):
        """Crea una nueva categoría."""
        return Categoria.objects.create(**data)

    @staticmethod
    def update(id, data):
        """Actualiza una categoría existente."""
        categoria = CategoriaRepository.get_by_id(id)
        if categoria:
            for key, value in data.items():
                setattr(categoria, key, value)
            categoria.save()
            return categoria
        return None

    @staticmethod
    def delete(id):
        """Elimina una categoría por su ID."""
        categoria = CategoriaRepository.get_by_id(id)
        if categoria:
            categoria.delete()
            return True
        return False

    @staticmethod
    def find_by_nombre_categoria_containing_ignore_case(nombre_categoria):
        """
        Busca categorías cuyo nombre contenga el texto indicado,
        sin importar mayúsculas o minúsculas.
        Equivalente a:
        List<Categoria> findByNombreCategoriaContainingIgnoreCase(String nombreCategoria);
        """
        return Categoria.objects.filter(nombre_categoria__icontains=nombre_categoria)
