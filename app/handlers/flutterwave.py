
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.extensions import db
from app.models import User, Wallet, PaymentTransaction
from app.payments.factory import get_provider

wallet_bp = Blueprint("wallet", __name__, url_prefix="/api")

@wallet_bp.route("/wallet/load", methods=["POST"])
def load_wallet():
    """
    Start a wallet funding flow.
    body: { "full_name": "...", "phone": "+234...", "amount": 5000.0, "provider": "flutterwave" }
    """
    data = request.get_json(force=True)
    full_name = data.get("full_name")
    phone = data.get("phone")
    amount = data.get("amount")
    provider_name = data.get("provider", current_app.config.get("DEFAULT_PAYMENT_PROVIDER", "flutterwave"))

    if not all([full_name, phone, amount]):
        return jsonify({"error": "full_name, phone, and amount required"}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # initialize provider
    try:
        provider = get_provider(provider_name)
        payment_info = provider.initialize_payment(user, float(amount))
    except Exception as e:
        current_app.logger.exception("Payment init failed")
        return jsonify({"error": "Payment initialization failed", "details": str(e)}), 500

    # Log payment transaction (authoritative ledger)
    txn = PaymentTransaction(
        provider=provider_name,
        provider_txn_id=payment_info.get("reference"),
        amount=float(amount),
        currency="NGN",
        direction="in",
        target_user_id=user.id,
        metadata={"full_name": full_name},
        processed=False,
        created_at=datetime.utcnow()
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({
        "message": "Payment initiated",
        "payment_link": payment_info.get("payment_link"),
        "reference": payment_info.get("reference"),
        "tx_ref": payment_info.get("tx_ref")
    }), 201

