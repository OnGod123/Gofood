from flask import Blueprint, request, jsonify, session, current_app, g
from functools import wraps
from datetime import datetime
import jwt
import uuid

from app.extensions import Base, r  # Redis and database
from app.database.user_models import User
from app.merchants.Database.vendors_data_base import Vendor

register_vendor_bp = Blueprint("register_vendor", __name__, url_prefix="/registeras")


# ---------------------------
# Token Authentication Helper
# ---------------------------
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
            return jsonify({"error": "Missing authentication token"}), 401

        try:
            # Decode token
            data = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            email = data.get("email")

            # Check Redis session
            if not r.exists(f"session:{email}"):
                return jsonify({"error": "Session expired"}), 401

            # Validate user from DB
            user = db.session.query(User).filter_by(email=email).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

            # Store in Flask global context
            g.current_user = user

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated


# -------------------------------------------------------
# /registeras/vendor → Register a new vendor (GET, POST)
# -------------------------------------------------------
@register_vendor_bp.route("/vendor", methods=["GET", "POST"])
@token_required
def register_as_vendor():
    user = g.current_user

    # ---------------- GET: check if user is already a vendor ----------------
    if request.method == "GET":
        vendor = db.session.query(Vendor).filter_by(name=user.name).first()
        if vendor:
            return jsonify({
                "message": "Vendor profile found",
                "vendor": vendor.to_dict()
            }), 200
        return jsonify({"message": "User not registered as vendor yet"}), 404

    # ---------------- POST: register as new vendor ----------------
    if request.method == "POST":
        data = request.get_json() or {}

        shop_name = data.get("shop_name")
        address = data.get("address")

        if not shop_name or not address:
            return jsonify({"error": "shop_name and address are required"}), 400

        # Prevent duplicate vendor registration
        existing_vendor = db.session.query(Vendor).filter_by(name=user.name).first()
        if existing_vendor:
            return jsonify({"error": "User already registered as vendor"}), 400

        # Create new vendor record
        new_vendor = Vendor(
            name=shop_name,
            address=address,
            created_at=datetime.utcnow(),
            is_open=True,  # Default open upon registration
        )

        db.session.add(new_vendor)
        db.session.commit()

        # Store session state
        session["vendor_id"] = new_vendor.id
        session["user_id"] = user.id
        session["is_authenticated"] = True
        session["vendor_created_at"] = new_vendor.created_at.isoformat()

        # Cache vendor ID in Redis for fast lookup
        r.set(f"vendor:{user.email}:id", new_vendor.id)

        return jsonify({
            "message": "Vendor registration successful",
            "vendor": new_vendor.to_dict()
        }), 201

