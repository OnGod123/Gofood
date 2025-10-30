import json
from app.extensions import r
from app.extensions import socketio

def listen_vendor_status_changes():
    pubsub = r.pubsub()
    pubsub.subscribe("vendor_status_changes")
    for msg in pubsub.listen():
        if msg and msg.get("type") == "message":
            data = json.loads(msg["data"])
            vendor_id = data.get("vendor_id")
            # Optionally re-cache
            r.setex(f"vendor_status:{vendor_id}", 300, data.get("new_status"))
            # If you maintain any in-process structures, update them here
