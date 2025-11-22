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

@rider_bp.route("/register", methods=["POST"])
def register_rider():
    data = request.get_json() if request.is_json else request.form

    phone = data.get("phone")
    email = data.get("email")
    username = data.get("username")

    if not any([phone, email, username]):
        return jsonify({"error": "Provide phone, email or username"}), 400

    # 1. CHECK IF USER ALREADY EXISTS
    user = User.query.filter(
        (User.phone == phone) |
        (User.email == email) |
        (User.username == username)
    ).first()

    if not user:
        return jsonify({
            "error": "User not registered",
            "signin_url": "https://yourapp.com/auth/register"
        }), 404

    # 2. CHECK IF USER IS ALREADY A RIDER
    existing_rider = Rider.query.filter_by(user_id=user.id).first()

    if existing_rider:
        token = create_access_token(identity={"id": existing_rider.id, "type": "rider"})
        return jsonify({
            "message": "User is already a rider",
            "rider": {
                "id": existing_rider.id,
                "email": user.email,
                "phone": user.phone
            },
            "token": token
        }), 200

    # 3. REGISTER AS NEW RIDER
    rider = Rider(user_id=user.id, status="active")
    db.session.add(rider)
    db.session.commit()

    token = create_access_token(identity={"id": rider.id, "type": "rider"})

    return jsonify({
        "message": "Rider registration successful",
        "rider": {
            "id": rider.id,
            "email": user.email,
            "phone": user.phone
        },
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


