import uuid
import hmac
import hashlib
import requests

from functools import wraps
from flask import request, Blueprint, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.whatsapp.session import load_session, save_session, clear_session
from app.whatsapp.utils import format_summary
from app.orders.validator import validate_items
from app.services.order_service import build_order
from app.payments.wallet import try_wallet_pay
from app.handlers.single_central_pay import build_payment_link
from app.websocket.vendor_notify import notify_vendor_new_order
from app.delivery.create import create_delivery
from app.delivery.redirect import redirect_to_bargain
from app.ai.parsers import ai_parse_items, ai_parse_address
from app.database.models import User, Vendor
from app import ws



class WhatsAppClient:
    def __init__(self, token: str, phone_number_id: str, api_version: str):
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



whatsapp_bp = Blueprint("whatsapp_bp", __name__, url_prefix="/whatsapp")

MENU_TEXT = (
    "Welcome 👋\n"
    "1️⃣ Order food\n"
    "2️⃣ Load wallet\n"
    "3️⃣ Track delivery\n"
    "Reply with a number or type an option."
)



@whatsapp_bp.route('/webhook', methods=['GET'])
def verify_whatsapp():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    expected = current_app.config.get('WHATSAPP_VERIFY_TOKEN')

    if mode == 'subscribe' and token and expected and token == expected:
        return challenge, 200

    return 'Forbidden', 403



class WhatsAppFlow:
    def __init__(self, phone, text, sender: WhatsAppClient):
        self.phone = phone
        self.text = text
        self.whatsapp = sender
        self.session = load_session(phone)
        self.state = self.session.get("state", "MENU")

    def send(self, msg):
        self.whatsapp.send_text(self.phone, msg)

    # MAIN FLOW (FULLY UNTOUCHED)
    def run(self):
        phone = self.phone
        text = self.text
        session = self.session
        state = self.state

        if self.state == "MENU":
            cmd = text.lower()

            if cmd in ("1", "order", "order food"):
                session.update({"state": "ASK_VENDOR"})
                save_session(phone, session)
                self.send(
                    "➡️ *Enter vendor name*\n\n"
                    "Example:\n`Jamborine`\n`Ofada Spot`\n`Chicken Republic`"
                )
                return "", 200

            if cmd in ("2", "wallet", "load"):
                link = build_payment_link(phone)
                self.send(f"Click to fund your wallet:\n{link}")
                return "", 200

            if cmd in ("3", "track"):
                session.update({"state": "TRACK"})
                save_session(phone, session)
                self.send("➡️ *Send delivery ID to track:*")
                return "", 200

            self.send(MENU_TEXT)
            return "", 200

        if self.state == "TRACK":
            msg = redirect_to_bargain(text)
            self.send(str(msg))
            session["state"] = "MENU"
            save_session(phone, session)
            return "", 200

        if self.state == "ASK_VENDOR":
            vendor = Vendor.query.filter(Vendor.name.ilike(f"%{text}%")).first()

            if not vendor:
                self.send(
                    "❌ Vendor not found.\n\n"
                    "Please enter a valid vendor name.\n"
                    "Example: `Jamborine`"
                )
                return "", 200

            session.update({
                "state": "ASK_ITEMS",
                "vendor_id": vendor.id,
                "vendor_name": vendor.name
            })
            save_session(phone, session)

            self.send(
                "➡️ *Send your items and quantities*\n\n"
                "Examples:\n"
                "`Jamborine rice quantity 2`\n"
                "`fish pie quantity 3`\n"
                "`Jamborine rice quantity 2, fish 2 quantities`\n"
                "`shawarma 1, cola 2, burger 3`"
            )
            return "", 200

        if self.state == "ASK_ITEMS":
            items = ai_parse_items(text)
            valid, validated_items = validate_items(session["vendor_id"], items)

            if not valid:
                self.send(
                    "❌ Some items are not sold by this vendor.\n"
                    "Please check and resend.\n\n"
                    "Examples:\n"
                    "`Jamborine rice quantity 2`\n"
                    "`fish pie quantity 1`\n"
                    "`shawarma 2, cola 1`"
                )
                return "", 200

            session.update({
                "state": "ASK_ADDRESS",
                "items": validated_items
            })
            save_session(phone, session)

            self.send(
                "➡️ *Send delivery address*\n\n"
                "Example:\n"
                "`Bolivard Starett Off Nnewi`\n"
                "`No 14 Odenigbo Street, Enugu`\n"
                "`Hostel A room 5 UNIZIK`"
            )
            return "", 200

        if self.state == "ASK_ADDRESS":
            address = ai_parse_address(text)

            if not address or len(address) < 4:
                self.send("❌ Address too short. Send a full address:")
                return "", 200

            session["address"] = address
            session["total"] = sum(i["qty"] * i["price"] for i in session["items"])
            session["state"] = "CONFIRM"
            save_session(phone, session)

            summary = format_summary(session)
            self.send(
                f"{summary}\n\n➡️ *Reply YES to confirm your order.*"
            )
            return "", 200

        if self.state == "CONFIRM":
            if text.lower() not in ("yes", "y"):
                session["state"] = "MENU"
                save_session(phone, session)
                self.send("❌ Order cancelled.")
                return "", 200

            user = User.query.filter_by(whatsapp_phone=phone).first()
            if not user:
                user = User(id=str(uuid.uuid4()), whatsapp_phone=phone, wallet_balance=0)
                from app.database import db
                db.session.add(user)
                db.session.commit()

            order = build_order(
                user_id=user.id,
                vendor_id=session["vendor_id"],
                items=session["items"],
                address=session["address"],
                phone=phone
            )

            pay = try_wallet_pay(user.id, session["total"])

            if pay.get("status") != "OK":
                link = build_payment_link(phone)
                self.send(
                    "❌ Payment failed.\n"
                    "Fund your wallet:\n" + link
                )
                return "", 200

            notify_vendor_new_order(order)

            try:
                vendor_room = session.get("vendor_name") or f"vendor_{session.get('vendor_id')}"
                broadcast_payload = {
                    "order_id": getattr(order, "id", None),
                    "vendor_id": session.get("vendor_id"),
                    "vendor_name": session.get("vendor_name"),
                    "buyer_phone": phone,
                    "items": session.get("items"),
                    "total": session.get("total"),
                    "address": session.get("address"),
                    "created_at": str(getattr(order, "created_at", "")),
                }
                ws.emit("vendor_new_order_details", broadcast_payload, room=vendor_room)
            except Exception:
                pass

            delivery = create_delivery(order)
            redirect_to_bargain(delivery.id)

            self.send(
                "✅ *Order placed successfully!*\n"
                "A rider is being assigned now."
            )

            session["state"] = "MENU"
            save_session(phone, session)
            return "", 200

        session["state"] = "MENU"
        save_session(phone, session)
        self.send(MENU_TEXT)
        return "", 200



@whatsapp_bp.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    # --- RAW BODY FOR SIGNATURE CHECK ---
    raw_body = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256') or request.headers.get('x-hub-signature-256')
    app_secret = current_app.config.get('WHATSAPP_APP_SECRET')

    # --- VERIFY ---
    if app_secret:
        if not verify_whatsapp_signature(raw_body, signature, app_secret):
            current_app.logger.warning("Invalid webhook signature")
            return 'Invalid signature', 401

    # --- EXTRACT MESSAGE (UNCHANGED) ---
    payload = request.get_json(force=True)
    phone = payload.get("from")
    text = payload.get("text", {}).get("body", "").strip()

    if not phone:
        return "Missing phone", 400

    sender = WhatsAppClient(
        token=current_app.config["WHATSAPP_TOKEN"],
        phone_number_id=current_app.config["META_PHONE_NUMBER_ID"],
        api_version=current_app.config["META_API_VERSION"],
    )

    flow = WhatsAppFlow(phone, text, sender)
    return flow.run()

