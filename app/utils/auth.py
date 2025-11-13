import jwt
from flask import current_app
from app.database.user_models import User
from app.extensions import Base

def verify_jwt_socket(token):
    try:
        payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        return db.session.get(User, payload.get("user_id"))
    except Exception:
        return None

