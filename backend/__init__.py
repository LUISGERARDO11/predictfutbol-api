# backend/__init__.py
from __future__ import absolute_import, unicode_literals

# Esto asegurará que se ejecute celery.py
from .celery import app as celery_app

__all__ = ('celery_app',)
