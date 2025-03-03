from django.apps import AppConfig

class ColegioappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "colegioapp"

    def ready(self):
        import colegioapp.signals  # Cargar los signals al iniciar la app
