# predicciones_futbol/celerybeat_schedule.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'actualizar-equipos-cada-24-horas': {
        'task': 'analysis_app.tasks.actualizar_equipos',
        'schedule': crontab(minute='*/1'),  # Ejecutar cada minuto
    },
}