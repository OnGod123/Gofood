from functools import wraps
from flask import request, jsonify, g
from app.models import User
from app.utils.jwt_tools import decode_token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({"message": "Token is invalid or expired"}), 401

        user = User.query.filter_by(id=payload['user_id']).first()
        if not user:
            return jsonify({"message": "User not found"}), 401

        g.current_user = user
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

