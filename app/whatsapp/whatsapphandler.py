try:
    from app.merchants.Database.order import OrderSingle, OrderMultiple
    from app.merchants.Database. vendors_data_base import FoodItem
    from app.merchants.Database.vendors_data_base import Vendor, Profile_Merchant
    from app.database.wallet import Wallet
    from app.database.user_models import User as AppUser
    from app.database.central_account import CentralAccount
    from app.database.payment_models import FullName
except Exception as e:
    raise RuntimeError(
        "Replace app.database.* imports with your real models. "
        "This file expects OrderSingle, FoodItem, Wallet, Vendor, AppUser, CentralAccount, FullName."
    )

class ProcessedMessage(db.Model):
    __tablename__ = 'processed_messages'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(255), unique=True, index=True, nullable=False)
    processed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# -------------------------
# WhatsApp client
# -------------------------
class WhatsAppClient:
    def __init__(self, token: str, phone_number_id: str, api_version: str = DEFAULT_API_VERSION):
        if not token or not phone_number_id:
            raise ValueError("WHATSAPP_TOKEN and META_PHONE_NUMBER_ID must be set")
        self.token = token
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.base = f"https://graph.facebook.com/{self.api_version}"

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def send_text(self, to: str, message: str, timeout: int = 10):
        url = f"{self.base}/{self.phone_number_id}/messages"
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': message}
        }
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=timeout)
        try:
            resp.raise_for_status()
        except Exception:
            current_app.logger.exception("WhatsApp send failed: %s", resp.text)
            raise
        return resp.json()
def require_json(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return wrapper

def verify_whatsapp_signature(raw_body: bytes, signature_header: str, app_secret: str) -> bool:
    if not signature_header or not app_secret:
        return False
    prefix = 'sha256='
    if not signature_header.startswith(prefix):
        return False
    sig_hex = signature_header[len(prefix):]
    mac = hmac.new(app_secret.encode('utf-8'), msg=raw_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), sig_hex)

def make_funding_url(frontend_url: str, phone: str, full_name: str, user_id: int = None):
    """
    Build a secure-ish funding URL to send to user.
    Include phone and fullname as query params (url-encoded).
    You can enhance with signed token in production (HMAC or JWT).
    """
    q = {'phone': phone, 'full_name': full_name}
    if user_id:
        q['uid'] = str(user_id)
    return frontend_url.rstrip('/') + '/?' + urllib.parse.urlencode(q)

# -------------------------
# Blueprints
# -------------------------
whatsapp_bp = Blueprint('whatsapp_handler', __name__)
central_bp = Blueprint("central", __name__, url_prefix="/central")

# ----- central fund_wallet endpoint (POST) -----
@central_bp.route("/fund_wallet", methods=["POST"])
@require_json
def fund_wallet_instructions():
    """
    Provide instructions to user on how to fund their wallet via central account.
    POST JSON:
      { "phone": "...", "full_name": "..." }
    Returns JSON with central account details + narration.
    """
    data = request.get_json()
    phone = data.get("phone")
    full_name = data.get("full_name")
    if not phone or not full_name:
        return jsonify({"error": "Both phone and full_name are required"}), 400

    user = AppUser.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    fullname_record = FullName.query.filter_by(user_id=user.id).first()
    if not fullname_record:
        fullname_record = FullName(user_id=user.id, full_name=full_name)
        db.session.add(fullname_record)
        db.session.commit()

    central = CentralAccount.query.first()
    if not central:
        return jsonify({"error": "Central account not configured"}), 500

    instructions = {
        "message": "Use the following details to fund your GoFood wallet",
        "central_account_number": central.account_number,
        "bank_name": central.bank_name,
        "amount": "Enter amount you wish to fund",
        "narration": f"{full_name} | {phone}",
        "note": "Ensure you put your full name and phone in the narration/remark field so it can be auto-credited."
    }
    return jsonify(instructions), 200

# ----- webhook verify -----
@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_whatsapp():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    expected = current_app.config.get('WHATSAPP_VERIFY_TOKEN')
    if mode == 'subscribe' and token and expected and token == expected:
        return challenge, 200
    return 'Forbidden', 403

# ----- webhook receive (POST) -----
@whatsapp_bp.route('/webhook', methods=['POST'])
@limiter.limit(lambda: current_app.config.get('RATE_LIMIT', '300/hour'))
def whatsapp_webhook():
    raw_body = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('x-hub-signature-256')
    app_secret = current_app.config.get('WHATSAPP_APP_SECRET')
    if app_secret:
        if not verify_whatsapp_signature(raw_body, signature, app_secret):
            current_app.logger.warning("Invalid webhook signature")
            return 'Invalid signature', 401

    try:
        payload = request.get_json(force=True)
    except Exception:
        current_app.logger.exception("Invalid JSON on webhook")
        return 'Bad Request', 400

    current_app.logger.debug("Webhook payload: %s", json.dumps(payload)[:2000])

    # iterate entries/changes/messages
    entries = payload.get('entry', [])
    for entry in entries:
        for change in entry.get('changes', []):
            value = change.get('value', {})
            messages = value.get('messages', [])
            for message in messages:
                message_id = message.get('id')
                if not message_id:
                    continue
                # idempotency
                if ProcessedMessage.query.filter_by(message_id=message_id).first():
                    current_app.logger.debug("Already processed %s", message_id)
                    continue
                pm = ProcessedMessage(message_id=message_id, processed_at=datetime.utcnow())
                db.session.add(pm)
                try:
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    current_app.logger.exception("Failed to mark processed message")
                    continue
                # process message
                try:
                    process_incoming_whatsapp_message(value, message)
                except Exception:
                    current_app.logger.exception("Error processing message %s", message_id)
    return '', 200
import json
from flask import current_app, session
from app.extensions import db
from app.database.user_models import user as AppUser, Wallet

def process_incoming_whatsapp_message(value: dict, message: dict):
    wa_from = message.get('from')
    wa_text = None

    if 'text' in message:
        wa_text = message['text'].get('body', '').strip()
    elif 'button' in message:
        wa_text = message['button'].get('text', '').strip()
    else:
        current_app.logger.info('Unsupported WA message type from %s', wa_from)
        return

    if not wa_text:
        return

    wa_client = WhatsAppClient(
        token=current_app.config['WHATSAPP_TOKEN'],
        phone_number_id=current_app.config['META_PHONE_NUMBER_ID'],
        api_version=current_app.config.get('WHATSAPP_API_VERSION', DEFAULT_API_VERSION)
    )

    text = wa_text.strip()

    # =========================================
    # 🧩 ORDER COMMAND (handles both formats)
    # =========================================
    if text.upper().startswith('ORDER '):
        try:
            payload = text[6:].strip()

            # 🧠 Try JSON format first
            try:
                order_data = json.loads(payload)
                vendor_name = order_data["vendor_name"]
                items = order_data["items"]

            except json.JSONDecodeError:
                # 🧠 Fallback to text format: "Vendor" | "Item":qty, ...
                if '|' not in payload:
                    wa_client.send_text(
                        wa_from,
                        'Usage:\n1️⃣ ORDER {"vendor_name": "MamaPut", "items": [{"food_name": "Rice", "quantity": 2}]}\n'
                        '2️⃣ ORDER "MamaPut" | "Rice":1,"Beans":2'
                    )
                    return

                vendor_part, items_part = payload.split('|', 1)
                vendor_name = vendor_part.strip().strip('"')
                raw_items = [i.strip() for i in items_part.split(',') if i.strip()]
                items = []
                for r in raw_items:
                    if ':' in r:
                        nm, q = r.split(':', 1)
                        items.append({'food_name': nm.strip().strip('"'), 'quantity': int(q)})
                    else:
                        items.append({'food_name': r.strip().strip('"'), 'quantity': 1})

            # 🧱 Find or create user
            user = AppUser.query.filter_by(phone=wa_from).first()
            if not user:
                user = AppUser(phone=wa_from)
                db.session.add(user)
                db.session.commit()
                w = Wallet(user_id=user.id, balance='0.00')
                db.session.add(w)
                db.session.commit()

            # 🧰 Create fake request to trigger order logic
            fake_req = {'vendor_name': vendor_name, 'items': items}
            with current_app.test_request_context(json=fake_req):
                session['user_id'] = user.id
                _attempt_place_order_and_handle_response(user, wa_client)

        except Exception as e:
            current_app.logger.exception("Error processing ORDER command: %s", str(e))
            wa_client.send_text(wa_from, "❌ Internal error processing your order. Try again later.")
        return

    # =========================================
    # 💰 BALANCE COMMAND
    # =========================================
    if text.upper() == 'BALANCE':
        user = AppUser.query.filter_by(phone=wa_from).first()
        if not user:
            wa_client.send_text(wa_from, 'No account found. Please create an account first.')
            return
        wallet = Wallet.query.filter_by(user_id=user.id).first()
        wa_client.send_text(wa_from, f"Your wallet balance is: ₦{wallet.balance if wallet else '0.00'}")
        return

    # =========================================
    # 🆘 HELP COMMAND (default)
    # =========================================
    help_text = (
        "🤖 Welcome to GoFood Bot!\n\n"
        "To order:\n"
        "➡️ ORDER {\"vendor_name\": \"Iya Amala\", \"items\": [{\"food_name\": \"Ewedu\", \"quantity\": 2}]}\n"
        "or\n"
        "➡️ ORDER \"MamaPut\" | \"Rice\":1,\"Beans\":2\n\n"
        "Other Commands:\n"
        "💰 BALANCE - Check your wallet\n"
        "🆘 HELP - Show this message"
    )
    wa_client.send_text(wa_from, help_text)

def _attempt_place_order_and_handle_response(user: AppUser, wa_client: WhatsAppClient):
    """
    This helper reads the current Flask test_request_context json payload
    and tries to place the order (using whatsapp_order() logic). If insufficient funds,
    send funding instructions via WhatsApp including a funding URL.
    """
    try:
        resp = whatsapp_order()  # uses session['user_id']
        # parse response
        if isinstance(resp, tuple):
            body, status = resp[0].get_json(), resp[1]
        else:
            body = resp.get_json() if hasattr(resp, 'get_json') else {}
            status = resp.status_code if hasattr(resp, 'status_code') else 200
    finally:
        session.pop('user_id', None)

    wa_to = user.phone
    if status in (200, 201):
        # Success
        wa_client.send_text(wa_to, f"✅ Order placed. ID: {body.get('order_id')} Total: ₦{body.get('total_amount')}")
        return {'ok': True, 'body': body}
    else:
        # If insufficient balance, the whatsapp_order returns 400 with 'Insufficient balance'
        err = body.get('error') if isinstance(body, dict) else str(body)
        if isinstance(err, str) and 'Insufficient balance' in err:
            # Prepare funding instructions and URL
            data = request.get_json() or {}
            # try to read full_name from payload or FullName model
            full_name = data.get('full_name') or (FullName.query.filter_by(user_id=user.id).first().full_name if FullName.query.filter_by(user_id=user.id).first() else '')
            frontend_fund_url = current_app.config.get('FRONTEND_FUND_URL')
            funding_url = make_funding_url(frontend_fund_url or current_app.config.get('BASE_URL', ''), user.phone, full_name or '')
            # Get central account details
            central = CentralAccount.query.first()
            if central:
                instr_text = (
                    f"❗ Insufficient funds to place your order.\n\n"
                    f"• Fund your wallet using:\n"
                    f"Bank: {central.bank_name}\n"
                    f"Account: {central.account_number}\n"
                    f"• Narration: {full_name} | {user.phone}\n\n"
                    f"Quick link to fund wallet: {funding_url}\n\n"
                    f"After you pay, your wallet will be updated automatically."
                )
            else:
                instr_text = (
                    f"❗ Insufficient funds to place your order.\n\n"
                    f"Please top up your wallet. Quick link: {funding_url}"
                )
            try:
                wa_client.send_text(wa_to, instr_text)
            except Exception:
                current_app.logger.exception("Failed to send funding instructions to %s", wa_to)
            return {'ok': False, 'error': 'insufficient_balance'}
        else:
            # Generic failure
            try:
                wa_client.send_text(wa_to, f"❌ Failed to place order: {err}")
            except Exception:
                current_app.logger.exception("Failed to send error text to %s", wa_to)
            return {'ok': False, 'error': 'other', 'detail': err}

# ----- main order endpoint (same logic but callable directly) -----
@whatsapp_bp.route('/order', methods=['POST'])
@require_json
def whatsapp_order():
    """
    Places an order on behalf of the currently authenticated user (session['user_id'] required).
    This endpoint is re-used by the WA inbound handler.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not authenticated (session required)'}), 401

    payload = request.get_json()
    vendor_name = payload.get('vendor_name')
    items_data = payload.get('items', [])

    if not (vendor_name and isinstance(items_data, list) and items_data):
        return jsonify({'error': 'Missing vendor_name or items'}), 400

    vendor = Vendor.query.filter_by(name=vendor_name).first()
    if not vendor:
        return jsonify({'error': f"Vendor '{vendor_name}' not found"}), 404

    food_names = [it.get('food_name') for it in items_data if it.get('food_name')]
    if not food_names:
        return jsonify({'error': 'No valid food names provided'}), 400

    food_items = FoodItem.query.filter(
        FoodItem.name.in_(food_names),
        FoodItem.vendor_id == vendor.id,
        FoodItem.is_available == True
    ).all()
    if not food_items:
        return jsonify({'error': 'No available items found for this vendor'}), 404

    total_amount = Decimal('0.00')
    order_details = []
    for it in items_data:
        name = it.get('food_name')
        if not name:
            continue
        food = next((f for f in food_items if f.name == name), None)
        if not food:
            continue
        qty = int(it.get('quantity', 1))
        try:
            price = Decimal(str(food.price))
        except (InvalidOperation, TypeError):
            price = Decimal('0.00')
        subtotal = price * qty
        total_amount += subtotal
        order_details.append({
            'food_id': food.id,
            'name': food.name,
            'price': str(price),
            'quantity': qty,
            'subtotal': str(subtotal)
        })

    if not order_details:
        return jsonify({'error': 'None of the requested items are available.'}), 400

    # Atomic debit + order create
    try:
        wallet = Wallet.query.filter_by(user_id=user_id).with_for_update().first()
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404
        if Decimal(str(wallet.balance)) < total_amount:
            return jsonify({
                'error': 'Insufficient balance',
                'wallet_balance': str(wallet.balance),
                'total_amount': str(total_amount)
            }), 400

        # Perform debit and create order
        wallet.balance = str(Decimal(str(wallet.balance)) - total_amount)
        db.session.add(wallet)

        order = OrderSingle(
            user_id=user_id,
            item_data=order_details,
            total=str(total_amount),
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to place order: %s", str(e))
        return jsonify({'error': 'Payment failed', 'details': str(e)}), 500

    return jsonify({
        'message': 'Order placed successfully',
        'order_id': order.id,
        'total_amount': str(total_amount),
        'remaining_balance': str(wallet.balance),
        'items': order_details
    }), 201

import re
import json

def parse_order_json(order_text: str):
    """
    Extract JSON structure from WhatsApp order text.
    Expected format:
    ORDER {
      "vendor": "Iya Amala",
      "items": [
        {"food_name": "Ewedu", "quantity": 2},
        {"food_name": "Amala", "quantity": 1}
      ]
    }
    """
    try:
        # Extract JSON part after 'ORDER'
        json_part = order_text.strip()[6:].strip()
        data = json.loads(json_part)

        # Validate structure
        vendor = data.get("vendor")
        items = data.get("items")
        if not vendor or not isinstance(items, list):
            raise ValueError("Missing or invalid vendor/items")

        # Ensure each item has food_name and quantity
        for it in items:
            if "food_name" not in it:
                raise ValueError("Each item must have a food_name field")
            if "quantity" not in it:
                it["quantity"] = 1  # default to 1

        return {"vendor_name": vendor, "items": items}
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format. Make sure it’s valid JSON.")
    except Exception as e:
        raise ValueError(str(e))

