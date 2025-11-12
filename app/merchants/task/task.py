from app.extensions import celery, mail
from flask_mail import Message
from app.models import Vendor
from twilio.rest import Client

@celery.task
def send_notification_async(notif_id):
    # load notif and handle push or websocket broadcast if needed
    pass

@celery.task
def send_email_notification(vendor_id, notif_data):
    vendor = Vendor.query.get(vendor_id)
    if not vendor or not vendor.email:
        return
    msg = Message(
        subject=f"New Order #{notif_data['order_id']}",
        recipients=[vendor.email],
        body=f"You have a new order. Details: {notif_data}"
    )
    mail.send(msg)

@celery.task
def send_whatsapp_message(vendor_id, notif_data):
    vendor = Vendor.query.get(vendor_id)
    if not vendor or not vendor.phone_number:
        return
    client = Client("TWILIO_SID", "TWILIO_AUTH_TOKEN")
    client.messages.create(
        from_="whatsapp:+14155238886",  # Twilio sandbox number
        to=f"whatsapp:{vendor.phone_number}",
        body=f"You have a new order (ID {notif_data['order_id']}). Please check your dashboard."
    )

