from flask import Blueprint, request, jsonify

wallet_bp = Blueprint("wallet_bp", __name__)

from app.handlers.payment_callbacks.monnify import handle_monnify_callback
from app.handlers.payment_callbacks.paystack import handle_paystack_callback
from app.handlers.payment_callbacks.flutterwave import handle_flutterwave_callback


@wallet_bp.route("/wallet/callback/<provider_name>", methods=["POST"])
def wallet_callback(provider_name):
    payload = request.get_json(force=True)

    if provider_name == "monnify":
        return handle_monnify_callback(payload)

    elif provider_name == "paystack":
        return handle_paystack_callback(payload)

    elif provider_name == "flutterwave":
        return handle_flutterwave_callback(payload)

    return jsonify({"error": "unsupported provider"}), 400

