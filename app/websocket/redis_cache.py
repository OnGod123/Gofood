import json
from app.extensions import r, db
from app.models import User, Vendor
from app.auth.jwt_utils import decode_jwt

CACHE_KEY = "user:session:{user_id}"
CACHE_EXP = 3600  # 1 hour cache TTL


def get_user_from_cache(user_id):
    """Get user from Redis cache if available."""
    key = CACHE_KEY.format(user_id=user_id)
    val = r.get(key)
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return None


def set_user_in_cache(user):
    """Save user info to Redis cache."""
    key = CACHE_KEY.format(user_id=user["id"])
    r.setex(key, CACHE_EXP, json.dumps(user))


def load_user_from_db(user_id, user_type="user"):
    """Load from DB depending on type."""
    model = Vendor if user_type == "vendor" else User
    u = db.session.get(model, user_id)
    if not u:
        return None
    return {"id": u.id, "name": u.name, "email": u.email, "type": user_type}


def get_user_from_token(token):
    """
    Universal user resolver for JWT → Redis → DB.
    Use this inside WebSocket handlers.
    """
    payload = decode_jwt(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    user_type = payload.get("role", "user")

    # Try cache first
    user = get_user_from_cache(user_id)
    if user:
        return user

    # Otherwise load from DB
    user = load_user_from_db(user_id, user_type)
    if user:
        set_user_in_cache(user)
    return user
def _save_chat_redis(room_id: str, msg: dict):
    key = REDIS_CHAT_LIST_KEY.format(room_id=room_id)
    try:
        # push message
        r.rpush(key, json.dumps(msg))
        # keep list bounded
        r.ltrim(key, -MAX_CHAT_HISTORY, -1)
        # reset TTL so active rooms stay alive 24h after last activity
        r.expire(key, CHAT_TTL)
        # also touch meta key TTL if exists
        meta_key = REDIS_CHAT_META_KEY.format(room_id=room_id)
        try:
            r.expire(meta_key, CHAT_TTL)
        except Exception:
            # meta expiry failure should not break message save
            pass
    except Exception:
        current_app.logger.exception("failed to push chat message to redis")

