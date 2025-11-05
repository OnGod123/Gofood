def make_room_id(user1: str, user2: str) -> str:
    """Create unique shared room id for any 2 users."""
    return "_".join(sorted([user1, user2]))


def save_message_redis(room_id: str, msg: dict):
    """Append a message to Redis list for this room."""
    key = REDIS_CHAT_LIST_KEY.format(room_id=room_id)
    r.rpush(key, json.dumps(msg))
    r.ltrim(key, -MAX_CHAT_HISTORY, -1)


def get_message_history(room_id: str, limit: int = 50):
    """Fetch last N messages for a room."""
    key = REDIS_CHAT_LIST_KEY.format(room_id=room_id)
    vals = r.lrange(key, -limit, -1)
    return [json.loads(v) for v in vals]
