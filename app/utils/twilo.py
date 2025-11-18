import os
from twilio.rest import Client
from app.utils.otp_service import send_otp as generate_and_store_otp
from app.utils.twilo import twilo_send_sms

_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def twilo_send_sms(to_number: str, message: str) -> str | None:
    """
    Send an SMS using Twilio. Returns Twilio SID on success, None on failure.
    This function is a thin transport — no OTP logic here.
    """
    try:
        msg = _client.messages.create(
            body=message,
            from_=TWILIO_FROM_NUMBER,
            to=to_number
        )
        return msg.sid
    except Exception as exc:
        # In production, replace print with structured logging
        print("twilo_send_sms error:", exc)
    return None



def send_otp_via_twilo(phone: str, context: str = "login", ttl: int = 300) -> dict:
    """
    Generate OTP (store in Redis) and send via Twilio transport.

    Returns a dict with:
        {"status": "sent", "sid": "<twilio_sid>"} on success
        {"status": "error", "reason": "..."} on failure

    NOTE: For security, this function does NOT return the OTP value.
    """
    otp = generate_and_store_otp(phone, context=context, ttl=ttl)

    message = f"Your verification code is {otp}. It expires in {ttl//60} minutes."
    sid = twilo_send_sms(phone, message)

    if sid:
        return {"status": "sent", "sid": sid}
    else:
        # Optionally: delete the Redis key so the OTP can't be used if SMS failed
        # from app.extensions import r
        # r.delete(f"otp:{context}:{phone}")
        return {"status": "error", "reason": "failed_to_send"}

