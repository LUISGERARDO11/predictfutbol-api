from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Establecer el módulo de configuración de Django para el entorno 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Usar una cadena aquí significa que el trabajador no tendrá que serializar
# la configuración del objeto al ejecutarse.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubrir y cargar automáticamente las tareas de todos los módulos de aplicaciones registradas
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
