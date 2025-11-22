from flask import Blueprint, jsonify, request
from app.extensions import Base, r
from app.merchants.Database.order import OrderSingle, OrderMultiple
from app.database.payment_models import PaymentTransaction
from app.merchants.Database.vendors_data_base import Vendor
from app.database.user_models import  User
from app.utils.auth import verify_jwt_token
from app.utils.token_service import generate_otp, verify_otp
from app.utils.services import send_sms
from datetime import datetime
import uuid
from app.sms_processor.otp_sender import send_payment_otp
from flask import Blueprint, jsonify, request
from app.extensions import Base
from app.database.wallet import Wallet, Transaction
from app.utils.jwt.auth import verify_jwt_tokem
import uuid
from app.services.payout.payout_processor import process_vendor_payout, PayoutError

wallet_payment_bp = Blueprint("wallet_payment_bp", __name__)

@wallet_payment_bp.route("/order/request-otp", methods=["POST"])
@verify_jwt_token
def request_payment_otp(current_user):
    try:
        user = User.query.get(current_user.id)

        if not user or not user.phone:
            return jsonify({"error": "Phone number not found"}), 404

        sent = send_payment_otp(user.phone, use="twilio")  # or use="gammu"

        if sent:
            return jsonify({"message": "OTP sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send OTP"}), 500

    except Exception as e:
        return jsonify({
            "error": "Failed to generate OTP",
            "details": str(e)
        }), 500

wallet_bp = Blueprint("wallet_bp", __name__, url_prefix="/wallet")

@wallet_bp.route("/balance", methods=["GET"])
@verify_jwt
def get_balance(user):
    wallet = Wallet.query.filter_by(user_id=user.id).first()
    return jsonify({"balance": wallet.balance if wallet else 0})

@wallet_bp.route("/transfer", methods=["POST"])
@verify_jwt
def transfer_funds(user):
    """
    Transfer funds from user wallet to vendor via selected provider
    """
    data = request.json
    vendor_id = data.get("vendor_id")
    order_id = data.get("order_id")
    amount = float(data.get("amount", 0))
    provider = data.get("provider")  # "paystack", "flutterwave", "monnify"

    if not all([vendor_id, order_id, amount, provider]):
        return jsonify({"status": "error", "reason": "Missing required fields"}), 400

    # Fetch wallet
    wallet = Wallet.query.filter_by(user_id=user.id).first()
    if not wallet or wallet.balance < amount:
        return jsonify({"status": "error", "reason": "Insufficient wallet balance"}), 400

    reference = f"TXN-{uuid.uuid4().hex[:12]}"
    txn = Transaction(
        user_id=user.id,
        vendor_id=vendor_id,
        order_id=order_id,
        amount=amount,
        type="payout",
        reference=reference,
        status="processing",
        created_at=datetime.utcnow()
    )
    db.session.add(txn)
    db.session.commit()

    try:
        # Process the payout through the chosen provider
        result = process_vendor_payout(
            user_id=user.id,
            vendor_id=vendor_id,
            order_id=order_id,
            amount=amount,
            provider=provider
        )

        # Update transaction status
        txn.status = "completed"
        txn.metadata = result.get("provider_response", {})
        db.session.commit()

        return jsonify({
            "status": "success",
            "transaction_id": reference,
            "amount": amount,
            "vendor_amount": result["vendor_amount"],
            "fee": result["fee"],
            "provider": provider,
            "wallet_balance": result["wallet_balance"],
            "provider_response": result["provider_response"]
        }), 200

    except PayoutError as e:
        # Update transaction as failed
        txn.status = "failed"
        txn.metadata = {"error": str(e)}
        db.session.commit()
        return jsonify({"status": "error", "reason": str(e)}), 400


moniepoint_bp = Blueprint("moniepoint_bp", __name__, url_prefix="/moniepoint")

@moniepoint_bp.route("/webhook", methods=["POST"])
def moniepoint_webhook():
    data = request.json
    full_name = data.get("full_name")
    amount = float(data.get("amount", 0))
    reference = data.get("reference", str(uuid.uuid4()))

    wallet = Wallet.query.filter_by(full_name=full_name).first()
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    wallet.balance += amount
    txn = Transaction(user_id=wallet.user_id, amount=amount, type="deposit",
                      reference=reference, status="completed")
    db.session.add(txn)
    db.session.commit()

    return jsonify({"status": "success"})
