
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
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


socketio = SocketIO()
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()
r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
Base = declarative_base()
limiter = Limiter(key_func=get_remote_address)

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"]
    )
    celery.conf.update(app.config)

    # Make celery tasks work with Flask context
class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery
