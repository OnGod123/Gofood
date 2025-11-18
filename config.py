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

     # MinIO
    MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioaccesskey")
    MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "miniosecretkey")
    MINIO_SECURE = bool(int(os.environ.get("MINIO_SECURE", 0)))

    OAUTH_GOOGLE_CLIENT_ID = os.environ.get("OAUTH_GOOGLE_CLIENT_ID")
    OAUTH_GOOGLE_CLIENT_SECRET = os.environ.get("OAUTH_GOOGLE_CLIENT_SECRET")
    OAUTH_FACEBOOK_CLIENT_ID = os.environ.get("OAUTH_FACEBOOK_CLIENT_ID")
    OAUTH_FACEBOOK_CLIENT_SECRET = os.environ.get("OAUTH_FACEBOOK_CLIENT_SECRET")


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
    WHATSAPP_SECRET = "..."
    FLUTTERWAVE_SECRET = "..."
    PAYSTACK_SECRET = "..."
    API_TOKEN = "..."
    DEFAULT_API_VERSION = "v17.0"


    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Environment
    APP_ENV = os.environ.get("APP_ENV", "development")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

    MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioaccesskey")
    MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "miniosecretkey")
    MINIO_SECURE = bool(int(os.environ.get("MINIO_SECURE", "0")))

