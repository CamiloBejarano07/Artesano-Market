"""
Decoradores de seguridad y autenticación para proteger vistas
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from core.models import Personas


def requires_login(view_func):
    """
    Decorador que requiere que el usuario esté autenticado (tenga sesión válida).
    Redirige a login si no hay sesión.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        
        # Si no hay user_id en sesión, redirigir a login
        if not user_id:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
        
        # Verificar que el usuario existe en BD
        try:
            persona = Personas.objects.get(id_personas=user_id)
        except Personas.DoesNotExist:
            request.session.flush()
            messages.error(request, "Sesión inválida. Por favor, inicia sesión nuevamente.")
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def requires_admin(view_func):
    """
    Decorador que requiere que el usuario sea administrador.
    Verifica que el rol sea 'admin' (case-insensitive).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        
        # Si no hay sesión, redirigir a login
        if not user_id:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
        
        # Obtener la persona y validar que sea admin
        try:
            persona = Personas.objects.get(id_personas=user_id)
        except Personas.DoesNotExist:
            request.session.flush()
            messages.error(request, "Sesión inválida. Por favor, inicia sesión nuevamente.")
            return redirect('login')
        
        # Validar que sea admin (case-insensitive)
        if not persona.rol or 'admin' not in persona.rol.lower():
            messages.error(request, "No tienes permisos para acceder a esta página. Se requiere ser administrador.")
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def requires_seller(view_func):
    """
    Decorador que requiere que el usuario sea vendedor.
    Verifica que el rol sea 'vendedor' (case-insensitive).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        
        # Si no hay sesión, redirigir a login
        if not user_id:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
        
        # Obtener la persona y validar que sea vendedor
        try:
            persona = Personas.objects.get(id_personas=user_id)
        except Personas.DoesNotExist:
            request.session.flush()
            messages.error(request, "Sesión inválida. Por favor, inicia sesión nuevamente.")
            return redirect('login')
        
        # Validar que sea vendedor (case-insensitive)
        if not persona.rol or 'vendedor' not in persona.rol.lower():
            messages.error(request, "No tienes permisos para acceder a esta página. Se requiere ser vendedor.")
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def requires_cliente(view_func):
    """
    Decorador que requiere que el usuario sea cliente.
    Verifica que el rol sea 'cliente' (case-insensitive).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        
        # Si no hay sesión, redirigir a login
        if not user_id:
            messages.error(request, "Debes iniciar sesión para acceder a esta página.")
            return redirect('login')
        
        # Obtener la persona y validar que sea cliente
        try:
            persona = Personas.objects.get(id_personas=user_id)
        except Personas.DoesNotExist:
            request.session.flush()
            messages.error(request, "Sesión inválida. Por favor, inicia sesión nuevamente.")
            return redirect('login')
        
        # Validar que sea cliente (case-insensitive)
        if not persona.rol or 'cliente' not in persona.rol.lower():
            messages.error(request, "No tienes permisos para acceder a esta página. Se requiere ser cliente.")
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
