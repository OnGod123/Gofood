
try:
    from flask import Blueprint, request, jsonify, g, url_for
    from datetime import datetime
    from sqlalchemy.exc import SQLAlchemyError
    from app.utils.vendor_status import vendor_must_be_open
    from app.extensions import Base, r
    from app.merchants.Database.vendors_data_base import FoodItem, Vendor
    from app.database.user_models import User
    from app.merchants.Database.order import OrderSingle, OrderMultiple
    from app.merchants.Database.notifications import Notification
    from app.utils.decorators import token_required
    from app.utils.tasks import (
    send_notification_async,
    send_whatsapp_message,
    send_email_notification,
    )
    from app.utils.jwt_tools import encode_token  # <-- you must have this or similar helper
except ImportError as e:
    raise RuntimeError(
        "Replace app.database.* imports with your real models. "
        "This file expects OrderSingle, FoodItem, Wallet, Vendor, AppUser, CentralAccount, FullName."
    )
order_bp = Blueprint("order_bp", __name__)


@order_bp.route("/order/multiple", methods=["POST", "GET"])
@token_required
@vendor_must_be_open
def multiple_order_handler():
    try:
        if request.method == "GET":
            orders = OrderMultiple.query.filter_by(user_id=g.user.id).all()
            return jsonify({"orders": [o.to_dict() for o in orders]}), 200

        data = request.get_json() or {}
        items = data.get("items")
        if not items or not isinstance(items, list):
            return jsonify({"error": "Items list required"}), 400

        total = 0
        validated_items = []
        vendor_ids = set()

        for entry in items:
            required = ["item_id", "quantity", "price"]
            if not all(k in entry for k in required):
                return jsonify({"error": f"Invalid item data: {entry}"}), 400

            item = FoodItem.query.get(entry["item_id"])
            if not item:
                return jsonify({"error": f"Item {entry['item_id']} not found"}), 404
            if float(entry["price"]) != float(item.price):
                return jsonify({"error": f"Price mismatch for item {entry['item_id']}"}), 409

            validated_items.append(entry)
            total += entry["quantity"] * entry["price"]
            vendor_ids.add(item.vendor_id)

        order = OrderMultiple(
            user_id=g.user.id,
            items_data=validated_items,
            total=total,
            created_at=datetime.utcnow(),
        )
        db.session.add(order)
        db.session.commit()

        # =============== CREATE NOTIFICATIONS PER VENDOR ===============
        notif_objects = []
        for vendor_id in vendor_ids:
            notif = Notification(
                user_id=vendor_id,
                order_id=str(order.id),
                type="new_multi_order",
                payload={
                    "vendors": list(vendor_ids),
                    "buyer_id": g.user.id,
                    "items": validated_items,
                },
            )
            db.session.add(notif)
            notif_objects.append(notif)
        db.session.commit()

        # =============== REDIS + CELERY ===============
        for notif in notif_objects:
            notif_dict = notif.to_dict()
            r.publish("notifications", notif_dict)
            send_notification_async.delay(notif.id)
            send_whatsapp_message.delay(notif.user_id, notif_dict)
            send_email_notification.delay(notif.user_id, notif_dict)

        # =============== REDIRECT LOGIC ===============
        is_vendor = Vendor.query.filter_by(user_id=g.user.id).first() is not None

        if is_vendor:
            # Vendor goes to the notification URL
            redirect_url = url_for(
                "notifications.notify_vendor_from_order",
                order_id=order.id,
                event_type="new_multi_order",
                _external=True,
            )
            jwt_token = None
        else:
            # Customer goes to the payment URL — with encoded order ID
            jwt_token = encode_order_id({"order_id": order.id})
            redirect_url = url_for(
                "payment.start_payment",
                order_id=order.id,
                total=total,
                token=jwt_token,
                _external=True,
            )

        return jsonify({
            "message": "Multiple-item order created successfully",
            "order_id": order.id,
            "redirect_url": redirect_url,
            "jwt": jwt_token,  # Optional: return so frontend can store/use
            "total": total,
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

from flask import Blueprint, request, jsonify, g, url_for
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import Base, r
from app.merchants.Database.vendors_data_base import FoodItem, Vendor
from app.database.user_models import User
from app.merchants.Database.order import OrderSingle
from app.merchants.Database.notifications import Notification
from app.utils.decorators import token_required
from app.utils.tasks import (
    send_notification_async,
    send_whatsapp_message,
    send_email_notification,
)
from app.utils.jwt_tools import encode_token  # <-- import your JWT utility
from app.utils.vendor_status import vendor_must_be_open

order_bp = Blueprint("order_bp", __name__)


@order_bp.route("/order/single", methods=["POST", "GET"])
@token_required
@vendor_must_be_open
def single_order_handler():
    try:
        if request.method == "GET":
            orders = OrderSingle.query.filter_by(user_id=g.user.id).all()
            return jsonify({"orders": [o.to_dict() for o in orders]}), 200

        # -------- POST ----------
        data = request.get_json() or {}
        required = ["item_id", "quantity", "price"]
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400

        item = FoodItem.query.get(data["item_id"])
        if not item:
            return jsonify({"error": "Item not found"}), 404
        if float(data["price"]) != float(item.price):
            return jsonify({"error": "Price mismatch"}), 409

        order = OrderSingle(
            user_id=g.user.id,
            item_data=data,
            total=data["quantity"] * data["price"],
            created_at=datetime.utcnow(),
        )
        db.session.add(order)
        db.session.commit()

        # =============== CREATE NOTIFICATION ===============
        notif = Notification(
            user_id=item.vendor_id,  # send to vendor
            order_id=str(order.id),
            type="new_order",
            payload={
                "item": data,
                "buyer_id": g.user.id,
                "buyer_name": getattr(g.user, "name", None),
            },
        )
        db.session.add(notif)
        db.session.commit()

        # =============== REDIS + CELERY ===============
        notif_dict = notif.to_dict()
        r.publish("notifications", notif_dict)

        # background async sends
        send_notification_async.delay(notif.id)
        send_whatsapp_message.delay(item.vendor_id, notif_dict)
        send_email_notification.delay(item.vendor_id, notif_dict)

        # =============== REDIRECT LOGIC ===============
        is_vendor = Vendor.query.filter_by(user_id=g.user.id).first() is not None

        if is_vendor:
            # Vendor goes to the notification page
            redirect_url = url_for(
                "notifications.notify_vendor_from_order",
                order_id=order.id,
                event_type="new_order",
                _external=True,
            )
            jwt_token = None
        else:
            # Customer goes to payment with JWT-encoded order ID
            jwt_token = encode_order_id({"order_id": order.id})
            redirect_url = url_for(
                "payment.start_payment",
                order_id=order.id,
                total=order.total,
                token=jwt_token,
                _external=True,
            )

        # =============== FINAL RESPONSE ===============
        return jsonify({
            "message": "Order created successfully",
            "order_id": order.id,
            "redirect_url": redirect_url,
            "jwt": jwt_token,
            "total": order.total,
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

