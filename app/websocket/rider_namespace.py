from flask_socketio import Namespace, emit, join_room, leave_room
from flask import request, g
from datetime import datetime
from app.extensions import db
from app.database.rider_models import Rider
from app.database.user_models import User
from flask_jwt_extended import decode_token

GLOBAL_ROOM = "all_participants"

class RiderNamespace(Namespace):

    def on_connect(self):
        token = (
            request.headers.get("Authorization")
            or request.args.get("token")
            or (request.json.get("token") if request.json else None)
        )

        if not token:
            print("No token")
            return False

        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        try:
            decoded = decode_token(token)["sub"]
            client_id = decoded["id"]
        except Exception as e:
            print("Invalid token:", e)
            return False

        # NOW CHECK DATABASE TO KNOW ROLE
        rider = Rider.query.get(client_id)
        user = User.query.get(client_id)

        if rider:
            g.client_type = "rider"
            g.client_id = rider.id
        elif user:
            g.client_type = "user"
            g.client_id = user.id
        else:
            print("ID does not exist in User or Rider table")
            return False

        print(f"Connected: {g.client_type} {g.client_id}")

        join_room(GLOBAL_ROOM)

        emit("connected", {
            "message": "Connected",
            "type": g.client_type,
            "id": g.client_id,
            "room": GLOBAL_ROOM
        })

    def on_update_location(self, data):
        if g.client_type != "rider":
            emit("error", {"message": "Only riders can send location"})
            return

        lat = data.get("lat")
        lng = data.get("lng")
        address = data.get("address")

        if not all([lat, lng, address]):
            emit("error", {"message": "Incomplete location data"})
            return

        rider = Rider.query.get(g.client_id)
        if not rider:
            emit("error", {"message": "Rider not found"})
            return

        # Save location
        rider.current_lat = lat
        rider.current_lng = lng
        rider.current_address = address
        db.session.commit()

        # Get rider's user info
        user = User.query.get(rider.user_id)

        data_packet = {
            "rider_id": g.client_id,
            "rider_name": user.fullname if user else "Unknown",
            "position": {
                "lat": lat,
                "lng": lng,
                "address": address
            },
            "time": datetime.utcnow().isoformat() + "Z"
        }

        emit("location_update", data_packet, room=GLOBAL_ROOM)


