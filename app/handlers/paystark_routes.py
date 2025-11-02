# app/routes/webhook_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.extensions import db
from app.models import Wallet, PaymentTransaction, Transaction
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

    # credit wallet
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

    db.session.add(wallet)
    db.session.add(txn)
    db.session.add(log_tx)
    db.session.commit()

    return jsonify({"message": "Wallet funded successfully", "user_id": txn.target_user_id, "amount": result["amount"]}), 200

