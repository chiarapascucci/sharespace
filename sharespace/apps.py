from django.apps import AppConfig

# basic sharespace configuration
class SharespaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sharespace'

    def ready(self):
        import sharespace.signals
