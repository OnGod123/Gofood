# app/utils/vendor_status.py
from functools import wraps
from flask import jsonify, g, request, current_app
from app.extensions import r, db, socketio
from app.database.vendor_models import Vendor  # adjust path
import json

VENDOR_STATUS_TTL = 300  # seconds

def get_cached_vendor_status(vendor_id):
    key = f"vendor_status:{vendor_id}"
    val = r.get(key)
    if val is None:
        return None
    # stored as "open" or "closed"
    return val.decode("utf-8")

def cache_vendor_status(vendor_id, status):
    key = f"vendor_status:{vendor_id}"
    r.setex(key, VENDOR_STATUS_TTL, status)
    # publish change for other processes
    r.publish("vendor_status_changes", json.dumps({"vendor_id": vendor_id, "status": status}))

def vendor_must_be_open(fn):
    """
    Use on order endpoints to ensure target vendor is open.
    Expects vendor_id to be present in JSON body or query params.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Try to find vendor_id from common places
        vendor_id = request.view_args.get("vendor_id") if request.view_args else None
        if not vendor_id:
            data = request.get_json(silent=True) or {}
            vendor_id = data.get("vendor_id") or request.args.get("vendor_id")

        if not vendor_id:
            return jsonify({"error": "vendor_id is required"}), 400

        # check cache first
        status = get_cached_vendor_status(vendor_id)
        if status is None:
            # fallback to DB
            vendor = db.session.query(Vendor).get(vendor_id)
            if not vendor:
                return jsonify({"error": "Vendor not found"}), 404
            status = "open" if getattr(vendor, "is_open", getattr(vendor, "is_active", True)) else "closed"
            cache_vendor_status(vendor_id, status)

        if status != "open":
            return jsonify({"error": "Vendor currently closed"}), 403

        return fn(*args, **kwargs)
    return wrapper

