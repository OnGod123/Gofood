import gammu
import re
from datetime import datetime
from app.extensions import db
from app.models import User, Wallet, CentralAccount, PaymentTransaction, FullName
from app.utils.services import send_sms

# --- Step 1: Sending money to central account (manual/external step) ---
# Normally, money is deposited to your Moniepoint/central account by someone sending it
# e.g., user or admin transfers money into central account
# The system will monitor SMS alerts for these incoming credits

# --- Step 2: Process incoming SMS ---
def process_incoming_sms():
    """
    Poll SMS inbox via Gammu, extract credit info, match user, credit wallet, and log transaction.
    """
    sm = gammu.StateMachine()
    sm.ReadConfig()
    sm.Init()

    inbox = sm.GetNextSMS(Start=True, Folder=0)  # Folder 0 = inbox

    while inbox:
        for msg in inbox:
            if msg.get('State') != 'UnRead':
                continue

            text = msg.get('Text', '')
            sender_number = msg.get('Number', '')
            received_at = msg.get('DateTime', datetime.utcnow())

            # --- Step 2a: Extract details from SMS ---
            sender_name = extract_name_from_text(text)
            amount = extract_amount_from_text(text)
            reference = extract_reference_from_text(text) or f"GAMMA-{datetime.utcnow().timestamp()}"

            if not amount:
                print("No amount found, skipping SMS")
                mark_sms_processed(sm, msg)
                continue

            # --- Step 2b: Match user ---
            user = User.query.filter_by(phone=sender_number).first()
            if not user and sender_name:
                full = FullName.query.filter(
                    FullName.full_name.ilike(f"%{sender_name.strip()}%")
                ).first()
                if full:
                    user = full.user

            if not user:
                print(f"No matching user for SMS from {sender_number} / {sender_name}")
                mark_sms_processed(sm, msg)
                continue

            # --- Step 2c: Credit wallet ---
            wallet = Wallet.query.filter_by(user_id=user.id).first()
            central = CentralAccount.query.first()

            if not wallet or not central or central.balance < amount:
                print("Insufficient central balance or missing wallet")
                mark_sms_processed(sm, msg)
                continue

            central.balance -= amount
            wallet.balance += amount

            # --- Step 2d: Log transaction ---
            trx = PaymentTransaction(
                amount=amount,
                sender_name=sender_name,
                sender_phone=sender_number,
                provider_txn_id=reference,
                direction="in",
                user_id=user.id,
                central_account_id=central.id,
                status="completed",
                created_at=datetime.utcnow(),
            )
            db.session.add(trx)
            db.session.commit()

            # --- Step 2e: Notify user ---
            try:
                send_sms(user.phone, f"Hi {user.phone}, your GoFood wallet has been credited ₦{amount:,.2f}")
            except Exception as e:
                print(f"SMS send failed: {e}")

            # --- Step 2f: Mark SMS as processed ---
            mark_sms_processed(sm, msg)

        inbox = sm.GetNextSMS()

def mark_sms_processed(sm, msg):
    """Delete or mark SMS as processed to prevent duplicate processing"""
    sm.DeleteSMS(Folder=0, Location=msg['Location'])

# --- Step 3: Parsing utilities ---
def extract_name_from_text(text):
    """
    Example heuristics to extract full name from bank credit alert SMS.
    Adapt this regex based on your bank's SMS format.
    """
    patterns = [
        r'from[:\s\-]+([A-Z][a-z]+ [A-Z][a-z]+)',  # e.g., "from John Doe"
        r'name[:\s\-]+([A-Z][a-z]+ [A-Z][a-z]+)',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return None

def extract_amount_from_text(text):
    """
    Extract amount from SMS using regex
    Example: "credited with NGN 5,000.00" or "₦5000"
    """
    match = re.search(r'[\d,]+(?:\.\d{2})?', text.replace("₦", "").replace("NGN", ""))
    if match:
        amount_str = match.group(0).replace(',', '')
        return float(amount_str)
    return None

def extract_reference_from_text(text):
    """
    Extract transaction reference from SMS if available
    """
    match = re.search(r'(TRX[0-9A-Za-z]+)', text)
    if match:
        return match.group(1)
    return None

# --- Step 4: Scheduler ---
# You can run this in background via Celery, APScheduler, or a cron job
def poll_sms_loop(interval=5):
    import time
    while True:
        try:
            process_incoming_sms()
        except Exception as e:
            print("Error processing SMS:", e)
        time.sleep(interval)
