# Fichier : dashboard/apps.py
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'

    def ready(self):
        # Importe les signaux pour s'assurer que l'initialisation de la DB est exécutée
        import dashboard.models