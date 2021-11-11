from django.apps import AppConfig


class SharespaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sharespace'

    def ready(self):
        import sharespace.signals
