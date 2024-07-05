from celery import shared_task
from .utils import fetch_teams_data
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def actualizar_equipos(self):
    logger.info('Tarea actualizar_equipos recibida...')
    print("Actualizando equipos...")
    try:
        logger.info('Ejecutando actualizar_equipos...')
        fetch_teams_data()
        logger.info('Datos de equipos actualizados: %s', fetch_teams_data.TEAMS_DATA)
    except Exception as e:
        logger.error(f'Error al ejecutar actualizar_equipos: {e}')
        raise e  # Asegúrate de levantar la excepción para que se registre correctamente

@shared_task
def tarea_de_prueba():
    print("Tarea de prueba ejecutada correctamente")
    return "Tarea de prueba completada"
