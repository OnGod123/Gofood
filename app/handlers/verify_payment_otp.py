from functools import wraps
from flask import request, jsonify, g
from app.models.user import User
from app.utils.services import send_sms
from app.utils.token_service import send_otp

def otp_request_required(context="payment", ttl=300):
    """
    Decorator to send OTP to user's phone before executing a sensitive action.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = User.query.get(g.user.id)
            if not user or not user.phone:
                return jsonify({"error": "No phone number found for this user"}), 404

            # Generate OTP and store it in Redis for the given context
            otp = send_otp(user.phone, context=context, ttl=ttl)
            sms_text = f"Your Gofood {context} verification code is {otp}"

            if not send_sms(user.phone, sms_text):
                return jsonify({"error": "Failed to send OTP"}), 500

            # Optional: return a message that OTP was sent
            return jsonify({"message": f"OTP sent successfully for {context}"}), 200

        return wrapper
    return decorator

