web: gunicorn backend.wsgi
worker: celery -A backend worker --loglevel=info
beat: celery -A backend beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
