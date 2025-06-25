from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        """
        Import signals when the app is ready.
        This ensures that signals are connected when Django starts.
        """
        import apps.core.signals
