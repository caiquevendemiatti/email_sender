import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_sender.settings')

app = Celery('email_sender')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
