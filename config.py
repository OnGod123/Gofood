import os

class Config:
    # Basic App Settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
    TESTING = os.environ.get("TESTING", "False").lower() == "true"

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///gofood.db")

    # Redis / SocketIO
    SOCKETIO_MESSAGE_QUEUE = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # File Uploads
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

    # JWT
    JWT_SECRET = os.environ.get("JWT_SECRET", "change_me")

    # Central Account Configuration
    CENTRAL_ACCOUNT_NUMBER = os.environ.get("CENTRAL_ACCOUNT_NUMBER", "")
    CENTRAL_ACCOUNT_BANK = os.environ.get("CENTRAL_ACCOUNT_BANK", "Moniepoint")

    # Moniepoint API
    MONIEPOINT_PAYOUT_URL = os.environ.get("MONIEPOINT_PAYOUT_URL", "")
    MONIEPOINT_SECRET = os.environ.get("MONIEPOINT_SECRET", "")

    # Celery
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # Session Expiration
    SESSION_EXPIRE = int(os.environ.get("SESSION_EXPIRE", "900"))

    # Payment
    PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "")
    DEFAULT_PAYMENT_PROVIDER = os.environ.get("DEFAULT_PAYMENT_PROVIDER", "paystack")

    # WhatsApp API Configuration
    WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
    META_PHONE_NUMBER_ID = os.environ.get("META_PHONE_NUMBER_ID", "")
    WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "verify-token")
    WHATSAPP_APP_SECRET = os.environ.get("WHATSAPP_APP_SECRET", "")
    WHATSAPP_API_VERSION = os.environ.get("WHATSAPP_API_VERSION", "v20.0")

    # Frontend URLs
    FRONTEND_FUND_URL = os.environ.get("FRONTEND_FUND_URL", "")
    BASE_URL = os.environ.get("BASE_URL", "")

    # Rate Limiting
    RATE_LIMIT = os.environ.get("RATE_LIMIT", "300/hour")




