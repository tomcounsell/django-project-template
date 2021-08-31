from django.apps import AppConfig


class CommonConfig(AppConfig):
    name = 'apps.communication'
    label = 'communication'
    default_auto_field = 'django.db.models.BigAutoField'
