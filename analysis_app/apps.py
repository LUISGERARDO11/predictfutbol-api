from django.apps import AppConfig


class AnalysisAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analysis_app'

    def ready(self):
        from .periodic_tasks import start_periodic_task
        # Intervalo en segundos (por ejemplo, cada hora)
        start_periodic_task(300)
