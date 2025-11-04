from flask import Blueprint, request, jsonify
from app.extensions import db
from app.database.user_models import User
from app.database.rider_models import Rider

rider_bp = Blueprint("rider", __name__, url_prefix="/rider")

@rider_bp.route("/register", methods=["POST"])
def register_rider():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    existing = Rider.query.filter_by(user_id=user_id).first()
    if existing:
        return jsonify({"message": "Already registered as rider"}), 200

    rider = Rider(user_id=user.id, status="active")
    db.session.add(rider)
    db.session.commit()

    return jsonify({"message": "Rider registered successfully", "rider": rider.to_dict()}), 201

