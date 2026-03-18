import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Celery is a task scheduling framework
app = Celery("lost_and_found")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()