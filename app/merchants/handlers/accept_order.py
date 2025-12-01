from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import r, socketio  # r = Redis client
from app.database.user_models import User
from app.database.rider_models import Rider

accept_order_bp = Blueprint("accept_order_bp", __name__, url_prefix="/rider")

@accept_order_bp.route("/accept_order", methods=["POST"])
@jwt_required()
def accept_order():
    """
    Rider accepts an order. Only the first rider can accept.
    """
    data = request.get_json()
    order_id = data.get("order_id")
    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400

    # Get rider from JWT
    rider_identity = get_jwt_identity()
    rider_id = rider_identity.get("id")

    # Key in Redis for this order
    redis_key = f"order:{order_id}:accepted_by"

    # Atomically set the order if not already accepted
    accepted_by = r.get(redis_key)
    if accepted_by:
        return jsonify({"error": "Order already accepted", "rider_id": accepted_by.decode()}), 409

    r.set(redis_key, rider_id)  # First rider wins
    r.expire(redis_key, 60*60)  # Optional: expire after 1 hour

    # Get user_id to notify
    user_id = r.get(f"order:{order_id}:user_id")
    if not user_id:
        return jsonify({"error": "User info not found"}), 500

    # Get rider info to send to user
    rider = Rider.query.get(rider_id)
    user_info = {
        "rider_id": rider.id,
        "rider_name": getattr(rider.user, "name", ""),
        "rider_phone": getattr(rider.user, "phone", ""),
    }

    # Send to user room
    socketio.emit("order_accepted", {"order_id": order_id, "rider": user_info}, room=f"user:{user_id.decode()}")

    return jsonify({"message": "Order accepted", "rider_id": rider_id}), 200


@accept_order_bp.route("/unaccept_order", methods=["POST"])
@jwt_required()
def unaccept_order():
    """
    Rider can unmark an order only if they were the one who accepted it.
    """
    data = request.get_json()
    order_id = data.get("order_id")
    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400

    rider_identity = get_jwt_identity()
    rider_id = rider_identity.get("id")
    redis_key = f"order:{order_id}:accepted_by"

    accepted_by = r.get(redis_key)
    if not accepted_by:
        return jsonify({"error": "Order not marked"}), 404

    if accepted_by.decode() != str(rider_id):
        return jsonify({"error": "You cannot unmark this order"}), 403

    r.delete(redis_key)
    return jsonify({"message": "Order unmarked"}), 200

