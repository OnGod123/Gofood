

from flask_socketio import emit, join_room
from app.extensions import socketio
from app.auth.jwt_utils import decode_jwt  # your JWT decoder

@socketio.on("connect", namespace="/vendor")
def vendor_connect(auth=None):
    """
    Authenticate vendor on connect.
    Join their vendor rooms automatically.
    """
    token = auth.get("token") if auth else None
    if not token:
        return False  # reject connection

    payload = decode_jwt(token)
    if not payload:
        return False

    vendor_id = payload.get("sub")
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return False

    # Use vendor's name to create room
    room_id = get_vendor_room(vendor.user_id, vendor.name)
    join_room(room_id)

    emit("connected", {"message": "connected to vendor room", "room": room_id})



def get_vendor_room(user_id: int, vendor_name: str) -> str:
    """
    Generate a deterministic Socket.IO room ID for a vendor related to a user.
    """
    vendor = Vendor.query.filter_by(user_id=user_id, name=vendor_name).first()
    if not vendor:
        # fallback: just use vendor_name
        return f"vendor_{vendor_name.lower().replace(' ', '_')}"
    return f"vendor_{vendor.id}"

