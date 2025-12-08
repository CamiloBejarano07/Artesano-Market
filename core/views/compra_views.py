from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from core.models import Compra
import csv
import json
from datetime import date


# ✅ Listar todas las compras con filtros opcionales
def listar_compras(request):
    estado = request.GET.get('estado')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    compras = Compra.objects.all()

    if estado:
        compras = compras.filter(estado_compra__iexact=estado)

    if desde:
        desde_date = parse_date(desde)
        if desde_date:
            compras = compras.filter(fecha_compra__gte=desde_date)

    if hasta:
        hasta_date = parse_date(hasta)
        if hasta_date:
            compras = compras.filter(fecha_compra__lte=hasta_date)

    data = list(compras.values())
    return JsonResponse(data, safe=False)


# ✅ Obtener una compra por ID
def obtener_compra(request, id):
    compra = get_object_or_404(Compra, pk=id)
    data = {
        'id': compra.id,
        'fecha_compra': compra.fecha_compra,
        'sub_total_compra': compra.sub_total_compra,
        'total_compra': compra.total_compra,
        'estado_compra': compra.estado_compra,
        'metodo_pago': compra.metodo_pago,
        'observaciones': compra.observaciones,
        'proveedor': str(compra.proveedor) if compra.proveedor else None,
        'vendedor': str(compra.vendedor) if compra.vendedor else None,
    }
    return JsonResponse(data)


# ✅ Crear nueva compra
@csrf_exempt
def crear_compra(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            compra = Compra.objects.create(
                fecha_compra=parse_date(data.get('fecha_compra', str(date.today()))),
                sub_total_compra=data.get('sub_total_compra'),
                total_compra=data.get('total_compra'),
                estado_compra=data.get('estado_compra'),
                metodo_pago=data.get('metodo_pago'),
                observaciones=data.get('observaciones'),
                proveedor_id=data.get('proveedor'),
                vendedor_id=data.get('vendedor'),
            )
            return JsonResponse({'message': 'Compra creada exitosamente', 'id': compra.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ✅ Actualizar una compra existente
@csrf_exempt
def actualizar_compra(request, id):
    compra = get_object_or_404(Compra, pk=id)
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            compra.fecha_compra = parse_date(data.get('fecha_compra', str(compra.fecha_compra)))
            compra.sub_total_compra = data.get('sub_total_compra', compra.sub_total_compra)
            compra.total_compra = data.get('total_compra', compra.total_compra)
            compra.estado_compra = data.get('estado_compra', compra.estado_compra)
            compra.metodo_pago = data.get('metodo_pago', compra.metodo_pago)
            compra.observaciones = data.get('observaciones', compra.observaciones)
            if data.get('proveedor'):
                compra.proveedor_id = data.get('proveedor')
            if data.get('vendedor'):
                compra.vendedor_id = data.get('vendedor')
            compra.save()
            return JsonResponse({'message': 'Compra actualizada correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ✅ Eliminar una compra
@csrf_exempt
def eliminar_compra(request, id):
    if request.method == 'DELETE':
        compra = get_object_or_404(Compra, pk=id)
        compra.delete()
        return JsonResponse({'message': 'Compra eliminada correctamente'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ✅ Exportar compras a CSV (como el Java)
def exportar_compras_csv(request):
    estado = request.GET.get('estado')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    compras = Compra.objects.all()

    if estado:
        compras = compras.filter(estado_compra__iexact=estado)
    if desde:
        desde_date = parse_date(desde)
        if desde_date:
            compras = compras.filter(fecha_compra__gte=desde_date)
    if hasta:
        hasta_date = parse_date(hasta)
        if hasta_date:
            compras = compras.filter(fecha_compra__lte=hasta_date)

    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="compras.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Fecha', 'Subtotal', 'Total', 'Estado', 'Método Pago', 'Proveedor', 'Vendedor'])

    for c in compras:
        writer.writerow([
            c.id,
            c.fecha_compra,
            c.sub_total_compra,
            c.total_compra,
            c.estado_compra,
            c.metodo_pago,
            str(c.proveedor) if c.proveedor else '',
            str(c.vendedor) if c.vendedor else '',
        ])

    return response
