from celery import Celery

from config import Config


celery = Celery('app.factory',
                backend=Config.CELERY_BACKEND_URL,
                broker=Config.CELERY_BROKER_URL)
