
from flask import Blueprint, request, jsonify
from app.database.user_models import User
from app.utils.services import send_sms
from app.utils.token_service import generate_jwt
from app.utils.otp_service import send_otp, verify_otp_code

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/auth/request-login-token", methods=["POST"])
def request_login_token():
    data = request.get_json()
    phone = data.get("phone")

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = send_otp(phone, context="login")
    sms_text = f"Your Gofood verification code is {otp}"

    if send_sms(phone, sms_text):
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send SMS"}), 500


@auth_bp.route("/auth/verify-login-token", methods=["POST"])
def verify_login_token():
    data = request.get_json()
    phone = data.get("phone")
    otp = data.get("otp")

    if not verify_otp_code(phone, otp, context="login"):
        return jsonify({"error": "Invalid or expired token"}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    jwt_token = generate_jwt(user.email or user.phone)
    return jsonify({
        "message": "Login successful",
        "token": jwt_token,
        "redirect": "/dashboard"
    }), 200

