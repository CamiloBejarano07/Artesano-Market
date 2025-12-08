import csv
import os
import uuid
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
except ImportError:
    canvas = None
    letter = None
from core.models import Productos, Vendedores, Personas
from django.shortcuts import render
from django.http import JsonResponse
from core.models import Productos, Categoria
from core.forms import ProductoCreateForm, ProductoEditForm
from core.models import Categoria


def catalogo_view(request):
    categorias = Categoria.objects.all()
    categoria_actual = request.GET.get('categoria')
    
    if categoria_actual:
        productos = Productos.objects.filter(categoria_id_categoria_id=categoria_actual)
    else:
        productos = Productos.objects.all()
        
    return render(request, 'pages/catalog.html', {
        'categorias': categorias,
        'productos': productos,
        'categoria_actual': categoria_actual
    })

def productos_por_categoria(request):
    categoria_nombre = request.GET.get('categoria')
    productos = Productos.objects.filter(categoria_id_categoria__nombre_categoria__iexact=categoria_nombre)
    data = []
    for p in productos:
        data.append({
            'nombre': p.nombre,
            'precio': p.precio,
            'imagen': p.imagen.url if hasattr(p.imagen, 'url') else p.imagen,
            'descripcion': p.descripcion_producto,
        })
    return JsonResponse(data, safe=False)


# LISTA DE PRODUCTOS (solo los del vendedor autenticado)
def productos(request):
    """Muestra la lista de productos del vendedor autenticado."""
    user_id = request.session.get("user_id")
    rol_sesion = request.session.get("rol")
    print("DEBUG: session user_id:", user_id, "rol:", rol_sesion)

    if not user_id:
        return HttpResponse("❌ No hay sesión activa. Por favor inicia sesión.")

    # Buscar la persona por id_personas
    persona = Personas.objects.filter(id_personas=user_id).first()
    if not persona:
        msg = f"❌ No se encontró Persona con id_personas={user_id}."
        print("DEBUG:", msg)
        return HttpResponse(msg)

    rol_persona = (persona.rol or "").lower()
    print(f"DEBUG: persona.id_personas={persona.id_personas} rol_persona='{rol_persona}' correo='{persona.correo_persona}'")

    # Buscar el vendedor asociado
    vendedor = Vendedores.objects.filter(personas_id_personas=persona).first()
    if not vendedor:
        vendedor_alt = Vendedores.objects.filter(personas_id_personas_id=persona.id_personas).first()
        if vendedor_alt:
            vendedor = vendedor_alt

    if not vendedor:
        msg = ("❌ No tienes permisos para ver productos (no eres vendedor).\n"
               "Comprueba:\n"
               "  - Que el registro en la tabla 'personas' tiene rol='vendedor' (o 'Vendedor').\n"
               "  - Que existe una fila en la tabla 'vendedores' vinculada a esa persona.\n"
               f"Detalles actuales: persona.rol='{persona.rol}', persona.id_personas={persona.id_personas}")
        print("DEBUG:", msg)
        return HttpResponse(msg.replace("\n", "<br/>"))

    # Obtener los productos del vendedor
    productos = Productos.objects.filter(vendedor=vendedor)

    # Filtrado opcional
    criterio = request.GET.get("criterio", "")
    valor = request.GET.get("valor", "")
    if criterio and valor:
        criterio = criterio.lower()
        if criterio == "nombre":
            productos = productos.filter(nombre__icontains=valor)
        elif criterio == "precio":
            productos = productos.filter(precio__icontains=valor)
        elif criterio == "stock":
            productos = productos.filter(cantidad_existente__icontains=valor)

    # Pasamos también la persona al template para mostrar el mensaje de bienvenida
    return render(request, "seller/productos.html", {
        "productos": productos,
        "criterio": criterio,
        "valor": valor,
        "persona": persona, 
    })


# CREAR PRODUCTO
def producto_create(request):
    """Crea un nuevo producto."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    persona = Personas.objects.filter(id_personas=user_id).first()
    vendedor = Vendedores.objects.filter(personas_id_personas=persona.id_personas).first() if persona else None

    if not vendedor:
        return HttpResponse("❌ No tienes permisos para crear productos (no eres vendedor).")
        
    # Obtener todas las categorías para el formulario
    categorias = Categoria.objects.all()

    form = ProductoCreateForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            # Extraer todos los valores validados
            nombre = form.cleaned_data.get("nombre")
            descripcion = form.cleaned_data.get("descripcion_producto")
            precio = form.cleaned_data.get("precio")
            cantidad = form.cleaned_data.get("cantidad_existente")
            referencia = form.cleaned_data.get("referencia")
            stock_min = form.cleaned_data.get("stock_min")
            stock_max = form.cleaned_data.get("stock_max")
            imagen = form.cleaned_data.get("imagen")

            nombre_archivo = None
            if imagen:
                nombre_archivo = f"{uuid.uuid4()}_{imagen.name}"
                ruta = os.path.join(settings.MEDIA_ROOT, "uploads", nombre_archivo)
                os.makedirs(os.path.dirname(ruta), exist_ok=True)
                with open(ruta, "wb+") as destino:
                    for chunk in imagen.chunks():
                        destino.write(chunk)

            # Obtener la categoría seleccionada
            categoria_id = form.cleaned_data.get("categoria_id_categoria")
            categoria = Categoria.objects.get(id_categoria=categoria_id.id_categoria) if categoria_id else None

            Productos.objects.create(
                nombre=nombre,
                descripcion_producto=descripcion,
                precio=precio,
                cantidad_existente=cantidad,
                referencia=referencia,
                stock_min=stock_min,
                stock_max=stock_max,
                vendedor=vendedor,
                imagen=f"uploads/{nombre_archivo}" if imagen else None,
                categoria_id_categoria=categoria
            )

            return redirect("productos")
        else:
            # Si hay errores de validación, se re-renderiza la plantilla con el formulario (incluyendo errores)
            return render(request, "seller/producto/create.html", {
                'categorias': categorias,
                'form': form
            })

    # GET: mostrar formulario vacío
    return render(request, "seller/producto/create.html", {
        'categorias': categorias,
        'form': form
    })


# EDITAR PRODUCTO
def producto_editar(request, id):
    """Edita un producto existente."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    producto = get_object_or_404(Productos, pk=id)
    persona = Personas.objects.filter(id_personas=user_id).first()
    vendedor = Vendedores.objects.filter(personas_id_personas=persona.id_personas).first() if persona else None

    if not vendedor or producto.vendedor != vendedor:
        return HttpResponse("❌ No tienes permisos para editar este producto.")

    if request.method == "POST":
        producto.nombre = request.POST.get("nombre")
        producto.descripcion_producto = request.POST.get("descripcion_producto")
        producto.precio = request.POST.get("precio")
        producto.cantidad_existente = request.POST.get("cantidad_existente")
        producto.referencia = request.POST.get("referencia")
        producto.stock_min = request.POST.get("stock_min")
        producto.stock_max = request.POST.get("stock_max")

        imagen = request.FILES.get("imagen")
        if imagen:
            nombre_archivo = f"{uuid.uuid4()}_{imagen.name}"
            ruta = os.path.join(settings.MEDIA_ROOT, "uploads", nombre_archivo)
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            with open(ruta, "wb+") as destino:
                for chunk in imagen.chunks():
                    destino.write(chunk)
            producto.imagen = f"uploads/{nombre_archivo}"

        producto.save()
        return redirect("productos")

    return render(request, "seller/producto/edit.html", {"producto": producto})


# ELIMINAR PRODUCTO
def producto_eliminar(request, id):
    """Elimina un producto."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    producto = get_object_or_404(Productos, pk=id)
    persona = Personas.objects.filter(id_personas=user_id).first()
    vendedor = Vendedores.objects.filter(personas_id_personas=persona.id_personas).first() if persona else None

    if not vendedor or producto.vendedor != vendedor:
        return HttpResponse("❌ No tienes permisos para eliminar este producto.")

    producto.delete()
    return redirect("productos")


# EXPORTAR PRODUCTOS A CSV
def productos_reporte_csv(request):
    """Genera un reporte CSV de los productos del vendedor."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    persona = Personas.objects.filter(id_personas=user_id).first()
    vendedor = Vendedores.objects.filter(personas_id_personas=persona.id_personas).first() if persona else None

    productos = Productos.objects.filter(vendedor=vendedor)

    criterio = request.GET.get("criterio")
    valor = request.GET.get("valor")
    if criterio and valor:
        criterio = criterio.lower()
        if criterio == "nombre":
            productos = productos.filter(nombre__icontains=valor)
        elif criterio == "precio":
            productos = productos.filter(precio=valor)
        elif criterio == "stock":
            productos = productos.filter(cantidad_existente=valor)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="productos.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Nombre", "Precio", "Cantidad", "Referencia"])
    for p in productos:
        writer.writerow([p.id_producto, p.nombre, p.precio, p.cantidad_existente, p.referencia])

    return response


#  EXPORTAR PRODUCTOS A PDF
def productos_pdf(request):
    """
    Genera un reporte PDF avanzado de los productos del vendedor.
    Incluye tabla, gráfico de barras de stock y gráfico circular de precios.
    Delega a report_views.productos_pdf para la implementación.
    """
    from core.views.report_views import generar_reporte_productos_pdf
    return generar_reporte_productos_pdf(request)

