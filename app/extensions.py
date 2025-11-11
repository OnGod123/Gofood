import os
import json
import logging
import hmac
import hashlib
import urllib.parse
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from functools import wraps
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
import redis
from sqlalchemy.orm import declarative_base
from celery import Celery
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

socketio = SocketIO()
migrate = Migrate()
oauth = OAuth()
r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
Base = declarative_base()
limiter = Limiter(key_func=get_remote_address)


def make_celery(app):
    """Create and configure a Celery instance tied to the Flask app."""
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
    )

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Ensure Celery tasks run within the Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def init_db(app):
    """Initialize SQLAlchemy engine and scoped session for Base models."""
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
    Base.metadata.bind = engine
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)
