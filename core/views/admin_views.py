from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from core.models import Vendedores
from core.services.email_service import EmailService
from core.models import Personas, Vendedores, Productos, Ventas, AuthUser
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from core.decorators import requires_admin
import datetime
import json
from django.utils.safestring import mark_safe




@requires_admin
def mostrar_formulario_correos(request):
    correos = []
    vendedores = Vendedores.objects.select_related('personas_id_personas').all()

    for v in vendedores:
        persona = getattr(v, 'personas_id_personas', None)
        if persona and getattr(persona, 'correo_persona', None):
            correos.append(persona.correo_persona)

    return render(request, 'admin/correos.html', {'correos': correos})



@requires_admin
def enviar_correos_masivos(request):
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        destinatarios = request.POST.getlist('destinatarios')
        archivo = request.FILES.get('archivo')

        try:
            # Si no se seleccionaron destinatarios, enviar a todos
            if not destinatarios:
                vendedores = Vendedores.objects.select_related('personas_id_personas').all()
                destinatarios = [
                    v.personas_id_personas.correo_persona
                    for v in vendedores
                    if v.personas_id_personas and v.personas_id_personas.correo_persona
                ]

            if not destinatarios:
                messages.error(request, 'No hay correos válidos de vendedores para enviar.')
                return redirect('mostrar_formulario_correos')

            servicio = EmailService()
            servicio.enviar_correo_masivo_con_adjunto(
                destinatarios,
                asunto,
                mensaje,
                archivo
            )

            messages.success(
                request,
                f'Correos enviados correctamente a {len(destinatarios)} destinatarios.'
            )

        except Exception as e:
            print("Error al enviar:", e)
            messages.error(request, f'Error al enviar correos: {str(e)}')

        return redirect('mostrar_formulario_correos')

    return HttpResponse("Método no permitido", status=405)



# Vista para el dashboard del administrador
@requires_admin
def estadisticas_admin(request):
    from django.utils.timezone import now
    from datetime import timedelta, datetime
    from django.db.models import Sum, Count
    import json
    
    # Obtener estadísticas generales
    total_products = Productos.objects.count()
    total_users = Personas.objects.filter(rol='cliente').count()
    total_sellers = Vendedores.objects.count()
    
    # Ventas del día de hoy - contar el número total de transacciones (no el dinero)
    # Usar timezone.now() para obtener la fecha actual en la zona horaria configurada
    today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    sales_today_count = Ventas.objects.filter(
        fecha_venta__gte=today_start,
        fecha_venta__lt=today_end
    ).count()
    
    # Total acumulado de ventas desde que se inició la aplicación (número total de transacciones)
    total_sales_all_time = Ventas.objects.count()
    
    # Obtener ventas acumuladas por fecha (para gráfica de crecimiento)
    from django.db.models.functions import TruncDate
    sales_by_date = Ventas.objects.annotate(
        date=TruncDate('fecha_venta')
    ).values('date').annotate(
        count=Count('id_venta')
    ).order_by('date')
    
    # Construir datos acumulados de ventas
    accumulated_sales = {}
    running_total = 0
    for sale in sales_by_date:
        if sale['date']:
            date_str = sale['date'].isoformat()
            running_total += sale['count']
            accumulated_sales[date_str] = running_total
    
    # Construir datos por mes para filtrado
    months_data = {}
    for sale in sales_by_date:
        if sale['date']:
            month_key = sale['date'].strftime('%Y-%m')
            if month_key not in months_data:
                months_data[month_key] = {}
            day = sale['date'].day
            months_data[month_key][day] = sale['count']
    
    # Obtener productos por vendedor
    products_by_seller = Vendedores.objects.annotate(
        product_count=Count('productos')
    ).values('personas_id_personas__nombre_persona', 'product_count').order_by('-product_count')
    
    # Preparar datos para la gráfica de productos por vendedor
    seller_names = []
    product_counts = []
    for seller in products_by_seller:
        seller_names.append(seller['personas_id_personas__nombre_persona'] or 'Sin nombre')
        product_counts.append(seller['product_count'])
    
    # Convertir a JSON para pasar a la plantilla
    accumulated_sales_json = json.dumps(accumulated_sales)
    months_data_json = json.dumps(months_data)
    sellers_data_json = json.dumps({
        'names': seller_names,
        'counts': product_counts
    })
    
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'total_sellers': total_sellers,
        'sales_today': sales_today_count,
        'total_sales_all_time': total_sales_all_time,
        'accumulated_sales': accumulated_sales_json,
        'months_data': months_data_json,
        'sellers_data': sellers_data_json
    }
    
    return render(request, 'admin/estadisticas.html', context)
