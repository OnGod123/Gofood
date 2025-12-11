from flask import Blueprint, render_template, request, jsonify
from app.extensions import db, socketio, geolocator
from app.merchants.Database.delivery import Delivery
from app.merchants.Database.order import OrderSingle, OrderMultiple
from app.database.user_models import User

delivery_bp = Blueprint("delivery_bp", __name__)
GLOBAL_ROOM = "all_participants"


def broadcast_order_to_riders(latest_order, delivery, extra_address_info=None):
    """Broadcast full order info to all riders, including address info."""
    if not latest_order or not delivery:
        return

    user = User.query.get(latest_order.user_id)
    if not user:
        return

    items_list = []
    if hasattr(latest_order, "items_data") and latest_order.items_data:
        items_list = latest_order.items_data
    elif hasattr(latest_order, "item_data") and latest_order.item_data:
        items_list = [latest_order.item_data]

    order_data = {
        "order_id": latest_order.id,
        "user_id": latest_order.user_id,
        "user_name": getattr(user, "name", ""),
        "user_phone": getattr(user, "phone", ""),
        "delivery_address": getattr(delivery, "address", ""),
        "total": getattr(latest_order, "total", 0),
        "items": items_list,
        "created_at": str(latest_order.created_at),
    }

    if extra_address_info:
        order_data.update(extra_address_info)

    socketio.emit("latest_order", order_data, room=GLOBAL_ROOM)


@delivery_bp.route("/delivery/<int:order_id>/location", methods=["GET", "POST"])
def manage_delivery_location(delivery_id):
    """GET: render delivery info page; POST: update delivery address and broadcast."""
    delivery = Delivery.query.get(delivery_id)
    if not delivery:
        return jsonify({"error": "Delivery not found"}), 404

    # --- GET REQUEST ---
    if request.method == "GET":
        # Get latest order for rendering
        latest_single = OrderSingle.query.filter_by(user_id=delivery.user_id)\
            .order_by(OrderSingle.created_at.desc()).first()
        latest_multiple = OrderMultiple.query.filter_by(user_id=delivery.user_id)\
            .order_by(OrderMultiple.created_at.desc()).first()
        latest_order = latest_single
        if latest_multiple and (not latest_single or latest_multiple.created_at > latest_single.created_at):
            latest_order = latest_multiple

        return render_template(
            "bargain.html",
            delivery_id=delivery.id,
            latest_order=latest_order,
            delivery_address=delivery.address
        )

    # --- POST REQUEST ---
    data = request.get_json() or {}
    mode = data.get("mode")
    extra_info = {"mode": mode}

    if mode == "manual":
        address = data.get("address")
        if not address:
            return jsonify({"error": "Missing address"}), 400
        delivery.address = address
        extra_info["resolved_address"] = address
        db.session.commit()

    elif mode == "auto":
        lat = data.get("latitude")
        lng = data.get("longitude")
        if not lat or not lng:
            return jsonify({"error": "Missing coordinates"}), 400

        location = geolocator.reverse(f"{lat}, {lng}", language="en")
        if not location:
            return jsonify({"error": "Could not resolve address"}), 400

        delivery.address = location.address
        extra_info["latitude"] = lat
        extra_info["longitude"] = lng
        extra_info["resolved_address"] = location.address
        db.session.commit()

    else:
        return jsonify({"error": "Invalid mode"}), 400

    # Get latest order
    latest_single = OrderSingle.query.filter_by(user_id=delivery.user_id)\
        .order_by(OrderSingle.created_at.desc()).first()
    latest_multiple = OrderMultiple.query.filter_by(user_id=delivery.user_id)\
        .order_by(OrderMultiple.created_at.desc()).first()
    latest_order = latest_single
    if latest_multiple and (not latest_single or latest_multiple.created_at > latest_single.created_at):
        latest_order = latest_multiple

    # Broadcast updated order + address
    broadcast_order_to_riders(latest_order, delivery, extra_address_info=extra_info)

    return jsonify({
        "status": "success",
        "address": delivery.address,
        "extra_info": extra_info
    })


