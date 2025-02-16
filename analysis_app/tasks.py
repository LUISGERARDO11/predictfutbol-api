# analysis_app/tasks.py

from django_q.tasks import schedule, Schedule
import logging
from .utils import fetch_teams_data, get_teams_next_season  # Asegúrate de que la importación sea correcta

logger = logging.getLogger(__name__)

def schedule_fetch_teams_data():
    logger.info('Programando la tarea fetch_teams_data para cada hora.')
    schedule(
        'analysis_app.utils.fetch_teams_data',  # Ruta completa del módulo y la función
        schedule_type=Schedule.HOURLY,  # Ejecutar cada hora
        repeats=-1  # Repetir indefinidamente
    )

def schedule_fetch_teams_next_season():
    logger.info('Programando la tarea get_teams_next_season para cada minuto.')
    schedule(
        'analysis_app.utils.get_teams_next_season',
        schedule_type=Schedule.HOURLY,  # Ejecutar cada hora
        repeats=-1  # Repetir indefinidamente
    )