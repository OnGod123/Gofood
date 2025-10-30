from flask_socketio import emit, join_room
from flask import request
from app.extensions import socketio, db, r
from app.merchant.database.notifications import BargainMessage
from app.utils.auth import verify_jwt_socket  # you’ll write this small helper

@socketio.on("connect", namespace="/bargain")
def handle_connect():
    token = request.args.get("token")
    user = verify_jwt_socket(token)
    if not user:
        return False  # reject connection

    order_id = request.args.get("order_id")
    join_room(f"order_{order_id}")
    print(f"User {user.id} connected to order {order_id}")

@socketio.on("bargain_message", namespace="/bargain")
def handle_bargain_message(data):
    user = verify_jwt_socket(request.args.get("token"))
    if not user:
        return

    order_id = data.get("order_id")
    message_text = data.get("body")
    metadata = data.get("metadata", {})
    recipient_id = data.get("recipient_id")
    sequence_id = data.get("sequence_id")

    msg = BargainMessage(
        order_id=order_id,
        sender_id=user.id,
        recipient_id=recipient_id,
        message=message_text,
        metadata=metadata,
        sequence_id=sequence_id,
    )
    db.session.add(msg)
    db.session.commit()

    # Publish to Redis (so other instances see it)
    r.publish(f"order_{order_id}", msg.to_dict())

    # Broadcast to all sockets in this order room
    emit("bargain_message", msg.to_dict(), room=f"order_{order_id}")

