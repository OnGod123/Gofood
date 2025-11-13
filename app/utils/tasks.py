
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

