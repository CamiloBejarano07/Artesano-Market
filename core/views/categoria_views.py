from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from core.models import Categoria, Personas
from django.contrib import messages
import json
from core.models import Productos
from django.conf import settings
from django.db.models import Q
from core.decorators import requires_admin

# ✅ Vista del catálogo (HTML)
def mostrar_catalogo(request):
    """Mostrar catálogo con soporte de filtros (búsqueda, categoría, rangos de precio, orden).

    Implementa la lógica de filtrado en el servidor para que la plantilla solo muestre resultados.
    """
    categorias = Categoria.objects.all()

    # Parámetros de filtrado
    q = request.GET.get('q') or request.GET.get('busqueda') or ''
    categoria_id = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    orden = request.GET.get('orden')

    productos_qs = Productos.objects.select_related('categoria_id_categoria', 'vendedor')

    if q:
        productos_qs = productos_qs.filter(
            Q(nombre__icontains=q) | Q(descripcion_producto__icontains=q) | Q(referencia__icontains=q)
        )

    if categoria_id:
        try:
            productos_qs = productos_qs.filter(categoria_id_categoria_id=int(categoria_id))
        except Exception:
            pass

    try:
        if precio_min:
            productos_qs = productos_qs.filter(precio__gte=float(precio_min))
        if precio_max:
            productos_qs = productos_qs.filter(precio__lte=float(precio_max))
    except ValueError:
        # Ignorar parámetros no numéricos
        pass

    # Ordenamiento
    if orden:
        if orden == 'precio_asc':
            productos_qs = productos_qs.order_by('precio')
        elif orden == 'precio_desc':
            productos_qs = productos_qs.order_by('-precio')
        elif orden == 'stock_desc':
            productos_qs = productos_qs.order_by('-cantidad_existente')
        elif orden == 'stock_asc':
            productos_qs = productos_qs.order_by('cantidad_existente')
        elif orden == 'nombre':
            productos_qs = productos_qs.order_by('nombre')

    user = request.session.get('user_id', None)

    contexto = {
        'categorias': categorias,
        'productos': productos_qs,
        'categoria_actual': categoria_id,
        'MEDIA_URL': settings.MEDIA_URL,
        'user': user,
    }

    return render(request, 'pages/catalog.html', contexto)


# ✅ Listar todas o filtrar por nombre (JSON)
def listar_categorias(request):
    nombre = request.GET.get('nombre', None)
    if nombre:
        categorias = Categoria.objects.filter(nombre_categoria__icontains=nombre)
    else:
        categorias = Categoria.objects.all()

    data = list(categorias.values())
    return JsonResponse(data, safe=False)


# ✅ Obtener por ID (JSON)
def obtener_categoria(request, id):
    categoria = get_object_or_404(Categoria, pk=id)
    data = {
        'id_categoria': categoria.id_categoria,
        'nombre_categoria': categoria.nombre_categoria,
        'descripcion': categoria.descripcion
    }
    return JsonResponse(data)


# ✅ Crear nueva categoría (JSON)
@csrf_exempt
def crear_categoria(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            categoria = Categoria.objects.create(
                nombre_categoria=data.get('nombre_categoria'),
                descripcion=data.get('descripcion', '')
            )
            return JsonResponse({'message': 'Categoría creada', 'id': categoria.id_categoria}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ✅ Actualizar categoría (JSON)
@csrf_exempt
def actualizar_categoria(request, id):
    if request.method == 'PUT':
        try:
            categoria = get_object_or_404(Categoria, pk=id)
            data = json.loads(request.body)
            categoria.nombre_categoria = data.get('nombre_categoria', categoria.nombre_categoria)
            categoria.descripcion = data.get('descripcion', categoria.descripcion)
            categoria.save()
            return JsonResponse({'message': 'Categoría actualizada'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ✅ Eliminar categoría (JSON)
@csrf_exempt
def eliminar_categoria(request, id):
    if request.method == 'DELETE':
        try:
            categoria = get_object_or_404(Categoria, pk=id)
            categoria.delete()
            return JsonResponse({'message': 'Categoría eliminada'})
        except Exception as e:
            error_str = str(e)
            if "foreign key constraint fails" in error_str.lower() or "1451" in error_str:
                return JsonResponse({'error': '❌ No se puede eliminar esta categoría porque tiene productos asociados. Primero elimina o reasigna los productos.'}, status=400)
            else:
                return JsonResponse({'error': '❌ Error al eliminar la categoría. Por favor intenta de nuevo.'}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ✅ Exportar categorías a CSV (descargable)
def exportar_csv(request):
    categorias = Categoria.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="categorias.csv"'

    response.write("id_categoria,nombre_categoria,descripcion\n")
    for c in categorias:
        response.write(f"{c.id_categoria},{c.nombre_categoria},{c.descripcion or ''}\n")

    return response


# ======================================================
#  CRUD DE CATEGORÍAS (ADMIN)
# ======================================================
@requires_admin
def listar_categorias_admin(request):
    """Lista todas las categorías para el administrador."""
    # La autenticación ya está validada por el decorator @requires_admin
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()

    categorias = Categoria.objects.all().order_by('nombre_categoria')

    context = {
        'categorias': categorias,
        'user_logged': True,
        'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
    }

    return render(request, 'admin/categorias_lista.html', context)


@requires_admin
def crear_categoria_admin(request):
    """Permite crear una nueva categoría."""
    # La autenticación ya está validada por el decorator @requires_admin
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()

    if request.method == 'GET':
        return render(request, 'admin/categoria_crear.html', {
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
        })

    # POST
    nombre = request.POST.get('nombre_categoria', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()

    if not nombre:
        messages.error(request, "El nombre de la categoría es obligatorio.")
        return render(request, 'admin/categoria_crear.html', {
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
        })

    try:
        Categoria.objects.create(
            nombre_categoria=nombre,
            descripcion=descripcion or None
        )
        messages.success(request, "Categoría creada correctamente.")
        return redirect('listar_categorias_admin')
    except Exception as e:
        messages.error(request, f"Error al crear la categoría: {str(e)}")
        return render(request, 'admin/categoria_crear.html', {
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
        })


@requires_admin
def editar_categoria_admin(request, id):
    """Permite editar una categoría existente."""
    # La autenticación ya está validada por el decorator @requires_admin
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()

    categoria = get_object_or_404(Categoria, pk=id)

    if request.method == 'GET':
        return render(request, 'admin/categoria_editar.html', {
            'categoria': categoria,
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
        })

    # POST
    nombre = request.POST.get('nombre_categoria', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()

    if not nombre:
        messages.error(request, "El nombre de la categoría es obligatorio.")
        return render(request, 'admin/categoria_editar.html', {
            'categoria': categoria,
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
        })

    try:
        categoria.nombre_categoria = nombre
        categoria.descripcion = descripcion or None
        categoria.save()
        messages.success(request, "Categoría actualizada correctamente.")
        return redirect('listar_categorias_admin')
    except Exception as e:
        messages.error(request, f"Error al actualizar la categoría: {str(e)}")
        return render(request, 'admin/categoria_editar.html', {
            'categoria': categoria,
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
        })


@requires_admin
def eliminar_categoria_admin(request, id):
    """Permite eliminar una categoría."""
    # La autenticación ya está validada por el decorator @requires_admin
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()

    categoria = get_object_or_404(Categoria, pk=id)

    try:
        categoria.delete()
        messages.success(request, "Categoría eliminada correctamente.")
    except Exception as e:
        # Verificar si es un error de clave foránea
        error_str = str(e)
        if "foreign key constraint fails" in error_str.lower() or "1451" in error_str:
            messages.error(request, "❌ No se puede eliminar esta categoría porque tiene productos asociados. Primero elimina o reasigna los productos.")
        else:
            messages.error(request, "❌ Error al eliminar la categoría. Por favor intenta de nuevo.")

    return redirect('listar_categorias_admin')
