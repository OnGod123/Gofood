"""
Bargain socket handlers for namespace '/bargain'.

Provides:
- connect (auth via connect payload or query string)
- join_bargain / leave_bargain (room join/leave, send history)
- offer_fee (store latest fee, push history, persist lightly, broadcast)
- send_message (chat message -> redis history, db persist, broadcast)

Usage:
Import this module somewhere in your app factory (so socketio handlers are registered)
e.g. `import app.websocket.bargain_socket  # noqa: F401`
"""
import json
from datetime import datetime
from typing import Optional

import jwt
from flask import current_app, request
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio, r, db

# Try to import BargainMessage model from likely locations; adjust if your project differs
try:
    from app.merchant.database.notifications import BargainMessage as BargainMessageModel
except Exception:
    try:
        from app.merchant.Database import BargainMessage as BargainMessageModel  # fallback path
    except Exception:
        BargainMessageModel = None  # DB persistence will be a no-op if not available

# Optional Delivery model check when joining
try:
    from app.merchant.Database.delivery import Delivery
except Exception:
    Delivery = None

# User model for JWT lookup
try:
    from app.database.user_models import User
except Exception:
    User = None

# Redis key patterns
REDIS_BARGAIN_LIST_KEY = "bargain:messages:{delivery_id}"     # list of json messages (latest at tail)
REDIS_BARGAIN_FEE_KEY = "bargain:fee:{delivery_id}"          # latest fee (json)
MAX_HISTORY = 500  # cap history kept in redis


def _get_jwt_secret() -> str:
    # Look for a JWT secret in config, fall back to Flask SECRET_KEY if needed
    return current_app.config.get("JWT_SECRET", current_app.config.get("SECRET_KEY", ""))


def verify_jwt_socket(token: Optional[str]):
    """
    Lightweight JWT verification helper for socket connections.
    Expects token string or "Bearer <token>".
    Returns a User object from DB (if User model is available) or a dict with 'id' when decoding succeeds.
    Returns None on failure.
    """
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1].strip()

    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
    except Exception:
        current_app.logger.debug("JWT decode failed for socket token", exc_info=True)
        return None

    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
    if not user_id:
        return None

    if User:
        try:
            user = db.session.query(User).get(int(user_id))
            return user
        except Exception:
            current_app.logger.exception("failed to load user for socket auth")
            return None

    # If no User model available, return a lightweight object
    return type("SocketUser", (), {"id": int(user_id)})()


def _save_message_redis(delivery_id: int, msg: dict):
    key = REDIS_BARGAIN_LIST_KEY.format(delivery_id=delivery_id)
    try:
        r.rpush(key, json.dumps(msg))
        # keep list bounded
        r.ltrim(key, -MAX_HISTORY, -1)
    except Exception:
        current_app.logger.exception("failed to push bargain message to redis")


def _get_history_redis(delivery_id: int, limit: int = 100):
    key = REDIS_BARGAIN_LIST_KEY.format(delivery_id=delivery_id)
    try:
        vals = r.lrange(key, -limit, -1) or []
        # lrange returns bytes in many clients; decode if needed
        res = []
        for v in vals:
            if isinstance(v, bytes):
                v = v.decode()
            try:
                res.append(json.loads(v))
            except Exception:
                # if stored as plain string
                res.append(v)
        return res
    except Exception:
        current_app.logger.exception("failed to get history from redis")
        return []


def _save_message_db(order_id: str, sender_id: int, recipient_id: Optional[int], message: str, seq_id: int):
    if not BargainMessageModel:
        # DB not available in this environment
        return None
    try:
        bm = BargainMessageModel(
            order_id=order_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=message,
            metadata=None,
            sequence_id=seq_id,
            created_at=datetime.utcnow()
        )
        db.session.add(bm)
        db.session.commit()
        return bm
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed saving bargain message to DB")
        return None


@socketio.on("connect", namespace="/bargain")
def handle_connect(auth=None):
    """
    Accepts token via `auth` payload (preferred) or query string `?token=...`.
    Returns False to reject connection if authentication fails.
    """
    token = None
    try:
        token = auth.get("token") if auth else None
    except Exception:
        token = None

    if not token:
        # fallback to query string
        token = request.args.get("token")

    user = verify_jwt_socket(token)
    if not user:
        current_app.logger.debug("socket connect rejected: auth failed")
        return False  # reject connection

    # Send acknowledgement
    emit("connected", {"message": "authenticated", "user_id": getattr(user, "id", None)}, room=request.sid)


@socketio.on("join_bargain", namespace="/bargain")
def on_join_bargain(data):
    """
    data: { "delivery_id": <int>, "token": <jwt optional if not passed in connect> }
    """
    token = data.get("token") if isinstance(data, dict) else None
    delivery_id = data.get("delivery_id") if isinstance(data, dict) else None

    if token:
        user = verify_jwt_socket(token)
    else:
        # try query-string token as fallback
        user = verify_jwt_socket(request.args.get("token"))

    if not user:
        emit("error", {"error": "authentication required"}, room=request.sid)
        return

    if not delivery_id:
        emit("error", {"error": "delivery_id required"}, room=request.sid)
        return

    # optional DB check: ensure delivery exists
    if Delivery:
        try:
            delivery = db.session.query(Delivery).get(int(delivery_id))
            if not delivery:
                emit("error", {"error": "delivery not found"}, room=request.sid)
                return
        except Exception:
            current_app.logger.exception("error checking delivery existence")

    room = f"delivery:{delivery_id}"
    join_room(room)

    # send last history to the joining socket only
    history = _get_history_redis(delivery_id, limit=200)
    emit("bargain_history", {"history": history}, room=request.sid)


@socketio.on("leave_bargain", namespace="/bargain")
def on_leave_bargain(data):
    delivery_id = data.get("delivery_id") if isinstance(data, dict) else None
    if not delivery_id:
        emit("error", {"error": "delivery_id required"}, room=request.sid)
        return
    room = f"delivery:{delivery_id}"
    leave_room(room)
    emit("left", {"delivery_id": delivery_id}, room=request.sid)


@socketio.on("offer_fee", namespace="/bargain")
def on_offer_fee(data):
    """
    data: { "delivery_id": int, "fee": float, "message": str (optional), "token": <jwt optional> }
    """
    token = data.get("token") if isinstance(data, dict) else None
    delivery_id = data.get("delivery_id") if isinstance(data, dict) else None
    fee = data.get("fee") if isinstance(data, dict) else None
    message = data.get("message", "") if isinstance(data, dict) else ""

    # try fallback token if not provided in payload
    if not token:
        token = request.args.get("token")

    user = verify_jwt_socket(token)
    if not user:
        emit("error", {"error": "authentication required"}, room=request.sid)
        return

    if delivery_id is None:
        emit("error", {"error": "delivery_id required"}, room=request.sid)
        return

    # validate fee
    try:
        fee = float(fee)
    except Exception:
        emit("error", {"error": "invalid fee"}, room=request.sid)
        return

    fee_key = REDIS_BARGAIN_FEE_KEY.format(delivery_id=delivery_id)
    fee_payload = {"fee": fee, "by_user": getattr(user, "id", None), "ts": datetime.utcnow().isoformat()}
    try:
        r.set(fee_key, json.dumps(fee_payload))
    except Exception:
        current_app.logger.exception("failed to set fee key in redis")

    payload = {
        "delivery_id": delivery_id,
        "new_fee": fee,
        "by_user": {"id": getattr(user, "id", None), "name": getattr(user, "name", "")},
        "message": message,
        "ts": datetime.utcnow().isoformat(),
        "type": "fee_offer",
    }

    # Save to redis history
    _save_message_redis(delivery_id, payload)

    # Persist to DB (non-blocking)
    seq = 0
    try:
        seq = r.llen(REDIS_BARGAIN_LIST_KEY.format(delivery_id=delivery_id)) or 0
    except Exception:
        current_app.logger.exception("failed to get sequence from redis len")

    try:
        _save_message_db(str(delivery_id), getattr(user, "id", None), None, f"Fee offer: {fee} {message}", seq)
    except Exception:
        current_app.logger.exception("failed to persist fee offer")

    # Publish to other instances, then broadcast locally
    try:
        r.publish(f"delivery:{delivery_id}", json.dumps(payload))
    except Exception:
        current_app.logger.exception("failed to publish fee update to redis")

    room = f"delivery:{delivery_id}"
    emit("fee_update", payload, room=room)


@socketio.on("send_message", namespace="/bargain")
def on_send_message(data):
    """
    data: { "delivery_id": int, "message": str, "recipient_id": int (optional), "token": <jwt optional> }
    """
    token = data.get("token") if isinstance(data, dict) else None
    delivery_id = data.get("delivery_id") if isinstance(data, dict) else None
    message = (data.get("message") or "").strip() if isinstance(data, dict) else ""
    recipient_id = data.get("recipient_id") if isinstance(data, dict) else None

    if not token:
        token = request.args.get("token")

    user = verify_jwt_socket(token)
    if not user:
        emit("error", {"error": "authentication required"}, room=request.sid)
        return

    if not delivery_id:
        emit("error", {"error": "delivery_id required"}, room=request.sid)
        return

    if not message:
        emit("error", {"error": "empty message"}, room=request.sid)
        return

    payload = {
        "type": "chat_message",
        "delivery_id": delivery_id,
        "message": message,
        "sender": {"id": getattr(user, "id", None), "name": getattr(user, "name", None)},
        "recipient_id": recipient_id,
        "ts": datetime.utcnow().isoformat(),
    }

    # Save to redis chat list & persist to DB
    _save_message_redis(delivery_id, payload)

    seq = 0
    try:
        seq = r.llen(REDIS_BARGAIN_LIST_KEY.format(delivery_id=delivery_id)) or 0
    except Exception:
        current_app.logger.exception("failed to read sequence length")

    try:
        _save_message_db(str(delivery_id), getattr(user, "id", None), recipient_id or 0, message, seq)
    except Exception:
        current_app.logger.exception("Failed to save chat message to DB")

    # publish to other instances (so they can also forward to their connected sockets)
    try:
        r.publish(f"delivery:{delivery_id}", json.dumps(payload))
    except Exception:
        current_app.logger.exception("failed to publish chat message to redis")

    room = f"delivery:{delivery_id}"
    emit("chat_message", payload, room=room)
