from functools import wraps
from flask import request, jsonify, g
from app.database.user_models import User


def vendor_must_be_open(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        vendor_id = request.json.get('vendor_id')
        if not vendor_id:
            return jsonify({"message": "vendor_id required"}), 400

        from app.models import Vendor
        vendor = Vendor.query.get(vendor_id)
        if not vendor or not vendor.is_open:
            return jsonify({"message": "Vendor is closed"}), 403

        g.vendor = vendor
        return f(*args, **kwargs)
    return decorated

