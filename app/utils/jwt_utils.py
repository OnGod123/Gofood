import jwt
from flask import request
from jwt import ExpiredSignatureError, InvalidTokenError

SECRET_KEY = "your_app_secret_here"

def get_user_from_jwt():
    """Extract user_id and email from JWT token in headers."""
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise PermissionError("Missing or invalid Authorization header")

    token = token.split("Bearer ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {
            "user_id": payload.get("user_id"),
            "email": payload.get("email")
        }
    except ExpiredSignatureError:
        raise PermissionError("Token expired")
    except InvalidTokenError:
        raise PermissionError("Invalid token")

