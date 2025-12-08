from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
import json

from core.models import Personas, Clientes



@method_decorator(csrf_exempt, name='dispatch')
class PersonasView(View):

    # Obtener todas las personas o aplicar filtro
    def get(self, request, id=None):
        criterio = request.GET.get("criterio")
        valor = request.GET.get("valor")

        if id:
            persona = get_object_or_404(Personas, pk=id)
            data = {
                "id": persona.id,
                "nombre": persona.nombre_persona,
                "apellido": persona.apellido_persona,
                "correo": persona.correo_persona,
                "telefono": persona.telefono,
                "direccion": persona.direccion,
                "rol": persona.rol,
            }
            return JsonResponse(data)

        if criterio and valor:
            filtro = {
                "nombre": "nombre_persona__icontains",
                "apellido": "apellido_persona__icontains",
                "correo": "correo_persona__icontains",
                "telefono": "telefono__icontains"
            }.get(criterio.lower())

            if filtro:
                personas = Personas.objects.filter(**{filtro: valor})
            else:
                personas = Personas.objects.all()
        else:
            personas = Personas.objects.all()

        data = list(personas.values(
            "id", "nombre_persona", "apellido_persona", "correo_persona",
            "telefono", "direccion", "rol"
        ))
        return JsonResponse(data, safe=False)

    # Registrar nueva persona
    def post(self, request):
        try:
            data = json.loads(request.body)

            correo = data.get("correo_persona")
            if Personas.objects.filter(correo_persona=correo).exists():
                return JsonResponse({"error": "El correo ya está registrado."}, status=400)

            persona = Personas(
                nombre_persona=data.get("nombre_persona"),
                apellido_persona=data.get("apellido_persona"),
                correo_persona=correo,
                telefono=data.get("telefono"),
                direccion=data.get("direccion"),
                rol=data.get("rol"),
                password=make_password(data.get("password"))
            )
            persona.save()

            # Crear cliente si el rol es Cliente
            if persona.rol.lower() == "cliente":
                Clientes.objects.create(id=persona.id)

            return JsonResponse({"mensaje": f"Registro exitoso para {correo}"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # Actualizar persona existente
    def put(self, request, id):
        try:
            persona = get_object_or_404(Personas, pk=id)
            data = json.loads(request.body)

            persona.nombre_persona = data.get("nombre_persona", persona.nombre_persona)
            persona.apellido_persona = data.get("apellido_persona", persona.apellido_persona)
            persona.correo_persona = data.get("correo_persona", persona.correo_persona)
            persona.telefono = data.get("telefono", persona.telefono)
            persona.direccion = data.get("direccion", persona.direccion)
            persona.rol = data.get("rol", persona.rol)
            persona.save()

            return JsonResponse({"mensaje": "Persona actualizada correctamente."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # Eliminar persona
    def delete(self, request, id):
        persona = Personas.objects.filter(pk=id).first()
        if not persona:
            return JsonResponse({"error": "Persona no encontrada."}, status=404)

        persona.delete()
        Clientes.objects.filter(id=id).delete()  # elimina cliente si existe

        return JsonResponse({"mensaje": "Persona eliminada correctamente."})
