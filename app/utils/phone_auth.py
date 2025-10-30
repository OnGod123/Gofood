
from flask import request, jsonify, current_app
from app.extensions import db
from app.database.user_models import User
from app.utils.services import send_sms
from app.utils.token_service import generate_otp, verify_otp, generate_jwt

def request_login_token():
    data = request.get_json()
    phone = data.get("phone")

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    otp = generate_otp(phone)
    sms_text = f"Your Gofood verification code is {otp}"

    if send_sms(phone, sms_text):
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        return jsonify({"error": "Failed to send SMS"}), 500

def verify_login_token():
    data = request.get_json()
    phone = data.get("phone")
    otp = data.get("otp")

    if not verify_otp(phone, otp):
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

