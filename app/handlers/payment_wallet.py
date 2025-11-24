from flask import Blueprint, jsonify, request, url_for
from app.extensions import Base, r
from app.merchants.Database.order import OrderSingle, OrderMultiple
from app.merchants.Database import Vendors_payment_service
from app.merchants.Database.vendors_data_base import Vendor
from app.handlers.wallet import Wallet
from app.utils.auth import verify_jwt_token
from app.utils.otp import otp_request_required
from datetime import datetime
from app.handlers.payout_engine import process_vendor_payout
import uuid

wallet_payment_bp = Blueprint("wallet_payment_bp", __name__)

@otp_request_required(context="payment", ttl=300)
@wallet_payment_bp.route("/order/proceed-to-payment/<order_id>", methods=["POST"])
@verify_jwt_token
@otp_request_required(context="payment", ttl=300)
def proceed_to_payment(current_user, order_id):
    """
    Process payment using internal wallet instead of external gateway.
    """
    try:
        
        orders = OrderSingle.query.filter_by(
            user_id=current_user.id, order_id=order_id, status="pending"
        ).all()

        if not orders:
            return jsonify({"error": "No pending orders found"}), 404

        total_amount = sum(o.total_price for o in orders)
        vendor_id = orders[0].vendor_id

        
        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if not wallet:
            return jsonify({"error": "Wallet not found for user"}), 404

        
        if wallet.balance < total_amount:
            return jsonify({
                "error": "Insufficient balance. Please fund your wallet."
            }), 400

        
        ref = str(uuid.uuid4())

        with db.session.begin_nested():

            
            wallet.debit(total_amount)

            
            for o in orders:
                o.status = "paid"


            payment = Vendoes_Payment_service(
                id=uuid.uuid4(),
                user_id=current_user.id,
                vendor_id=vendor_id,
                order_id=order_id,
                amount=total_amount,
                status="successful",
                payment_gateway="wallet",
                reference=ref,
                created_at=datetime.utcnow(),
            )
            db.session.add(payment)

        db.session.commit()

        
        r.setex(
            f"payment:{order_id}",
            300,
            f"{total_amount}|{current_user.id}|{vendor_id}"
        )
        
        payout_result = process_vendor_payout(
            user_id=current_user.id,
            vendor_id=vendor_id,
            order_id=order_id,
            amount=total_amount,
            provider="moniepoint"  # or paystack, flutterwave…
        )

        
        delivery_url = url_for(
            "delivery_bp.start_delivery_process",
            order_id=order_id,
            _external=True
        )

        # (Optional WebSocket or Celery notification)
        # socketio.emit("payment_successful", {"vendor_id": vendor_id, "amount": total_amount})

        return jsonify({
            "message": "Payment completed successfully via wallet",
            "reference": ref,
            "amount": total_amount,
            "wallet_balance": wallet.balance,
            "redirect_to_delivery": delivery_url
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Wallet payment failed",
            "details": str(e)
        }), 500

