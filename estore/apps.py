from django.apps import AppConfig


class EstoreConfig(AppConfig):
    name = 'estore'
    
    def ready(self):
        from . import signals