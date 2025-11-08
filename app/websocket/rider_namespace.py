from flask_socketio import Namespace, emit, join_room, leave_room
from datetime import datetime
from app.extensions import db, r
from app.database.rider_models import Rider
from app.database.user_models import User

# Shared room name for all users and riders
GLOBAL_ROOM = "all_participants"

class RiderNamespace(Namespace):
    def on_connect(self):
        """Authenticate if needed, then join the global room."""
        join_room(GLOBAL_ROOM)
        emit("connected", {"message": "Connected to rider namespace", "room": GLOBAL_ROOM})

    def on_join(self, data):
        """
        Optional explicit join.
        Every user/rider is in the global room, but you can still track joins.
        """
        user_type = data.get("type", "user")  # "user" or "rider"
        user_id = data.get("id")
        if not user_id:
            emit("error", {"message": "id required"})
            return

        join_room(GLOBAL_ROOM)
        emit("joined", {"room": GLOBAL_ROOM, "user_type": user_type, "user_id": user_id}, room=GLOBAL_ROOM)

    def on_update_location(self, data):
        """
        Rider sends location; broadcast to all participants.
        """
        rider_id = data.get("rider_id")
        lat = data.get("lat")
        lng = data.get("lng")
        address = data.get("address")

        if not all([rider_id, lat, lng, address]):
            emit("error", {"message": "Incomplete data"})
            return

        # Save to DB
        rider = Rider.query.get(rider_id)
        if not rider:
            emit("error", {"message": "Rider not found"})
            return

        rider.current_lat = lat
        rider.current_lng = lng
        rider.current_address = address
        db.session.commit()

        # Fetch user info
        user = User.query.get(rider.user_id)
        data_packet = {
            "rider_name": user.fullname if user else "Unknown",
            "position": {"lat": lat, "lng": lng, "address": address},
            "time": datetime.utcnow().isoformat() + "Z"
        }

        # Broadcast to all in the global room
        emit("location_update", data_packet, room=GLOBAL_ROOM)

