from flask import Blueprint, request, jsonify, g
from app.extensions import db, r
from app.models.user import User
from app.utils.auth import token_required
from app.utils.services import send_sms
from app.utils.token_service import generate_otp, verify_otp

wallet_payment_bp = Blueprint("wallet_payment_bp", __name__)

@wallet_payment_bp.route("/order/request-phone-verification", methods=["POST"])
@token_required
def request_phone_verification():
    """
    Sends OTP to user's registered phone before wallet payment.
    """
    try:
        user = User.query.get(g.user.id)
        if not user or not user.phone:
            return jsonify({"error": "No phone number found for this user"}), 404

        otp = generate_otp(user.phone)
        sms_text = f"Your Gofood payment verification code is {otp}"

        if send_sms(user.phone, sms_text):
            # Cache OTP session for payment
            r.setex(f"otp:payment:{user.phone}", 300, otp)
            return jsonify({"message": "OTP sent successfully"}), 200
        else:
            return jsonify({"error": "Failed to send OTP"}), 500

    except Exception as e:
        return jsonify({"error": "Failed to send OTP", "details": str(e)}), 500

