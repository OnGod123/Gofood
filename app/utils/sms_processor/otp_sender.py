from app.sms_processor.twilio_sms import twilio_send_sms
from app.sms_processor.gammu_sms import send_sms
from app.sms_processor.otp_service import generate_and_store_otp

def send_payment_otp(phone: str, use="twilio"):
    """
    Generate OTP, store it in Redis, and transport via chosen SMS provider.
    """

    otp = generate_and_store_otp(phone, context="payment", ttl=300)
    message = f"Your Gofood payment OTP is {otp}. It expires in 5 minutes."

    if use == "twilio":
        sid = twilio_send_sms(phone, message)
        if sid:
            return True
        return False

    if use == "gammu":
        return send_sms(phone, message)

    return False

