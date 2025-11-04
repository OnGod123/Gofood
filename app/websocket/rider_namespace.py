from flask_socketio import Namespace, emit, join_room
from datetime import datetime
from app.extensions import db
from app.database.rider_models import Rider
from app.database.user_models import User

class RiderNamespace(Namespace):
    def on_connect(self):
        emit("connected", {"message": "Rider socket connected"})

    def on_join(self, data):
        rider_id = data.get("rider_id")
        join_room(f"rider_{rider_id}")
        emit("joined", {"room": f"rider_{rider_id}"})

    def on_update_location(self, data):
        rider_id = data.get("rider_id")
        lat = data.get("lat")
        lng = data.get("lng")
        address = data.get("address")

        if not all([rider_id, lat, lng, address]):
            emit("error", {"message": "Incomplete data"})
            return

        rider = Rider.query.get(rider_id)
        if not rider:
            emit("error", {"message": "Rider not found"})
            return

        rider.current_lat = lat
        rider.current_lng = lng
        rider.current_address = address
        db.session.commit()

        user = User.query.get(rider.user_id)
        data_packet = {
            "rider_name": user.fullname if user else "Unknown",
            "position": address,
            "time": datetime.utcnow().isoformat() + "Z"
        }

        emit("location_update", data_packet, broadcast=True)

