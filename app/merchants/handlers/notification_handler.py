
from flask import Blueprint, request, jsonify, url_for
from app.extensions import db, r
from app.merchants.Database.notifications import Notification
from app.merchants.Database.vendors_data_base import FoodItem
from app.merchants.Database.order import OrderSingle, OrderMultiple
from app.database.user_models import User
from app.utils.tasks import (
    send_notification_async, send_whatsapp_message, send_email_notification
)

notification_bp = Blueprint("notifications", __name__)

@notification_bp.route("/notifications/order", methods=["GET"])
def notify_vendor_from_order():
    """
    This route is triggered when an order is created.
    Example:
    /notifications/order?order_id=123&event_type=new_order
    """
    order_id = request.args.get("order_id")
    event_type = request.args.get("event_type", "new_order")

    if not order_id:
        return jsonify({"error": "Missing order_id"}), 400

    # Try to find order in both tables
    order = OrderSingle.query.get(order_id) or OrderMultiple.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    notifications = []

    # SINGLE ORDER
    if isinstance(order, OrderSingle):
        item_data = order.item_data or {}
        item = FoodItem.query.get(item_data.get("item_id"))
        if not item:
            return jsonify({"error": "Item not found"}), 404

        notif = Notification(
            user_id=item.vendor_id,
            order_id=str(order.id),
            type=event_type,
            payload={
                "buyer_id": order.user_id,
                "item": item_data,
                "total": order.total,
            },
        )
        db.session.add(notif)
        notifications.append(notif)

    # MULTIPLE ORDER
    elif isinstance(order, OrderMultiple):
        vendor_ids = {FoodItem.query.get(i["item_id"]).vendor_id for i in order.items_data}
        for vid in vendor_ids:
            notif = Notification(
                user_id=vid,
                order_id=str(order.id),
                type=event_type,
                payload={
                    "vendors": list(vendor_ids),
                    "buyer_id": order.user_id,
                    "items": order.items_data,
                    "total": order.total,
                },
            )
            db.session.add(notif)
            notifications.append(notif)

    db.session.commit()

    # Send notifications through Redis + background tasks
    for notif in notifications:
        notif_dict = notif.to_dict()
        r.publish("notifications", notif_dict)
        send_notification_async.delay(notif.id)
        send_whatsapp_message.delay(notif.user_id, notif_dict)
        send_email_notification.delay(notif.user_id, notif_dict)

    return jsonify({
        "message": "Vendor(s) notified successfully",
        "order_id": order.id,
        "notifications": [n.to_dict() for n in notifications],
    }), 200

