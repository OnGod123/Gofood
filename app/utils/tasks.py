# app/utils/tasks.py
from threading import Thread
from flask import current_app
from app.utils.sms import send_sms  # your SMS function
from app.utils.email import send_email  # your email function

def send_notification_async(func, *args, **kwargs):
    """Run any function asynchronously in a thread."""
    Thread(target=func, args=args, kwargs=kwargs).start()

def send_whatsapp_message(phone, message):
    """Send a WhatsApp message (replace with actual API integration)."""
    # Example using your WhatsApp API class
    from app.utils.whatsapp_client import WhatsAppClient
    client = WhatsAppClient(phone_number_id=current_app.config["WHATSAPP_NUMBER_ID"])
    return client.send_text(phone, message)

def send_email_notification(to_email, subject, body, html_body=None):
    """Send an email notification."""
    return send_email(to_email, subject, body, html_body)

