import os
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def twilio_send_sms(to_number: str, message: str) -> str | None:
    """
    Send SMS using Twilio.
    Returns Twilio SID on success, None on failure.
    """
    try:
        msg = _client.messages.create(
            body=message,
            from_=TWILIO_FROM_NUMBER,
            to=to_number
        )
        return msg.sid

    except Exception as exc:
        print("twilio_send_sms error:", exc)
        return None

