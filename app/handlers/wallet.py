from flask import Blueprint, jsonify, request
from app.extensions import db, r
from app.database.models import Order, Payment, Vendor, Wallet, User
from app.utils.auth import verify_jwt_token
from app.utils.token_service import generate_otp, verify_otp
from app.utils.services import send_sms
from datetime import datetime
import uuid
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models.wallet import Wallet, Transaction
from app.utils.jwt_utils import verify_jwt
import uuid

wallet_payment_bp = Blueprint("wallet_payment_bp", __name__)

# ===========================
# 1️⃣ Request OTP for payment
# ===========================
@wallet_payment_bp.route("/order/request-otp", methods=["POST"])
@verify_jwt_token
def request_payment_otp(current_user):
    """
    Sends an OTP to the user's registered phone number for wallet transaction confirmation.
    """
    try:
        user = User.query.get(current_user.id)
        if not user or not user.phone:
            return jsonify({"error": "Phone number not found"}), 404

        otp = generate_otp(user.phone)
        sms_text = f"Your Gofood wallet payment code is {otp}. It expires in 5 minutes."

        if send_sms(user.phone, sms_text):
            return jsonify({"message": "OTP sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send OTP"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to generate OTP", "details": str(e)}), 500

wallet_bp = Blueprint("wallet_bp", __name__, url_prefix="/wallet")

@wallet_bp.route("/balance", methods=["GET"])
@verify_jwt
def get_balance(user):
    wallet = Wallet.query.filter_by(user_id=user.id).first()
    return jsonify({"balance": wallet.balance if wallet else 0})

@wallet_bp.route("/transfer", methods=["POST"])
@verify_jwt
def transfer_funds(user):
    data = request.json
    vendor_id = data.get("vendor_id")
    amount = float(data.get("amount"))
    wallet = Wallet.query.filter_by(user_id=user.id).first()
    if not wallet or wallet.balance < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    txn = Transaction(user_id=user.id, vendor_id=vendor_id, amount=amount,
                      type="payout", reference=str(uuid.uuid4()), status="completed")
    wallet.balance -= amount
    db.session.add(txn)
    db.session.commit()
    return jsonify({"status": "success", "txn_id": txn.reference})


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
