from flask import Blueprint, request, jsonify, g, current_app
from datetime import datetime, timedelta
from app.extensions import db, r, socketio
from app.database.vendor_models import Vendor
from app.database.vendor_status import VendorStatusLog
from app.utils.auth import verify_jwt_token  # your auth decorator that yields current_user
from app.utils.vendor_status import cache_vendor_status
import json

vendor_status_bp = Blueprint("vendor_status_bp", __name__)

# Rate limit settings
TOGGLE_LIMIT = 5           # max toggles
TOGGLE_WINDOW = 60 * 5     # seconds (5 minutes)

def rate_limited_toggle_key(vendor_id, user_id):
    return f"vendor_toggle:{vendor_id}:{user_id}"

@vendor_status_bp.route("/vendor/status", methods=["POST"])
@verify_jwt_token
def set_vendor_status(current_user):
    """
    Vendor toggles shop open/closed.
    Body: {"vendor_id": 12, "status": "open"} where status is "open" or "closed"
    """
    data = request.get_json() or {}
    vendor_id = data.get("vendor_id")
    new_status = (data.get("status") or "").lower()

    if new_status not in ("open", "closed"):
        return jsonify({"error": "Invalid status. Allowed: open, closed"}), 400

    # fetch vendor
    vendor = db.session.query(Vendor).get(vendor_id)
    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404

    # ensure current_user owns vendor
    if getattr(vendor, "user_id", None) != current_user.id:
        return jsonify({"error": "Forbidden: you can only toggle your own vendor"}), 403

    # rate limit toggles per vendor+user
    key = rate_limited_toggle_key(vendor_id, current_user.id)
    count = r.get(key)
    if count is None:
        r.setex(key, TOGGLE_WINDOW, 1)
    else:
        count = int(count)
        if count >= TOGGLE_LIMIT:
            return jsonify({"error": "Too many status changes. Try again later."}), 429
        else:
            r.incr(key)

    old_status = "open" if getattr(vendor, "is_open", getattr(vendor, "is_active", True)) else "closed"

    # update DB and log atomically
    try:
        vendor.is_open = True if new_status == "open" else False
        vendor.updated_at = datetime.utcnow()
        db.session.add(vendor)

        log = VendorStatusLog(
            vendor_id=vendor.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=current_user.id,
            changed_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Failed to set vendor status")
        return jsonify({"error": "Failed to change status", "details": str(e)}), 500

    # cache the new status and publish
    cache_vendor_status(vendor.id, new_status)

    # notify connected clients via socketio (room: vendor_<id>)
    payload = {"vendor_id": vendor.id, "new_status": new_status}
    try:
        # publish to websocket room; frontends should join vendor_{id} room
        socketio.emit("vendor_status_update", payload, room=f"vendor_{vendor.id}", namespace="/bargain")
    except Exception as e:
        current_app.logger.warning(f"SocketIO emit failed: {e}")

    # publish a Redis message (for other instances to pick up if they don't use socketio message_queue)
    r.publish("vendor_status_changes", json.dumps(payload))

    current_app.logger.info(f"Vendor {vendor.id} status changed from {old_status} to {new_status} by user {current_user.id}")

    return jsonify({"message": "Vendor status updated", "vendor_id": vendor.id, "new_status": new_status}), 200
