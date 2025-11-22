
import jwt
from flask import current_app
from datetime import datetime, timedelta

def encode_token(payload, expires_in=3600):
    """
    Encode a JWT token with only the provided payload.
    Default expiration is 1 hour.
    """
    secret_key = current_app.config.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY is not set in Flask config")

    payload_copy = payload.copy()
    payload_copy["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)

    token = jwt.encode(payload_copy, secret_key, algorithm="HS256")
    return token


def encode_order_id(order_id, expires_in=3600):
    """
    Encode a JWT token containing only the order ID.
    Returns a JWT string.
    """
    if not order_id:
        raise ValueError("order_id is required")

    payload = {"order_id": order_id}
    return encode_token(payload, expires_in=expires_in)

