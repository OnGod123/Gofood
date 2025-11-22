import jwt
from flask import request, current_app
from jwt import ExpiredSignatureError, InvalidTokenError

def get_user_from_jwt():
    """Extract user_id, username, and email from JWT token in headers."""
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise PermissionError("Missing or invalid Authorization header")

    # Remove 'Bearer ' prefix
    token = token.split("Bearer ")[1]

    try:
        # Use the Flask app secret key from config
        secret_key = current_app.config.get("SECRET_KEY")
        if not secret_key:
            raise RuntimeError("SECRET_KEY is not set in Flask config")

        # Decode JWT payload
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        return {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email")
        }

    except ExpiredSignatureError:
        raise PermissionError("Token expired")
    except InvalidTokenError:
        raise PermissionError("Invalid token")


