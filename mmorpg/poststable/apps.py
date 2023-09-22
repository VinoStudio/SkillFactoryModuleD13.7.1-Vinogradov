from django.apps import AppConfig


class PoststableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poststable'

    def ready(self):
        import poststable.signals
