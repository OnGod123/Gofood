import json
from datetime import datetime
from flask import current_app
from flask_socketio import join_room, leave_room, emit
from app.extensions import socketio, r, db
from app.merchant.Database.delivery import Delivery
from app.merchant.Database import BargainMessage as BargainMessageModel  # adjust if different path
from app.utils import verify_jwt_socket  # earlier helper
from app.database.user_models import User

# Redis key patterns
REDIS_BARGAIN_LIST_KEY = "bargain:messages:{delivery_id}"     # list of json messages (latest at tail)
REDIS_BARGAIN_LOCK = "bargain:lock:{delivery_id}"
REDIS_BARGAIN_FEE_KEY = "bargain:fee:{delivery_id}"          # latest fee (float or string)

# Maximum history to keep in redis (for performance)
MAX_HISTORY = 500


def _save_message_redis(delivery_id: int, msg: dict):
    key = REDIS_BARGAIN_LIST_KEY.format(delivery_id=delivery_id)
    r.rpush(key, json.dumps(msg))
    # trim to keep list bounded
    r.ltrim(key, -MAX_HISTORY, -1)


def _get_history_redis(delivery_id: int, limit: int = 100):
    key = REDIS_BARGAIN_LIST_KEY.format(delivery_id=delivery_id)
    vals = r.lrange(key, -limit, -1) or []
    return [json.loads(v) for v in vals]


def _save_message_db(order_id: str, sender_id: int, recipient_id: int, message: str, seq_id: int):
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
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Failed saving bargain message to DB")
        return None
    return bm


@socketio.on("connect")
def on_connect(auth):
    """
    When a client connects, they should pass token either in query string as ?token=...,
    or in the connect 'auth' payload (socket.io v3+ supports auth payload).
    We'll validate that token and store user object in session (flask-socketio).
    """
    token = None
    # preferred location: auth payload
    try:
        token = auth.get("token") if auth else None
    except Exception:
        token = None

    if not token:
        # fallback to query string
        token = current_app.socketio.server.environ.get(request.sid, {}).get("QUERY_STRING")
        # not ideal; in many deployments token will be set in auth payload

    user = None
    if token:
        user = verify_jwt_socket(token)
    if not user:
        # reject connection
        return False  # disconnects client

    # we can set user on the socket session
    # flask-socketio's 'session' is separate from flask.session; use `flask_socketio` session if needed
    # but for simplicity, we store small info in server-side 'r' if necessary
    emit("connected", {"message": "authenticated"})


@socketio.on("join_bargain")
def on_join_bargain(data):
    """
    data: { "delivery_id": <int>, "token": <jwt optional if not passed in connect> }
    """
    token = data.get("token")
    delivery_id = data.get("delivery_id")
    if token:
        user = verify_jwt_socket(token)
    else:
        # try to use verification again (some clients connect without auth)
        user = None
    if not user:
        emit("error", {"error": "authentication required"})
        return

    # optional: check delivery belongs to user or vendor is allowed
    delivery = db.session.query(Delivery).get(delivery_id)
    if not delivery:
        emit("error", {"error": "delivery not found"})
        return

    room = f"delivery:{delivery_id}"
    join_room(room)

    # send last history
    history = _get_history_redis(delivery_id, limit=200)
    emit("bargain_history", {"history": history}, room=request.sid)


@socketio.on("leave_bargain")
def on_leave_bargain(data):
    delivery_id = data.get("delivery_id")
    room = f"delivery:{delivery_id}"
    leave_room(room)
    emit("left", {"delivery_id": delivery_id})


@socketio.on("offer_fee")
def on_offer_fee(data):
    """
    data: { "delivery_id": int, "fee": float, "message": str (optional), "token": <jwt optional> }
    """
    token = data.get("token")
    delivery_id = data.get("delivery_id")
    fee = data.get("fee")
    message = data.get("message", "")

    if token:
        user = verify_jwt_socket(token)
    else:
        user = None

    if not user:
        emit("error", {"error": "authentication required"})
        return

    # Basic validation
    try:
        fee = float(fee)
    except Exception:
        emit("error", {"error": "invalid fee"})
        return

    # store latest fee in redis
    fee_key = REDIS_BARGAIN_FEE_KEY.format(delivery_id=delivery_id)
    r.set(fee_key, json.dumps({"fee": fee, "by_user": user.id, "ts": datetime.utcnow().isoformat()}))

    # message payload to broadcast
    payload = {
        "delivery_id": delivery_id,
        "new_fee": fee,
        "by_user": {"id": user.id, "name": getattr(user, "name", "")},
        "message": message,
        "ts": datetime.utcnow().isoformat()
    }

    # Save to redis history
    _save_message_redis(delivery_id, {"type": "fee_offer", **payload})

    # Persist to DB (sequence id found from redis length)
    seq = r.llen(REDIS_BARGAIN_LIST_KEY.format(delivery_id=delivery_id))
    try:
        _save_message_db(str(delivery_id), user.id, None, f"Fee offer: {fee} {message}", seq)
    except Exception:
        # DB save failure should not block broadcast
        current_app.logger.exception("failed to persist fee offer")

    # Broadcast to room
    room = f"delivery:{delivery_id}"
    emit("fee_update", payload, room=room)


@socketio.on("send_message")
def on_send_message(data):
    """
    data: { "delivery_id": int, "message": str, "recipient_id": int (optional), "token": <jwt optional> }
    """
    token = data.get("token")
    delivery_id = data.get("delivery_id")
    message = data.get("message", "").strip()
    recipient_id = data.get("recipient_id")

    if token:
        user = verify_jwt_socket(token)
    else:
        user = None

    if not user:
        emit("error", {"error": "authentication required"})
        return

    if not message:
        emit("error", {"error": "empty message"})
        return

    payload = {
        "type": "chat_message",
        "delivery_id": delivery_id,
        "message": message,
        "sender": {"id": user.id, "name": getattr(user, "name", None)},
        "recipient_id": recipient_id,
        "ts": datetime.utcnow().isoformat(),
    }

    # Save to redis chat list & persist to DB
    _save_message_redis(delivery_id, payload)

    seq = r.llen(REDIS_BARGAIN_LIST_KEY.format(delivery_id=delivery_id))
    try:
        _save_message_db(str(delivery_id), user.id, recipient_id or 0, message, seq)
    except Exception:
        current_app.logger.exception("Failed to save chat message to DB")

    room = f"delivery:{delivery_id}"
    emit("chat_message", payload, room=room)


# Optional: a simple namespace for HTTP to get history quickly
# You can implement an HTTP route to expose history (cached from Redis)

