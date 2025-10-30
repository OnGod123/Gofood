from app import create_app
from app.extensions import db
from app.merchant.database.notifications import Notification

app = create_app()
celery = app.celery

@celery.task
def send_notification_async(notification_id):
    notif = db.session.get(Notification, notification_id)
    if not notif:
        return
    # Example: simulate email/push sending
    print(f"Sending notification to user {notif.user_id} for order {notif.order_id}")

