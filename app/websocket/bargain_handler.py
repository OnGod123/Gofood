import json
from datetime import datetime
from typing import Optional
from flask import current_app, request
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio, r, db
from app.auth.jwt_utils import decode_jwt  # your JWT resolver
from app.models import User, Vendor

# Redis chat constants
REDIS_CHAT_LIST_KEY = "chat:messages:{room_id}"
MAX_CHAT_HISTORY = 500
CHAT_TTL = 24 * 3600  # 24h

# ----- Utilities -----
def make_room_id(user1: str, user2: str) -> str:
    """Deterministic room id for two users."""
    return "_".join(sorted([str(user1), str(user2)]))

def get_user_from_token(token: str):
    """Resolve JWT → Redis cache → DB."""
    if not token:
        return None
    payload = decode_jwt(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    user_type = payload.get("role", "user")
    if not user_id:
        return None

    # Try Redis cache
    cache_key = f"user:session:{user_id}"
    val = r.get(cache_key)
    if val:
        try:
            return json.loads(val)
        except Exception:
            pass

    # Load from DB
    model = Vendor if user_type == "vendor" else User
    u = db.session.get(model, user_id)
    if not u:
        return None
    user = {"id": u.id, "name": getattr(u, "name", ""), "type": user_type}
    r.setex(cache_key, 3600, json.dumps(user))  # cache 1h
    return user

def save_message_redis(room_id: str, msg: dict):
    """Append a message to Redis list for this room."""
    key = REDIS_CHAT_LIST_KEY.format(room_id=room_id)
    try:
        r.rpush(key, json.dumps(msg))
        r.ltrim(key, -MAX_CHAT_HISTORY, -1)
        r.expire(key, CHAT_TTL)
    except Exception:
        current_app.logger.exception(f"Failed saving message for room {room_id}")

def get_message_history(room_id: str, limit: int = 50):
    """Fetch last N messages for a room."""
    key = REDIS_CHAT_LIST_KEY.format(room_id=room_id)
    try:
        vals = r.lrange(key, -limit, -1)
        return [json.loads(v) for v in vals]
    except Exception:
        return []

# ----- SocketIO Handlers -----
@socketio.on("connect", namespace="/bargain")
def handle_connect(auth=None):
    """Authenticate socket using JWT from payload or query string."""
    token = None
    if auth:
        token = auth.get("token")
    if not token:
        token = request.args.get("token")
    user = get_user_from_token(token)
    if not user:
        return False  # reject connection
    emit("connected", {"message": "authenticated", "user": user}, room=request.sid)

@socketio.on("join_room", namespace="/bargain")
def on_join(data):
    """
    Join a room.
    For 1:1: data={"partner": <user_id>}
    For group: data={"room_id": <room_id>}
    """
    token = data.get("token")
    user = get_user_from_token(token)
    if not user:
        emit("error", {"error": "auth required"}, room=request.sid)
        return

    # Determine room
    partner = data.get("partner")
    room_id = data.get("room_id")
    if partner:
        room_id = make_room_id(str(user["id"]), str(partner))
    if not room_id:
        emit("error", {"error": "room_id required"}, room=request.sid)
        return

    join_room(room_id)
    # Send last 100 messages
    history = get_message_history(room_id, limit=100)
    emit("room_history", {"room_id": room_id, "history": history}, room=request.sid)
    emit("joined", {"room_id": room_id, "user": user}, room=request.sid)

@socketio.on("leave_room", namespace="/bargain")
def on_leave(data):
    room_id = data.get("room_id")
    if not room_id:
        emit("error", {"error": "room_id required"}, room=request.sid)
        return
    leave_room(room_id)
    emit("left", {"room_id": room_id}, room=request.sid)

@socketio.on("send_message", namespace="/bargain")
def on_send_message(data):
    """
    Send a chat message.
    data={"message": <str>, "room_id": <str>, "token": <jwt>, "recipient_id": <optional>}
    """
    token = data.get("token")
    message = (data.get("message") or "").strip()
    room_id = data.get("room_id")
    recipient_id = data.get("recipient_id")

    user = get_user_from_token(token)
    if not user or not message or not room_id:
        emit("error", {"error": "invalid payload"}, room=request.sid)
        return

    payload = {
        "type": "chat_message",
        "room_id": room_id,
        "message": message,
        "sender": user,
        "recipient_id": recipient_id,
        "ts": datetime.utcnow().isoformat()
    }

    # Save & publish
    save_message_redis(room_id, payload)
    try:
        r.publish(f"room:{room_id}", json.dumps(payload))
    except Exception:
        current_app.logger.exception("failed to publish message")

    emit("chat_message", payload, room=room_id)

@socketio.on("offer_fee", namespace="/bargain")
def on_offer_fee(data):
    """Optional: same as send_message but for fee offers in group delivery rooms."""
    token = data.get("token")
    user = get_user_from_token(token)
    if not user:
        emit("error", {"error": "auth required"}, room=request.sid)
        return

    room_id = data.get("room_id")
    fee = data.get("fee")
    msg = data.get("message", "")
    if not room_id or fee is None:
        emit("error", {"error": "room_id & fee required"}, room=request.sid)
        return

    payload = {
        "type": "fee_offer",
        "room_id": room_id,
        "fee": float(fee),
        "message": msg,
        "by_user": user,
        "ts": datetime.utcnow().isoformat()
    }

    save_message_redis(room_id, payload)
    try:
        r.publish(f"room:{room_id}", json.dumps(payload))
    except Exception:
        current_app.logger.exception("failed to publish fee offer")
    emit("fee_update", payload, room=room_id)

