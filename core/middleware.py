"""
Middleware para limpiar sesiones al reiniciar el servidor (Django 5+)
"""
import logging
import os
from django.contrib.sessions.models import Session
from django.utils.decorators import sync_and_async_middleware

logger = logging.getLogger(__name__)

# Variable global para rastrear si ya se limpió en este arranque
_sessions_cleared = False


@sync_and_async_middleware
class ClearSessionsOnStartupMiddleware:
    """
    Middleware que elimina todas las sesiones al primer request después de un reinicio del servidor.
    
    Funciona detectando si el archivo de PID del servidor cambió,
    lo que indica un reinicio.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self._check_and_clear_sessions()
    
    def _check_and_clear_sessions(self):
        """Limpia las sesiones una sola vez por arranque del servidor."""
        global _sessions_cleared
        
        if _sessions_cleared:
            return
        
        try:
            deleted_count, _ = Session.objects.all().delete()
            if deleted_count > 0:
                logger.info(f"[STARTUP] Se eliminaron {deleted_count} sesiones de usuario al reiniciar el servidor")
            else:
                logger.info("[STARTUP] No había sesiones activas. Base de datos limpia.")
            _sessions_cleared = True
        except Exception as e:
            logger.error(f"[STARTUP] Error al limpiar sesiones: {str(e)}")
            _sessions_cleared = True
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
