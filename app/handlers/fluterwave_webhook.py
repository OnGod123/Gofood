# app/routes/webhook_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.extensions import db
from app.models import Wallet, PaymentTransaction, Transaction
from app.payments.factory import get_provider

webhook_bp = Blueprint("webhook", __name__, url_prefix="/webhook")

def verify_flutterwave_signature(req):
    # Flutterwave sends header 'verif-hash' that must match the secret you set in dashboard
    expected = current_app.config.get("FLW_WEBHOOK_SECRET")
    if not expected:
        # if no secret configured, skip verification (not recommended)
        current_app.logger.warning("FLW_WEBHOOK_SECRET not set — skipping signature verification")
        return True
    header = req.headers.get("verif-hash")
    if not header:
        current_app.logger.warning("Missing verif-hash header")
        return False
    return header == expected

@webhook_bp.route("/flutterwave", methods=["POST"])
def flutterwave_webhook():
    # Step 0: verify signature
    if not verify_flutterwave_signature(request):
        return jsonify({"error": "Invalid signature"}), 403

    payload = request.get_json(force=True)
    # Flutterwave sends event & data, e.g., payload['event'] and payload['data']
    data = payload.get("data") or payload
    # The transaction id is typically data['id'] and tx_ref is data['tx_ref']
    trans_id = data.get("id") or data.get("transaction_id")
    tx_ref = data.get("tx_ref") or data.get("reference")

    # Determine what to verify: prefer id, otherwise use tx_ref
    reference_for_verify = trans_id if trans_id is not None else tx_ref
    if not reference_for_verify:
        current_app.logger.error("No reference found in webhook payload")
        return jsonify({"error": "No reference found"}), 400

    provider = get_provider("flutterwave")
    try:
        result = provider.verify_payment(reference_for_verify)
    except Exception as e:
        current_app.logger.exception("Flutterwave verify failed")
        return jsonify({"error": "Verification failed", "details": str(e)}), 500

    # Must be successful before crediting
    if result.get("status") != "successful":
        current_app.logger.info("Flutterwave payment not successful: %s", result)
        return jsonify({"message": "Payment not successful", "status": result.get("status")}), 200

    # Find PaymentTransaction record by provider_txn_id or tx_ref
    txn = None
    if trans_id:
        txn = PaymentTransaction.query.filter_by(provider_txn_id=str(trans_id)).first()
    if not txn and tx_ref:
        txn = PaymentTransaction.query.filter(PaymentTransaction.metadata["tx_ref"].astext == tx_ref).first() \
              if hasattr(PaymentTransaction, "metadata") and PaymentTransaction.metadata is not None else None

    # Fallback try provider_txn_id == tx_ref
    if not txn:
        txn = PaymentTransaction.query.filter_by(provider_txn_id=str(tx_ref)).first()

    if not txn:
        # Optionally create a new PaymentTransaction record to represent an incoming deposit
        current_app.logger.warning("PaymentTransaction record not found for reference %s", reference_for_verify)
        return jsonify({"error": "Transaction record not found"}), 404

    # Idempotency check
    if txn.processed:
        return jsonify({"message": "Already processed"}), 200

    # Credit wallet (use DB transaction and locking to avoid races)
    wallet = Wallet.query.filter_by(user_id=txn.target_user_id).with_for_update().first()
    if not wallet:
        current_app.logger.error("Wallet not found for user %s", txn.target_user_id)
        return jsonify({"error": "Wallet not found"}), 404

    wallet.credit(result["amount"])
    txn.processed = True
    txn.processed_at = datetime.utcnow()

    log_tx = Transaction(
        user_id=txn.target_user_id,
        amount=result["amount"],
        type="funding",
        reference=str(reference_for_verify),
        status="success",
        created_at=datetime.utcnow()
    )

    db.session.add(wallet)
    db.session.add(txn)
    db.session.add(log_tx)
    db.session.commit()

    # Optionally notify user (WhatsApp/email) in a background job
    return jsonify({"message": "Wallet funded", "user_id": txn.target_user_id, "amount": result["amount"]}), 200

