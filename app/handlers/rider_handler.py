from flask import Blueprint, request, jsonify
from app.extensions import db
from app.database.user_models import User
from app.database.rider_models import Rider
from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.database.user_models import User
from app.database.rider_models import Rider


rider_bp = Blueprint("rider", __name__, url_prefix="/rider")
# ------------------------
# Register Rider (GET + POST)
# ------------------------
@rider_bp.route("/register", methods=["GET", "POST"])
def register_rider():
    if request.method == "GET":
        # Render a simple registration form
        return render_template("rider_register.html")

    # POST - form or JSON
    data = request.get_json() if request.is_json else request.form

    phone = data.get("phone")
    email = data.get("email")
    password = data.get("password")

    if not all([phone, email, password]):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Create User
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        phone=phone,
    )
    db.session.add(user)
    db.session.commit()

    # Create Rider
    rider = Rider(user_id=user.id, status="active")
    db.session.add(rider)
    db.session.commit()

    # Generate JWT
    token = create_access_token(identity=user.id)

    return jsonify({
        "message": "Rider registered successfully",
        "rider": {"id": rider.id, "email": user.email, "phone": user.phone},
        "token": token
    }), 201


# ------------------------
# Get Rider Profile (JWT protected)
# ------------------------
@rider_bp.route("rider/profile", methods=["GET"])
@jwt_required()
def rider_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    rider = Rider.query.filter_by(user_id=user.id).first()
    if not rider:
        return jsonify({"error": "Rider profile not found"}), 404

    return jsonify({
        "name": getattr(user, "name", "Unnamed Rider"),
        "email": user.email,
        "phone": user.phone,
        "status": rider.status
    })


