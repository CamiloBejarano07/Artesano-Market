from django.shortcuts import render, redirect
from core.models import Productos, Clientes, Vendedores, Ventas, Personas, Compra, CompraHasProductos, ProductosHasVentas
from core.models import Categoria
from django.db.models import Prefetch
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
import json
from django.http import JsonResponse
from core.services.email_service import ReceiptEmailService
from core.decorators import requires_seller, requires_admin, requires_cliente

# NOTA: Stripe se puede importar aquí cuando sea necesario integrar pagos reales

#try:
#   import stripe
#  stripe.api_key = settings.STRIPE_SECRET_KEY
#except ImportError:
# stripe = None



# Página principal
def home(request):
    # Detectar si el usuario está autenticado por sesión
    user_id = request.session.get('user_id')
    user_logged = False
    user_name = None

    if user_id:
        user_logged = True
        try:
            persona = Personas.objects.filter(id_personas=user_id).first()
            if persona:
                user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()
        except Exception:
            user_name = None
    
    # Obtener productos registrados para mostrar como "destacados" (últimos 10)
    try:
        productos_destacados = Productos.objects.order_by('-id_producto')[:10]
    except Exception:
        productos_destacados = []

    # Añadir role del usuario si está autenticado
    user_role = None
    try:
        if user_id and persona and hasattr(persona, 'rol'):
            user_role = persona.rol
    except Exception:
        user_role = None

    context = {
        'user_logged': user_logged,
        'user_name': user_name,
        'user_role': user_role,
        'productos_destacados': productos_destacados,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    
    return render(request, 'pages/index.html', context)

# Catálogo general
def catalog(request):
    # Parámetros de filtrado
    categoria_id = request.GET.get('categoria')
    q = request.GET.get('q') or request.GET.get('busqueda') or ''
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    orden = request.GET.get('orden')

    # Obtener todas las categorías
    categorias = Categoria.objects.all()

    productos = Productos.objects.select_related('categoria_id_categoria', 'vendedor').all()

    # Aplicar filtros
    from django.db.models import Q

    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(descripcion_producto__icontains=q) | Q(referencia__icontains=q)
        )

    if categoria_id:
        try:
            productos = productos.filter(categoria_id_categoria_id=int(categoria_id))
        except Exception:
            pass

    try:
        if precio_min:
            productos = productos.filter(precio__gte=float(precio_min))
        if precio_max:
            productos = productos.filter(precio__lte=float(precio_max))
    except ValueError:
        pass

    if orden:
        if orden == 'precio_asc':
            productos = productos.order_by('precio')
        elif orden == 'precio_desc':
            productos = productos.order_by('-precio')
        elif orden == 'stock_desc':
            productos = productos.order_by('-cantidad_existente')
        elif orden == 'stock_asc':
            productos = productos.order_by('cantidad_existente')
        elif orden == 'nombre':
            productos = productos.order_by('nombre')
    
    # Detectar si el usuario está autenticado por sesión
    user_id = request.session.get('user_id')
    user_logged = False
    user_name = None

    if user_id:
        user_logged = True
        try:
            persona = Personas.objects.filter(id_personas=user_id).first()
            if persona:
                user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()
        except Exception:
            user_name = None
    
    # Añadir role del usuario al contexto para las plantillas
    user_role = None
    try:
        if user_id and persona and hasattr(persona, 'rol'):
            user_role = persona.rol
    except Exception:
        user_role = None

    context = {
        'categorias': categorias,
        'productos': productos,
        'categoria_actual': categoria_id,
        'MEDIA_URL': settings.MEDIA_URL,
        'user_logged': user_logged,
        'user_name': user_name,
        'user_role': user_role,
    }
    
    return render(request, 'pages/catalog.html', context)


def disminuir_carrito(request, producto_id):
    """Disminuye en 1 la cantidad de un producto en el carrito de sesión.
    Si la cantidad llega a 0, lo elimina.
    """
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        pid = str(producto_id)
        if pid in carrito:
            try:
                carrito[pid] = int(carrito[pid]) - 1
            except Exception:
                carrito[pid] = 0

            if carrito[pid] <= 0:
                carrito.pop(pid, None)

            request.session['carrito'] = carrito
            request.session.modified = True

    return redirect('cart')


def eliminar_carrito(request, producto_id):
    """Elimina por completo un producto del carrito de sesión."""
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        pid = str(producto_id)
        if pid in carrito:
            carrito.pop(pid, None)
            request.session['carrito'] = carrito
            request.session.modified = True

    return redirect('cart')

# Página de ayuda
def help_page(request):
    from core.forms import ContactFormForm
    from django.core.mail import send_mail
    from django.conf import settings
    from django.contrib import messages
    
    # Detectar si el usuario está autenticado por sesión
    user_id = request.session.get('user_id')
    user_logged = False
    user_name = None

    if user_id:
        user_logged = True
        try:
            persona = Personas.objects.filter(id_personas=user_id).first()
            if persona:
                user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()
        except Exception:
            user_name = None
    
    # Añadir role del usuario si está autenticado
    user_role = None
    try:
        if user_id:
            persona = Personas.objects.filter(id_personas=user_id).first()
            if persona and hasattr(persona, 'rol'):
                user_role = persona.rol
    except Exception:
        user_role = None

    form = None
    
    if request.method == 'POST':
        form = ContactFormForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            lastname = form.cleaned_data.get('lastname')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone', '')
            message = form.cleaned_data.get('message')
            
            # Preparar el contenido del correo
            subject = 'Nuevo mensaje desde formulario de contacto - Artesano Market'
            
            email_body = f"""
Nuevo mensaje de contacto desde Artesano Market

INFORMACIÓN DEL REMITENTE:
Nombre: {name} {lastname}
Email: {email}
Teléfono: {phone if phone else 'No proporcionado'}

MENSAJE:
{message}

---
Este mensaje fue enviado automáticamente desde el formulario de contacto de Artesano Market.
"""
            
            try:
                # Enviar el correo al email configurado en settings
                send_mail(
                    subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, '¡Tu mensaje ha sido enviado correctamente! Nos pondremos en contacto pronto.')
                form = ContactFormForm()  # Crear nuevo formulario vacío después del envío exitoso
            except Exception as e:
                messages.error(request, f'Hubo un error al enviar el mensaje. Por favor, intenta de nuevo.')
        else:
            # Si el formulario no es válido, Django mostrará los errores automáticamente
            pass
    else:
        form = ContactFormForm()

    context = {
        'user_logged': user_logged,
        'user_name': user_name,
        'user_role': user_role,
        'form': form,
    }
    
    return render(request, 'pages/help.html', context)

def cart(request):
    carrito = request.session.get('carrito', {})
    productos = []
    total = 0
    # Detectar si el usuario está autenticado por sesión
    user_id = request.session.get('user_id')
    user_logged = False
    user_name = None

    if user_id:
        user_logged = True
        try:
            persona = Personas.objects.filter(id_personas=user_id).first()
            if persona:
                user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()
        except Exception:
            user_name = None

    for producto_id, cantidad in list(carrito.items()):
        try:
            producto = Productos.objects.get(id_producto=producto_id)
            subtotal = producto.precio * cantidad
            total += subtotal
            productos.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        except Productos.DoesNotExist:
            # Si el producto ya no existe, lo eliminamos del carrito
            del carrito[producto_id]
            request.session['carrito'] = carrito

    # Añadir role del usuario al contexto del carrito
    user_role = None
    try:
        if user_id:
            persona = Personas.objects.filter(id_personas=user_id).first()
            if persona and hasattr(persona, 'rol'):
                user_role = persona.rol
    except Exception:
        user_role = None

    return render(request, 'pages/cart.html', {
        'productos': productos,
        'total': total,
        'MEDIA_URL': settings.MEDIA_URL,
        'user_logged': user_logged,
        'user_name': user_name,
        'user_role': user_role,
    })


def agregar_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        producto_id = str(producto_id)

        if producto_id in carrito:
            carrito[producto_id] += 1
        else:
            carrito[producto_id] = 1

        request.session['carrito'] = carrito

    return redirect('cart')


# Proceder al pago (SIMULACIÓN - Sin Stripe por ahora)
def checkout(request):
    """
    Vista de checkout con guardado real de compras y ventas:
    1. Verifica si el usuario está autenticado (tiene user_id en sesión)
    2. Si no está autenticado, redirige a login
    3. Si está autenticado, muestra formulario de checkout
    4. Al hacer POST:
       - Verifica stock disponible
       - Crea registro de venta en tabla Ventas
       - Crea relaciones en tabla ProductosHasVentas
       - Descuenta stock de productos
       - Limpia carrito
       - Retorna confirmación
    
    NOTA: La compra se registra cuando el cliente compra al vendedor
    """
    
    # Verificar si el usuario está autenticado
    user_id = request.session.get("user_id")
    
    if not user_id:
        messages.warning(request, "Debes iniciar sesión para completar la compra.")
        return redirect("login")
    
    # Usuario autenticado
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.warning(request, "El carrito está vacío.")
        return redirect('cart')
    
    # Si llega aquí con GET, mostrar el template de checkout
    if request.method == 'GET':
        # Calcular total para mostrar en el template
        total = 0
        for producto_id, cantidad in carrito.items():
            try:
                producto = Productos.objects.get(id_producto=producto_id)
                total += producto.precio * cantidad
            except Productos.DoesNotExist:
                continue
        
        # Información de sesión para el template
        user_id = request.session.get('user_id')
        user_logged = False
        user_name = None
        if user_id:
            user_logged = True
            try:
                persona = Personas.objects.filter(id_personas=user_id).first()
                if persona:
                    user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()
                    # Obtener rol si existe
                    user_role = persona.rol if hasattr(persona, 'rol') else None
            except Exception:
                user_name = None

        context = {
            'total': total,
            'total_cents': int(total * 100),
            'user_logged': user_logged,
            'user_name': user_name,
        }
        return render(request, 'pages/chekout.html', context)
    
    # Si es POST, procesar la compra
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            metodo_pago = request.POST.get('metodo_pago', 'Tarjeta')
            direccion_envio = request.POST.get('direccion_envio', '')
            comentarios = request.POST.get('comentarios', '')
            
            # Buscar cliente y persona en BD
            persona = Personas.objects.get(id_personas=user_id)
            
            # ✅ Obtener o crear cliente si no existe (para usuarios registrados antes del fix)
            cliente, created = Clientes.objects.get_or_create(personas_id_personas=persona)
            
            # Calcular totales del carrito y validar stock
            productos_carrito = []
            total_compra = 0.0
            
            for producto_id, cantidad in carrito.items():
                try:
                    producto = Productos.objects.get(id_producto=producto_id)
                    subtotal = float(producto.precio) * int(cantidad)
                    total_compra += subtotal
                    productos_carrito.append({
                        'producto': producto,
                        'cantidad': int(cantidad),
                        'subtotal': subtotal
                    })
                except Productos.DoesNotExist:
                    continue
            
            # Verificar stock disponible ANTES de procesar la compra
            for item in productos_carrito:
                producto = item['producto']
                cantidad_vendida = item['cantidad']
                
                if producto.cantidad_existente < cantidad_vendida:
                    return JsonResponse({
                        'success': False,
                        'error': f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.cantidad_existente}"
                    }, status=400)
            
            # ✅ PROCESAR COMPRA EXITOSA
            # Crear registro de venta
            fecha_venta = timezone.now()
            fecha_entrega_estimada = fecha_venta + timedelta(days=3)  # Entrega en 3 días
            
            venta = Ventas.objects.create(
                clientes_personas_id_personas=cliente,
                vendedores_personas_id_personas=None,  # Se asignará según el vendedor del producto
                metodo_pago=metodo_pago,
                direccion_envio=direccion_envio,
                comentarios=comentarios,
                sub_total=total_compra,
                total=total_compra,
                descuento=0.0,
                estado='Pagado',
                fecha_venta=fecha_venta,
                fecha_entrega_estimada=fecha_entrega_estimada
            )
            
            # ✅ ENVIAR COMPROBANTE DE PAGO POR EMAIL
            # Preparar datos de productos para el email
            productos_para_email = []
            for item in productos_carrito:
                producto = item['producto']
                cantidad = item['cantidad']
                precio_unitario = producto.precio
                subtotal = item['subtotal']
                
                productos_para_email.append({
                    'nombre': producto.nombre,
                    'cantidad': cantidad,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal
                })
            
            # Enviar email con comprobante (manejo de errores incorporado en el servicio)
            ReceiptEmailService.enviar_comprobante(venta, persona, productos_para_email, request)
            
            # Procesar cada producto: descontar stock y crear relaciones
            for item in productos_carrito:
                producto = item['producto']
                cantidad_vendida = item['cantidad']
                
                # ✅ DESCONTAR STOCK DEL PRODUCTO
                producto.cantidad_existente -= cantidad_vendida
                producto.save()
                
                # ✅ REGISTRAR EN TABLA ProductosHasVentas
                ProductosHasVentas.objects.create(
                    producto_id_producto=producto,
                    ventas_id_venta=venta,
                    cantidad=cantidad_vendida
                )
                
                # ✅ CREAR REGISTRO EN TABLA COMPRA (si el vendedor es el que compra al proveedor)
                # La compra registra cuando el vendedor compró al proveedor
                # Aquí es opcional, pero lo incluimos para completes la trazabilidad
                if producto.vendedor:
                    compra = Compra.objects.create(
                        fecha_compra=fecha_venta.date(),
                        metodo_pago=metodo_pago,
                        observaciones=f"Venta a cliente {persona.nombre_persona}",
                        sub_total_compra=item['subtotal'],
                        total_compra=item['subtotal'],
                        estado_compra='Completada',
                        vendedores_personas_id_personas=producto.vendedor,
                        proveedores_id_proveedores=None  # Sin proveedor específico
                    )
                    
                    # ✅ REGISTRAR EN TABLA CompraHasProductos
                    CompraHasProductos.objects.create(
                        compra_id_venta=compra,
                        producto_id_producto=producto
                    )
            
            # ✅ LIMPIAR CARRITO DESPUÉS DE COMPRA EXITOSA
            request.session['carrito'] = {}
            request.session.modified = True
            
            # Retornar éxito
            # Generar número de pedido a partir del id de la venta (sin alterar la BD)
            order_id = getattr(venta, 'id_venta', None) or getattr(venta, 'id', None)
            order_number = f"ART-000{order_id}" if order_id is not None else None

            # Redirigir a la página de confirmación (usamos la misma ruta de checkout con params)
            redirect_url = '/checkout/'
            if order_number:
                redirect_url = f"/checkout/?success=1&order={order_number}"

            return JsonResponse({
                'success': True,
                'message': '¡Compra completada exitosamente!',
                'order_number': order_number,
                'redirect_url': redirect_url
            })
        
        except Personas.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Error: No se encontró tu información de usuario.'
            }, status=400)
        except Exception as e:
            print(f"Error en checkout: {str(e)}")  # Para debugging
            return JsonResponse({
                'success': False,
                'error': f'Error al procesar la compra: {str(e)}'
            }, status=400)



# Error 404
def error404(request):
    return render(request, 'pages/error404.html')


# Detalle de producto
def product(request):
    
    producto_id = request.GET.get('id')
    if producto_id:
        producto = Productos.objects.select_related(
            'categoria_id_categoria', 
            'vendedor', 
            'vendedor__personas_id_personas'
        ).get(id_producto=producto_id)
        
        # Detectar si el usuario está autenticado por sesión
        user_id = request.session.get('user_id')
        user_logged = False
        user_name = None

        if user_id:
            user_logged = True
            try:
                persona = Personas.objects.filter(id_personas=user_id).first()
                if persona:
                    user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()
            except Exception:
                user_name = None
        
        from django.conf import settings
        return render(request, 'pages/product.html', {
            'producto': producto,
            'MEDIA_URL': settings.MEDIA_URL,
            'user_logged': user_logged,
            'user_name': user_name,
            'user_role': locals().get('user_role', None),
        })
    
    return redirect('catalog')

# DASHBOARDS por rol
@requires_admin
def dashboard_admin(request):
    return render(request, 'admin/dashboard.html')

@requires_seller
def dashboard_seller(request):
    return render(request, 'seller/dashboard.html')

def dashboard_cliente(request):
    # Detectar si el usuario está autenticado por sesión
    user_id = request.session.get('user_id')
    user_logged = False
    user_name = None

    if user_id:
        user_logged = True
        try:
            persona = Personas.objects.filter(id_personas=user_id).first()
            if persona:
                user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()
        except Exception:
            user_name = None

    # Obtener productos registrados para mostrar como "destacados" (últimos 10)
    try:
        productos_destacados = Productos.objects.order_by('-id_producto')[:10]
    except Exception:
        productos_destacados = []

    context = {
        'user_logged': user_logged,
        'user_name': user_name,
        'productos_destacados': productos_destacados,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'cliente/dashboard.html', context)


# Historial de pedidos del cliente autenticado
def historial(request):

    # Detectar usuario logueado por sesión
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Debes iniciar sesión para ver tu historial.")
        return redirect('login')

    persona = Personas.objects.filter(id_personas=user_id).first()
    cliente = Clientes.objects.filter(personas_id_personas=persona).first() if persona else None

    ventas_formateadas = []
    if cliente:
        ventas = Ventas.objects.filter(clientes_personas_id_personas=cliente).order_by('-fecha_venta')
        for v in ventas:
            productos_rel = ProductosHasVentas.objects.filter(ventas_id_venta=v).select_related('producto_id_producto')
            lista_productos = []
            imagen_principal = None
            total_lineas = 0.0
            for pr in productos_rel:
                producto = pr.producto_id_producto
                # Obtener cantidad: usar el valor guardado, o 1 como fallback
                cantidad = int(pr.cantidad) if pr.cantidad and pr.cantidad > 0 else 1
                precio_unitario = float(producto.precio) if producto.precio else 0.0
                total_linea = precio_unitario * cantidad
                total_lineas += total_linea
                
                if not imagen_principal and producto.imagen:
                    imagen_principal = producto.imagen
                lista_productos.append({
                    'nombre': producto.nombre,
                    'precio_unitario': precio_unitario,
                    'cantidad': cantidad,
                    'total_linea': total_linea,
                    'imagen': producto.imagen if producto.imagen else None,
                })
            ventas_formateadas.append({
                'order_number': f"ART-000{v.id_venta}",
                'estado': v.estado,
                'fecha_venta': v.fecha_venta,
                'direccion_envio': v.direccion_envio if hasattr(v, "direccion_envio") else "No registrado",
                'main_image': imagen_principal,
                'productos': lista_productos,
                'total_venta': total_lineas,
            })

    contexto = {
        'user_logged': True,
        'ventas': ventas_formateadas,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    return render(request, 'cliente/historial.html', contexto)


# CONFIGURACIONES
@requires_admin
def admin_settings(request):
    """Mostrar página de configuraciones para administrador."""
    # La autenticación ya está validada por el decorator @requires_admin
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()

    context = {
        'user_logged': True,
        'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
    }

    return render(request, 'admin/settings.html', context)

@requires_seller
def seller_settings(request):
    return render(request, 'seller/settings.html')


@requires_cliente
def cliente_settings(request):
    # Mostrar página de configuraciones para clientes
    # La autenticación ya está validada por el decorator @requires_cliente
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()
    user_name = None
    if persona:
        user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()

    context = {
        'user_logged': True,
        'user_name': user_name,
    }

    return render(request, 'cliente/settings.html', context)


@requires_cliente
def cliente_perfil(request):
    # Mostrar perfil del cliente (diseño solo de interfaz)
    # La autenticación ya está validada por el decorator @requires_cliente
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()
    user_name = None
    if persona:
        user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()

    context = {
        'user_logged': True,
        'user_name': user_name,
        'persona': persona,
    }

    return render(request, 'cliente/perfil.html', context)


@requires_cliente
def editar_perfil(request):
    # Permitir al cliente editar sus datos y cambiar contraseña
    # La autenticación ya está validada por el decorator @requires_cliente
    user_id = request.session.get('user_id')

    persona = Personas.objects.filter(id_personas=user_id).first()
    if not persona:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    errors = {}

    # Solo el propietario puede modificar sus datos
    if request.method == 'GET':
        return render(request, 'cliente/editar_perfil.html', {
            'persona': persona,
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
            'errors': errors,
        })

    # POST: procesar actualización de datos o cambio de contraseña
    if request.method == 'POST':
        # Determinar qué acción se solicitó desde el formulario
        action = request.POST.get('action')

        # Campos de perfil
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')

        # Campos de contraseña
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Si la acción es actualizar solo info
        if action == 'update_info' or not action:
            # Validar que el correo no esté en uso por otro usuario
            if correo and Personas.objects.filter(correo_persona=correo).exclude(id_personas=persona.id_personas).exists():
                errors['correo'] = "El correo ya está en uso por otro usuario."
                return render(request, 'cliente/editar_perfil.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            # Actualizar solo datos personales (no tocar contraseña)
            persona.nombre_persona = nombre or persona.nombre_persona
            persona.apellido_persona = apellido or persona.apellido_persona
            persona.correo_persona = correo or persona.correo_persona
            persona.telefono = telefono or persona.telefono
            persona.direccion = direccion or persona.direccion

            try:
                persona.save()
                # Asegurar relación en tabla Clientes si el rol es cliente
                try:
                    if persona.rol and persona.rol.lower() == 'cliente':
                        Clientes.objects.get_or_create(personas_id_personas=persona)
                except Exception:
                    pass

                messages.success(request, "✅ Perfil actualizado correctamente.", extra_tags='profile_update')
                return redirect('editar_perfil')
            except Exception as e:
                errors['general'] = f"Error al guardar los cambios: {str(e)}"
                return render(request, 'cliente/editar_perfil.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

        # Si la acción es actualizar solo contraseña
        if action == 'update_password':
            # Validar campos de contraseña
            if not current_password:
                errors['current_password'] = "Debes ingresar tu contraseña actual para cambiar la contraseña."
                return render(request, 'cliente/editar_perfil.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            # Verificar contraseña actual: aceptar hash o texto plano y re-hashear si es necesario
            current_ok = False
            try:
                if persona.password and check_password(current_password, persona.password):
                    current_ok = True
                else:
                    if persona.password and persona.password == current_password:
                        # Re-hashear la contraseña almacenada en texto plano
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
                return render(request, 'cliente/editar_perfil.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            if not new_password or not confirm_password:
                errors['new_password'] = "Ingresa la nueva contraseña y confirmación."
                return render(request, 'cliente/editar_perfil.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            if new_password != confirm_password:
                errors['confirm_password'] = "La nueva contraseña y la confirmación no coinciden."
                return render(request, 'cliente/editar_perfil.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            # Validar fuerza de contraseña
            from core.views.auth_views import validate_password
            valid_pass, pass_msg = validate_password(new_password)
            if not valid_pass:
                errors['new_password'] = pass_msg
                return render(request, 'cliente/editar_perfil.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            # Guardar nueva contraseña (hash)
            persona.password = make_password(new_password)
            try:
                persona.save()
            except Exception as e:
                errors['general'] = f"Error al guardar la nueva contraseña: {str(e)}"
                return render(request, 'cliente/editar_perfil.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            # Después de cambiar la contraseña, pedimos re-login por seguridad
            request.session.flush()
            messages.success(request, "Contraseña actualizada. Por favor, inicia sesión nuevamente.")
            return redirect('login')

        # Si la acción es otra (por seguridad), redirigir
        messages.error(request, "Acción desconocida.")
        return redirect('editar_perfil')

# Vistas para seller perfil y edición de perfil


@requires_seller
def seller_perfil(request):
    # La autenticación ya está validada por el decorator @requires_seller
    # Mostrar perfil del vendedor
    user_id = request.session.get('user_id')

    persona = Personas.objects.filter(id_personas=user_id).first()
    if not persona:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    user_name = f"{persona.nombre_persona} {persona.apellido_persona}".strip()

    context = {
        'user_logged': True,
        'user_name': user_name,
        'persona': persona,
    }

    return render(request, 'seller/perfil_seller.html', context)

@requires_seller
def editar_perfil_seller(request):
    # La autenticación ya está validada por el decorator @requires_seller
    # Permitir al vendedor editar sus datos y cambiar contraseña
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()
    if not persona:
        messages.error(request, "Usuario no encontrado.")
        return redirect('login')

    errors = {}

    # GET → Mostrar formulario
    if request.method == 'GET':
        return render(request, 'seller/editar_perfil_seller.html', {
            'persona': persona,
            'user_logged': True,
            'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
            'errors': errors,
        })

    # POST → Procesar formulario
    if request.method == 'POST':
        action = request.POST.get('action')

        # Campos del perfil
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')

        # Campos de contraseña
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # --- ACTUALIZAR SOLO DATOS ---
        if action == 'update_info' or not action:

            # Validar correo único
            if correo and Personas.objects.filter(correo_persona=correo).exclude(id_personas=persona.id_personas).exists():
                errors['correo'] = "El correo ya está en uso por otro usuario."
                return render(request, 'seller/editar_perfil_seller.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            # Actualizar datos
            persona.nombre_persona = nombre or persona.nombre_persona
            persona.apellido_persona = apellido or persona.apellido_persona
            persona.correo_persona = correo or persona.correo_persona
            persona.telefono = telefono or persona.telefono
            persona.direccion = direccion or persona.direccion

            try:
                persona.save()

                # Registrar relación en tabla Vendedores si aplica
                try:
                    if persona.rol and persona.rol.lower() == 'vendedor':
                        Vendedores.objects.get_or_create(personas_id_personas=persona)
                except Exception:
                    pass

                messages.success(request, "✅ Perfil actualizado correctamente.", extra_tags='profile_update')
                return redirect('editar_perfil_seller')

            except Exception as e:
                errors['general'] = f"Error al guardar los cambios: {str(e)}"
                return render(request, 'seller/editar_perfil_seller.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

        # --- ACTUALIZAR CONTRASEÑA ---
        if action == 'update_password':

            # Validar contraseña actual
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
                    # Si estaba guardada en texto plano → la re-hashea
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

            # Validar nueva contraseña
            if not new_password or not confirm_password:
                errors['new_password'] = "Ingresa la nueva contraseña y su confirmación."
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

            # Validar fuerza de contraseña
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

            # Guardar nueva contraseña
            persona.password = make_password(new_password)
            try:
                persona.save()
            except Exception as e:
                errors['general'] = f"Error al cambiar la contraseña: {str(e)}"
                return render(request, 'seller/editar_perfil_seller.html', {
                    'persona': persona,
                    'user_logged': True,
                    'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
                    'errors': errors,
                })

            # Cerrar sesión por seguridad
            request.session.flush()
            messages.success(request, "Contraseña actualizada. Inicia sesión nuevamente.")
            return redirect('login')

        # Acciones inválidas
        messages.error(request, "Acción desconocida.")
        return redirect('editar_perfil_seller')


# ======================================================
#  PERFIL DEL ADMINISTRADOR
# ======================================================
@requires_admin
def admin_perfil(request):
    """Muestra el perfil del administrador con sus datos personales."""
    # La autenticación ya está validada por el decorator @requires_admin
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()

    # Verificar rol
    if not persona.rol or persona.rol.lower() not in ['administrador', 'admin']:
        messages.error(request, "No tienes permisos para ver este perfil.")
        return redirect('inicio')

    context = {
        'user_logged': True,
        'user_name': f"{persona.nombre_persona} {persona.apellido_persona}".strip(),
        'persona': persona,
    }

    return render(request, 'admin/perfil_admin.html', context)


@requires_admin
def editar_perfil_admin(request):
    """Permite al administrador editar sus datos y cambiar contraseña."""
    # La autenticación ya está validada por el decorator @requires_admin
    user_id = request.session.get('user_id')
    persona = Personas.objects.filter(id_personas=user_id).first()

    errors = {}

    if request.method == 'GET':
        return render(request, 'admin/editar_perfil_admin.html', {
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
            return render(request, 'admin/editar_perfil_admin.html', {
                'persona': persona,
                'user_logged': True,
                'errors': errors,
            })

        persona.nombre_persona = nombre or persona.nombre_persona
        persona.apellido_persona = apellido or persona.apellido_persona
        persona.correo_persona = correo or persona.correo_persona
        persona.telefono = telefono or persona.telefono
        persona.direccion = direccion or persona.direccion

        try:
            persona.save()
            messages.success(request, "✅ Perfil actualizado correctamente.", extra_tags='profile_update')
            return redirect('editar_perfil_admin')
        except Exception as e:
            errors['general'] = f"Error al guardar los cambios: {str(e)}"
            return render(request, 'admin/editar_perfil_admin.html', {
                'persona': persona,
                'user_logged': True,
                'errors': errors,
            })

    if action == 'update_password':
        if not current_password:
            errors['current_password'] = "Debes ingresar tu contraseña actual para cambiar la contraseña."
            return render(request, 'admin/editar_perfil_admin.html', {
                'persona': persona,
                'user_logged': True,
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
            return render(request, 'admin/editar_perfil_admin.html', {
                'persona': persona,
                'user_logged': True,
                'errors': errors,
            })

        if not new_password or not confirm_password:
            errors['new_password'] = "Ingresa la nueva contraseña y confirmación."
            return render(request, 'admin/editar_perfil_admin.html', {
                'persona': persona,
                'user_logged': True,
                'errors': errors,
            })

        if new_password != confirm_password:
            errors['confirm_password'] = "La nueva contraseña y la confirmación no coinciden."
            return render(request, 'admin/editar_perfil_admin.html', {
                'persona': persona,
                'user_logged': True,
                'errors': errors,
            })

        from core.views.auth_views import validate_password
        valid_pass, pass_msg = validate_password(new_password)
        if not valid_pass:
            errors['new_password'] = pass_msg
            return render(request, 'admin/editar_perfil_admin.html', {
                'persona': persona,
                'user_logged': True,
                'errors': errors,
            })

        persona.password = make_password(new_password)
        try:
            persona.save()
        except Exception as e:
            errors['general'] = f"Error al guardar la nueva contraseña: {str(e)}"
            return render(request, 'admin/editar_perfil_admin.html', {
                'persona': persona,
                'user_logged': True,
                'errors': errors,
            })

        request.session.flush()
        messages.success(request, "Contraseña actualizada. Por favor, inicia sesión nuevamente.")
        return redirect('login')
