# analysis_app/apps.py

from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)

class AnalysisAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analysis_app'

    def ready(self):
        post_migrate.connect(self.schedule_task, sender=self)

    def schedule_task(self, **kwargs):
        from django_q.models import Schedule
        from .tasks import schedule_fetch_teams_data
        if not Schedule.objects.filter(func='analysis_app.utils.fetch_teams_data').exists():
            schedule_fetch_teams_data()
