
from threading import Thread
from app.utils.email_helper import  send_email
from app.whatsapp.whatsapphandler import WhatsAppClient  

def run_async(func, *args, **kwargs):
    """Run a function asynchronously in a thread."""
    Thread(target=func, args=args, kwargs=kwargs).start()

def send_email_notification(to_email, subject, body, html_body=None):
    return send_email(to_email, subject, body, html_body)

def send_whatsapp_message(to, message):
    client = WhatsAppClient(token="YOUR_TOKEN", phone_number_id="YOUR_PHONE_ID")
    return client.send_text(to=to, message=message)

def _send_notification(notification_id):
    """
    Actual notification logic.
    Marks as sent and optionally triggers other notifications.
    """
    notif = Notification.query.get(notification_id)
    if not notif:
        return None

    # Mark notification as sent
    notif.sent = True
    db.session.commit()

    # Example: send WhatsApp or email (optional)
    # run_async(send_whatsapp_message, notif.user_id, notif.to_dict())
    # run_async(send_email_notification, notif.user_id, "New Notification", str(notif.to_dict()))

    return notif

def send_notification_async(notification_id):
    """
    Public function to run notification logic in the background.
    """
    run_async(_send_notification, notification_id)
