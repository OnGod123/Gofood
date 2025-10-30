from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.extensions import db
from app.merchant.Database.delivery import Delivery
from app.merchant.Database.order import OrderSingle, OrderMultiple
from app.utils import get_latest_order

delivery_bp = Blueprint("delivery", __name__)

@delivery_bp.route("/delivery", methods=["GET", "POST"])
def delivery_handler():
      # example; normally get from session or JWT

    if request.method == "POST":
        user_id = session.get("user_id")
        address = request.form.get("address") or request.json.get("address")
        if not address:
            return jsonify({"error": "Address required"}), 400

        latest_order = get_latest_order(db.session, user_id)
        if not latest_order:
            return jsonify({"error": "No orders found"}), 404

        delivery = Delivery(
            user_id=user_id,
            address=address,
            order_single_id=getattr(latest_order, "id", None) if isinstance(latest_order, OrderSingle) else None,
            order_multiple_id=getattr(latest_order, "id", None) if isinstance(latest_order, OrderMultiple) else None
        )
        db.session.add(delivery)
        db.session.commit()

        # Redirect to WebSocket bargain page
        return redirect(url_for("delivery.bargain_page", delivery_id=delivery.id))

    # ---- GET method: show latest delivery ----
    delivery = (
        db.session.query(Delivery)
        .filter_by(user_id=user_id)
        .order_by(Delivery.created_at.desc())
        .first()
    )

    if not delivery:
        return jsonify({"message": "No deliveries yet"})

    data = {
        "id": delivery.id,
        "address": delivery.address,
        "status": delivery.status,
        "delivery_fee": delivery.delivery_fee,
        "created_at": delivery.created_at,
    }

    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        return jsonify(data)
    else:
        return render_template("delivery.html", delivery=data)

