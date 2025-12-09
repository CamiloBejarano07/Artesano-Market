from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Se ejecuta cuando la app 'core' está lista.
        En Django 5, es el lugar idóneo para inicializar lógica de arranque.
        El middleware ClearSessionsOnStartupMiddleware se encargará de limpiar sesiones.
        """
        logger.info("[INIT] App 'core' inicializada correctamente")
