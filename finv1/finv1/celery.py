from __future__ import absolute_import, unicode_literals

import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finv1.settings')

app = Celery("finv1")

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'every-day': {
        'task': 'main.tasks.send',
        'schedule': 86400.0,
    }
}

app.autodiscover_tasks()