from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.extensions import db
from app.database import Wallet, PaymentTransaction, Transaction
from app.payments.factory import get_provider

webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")

@webhook_bp.route("paystark/payment", methods=["POST"])
def payment_webhook():
    payload = request.get_json(force=True)
    provider_name = payload.get("provider", None) or current_app.config.get("DEFAULT_PAYMENT_PROVIDER", "paystack")
    reference = payload.get("reference") or payload.get("data", {}).get("reference")

    if not reference:
        return jsonify({"error": "Missing payment reference"}), 400

    try:
        provider = get_provider(provider_name)
        result = provider.verify_payment(reference)
    except Exception as e:
        current_app.logger.exception("Payment verification failed")
        return jsonify({"error": "Verification failed", "details": str(e)}), 500

    if result.get("status", "").lower() != "success":
        return jsonify({"error": "Payment not verified", "detail_status": result.get("status")}), 400

    txn = PaymentTransaction.query.filter_by(provider_txn_id=reference).first()
    if not txn:
        # Optionally: create a record if not found (depends on provider flow)
        current_app.logger.warning("PaymentTransaction not found for reference %s", reference)
        return jsonify({"error": "Transaction not found"}), 404

    if txn.processed:
        return jsonify({"message": "Already processed"}), 200

    wallet = Wallet.query.filter_by(user_id=txn.target_user_id).with_for_update().first()
    if not wallet:
        return jsonify({"error": "Wallet not found for user"}), 404

    wallet.credit(result["amount"])
    txn.processed = True
    txn.processed_at = datetime.utcnow()

    log_tx = Transaction(
        user_id=txn.target_user_id,
        amount=result["amount"],
        type="funding",
        reference=reference,
        status="success",
        created_at=datetime.utcnow()
    )

    session.add(wallet)
    session.add(txn)
    session.add(log_tx)
    session.commit()

    return jsonify({"message": "Wallet funded successfully", "user_id": txn.target_user_id, "amount": result["amount"]}), 200


from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.extensions import db
from app.models import User, Wallet, PaymentTransaction
from app.payments.factory import get_provider

wallet_bp = Blueprint("wallet", __name__, url_prefix="/api")

@wallet_bp.route("paystark/wallet/load", methods=["POST"])
def load_wallet():
    data = request.get_json(force=True)
    full_name = data.get("full_name")
    phone = data.get("phone")
    amount = data.get("amount")
    provider_name = data.get("provider", current_app.config.get("DEFAULT_PAYMENT_PROVIDER", "paystack"))

    if not all([full_name, phone, amount]):
        return jsonify({"error": "full_name, phone, and amount are required"}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        provider = get_provider(provider_name)
        payment_info = provider.initialize_payment(user, float(amount))
    except Exception as e:
        current_app.logger.exception("Payment init failed")
        return jsonify({"error": "Payment initialization failed", "details": str(e)}), 500

    txn = PaymentTransaction(
        provider=provider_name,
        provider_txn_id=payment_info.get("reference"),
        amount=float(amount),
        direction="in",
        target_user_id=user.id,
        metadata={"full_name": full_name},
        processed=False,
        created_at=datetime.utcnow()
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({
        "message": "Payment initiated successfully",
        "payment_link": payment_info.get("authorization_url"),
        "reference": payment_info.get("reference")
    }), 201
