from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from core.models import Clientes

# ✅ Listar todos los clientes
def listar_clientes(request):
    clientes = list(Clientes.objects.all().values())
    return JsonResponse(clientes, safe=False)


# ✅ Obtener cliente por ID
def obtener_cliente(request, id):
    cliente = get_object_or_404(Clientes, pk=id)
    data = {
        'id_cliente': cliente.id_cliente,
        'nombre': cliente.nombre,
        'apellido': cliente.apellido,
        'correo': cliente.correo,
        'telefono': cliente.telefono,
    }
    return JsonResponse(data)


# ✅ Eliminar cliente
@csrf_exempt
def eliminar_cliente(request, id):
    if request.method == 'DELETE':
        cliente = get_object_or_404(Clientes, pk=id)
        cliente.delete()
        return JsonResponse({'message': 'Cliente eliminado correctamente'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)
