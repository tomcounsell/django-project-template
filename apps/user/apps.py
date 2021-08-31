from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = 'apps.user'
    label = 'user'
    verbose_name = 'Users & Authentication'
    default_auto_field = 'django.db.models.BigAutoField'
