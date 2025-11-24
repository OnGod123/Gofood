from flask import Blueprint, render_template, jsonify
from app.extensions import db, socketio
from app.merchants.Database.delivery import Delivery
from app.merchants.Database.order import OrderSingle, OrderMultiple
from app.database.user_models import User

delivery_bp = Blueprint("delivery_bp", __name__)
GLOBAL_ROOM = "all_participants"

def broadcast_order_to_riders(latest_order, delivery):
    """Broadcast full order info to all riders."""
    if not latest_order or not delivery:
        return

    user = User.query.get(latest_order.user_id)
    if not user:
        return

    # Prepare items list for broadcasting
    items_list = []
    if hasattr(latest_order, "items_data") and latest_order.items_data:
        items_list = latest_order.items_data  # Multiple items order
    elif hasattr(latest_order, "item_data") and latest_order.item_data:
        items_list = [latest_order.item_data]  # Single item order

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

    socketio.emit("latest_order", order_data, room=GLOBAL_ROOM)


@delivery_bp.route("/delivery/<int:delivery_id>/bargain")
def bargain_page(delivery_id):
    """HTTP endpoint to view latest order and broadcast it."""
    delivery = Delivery.query.get(delivery_id)
    if not delivery:
        return jsonify({"error": "Delivery not found"}), 404

    # Fetch latest single and multiple orders for the delivery's user
    latest_single_order = (
        OrderSingle.query.filter_by(user_id=delivery.user_id)
        .order_by(OrderSingle.created_at.desc())
        .first()
    )
    latest_multiple_order = (
        OrderMultiple.query.filter_by(user_id=delivery.user_id)
        .order_by(OrderMultiple.created_at.desc())
        .first()
    )

    # Determine the latest overall order
    latest_order = latest_single_order
    if latest_multiple_order:
        if not latest_single_order or latest_multiple_order.created_at > latest_single_order.created_at:
            latest_order = latest_multiple_order

    # Broadcast order data to all riders
    broadcast_order_to_riders(latest_order, delivery)

    # Render HTTP template with latest order info
    return render_template("bargain.html", delivery_id=delivery_id, latest_order=latest_order)


