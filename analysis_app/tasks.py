import logging
from django_q.tasks import schedule, Schedule
from .utils import fetch_teams_data, get_teams_next_season, get_scheduled_matches

logger = logging.getLogger(__name__)

def schedule_fetch_teams_data():
    logger.info('Programando la tarea fetch_teams_data para cada minuto.')
    schedule(
        'analysis_app.utils.fetch_teams_data',
        schedule_type=Schedule.MINUTES,
        minutes=1,  # Esto configura la tarea para ejecutarse cada minuto
        repeats=-1  # Repetir indefinidamente
    )

def schedule_get_teams_next_season():
    logger.info('Programando la tarea get_teams_next_season para cada minuto.')
    schedule(
        'analysis_app.utils.get_teams_next_season',
        schedule_type=Schedule.MINUTES,
        minutes=1,  # Esto configura la tarea para ejecutarse cada minuto
        repeats=-1  # Repetir indefinidamente
    )

def schedule_get_scheduled_matches():
    logger.info('Programando la tarea get_scheduled_matches para cada minuto.')
    schedule(
        'analysis_app.utils.get_scheduled_matches',
        schedule_type=Schedule.MINUTES,
        minutes=1,  # Esto configura la tarea para ejecutarse cada minuto
        repeats=-1  # Repetir indefinidamente
    )
