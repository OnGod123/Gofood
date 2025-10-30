from flask import Blueprint, jsonify, request
from app.extensions import db, r
from app.database.models import Order, Payment, Vendor, Wallet
from app.utils.auth import verify_jwt_token
from datetime import datetime
import uuid

wallet_payment_bp = Blueprint("wallet_payment_bp", __name__)

@wallet_payment_bp.route("/order/proceed-to-payment", methods=["POST"])
@verify_jwt_token
def proceed_to_payment(current_user):
    """
    Process payment using internal wallet instead of external gateway.
    """
    try:
        data = request.get_json()
        order_id = data.get("order_id")

        if not order_id:
            return jsonify({"error": "order_id is required"}), 400

        # 1️⃣ Fetch pending orders
        orders = Order.query.filter_by(
            user_id=current_user.id, order_id=order_id, status="pending"
        ).all()

        if not orders:
            return jsonify({"error": "No pending orders found"}), 404

        total_amount = sum(order.total_price for order in orders)
        vendor_id = orders[0].vendor_id

        # 2️⃣ Fetch wallet
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if not wallet:
            return jsonify({"error": "Wallet not found for user"}), 404

        # 3️⃣ Ensure sufficient balance
        if wallet.balance < total_amount:
            return jsonify({"error": "Insufficient balance. Please fund your wallet."}), 400

        # 4️⃣ Perform payment atomically
        ref = str(uuid.uuid4())

        with db.session.begin_nested():
            # Deduct from user wallet
            wallet.debit(total_amount)

            # Mark all orders as paid
            for order in orders:
                order.status = "paid"

            # Create payment record
            payment = Payment(
                id=uuid.uuid4(),
                user_id=current_user.id,
                vendor_id=vendor_id,
                order_id=order_id,
                amount=total_amount,
                status="successful",
                payment_gateway="wallet",
                created_at=datetime.utcnow(),
            )
            db.session.add(payment)

        db.session.commit()

        # 5️⃣ Cache summary
        r.setex(f"payment:{order_id}", 300, f"{total_amount}|{current_user.id}|{vendor_id}")
          # 6️⃣ Build redirect to delivery handler
        delivery_url = url_for(
            "delivery_bp.start_delivery_process",  # <-- your delivery handler endpoint
            order_id=order_id,
            _external=True
        )

        # 6️⃣ Vendor Notification (WebSocket/Celery)
        # socketio.emit("payment_successful", {"vendor_id": vendor_id, "amount": total_amount})

        return jsonify({
            "message": "Payment completed successfully via wallet",
            "reference": ref,
            "amount": total_amount,
            "wallet_balance": wallet.balance
             "redirect_to_delivery": delivery_url
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Wallet payment failed", "details": str(e)}), 500

