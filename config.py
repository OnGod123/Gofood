
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
    DEBUG = True
    TESTING = False
    # Add other config options as needed
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///gofood.db")
    SOCKETIO_MESSAGE_QUEUE = os.environ.get("REDIS_URL", "redis://")
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
    JWT_SECRET = os.environ.get("JWT_SECRET", "change_me")
    CENTRAL_ACCOUNT_NUMBER = os.environ.get("CENTRAL_ACCOUNT_NUMBER", "")
    CENTRAL_ACCOUNT_BANK = os.environ.get("CENTRAL_ACCOUNT_BANK", "Moniepoint")
    MONIEPOINT_PAYOUT_URL = os.environ.get("MONIEPOINT_PAYOUT_URL", "")
    MONIEPOINT_SECRET = os.environ.get("MONIEPOINT_SECRET", "")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    SESSION_EXPIRE = int(os.environ.get("SESSION_EXPIRE", "900"))


