# predicciones_futbol/__init__.py
from __future__ import absolute_import, unicode_literals

# Esto asegurará que se carguen las tareas de Celery
from .celery import app as celery_app

__all__ = ('celery_app',)
