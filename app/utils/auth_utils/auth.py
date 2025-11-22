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




import jwt
from flask import request, jsonify, current_app
from functools import wraps
from app.merchants.Database.user import User  # update path to your user model

def verify_jwt_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization header missing"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

            user_id = payload.get("user_id")
            if not user_id:
                return jsonify({"error": "Invalid token payload"}), 401

            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            # inject the user into the route function
            return func(user, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401

        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

    return wrapper




from functools import wraps
from flask import request, jsonify, g
from app.database.user_models import User
from app.utils.jwt_utils import get_user_from_jwt

def token_required(f):
    """
    Flask route decorator to ensure that a valid JWT token is present.
    Attaches the user info to `g.user` for use in routes.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Extract user info from JWT
            user_info = get_user_from_jwt()
            # Attach to Flask `g` object for global access in the request
            g.user = user_info
        except PermissionError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)
    return decorated

