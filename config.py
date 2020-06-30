import os
from dotenv import load_dotenv

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(APP_ROOT, '.env')

# import .env file, so the variables are set when the class is constructed
load_dotenv(dotenv_path)


class Config(object):
    """Base configuration."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    """Celery"""
    CELERY_BACKEND_URL = os.environ.get('CELERY_BACKEND_URL')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    """Selenium"""
    SELENIUM_MODE = os.environ.get('SELENIUM_MODE')
    SELENIUM_REMOTE_URL = os.environ.get('SELENIUM_REMOTE_URL')
    """Import other env variables here"""
    LINKEDIN_EMAIL = os.environ.get('LINKEDIN_EMAIL')
    LINKEDIN_PASSWORD = os.environ.get('LINKEDIN_PASSWORD')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
