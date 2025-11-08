from app.extensions import r
from app.utils.token_service import generate_otp
from datetime import timedelta

def send_otp(phone, context="login", ttl=300):
    """Generate and store OTP in Redis with context key."""
    otp = generate_otp(phone)
    key = f"otp:{context}:{phone}"
    r.setex(key, ttl, otp)
    return otp

def verify_otp_code(phone, otp, context="login"):
    """Verify OTP against Redis for given context."""
    key = f"otp:{context}:{phone}"
    stored_otp = r.get(key)
    if stored_otp and stored_otp.decode() == otp:
        r.delete(key)  # one-time use
        return True
    return False
