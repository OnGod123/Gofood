@wallet_bp.route("/wallet/callback/<provider_name>", methods=["POST"])
def wallet_callback(provider_name):
    payload = request.get_json(force=True)

    if provider_name == "monnify":
        return handle_monnify_callback(payload)
    elif provider_name == "paystack":
        return handle_paystack_callback(payload)
    elif provider_name == "flutterwave":
        return handle_flutterwave_callback(payload)
    else:
        return jsonify({"error": "unsupported provider"}), 400

    return jsonify({"status": "success"}), 200

