from django.apps import AppConfig


class InsightsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.insights"

    def ready(self):
        """
        Ensures that signal handlers are imported and registered when the app is ready.
        """
        import apps.insights.signals
