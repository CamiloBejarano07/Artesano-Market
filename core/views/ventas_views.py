from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods
import json, csv

from core.models import Ventas


# ✅ Listar ventas con filtros
@require_http_methods(["GET"])
def listar_ventas(request):
    estado = request.GET.get("estado")
    metodo_pago = request.GET.get("metodoPago")
    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")

    ventas = Ventas.objects.all()

    if estado:
        ventas = ventas.filter(estado__iexact=estado)
    if metodo_pago:
        ventas = ventas.filter(metodoPago__iexact=metodo_pago)
    if desde:
        ventas = ventas.filter(fechaVenta__gte=parse_date(desde))
    if hasta:
        ventas = ventas.filter(fechaVenta__lte=parse_date(hasta))

    data = [
        {
            "id": v.id,
            "fechaVenta": v.fechaVenta,
            "subTotal": v.subTotal,
            "total": v.total,
            "metodoPago": v.metodoPago,
            "estado": v.estado,
            "direccionEnvio": v.direccionEnvio,
            "descuento": v.descuento,
            "comentarios": v.comentarios,
            "fechaEntregaEstimada": v.fechaEntregaEstimada,
            "cliente": v.cliente.persona.nombrePersona if v.cliente and v.cliente.persona else None,
            "vendedor": v.vendedor.persona.nombrePersona if v.vendedor and v.vendedor.persona else None,
        }
        for v in ventas
    ]

    return JsonResponse(data, safe=False)


# ✅ Obtener venta por ID
@require_http_methods(["GET"])
def obtener_venta(request, id):
    venta = get_object_or_404(Ventas, pk=id)
    data = {
        "id": venta.id,
        "fechaVenta": venta.fechaVenta,
        "subTotal": venta.subTotal,
        "total": venta.total,
        "metodoPago": venta.metodoPago,
        "estado": venta.estado,
        "direccionEnvio": venta.direccionEnvio,
        "descuento": venta.descuento,
        "comentarios": venta.comentarios,
        "fechaEntregaEstimada": venta.fechaEntregaEstimada,
        "cliente": venta.cliente.persona.nombrePersona if venta.cliente and venta.cliente.persona else None,
        "vendedor": venta.vendedor.persona.nombrePersona if venta.vendedor and venta.vendedor.persona else None,
    }
    return JsonResponse(data)


# ✅ Crear venta
@csrf_exempt
@require_http_methods(["POST"])
def crear_venta(request):
    data = json.loads(request.body)
    venta = Ventas.objects.create(
        fechaVenta=data.get("fechaVenta"),
        subTotal=data.get("subTotal"),
        total=data.get("total"),
        metodoPago=data.get("metodoPago"),
        estado=data.get("estado"),
        direccionEnvio=data.get("direccionEnvio"),
        descuento=data.get("descuento"),
        comentarios=data.get("comentarios"),
        fechaEntregaEstimada=data.get("fechaEntregaEstimada"),
        cliente_id=data.get("cliente"),  # se pasa el ID del cliente
        vendedor_id=data.get("vendedor"),  # se pasa el ID del vendedor
    )
    return JsonResponse({"message": "Venta creada correctamente", "id": venta.id})


# ✅ Actualizar venta
@csrf_exempt
@require_http_methods(["PUT"])
def actualizar_venta(request, id):
    venta = get_object_or_404(Ventas, pk=id)
    data = json.loads(request.body)

    venta.fechaVenta = data.get("fechaVenta", venta.fechaVenta)
    venta.subTotal = data.get("subTotal", venta.subTotal)
    venta.total = data.get("total", venta.total)
    venta.metodoPago = data.get("metodoPago", venta.metodoPago)
    venta.estado = data.get("estado", venta.estado)
    venta.direccionEnvio = data.get("direccionEnvio", venta.direccionEnvio)
    venta.descuento = data.get("descuento", venta.descuento)
    venta.comentarios = data.get("comentarios", venta.comentarios)
    venta.fechaEntregaEstimada = data.get("fechaEntregaEstimada", venta.fechaEntregaEstimada)
    if data.get("cliente"):
        venta.cliente_id = data["cliente"]
    if data.get("vendedor"):
        venta.vendedor_id = data["vendedor"]

    venta.save()
    return JsonResponse({"message": "Venta actualizada correctamente"})


# ✅ Eliminar venta
@csrf_exempt
@require_http_methods(["DELETE"])
def eliminar_venta(request, id):
    venta = Ventas.objects.filter(pk=id).first()
    if not venta:
        return JsonResponse({"error": "Venta no encontrada"}, status=404)

    venta.delete()
    return JsonResponse({"message": "Venta eliminada correctamente"})


# ✅ Exportar CSV
@require_http_methods(["GET"])
def exportar_csv_ventas(request):
    estado = request.GET.get("estado")
    metodo_pago = request.GET.get("metodoPago")
    desde = request.GET.get("desde")
    hasta = request.GET.get("hasta")

    ventas = Ventas.objects.all()
    if estado:
        ventas = ventas.filter(estado__iexact=estado)
    if metodo_pago:
        ventas = ventas.filter(metodoPago__iexact=metodo_pago)
    if desde:
        ventas = ventas.filter(fechaVenta__gte=parse_date(desde))
    if hasta:
        ventas = ventas.filter(fechaVenta__lte=parse_date(hasta))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="ventas.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Fecha", "Total", "Estado", "MetodoPago", "Cliente", "Vendedor"])

    for v in ventas:
        cliente = v.cliente.persona.nombrePersona if v.cliente and v.cliente.persona else ""
        vendedor = v.vendedor.persona.nombrePersona if v.vendedor and v.vendedor.persona else ""
        writer.writerow([
            v.id,
            v.fechaVenta,
            v.total,
            v.estado,
            v.metodoPago,
            cliente,
            vendedor,
        ])

    return response
