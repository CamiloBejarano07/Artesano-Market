from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password
import csv, io

from core.models import Personas, Productos, Vendedores
from django.contrib.auth.hashers import check_password

from django.conf import settings
from django.utils import timezone
from django.shortcuts import render


# ======================================================
#  LISTAR VENDEDORES
# ======================================================
def listar_vendedores(request):
    vendedores = Vendedores.objects.select_related("personas_id_personas").all()
    return render(request, "admin/lista.html", {"vendedores": vendedores})


# ======================================================
#  CREAR VENDEDOR
# ======================================================
def crear_vendedor(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre_persona")
        apellido = request.POST.get("apellido_persona")
        correo = request.POST.get("correo_persona")
        telefono = request.POST.get("telefono")
        direccion = request.POST.get("direccion")
        password = request.POST.get("password")

        # Validar correo duplicado
        if Personas.objects.filter(correo_persona=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect("crear_vendedor")

        persona = Personas.objects.create(
            nombre_persona=nombre,
            apellido_persona=apellido,
            correo_persona=correo,
            telefono=telefono,
            direccion=direccion,
            rol="Vendedor",
            estado="Activo", 
            password=make_password(password),
        )

        Vendedores.objects.create(personas_id_personas=persona)

        messages.success(request, "Vendedor creado exitosamente.")
        return redirect("listar_vendedores")

    return render(request, "admin/create.html")


# ======================================================
#  DETALLE DEL VENDEDOR
# ======================================================
def detalle_vendedor(request, id):
    persona = get_object_or_404(Personas, id_personas=id)
    vendedor = get_object_or_404(Vendedores, personas_id_personas=persona)
    return render(request, "admin/show.html", {"vendedor": vendedor})


# ======================================================
#  EDITAR VENDEDOR
# ======================================================
def editar_vendedor(request, id):
    persona = get_object_or_404(Personas, id_personas=id)
    vendedor = get_object_or_404(Vendedores, personas_id_personas=persona)

    if request.method == "POST":
        persona.nombre_persona = request.POST.get("nombre_persona")
        persona.apellido_persona = request.POST.get("apellido_persona")
        persona.correo_persona = request.POST.get("correo_persona")
        persona.telefono = request.POST.get("telefono")
        persona.direccion = request.POST.get("direccion")
        persona.save()

        messages.success(request, "Vendedor actualizado correctamente.")
        return redirect("detalle_vendedor", id=persona.id_personas)

    return render(request, "admin/edit.html", {"persona": persona})


# ======================================================
# SUSPENDER VENDEDOR (NO ELIMINAR)
# ======================================================
def eliminar_vendedor(request, id):
    persona = get_object_or_404(Personas, id_personas=id)
    vendedor = get_object_or_404(Vendedores, personas_id_personas=persona)

    # En lugar de eliminar, cambia el estado
    persona.estado = "Suspendido"
    persona.save()

    messages.warning(request, f"El vendedor {persona.nombre_persona} ha sido suspendido.")
    return redirect("listar_vendedores")


# ======================================================
#  REACTIVAR VENDEDOR
# ======================================================

def reactivar_vendedor(request, id):
    """Vuelve a activar un vendedor que estaba suspendido.

    Esta vista acepta únicamente peticiones POST para evitar activaciones por GET.
    """
    persona = get_object_or_404(Personas, id_personas=id)
    vendedor = get_object_or_404(Vendedores, personas_id_personas=persona)

    if request.method != "POST":
        messages.info(request, "Acción inválida. La reactivación debe realizarse mediante un formulario.")
        return redirect("listar_vendedores")

    if persona.estado and persona.estado.lower() == "activo":
        messages.info(request, f"El vendedor {persona.nombre_persona} ya está activo.")
        return redirect("listar_vendedores")

    persona.estado = "Activo"
    persona.save()

    messages.success(request, f"El vendedor {persona.nombre_persona} ha sido reactivado.")
    return redirect("listar_vendedores")


# ======================================================
# FILTRAR VENDEDORES
# ======================================================
def filtrar_vendedores(request):
    criterio = request.GET.get("criterio")
    busqueda = request.GET.get("busqueda", "")
    estado = request.GET.get("estado", "")

    vendedores = Vendedores.objects.select_related("personas_id_personas").all()

    if criterio and busqueda:
        if criterio == "nombre":
            vendedores = vendedores.filter(personas_id_personas__nombre_persona__icontains=busqueda)
        elif criterio == "apellido":
            vendedores = vendedores.filter(personas_id_personas__apellido_persona__icontains=busqueda)
        elif criterio == "correo":
            vendedores = vendedores.filter(personas_id_personas__correo_persona__icontains=busqueda)
        elif criterio == "telefono":
            vendedores = vendedores.filter(personas_id_personas__telefono__icontains=busqueda)

    if estado:
        vendedores = vendedores.filter(personas_id_personas__estado__iexact=estado)

    return render(
        request,
        "admin/lista.html",
        {
            "vendedores": vendedores,
            "criterio": criterio,
            "busqueda": busqueda,
            "estado": estado,
        },
    )


# ======================================================
# REPORTE DE VENDEDORES
# ======================================================
def reporte_vendedores(request):
    criterio = request.GET.get('criterio')
    busqueda = request.GET.get('busqueda')

    vendedores = Vendedores.objects.select_related('personas_id_personas')

    if criterio and busqueda:
        if criterio == 'nombre':
            vendedores = vendedores.filter(personas_id_personas__nombre_persona__icontains=busqueda)
        elif criterio == 'apellido':
            vendedores = vendedores.filter(personas_id_personas__apellido_persona__icontains=busqueda)
        elif criterio == 'correo':
            vendedores = vendedores.filter(personas_id_personas__correo_persona__icontains=busqueda)
        elif criterio == 'telefono':
            vendedores = vendedores.filter(personas_id_personas__telefono__icontains=busqueda)
        elif criterio == 'direccion':
            vendedores = vendedores.filter(personas_id_personas__direccion__icontains=busqueda)

    contexto = {
        'vendedores': vendedores,
        'criterio': criterio,
        'busqueda': busqueda,
        'fecha_actual': datetime.now(),
    }

    return render(request, 'admin/reporte_vendedores.html', contexto)


# ======================================================
# EXPORTAR A CSV
# ======================================================
def exportar_csv(request):
    vendedores = Vendedores.objects.select_related("personas_id_personas").all()

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="vendedores.csv"'

    writer = csv.writer(response)
    writer.writerow(["Nombre", "Apellido", "Correo", "Teléfono", "Dirección", "Estado"])

    for v in vendedores:
        p = v.personas_id_personas
        writer.writerow([p.nombre_persona, p.apellido_persona, p.correo_persona, p.telefono, p.direccion, p.estado])

    return response


# ======================================================
# CARGA MASIVA DESDE CSV
# ======================================================
def cargar_csv(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        data = file.read().decode("utf-8")
        io_string = io.StringIO(data)
        reader = csv.reader(io_string, delimiter=",")
        next(reader, None)  

        for row in reader:
            if len(row) < 6:
                continue  

            correo = row[2]
            if Personas.objects.filter(correo_persona=correo).exists():
                continue  

            persona = Personas.objects.create(
                nombre_persona=row[0],
                apellido_persona=row[1],
                correo_persona=correo,
                direccion=row[3],
                password=make_password(row[4]),
                rol="Vendedor",
                telefono=row[5],
                estado="Activo",
            )

            Vendedores.objects.create(personas_id_personas=persona)

        messages.success(request, "Archivo CSV cargado correctamente.")
    else:
        messages.error(request, "Debes seleccionar un archivo CSV válido.")

    return redirect("listar_vendedores")


# ======================================================
#  PERFIL DEL VENDEDOR (cliente-equivalente)
# ======================================================
def perfil_seller(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión para ver tu perfil de vendedor.")
        return redirect('login')

    persona = Personas.objects.filter(id_personas=user_id).first()
    if not persona:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    # Verificar rol
    if not persona.rol or persona.rol.lower() != 'vendedor':
        messages.error(request, "No tienes permisos para ver este perfil.")
        return redirect('inicio')

    context = {
        'user_logged': True,
        'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
        'persona': persona,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'seller/perfil_seller.html', context)


# ======================================================
#  EDITAR PERFIL VENDEDOR (editar datos y/o contraseña)
# ======================================================
def editar_perfil_seller(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión para editar tu perfil.")
        return redirect('login')

    persona = Personas.objects.filter(id_personas=user_id).first()
    if not persona:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    # Solo vendedores
    if not persona.rol or persona.rol.lower() != 'vendedor':
        messages.error(request, "No tienes permisos para editar este perfil.")
        return redirect('inicio')

    errors = {}

    if request.method == 'GET':
        return render(request, 'seller/editar_perfil_seller.html', {
            'persona': persona,
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
            'errors': errors,
        })

    # POST
    action = request.POST.get('action')

    # Campos perfil
    nombre = request.POST.get('nombre')
    apellido = request.POST.get('apellido')
    correo = request.POST.get('correo')
    telefono = request.POST.get('telefono')
    direccion = request.POST.get('direccion')

    # Campos contraseña
    current_password = request.POST.get('current_password')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')

    if action == 'update_info' or not action:
        if correo and Personas.objects.filter(correo_persona=correo).exclude(id_personas=persona.id_personas).exists():
            errors['correo'] = "El correo ya está en uso por otro usuario."
            return render(request, 'seller/editar_perfil_seller.html', {
                'persona': persona,
                'user_logged': True,
                'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                'errors': errors,
            })

        persona.nombre_persona = nombre or persona.nombre_persona
        persona.apellido_persona = apellido or persona.apellido_persona
        persona.correo_persona = correo or persona.correo_persona
        persona.telefono = telefono or persona.telefono
        persona.direccion = direccion or persona.direccion

        try:
            persona.save()
            # Asegurar relación en tabla Vendedores
            try:
                if persona.rol and persona.rol.lower() == 'vendedor':
                    Vendedores.objects.get_or_create(personas_id_personas=persona)
            except Exception:
                pass

            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('perfil_seller')
        except Exception as e:
            errors['general'] = f"Error al guardar los cambios: {str(e)}"
            return render(request, 'seller/editar_perfil_seller.html', {
                'persona': persona,
                'user_logged': True,
                'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                'errors': errors,
            })

    if action == 'update_password':
        if not current_password:
            errors['current_password'] = "Debes ingresar tu contraseña actual para cambiar la contraseña."
            return render(request, 'seller/editar_perfil_seller.html', {
                'persona': persona,
                'user_logged': True,
                'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                'errors': errors,
            })

        current_ok = False
        try:
            if persona.password and check_password(current_password, persona.password):
                current_ok = True
            else:
                if persona.password and persona.password == current_password:
                    persona.password = make_password(current_password)
                    persona.save()
                    current_ok = True
        except Exception:
            if persona.password and persona.password == current_password:
                persona.password = make_password(current_password)
                persona.save()
                current_ok = True

        if not current_ok:
            errors['current_password'] = "La contraseña actual es incorrecta."
            return render(request, 'seller/editar_perfil_seller.html', {
                'persona': persona,
                'user_logged': True,
                'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                'errors': errors,
            })

        if not new_password or not confirm_password:
            errors['new_password'] = "Ingresa la nueva contraseña y confirmación."
            return render(request, 'seller/editar_perfil_seller.html', {
                'persona': persona,
                'user_logged': True,
                'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                'errors': errors,
            })

        if new_password != confirm_password:
            errors['confirm_password'] = "La nueva contraseña y la confirmación no coinciden."
            return render(request, 'seller/editar_perfil_seller.html', {
                'persona': persona,
                'user_logged': True,
                'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                'errors': errors,
            })

        from core.views.auth_views import validate_password
        valid_pass, pass_msg = validate_password(new_password)
        if not valid_pass:
            errors['new_password'] = pass_msg
            return render(request, 'seller/editar_perfil_seller.html', {
                'persona': persona,
                'user_logged': True,
                'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                'errors': errors,
            })

        persona.password = make_password(new_password)
        try:
            persona.save()
        except Exception as e:
            errors['general'] = f"Error al guardar la nueva contraseña: {str(e)}"
            return render(request, 'seller/editar_perfil_seller.html', {
                'persona': persona,
                'user_logged': True,
                'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                'errors': errors,
            })

        request.session.flush()
        messages.success(request, "Contraseña actualizada. Por favor, inicia sesión nuevamente.")
        return redirect('login')


# ======================================================
#  DASHBOARD DEL VENDEDOR
# ======================================================
def dashboard_vendedor(request):
    from django.utils.timezone import now
    from django.db.models import Count, Sum, F, Q
    from django.db.models.functions import TruncDate
    import json
    
    # ========== VALIDACIÓN DE SESIÓN Y AUTENTICACIÓN ==========
    # Verificar que existe sesión de usuario
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    # Obtener la persona autenticada
    try:
        persona = Personas.objects.get(id_personas=user_id)
    except Personas.DoesNotExist:
        request.session.flush()  # Limpiar sesión corrupta
        return redirect('login')
    
    # Validar que la persona sea vendedor (sensible a mayúsculas)
    if not persona.rol or persona.rol.lower() != 'vendedor':
        return redirect('login')
    
    # Obtener el objeto Vendedores del usuario autenticado
    try:
        vendedor = Vendedores.objects.get(personas_id_personas=persona)
    except Vendedores.DoesNotExist:
        return redirect('login')
    
    # Importar modelos necesarios
    from core.models import Productos, Ventas, ProductosHasVentas, Categoria
    
    # ========== GARANTÍA DE SEGURIDAD ==========
    # IMPORTANTE: TODAS las consultas filtran exclusivamente por:
    #   - Productos.objects.filter(vendedor=vendedor)
    #   - Ventas.objects.filter(productoshasventas__producto_id_producto__vendedor=vendedor)
    # Esto garantiza aislamiento total: cada vendedor SOLO ve sus datos
    # ==========================================="
    
    # ========== 1. PRODUCTOS REGISTRADOS ==========
    # Contar productos del vendedor autenticado
    try:
        seller_products = Productos.objects.filter(vendedor=vendedor).count()
    except Exception as e:
        seller_products = 0
    
    # ========== 2. VENTAS DEL DÍA ==========
    # Obtener total de ventas y cantidad de ventas de HOY del vendedor
    today = now().date()
    try:
        ventas_hoy = Ventas.objects.filter(
            productoshasventas__producto_id_producto__vendedor=vendedor,
            fecha_venta__date=today
        ).values('id_venta').annotate(
            total_venta=F('total')
        ).aggregate(
            total=Sum('total_venta'),
            count=Count('id_venta')
        )
        sales_today = float(ventas_hoy.get('total') or 0)
        sales_today_count = int(ventas_hoy.get('count') or 0)
    except Exception as e:
        sales_today = 0.0
        sales_today_count = 0
    
    # ========== 3. INGRESOS TOTALES ACUMULADOS ==========
    # Obtener suma total de TODAS las ventas del vendedor (historial completo)
    try:
        ventas_totales_agg = Ventas.objects.filter(
            productoshasventas__producto_id_producto__vendedor=vendedor
        ).values('id_venta').annotate(
            total_venta=F('total')
        ).aggregate(
            total=Sum('total_venta'),
            count=Count('id_venta')
        )
        total_earnings = float(ventas_totales_agg.get('total') or 0)
        total_sales_count = int(ventas_totales_agg.get('count') or 0)
    except Exception as e:
        total_earnings = 0.0
        total_sales_count = 0
    
    # ========== 4. PEDIDOS COMPLETADOS ==========
    # Contar TODAS las ventas completadas del vendedor
    try:
        completed_orders = Ventas.objects.filter(
            productoshasventas__producto_id_producto__vendedor=vendedor
        ).values('id_venta').count()
    except Exception as e:
        completed_orders = 0
    
    # ========== 5. PRODUCTOS MÁS VENDIDOS ==========
    # Obtener top 10 de productos del vendedor ordenados por cantidad de ventas
    try:
        best_products = Productos.objects.filter(
            vendedor=vendedor,
            productoshasventas__isnull=False  # Solo productos con ventas
        ).values('id_producto', 'nombre').annotate(
            sales_count=Count('productoshasventas')
        ).order_by('-sales_count')[:10]
        
        if best_products:
            product_names = [p['nombre'] or f"Producto {p['id_producto']}" for p in best_products]
            product_counts = [int(p['sales_count']) for p in best_products]
        else:
            product_names = []
            product_counts = []
    except Exception as e:
        product_names = []
        product_counts = []
    
    products_data_json = json.dumps({'names': product_names, 'counts': product_counts})
    
    # ========== 6. STOCK DE PRODUCTOS ==========
    # Traer estado de stock actual vs min/max para cada producto del vendedor
    stock_names = []
    stock_current = []
    stock_min = []
    stock_max = []
    
    try:
        stock_data = Productos.objects.filter(
            vendedor=vendedor
        ).values('nombre', 'cantidad_existente', 'stock_min', 'stock_max').order_by('nombre')
        
        for p in stock_data:
            stock_names.append(p['nombre'] or 'Sin nombre')
            stock_current.append(int(p['cantidad_existente'] or 0))
            stock_min.append(int(p['stock_min'] or 0))
            stock_max.append(int(p['stock_max'] or 0))
    except Exception as e:
        pass  # stock_names/current/min/max quedan vacíos
    
    stock_data_json = json.dumps({'names': stock_names, 'current': stock_current, 'minStock': stock_min, 'maxStock': stock_max})
    
    # ========== 7. PRODUCTOS POR CATEGORÍA ==========
    # Contar cuántos productos del vendedor hay en cada categoría
    category_names = []
    category_counts = []
    
    try:
        category_data = list(
            Productos.objects.filter(vendedor=vendedor).values(
                'categoria_id_categoria__nombre_categoria'
            ).annotate(count=Count('id_producto')).order_by('-count')
        )
        
        if category_data:
            category_names = [
                c['categoria_id_categoria__nombre_categoria'] or 'Sin categoría' 
                for c in category_data
            ]
            category_counts = [c['count'] for c in category_data]
    except Exception as e:
        pass  # category_names/counts quedan vacíos
    
    category_data_json = json.dumps({'names': category_names, 'counts': category_counts})
    
    # ========== 8. VENTAS POR PERÍODO (Día/Mes/Año) ==========
    # Agrupar ventas del vendedor por período para gráficas dinámicas
    sales_by_day = {}
    sales_by_month = {}
    sales_by_year = {}
    
    try:
        sales_by_date_raw = Ventas.objects.filter(
            productoshasventas__producto_id_producto__vendedor=vendedor
        ).values('id_venta', 'total', 'fecha_venta').order_by('fecha_venta')
        
        for venta in sales_by_date_raw:
            if venta['fecha_venta']:
                fecha = venta['fecha_venta']
                total = float(venta['total'] or 0)
                
                # Agrupar por día (YYYY-MM-DD)
                date_key = fecha.date().isoformat()
                if date_key not in sales_by_day:
                    sales_by_day[date_key] = {'amount': 0.0, 'count': 0}
                sales_by_day[date_key]['amount'] += total
                sales_by_day[date_key]['count'] += 1
                
                # Agrupar por mes (YYYY-MM)
                month_key = date_key[:7]
                if month_key not in sales_by_month:
                    sales_by_month[month_key] = {'amount': 0.0, 'count': 0}
                sales_by_month[month_key]['amount'] += total
                sales_by_month[month_key]['count'] += 1
                
                # Agrupar por año (YYYY)
                year_key = date_key[:4]
                if year_key not in sales_by_year:
                    sales_by_year[year_key] = {'amount': 0.0, 'count': 0}
                sales_by_year[year_key]['amount'] += total
                sales_by_year[year_key]['count'] += 1
    except Exception as e:
        pass  # sales_by_day/month/year quedan vacíos
    
    sales_data_json = json.dumps({
        'day': sales_by_day,
        'month': sales_by_month,
        'year': sales_by_year
    })
    
    # Validaciones: asegurar que todos los valores son válidos antes de pasar al contexto
    try:
        sales_today = float(sales_today) if sales_today else 0.0
        sales_today_count = int(sales_today_count) if sales_today_count else 0
        total_earnings = float(total_earnings) if total_earnings else 0.0
        total_sales_count = int(total_sales_count) if total_sales_count else 0
        completed_orders = int(completed_orders) if completed_orders else 0
        seller_products = int(seller_products) if seller_products else 0
    except (ValueError, TypeError):
        sales_today = 0.0
        sales_today_count = 0
        total_earnings = 0.0
        total_sales_count = 0
        completed_orders = 0
        seller_products = 0
    
    # Contexto con datos frescos de la base de datos (exclusivos del vendedor autenticado)
    context = {
        'seller_products': seller_products,
        'sales_today': round(sales_today, 2),
        'sales_today_float': sales_today,  # Valor sin redondeo para cálculos JS
        'sales_today_count': sales_today_count,
        'total_earnings': round(total_earnings, 2),
        'total_earnings_float': total_earnings,  # Valor sin redondeo para cálculos JS
        'total_sales_count': total_sales_count,
        'completed_orders': completed_orders,
        'products_data': products_data_json,
        'stock_data': stock_data_json,
        'category_data': category_data_json,
        'sales_data': sales_data_json,
        'vendedor': vendedor
    }
    
    return render(request, 'seller/estadisticas.html', context)


# ======================================================
#  PANEL DE PRODUCTOS DEL VENDEDOR
# ======================================================
def panel_productos_vendedor(request):
    """
    Panel para que el vendedor vea sus productos publicados y alerta de stock bajo.
    Muestra separadamente: Productos Publicados y Productos con Stock Bajo (≤5).
    """
    try:
        # Validar sesión del usuario
        if 'user_id' not in request.session:
            return redirect('login')
        
        # Obtener la persona autenticada
        persona = Personas.objects.get(id_personas=request.session['user_id'])
        
        # Verificar que sea vendedor
        vendedor = Vendedores.objects.get(personas_id_personas=persona)
        
        # Obtener todos los productos del vendedor
        todos_productos = Productos.objects.filter(vendedor=vendedor).order_by('-id_producto')
        
        # Procesar búsqueda y filtrado
        criterio = request.GET.get('criterio', 'nombre')
        valor = request.GET.get('valor', '').strip()
        
        if valor:
            if criterio == 'nombre':
                todos_productos = todos_productos.filter(nombre__icontains=valor)
            elif criterio == 'precio':
                try:
                    precio_valor = float(valor)
                    todos_productos = todos_productos.filter(precio=precio_valor)
                except ValueError:
                    pass
            elif criterio == 'stock':
                try:
                    stock_valor = int(valor)
                    todos_productos = todos_productos.filter(cantidad_existente=stock_valor)
                except ValueError:
                    pass
        
        # Separar productos por estado de stock
        productos_stock_bajo = []
        productos_publicados = []
        
        for producto in todos_productos:
            if producto.cantidad_existente <= 5:
                producto.stock_bajo_alerta = True
                productos_stock_bajo.append(producto)
            else:
                producto.stock_bajo_alerta = False
                productos_publicados.append(producto)
        
        context = {
            'productos_publicados': productos_publicados,
            'productos_stock_bajo': productos_stock_bajo,
            'total_productos': len(todos_productos),
            'total_stock_bajo': len(productos_stock_bajo),
            'vendedor': vendedor,
            'criterio': criterio,
            'valor': valor
        }
        
        return render(request, 'seller/panel_productos.html', context)
    
    except Personas.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')
    except Vendedores.DoesNotExist:
        messages.error(request, "No tienes permisos de vendedor.")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error al cargar el panel: {str(e)}")
        return redirect('login')


# ======================================================
# HISTORIAL DE VENTAS DEL VENDEDOR
# ======================================================
def historial_ventas_vendedor(request):
 
    try:
        # Validar sesión del usuario
        if 'user_id' not in request.session:
            messages.warning(request, "Debes iniciar sesión para ver tu historial de ventas.")
            return redirect('login')
        
        # Obtener la persona autenticada
        persona = Personas.objects.get(id_personas=request.session['user_id'])
        
        # Verificar que sea vendedor
        vendedor = Vendedores.objects.get(personas_id_personas=persona)
        
        # Importar modelos necesarios
        from core.models import Productos, ProductosHasVentas, Ventas
        from django.db.models import F, Sum, Count
        
        # ========== CALCULAR INGRESOS TOTALES (MISMA LÓGICA DEL DASHBOARD) ==========
        # Esto suma venta.total sin duplicar (agrupa por id_venta)
        try:
            ventas_totales_agg = Ventas.objects.filter(
                productoshasventas__producto_id_producto__vendedor=vendedor
            ).values('id_venta').annotate(
                total_venta=F('total')
            ).aggregate(
                total=Sum('total_venta'),
                count=Count('id_venta')
            )
            total_ingresos_dashboard = float(ventas_totales_agg.get('total') or 0)
            total_ventas_unicas = int(ventas_totales_agg.get('count') or 0)
        except Exception as e:
            total_ingresos_dashboard = 0.0
            total_ventas_unicas = 0
        
        # ========== OBTENER TODAS LAS LÍNEAS DE VENTA DEL VENDEDOR ==========
        # Para mostrar detalles, obtenemos ProductosHasVentas filtrado por vendedor
        lineas_venta = ProductosHasVentas.objects.filter(
            producto_id_producto__vendedor=vendedor
        ).select_related(
            'producto_id_producto',
            'ventas_id_venta',
            'ventas_id_venta__clientes_personas_id_personas'
        ).order_by('-ventas_id_venta__fecha_venta')
        
        ventas_detalles = []
        
        # Procesar cada línea de venta para mostrar
        for linea in lineas_venta:
            producto = linea.producto_id_producto
            venta = linea.ventas_id_venta
            cantidad = linea.cantidad or 1
            precio_unitario = float(producto.precio or 0)
            
            # Subtotal de la línea (para mostrar)
            subtotal_linea = precio_unitario * cantidad
            
            # Obtener datos del cliente
            cliente_nombre = "Desconocido"
            if venta.clientes_personas_id_personas:
                try:
                    cliente_obj = venta.clientes_personas_id_personas
                    persona_cliente = Personas.objects.get(
                        id_personas=cliente_obj.personas_id_personas_id
                    )
                    cliente_nombre = f"{persona_cliente.nombre_persona} {persona_cliente.apellido_persona}".strip()
                except:
                    cliente_nombre = "Cliente registrado"
            
            # Crear diccionario con datos de la línea de venta
            linea_venta_data = {
                'id_venta': venta.id_venta,
                'id_linea': f"{venta.id_venta}_{producto.id_producto}",
                'producto_nombre': producto.nombre or "Producto sin nombre",
                'producto_precio': precio_unitario,
                'cantidad': cantidad,
                'subtotal': subtotal_linea,  # Subtotal de la línea (para mostrar)
                'fecha_venta': venta.fecha_venta,
                'fecha_venta_formateada': timezone.localtime(venta.fecha_venta).strftime('%d/%m/%Y %H:%M:%S') if venta.fecha_venta else "Fecha desconocida",
                'cliente_nombre': cliente_nombre,
                'imagen': producto.imagen,
                'estado': venta.estado or "Pendiente",
                'metodo_pago': venta.metodo_pago or "No especificado",
                'total_venta': float(venta.total or 0),  # Total del pedido completo
            }
            
            ventas_detalles.append(linea_venta_data)
        
        # ========== ESTADÍSTICAS CORRECTAS ==========
        # Contar unidades vendidas
        total_unidades = sum(v['cantidad'] for v in ventas_detalles)
        
        context = {
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
            'vendedor': vendedor,
            'ventas': ventas_detalles,
            'total_lineas': len(ventas_detalles),
            'total_ventas': total_ventas_unicas,  # Ventas únicas (same as dashboard)
            'total_ingresos': round(total_ingresos_dashboard, 2),  # Same calculation as dashboard
            'total_unidades': total_unidades,
            'MEDIA_URL': settings.MEDIA_URL,
        }
        
        return render(request, 'seller/historial_ventas.html', context)
    
    except Personas.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')
    except Vendedores.DoesNotExist:
        messages.warning(request, "No tienes permisos de vendedor.")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error al cargar el historial de ventas: {str(e)}")
        return redirect('login')


# ========== MARCAR PEDIDO COMO ENVIADO ==========
def marcar_pedido_enviado(request, id_venta):
    """
    Marca un pedido como 'Enviado' cambiando el estado de la venta.
    Solo el vendedor propietario del pedido puede marcar como enviado.
    Envía un comprobante de envío al cliente por email.
    """
    try:
        # Validar sesión del usuario
        if 'user_id' not in request.session:
            messages.error(request, "Debes iniciar sesión para realizar esta acción.")
            return redirect('login')
        
        # Obtener la persona autenticada
        persona = Personas.objects.get(id_personas=request.session['user_id'])
        
        # Verificar que sea vendedor
        vendedor = Vendedores.objects.get(personas_id_personas=persona)
        
        # Importar modelos necesarios
        from core.models import Ventas, ProductosHasVentas, Clientes
        from core.services.email_service import ShipmentEmailService
        
        # Obtener la venta
        venta = Ventas.objects.get(id_venta=id_venta)
        
        # Verificar que la venta pertenece a este vendedor
        # Una venta pertenece al vendedor si tiene productos del vendedor
        productos_vendedor = ProductosHasVentas.objects.filter(
            ventas_id_venta=venta,
            producto_id_producto__vendedor=vendedor
        ).exists()
        
        if not productos_vendedor:
            messages.error(request, "No tienes permiso para actualizar este pedido.")
            return redirect('historial_ventas_vendedor')
        
        # Actualizar el estado a 'Enviado'
        venta.estado = 'Enviado'
        venta.save()
        
        # ✅ ENVIAR COMPROBANTE DE ENVÍO POR EMAIL
        try:
            # Obtener datos del cliente
            cliente = venta.clientes_personas_id_personas if hasattr(venta, 'clientes_personas_id_personas') else None
            
            if cliente:
                # Obtener persona del cliente
                cliente_persona = cliente if isinstance(cliente, Personas) else (cliente.personas_id_personas if hasattr(cliente, 'personas_id_personas') else None)
                
                # Preparar lista de productos para el email
                productos_para_email = []
                productos_rel = ProductosHasVentas.objects.filter(ventas_id_venta=venta).select_related('producto_id_producto')
                
                for pr in productos_rel:
                    producto = pr.producto_id_producto
                    cantidad = int(pr.cantidad) if pr.cantidad and pr.cantidad > 0 else 1
                    
                    productos_para_email.append({
                        'nombre': producto.nombre,
                        'cantidad': cantidad,
                    })
                
                # Enviar email con comprobante de envío
                ShipmentEmailService.enviar_comprobante_envio(venta, cliente_persona, productos_para_email, persona, request)
        except Exception as e:
            print(f"Error enviando comprobante de envío: {str(e)}")
            # No interrumpir el flujo si falla el email
        
        # Agregar mensaje con tag específico para que solo se muestre en el historial
        messages.success(request, "✅ Pedido marcado como enviado exitosamente.", extra_tags='shipping_notification')
        return redirect('historial_ventas_vendedor')
        
    except Personas.DoesNotExist:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')
    except Vendedores.DoesNotExist:
        messages.warning(request, "No tienes permisos de vendedor.")
        return redirect('login')
    except Ventas.DoesNotExist:
        messages.error(request, "Pedido no encontrado.")
        return redirect('historial_ventas_vendedor')
    except Exception as e:
        messages.error(request, f"Error al marcar pedido como enviado: {str(e)}")
        return redirect('historial_ventas_vendedor')
    except Exception as e:
        messages.error(request, f"Error al marcar pedido como enviado: {str(e)}")
        return redirect('historial_ventas_vendedor')

