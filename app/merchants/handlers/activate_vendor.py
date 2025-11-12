from flask import Blueprint, request, jsonify, session, g, current_app
from functools import wraps
import jwt
from datetime import datetime
from app.extensions import init_db, r  # r = Redis instance
from app.database.user_models import User
from app.merchants.Database.vendors_data_base import Vendor  # assuming vendor model exists

vendor_activity_bp = Blueprint("vendor_activity", __name__)

# ----------------------------
# AUTH DECORATOR (Token-based)
# ----------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header or session
        if "Authorization" in request.headers:
            auth_header = request.headers.get("Authorization")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        elif session.get("jwt"):
            token = session["jwt"]

        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            data = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            user_email = data.get("email")

            # Validate session in Redis
            if not r.exists(f"session:{user_email}"):
                return jsonify({"error": "Session expired or invalid"}), 401

            # Fetch user and vendor from DB
            user = db.session.query(User).filter_by(email=user_email).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            g.current_user = user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated


# ---------------------------------------
# POST /vendor/active — Update shop state
# ---------------------------------------
@vendor_activity_bp.route("/vendor/active", methods=["POST"])
@token_required
def update_vendor_status():
    """Allow a vendor to mark their shop as open or closed."""
    user = g.current_user
    data = request.get_json()

    # Validate input
    if not data or "is_active" not in data:
        return jsonify({"error": "Invalid request. Missing is_active field."}), 400

    is_active = data["is_active"]
    if not isinstance(is_active, bool):
        return jsonify({"error": "is_active must be a boolean"}), 400

    # Check if user is a vendor
    vendor = db.session.query(Vendor).filter_by(user_id=user.id).first()
    if not vendor:
        return jsonify({"error": "You are not registered as a vendor."}), 404

    # Update vendor status
    vendor.is_active = is_active
    vendor.updated_at = datetime.utcnow()
    db.session.commit()

    # Cache state in Redis
    r.set(f"vendor:{vendor.id}:is_active", str(is_active), ex=3600)

    # Track in Flask session
    session["vendor_is_active"] = is_active

    # Response message
    if is_active:
        message = "Vendor shop is now open."
    else:
        message = "Vendor shop has been closed."

    return jsonify({
        "message": message,
        "is_active": is_active
    }), 200


# -------------------------------------
# GET /vendor/active — Fetch shop state
# -------------------------------------
@vendor_activity_bp.route("/vendor/active", methods=["GET"])
@token_required
def get_vendor_status():
    """Fetch the vendor's current shop status."""
    user = g.current_user
    vendor = db.session.query(Vendor).filter_by(user_id=user.id).first()

    if not vendor:
        return jsonify({"error": "You are not registered as a vendor."}), 404

    # Try Redis cache first
    cached_state = r.get(f"vendor:{vendor.id}:is_active")
    if cached_state is not None:
        is_active = cached_state.decode("utf-8") == "True"
    else:
        is_active = vendor.is_active
        r.set(f"vendor:{vendor.id}:is_active", str(is_active), ex=3600)

    message = (
        "Your shop is currently open." if is_active else "Your shop is currently closed."
    )

    return jsonify({
        "vendor_id": vendor.id,
        "is_active": is_active,
        "message": message
    }), 200

