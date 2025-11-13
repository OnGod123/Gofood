from functools import wraps
from flask import request, jsonify, g
from app.database.user_models import User
from app.utils.jwt_utils import get_user_from_jwt

def token_required(f):
    """
    Flask route decorator to ensure that a valid JWT token is present.
    Attaches the user info to `g.user` for use in routes.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Extract user info from JWT
            user_info = get_user_from_jwt()
            # Attach to Flask `g` object for global access in the request
            g.user = user_info
        except PermissionError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)
    return decorated

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

