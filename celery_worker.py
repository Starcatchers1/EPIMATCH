#!/usr/bin/env python
import os

from app.utils.celery_util import init_celery
from config import DevConfig, ProdConfig
from app.factory import create_app
from app import celery

environment = os.getenv('FLASK_CONFIG') or 'development'
CONFIG = ProdConfig if environment == 'production' else DevConfig


flask_app = create_app(CONFIG)
init_celery(flask_app, celery)
