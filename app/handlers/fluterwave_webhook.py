# app/routes/webhook_routes.py
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app.extensions import db
from app.models import Wallet, PaymentTransaction, Transaction
from app.payments.factory import get_provider

flutterwave = Blueprint("webhook", __name__, url_prefix="/webhook")

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

@flutterwave_bp.route("/webhook", methods=["POST"])
def flutterwave_webhook():
    """Handle Flutterwave webhook callback"""
    # Verify webhook authenticity
    if not verify_flutterwave_signature(request):
        current_app.logger.warning("Invalid Flutterwave webhook signature")
        return jsonify({"error": "Invalid signature"}), 400

    payload = request.get_json(force=True)
    reference = payload.get("data", {}).get("tx_ref")

    if not reference:
        return jsonify({"error": "Missing transaction reference"}), 400

    provider_name = "flutterwave"
    try:
        provider = get_provider(provider_name)
        result = provider.verify_payment(reference)
    except Exception as e:
        current_app.logger.exception("Payment verification failed")
        return jsonify({"error": "Verification failed", "details": str(e)}), 500

    if result.get("status", "").lower() != "success":
        return jsonify({"error": "Payment not verified", "detail_status": result.get("status")}), 400

    # Find PaymentTransaction
    txn = PaymentTransaction.query.filter_by(provider_txn_id=reference).first()
    if not txn:
        return jsonify({"error": "Transaction not found"}), 404

    if txn.processed:
        return jsonify({"message": "Transaction already processed"}), 200

    # Find Central Account (Moniepoint)
    central = CentralAccount.query.filter_by(provider="moniepoint").first()
    if not central:
        return jsonify({"error": "Central Moniepoint account not configured"}), 500

    # Deduct from central, credit user wallet
    wallet = Wallet.query.filter_by(user_id=txn.target_user_id).first()
    if not wallet:
        return jsonify({"error": "User wallet not found"}), 404

    try:
        amount = txn.amount
        if central.balance < amount:
            current_app.logger.warning("Central account insufficient balance")
            return jsonify({"error": "Central account insufficient balance"}), 400

        # Perform the debit/credit
        central.balance -= amount
        wallet.balance += amount
        txn.processed = True
        txn.updated_at = datetime.utcnow()

        # Record ledger transactions
        debit_txn = Transaction(
            wallet_id=None,  # system account
            amount=amount,
            type="debit",
            description=f"Debit from central ({central.provider}) for {wallet.user.full_name}",
            reference=f"CENTRAL-{reference}",
            created_at=datetime.utcnow(),
        )
        credit_txn = Transaction(
            wallet_id=wallet.id,
            amount=amount,
            type="credit",
            description=f"Credit from central ({central.provider}) via Flutterwave",
            reference=f"USER-{reference}",
            created_at=datetime.utcnow(),
        )

        db.session.add_all([debit_txn, credit_txn])
        db.session.commit()
        current_app.logger.info(f"Wallet funded successfully for {wallet.user.full_name}")

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Error processing Flutterwave webhook")
        return jsonify({"error": "Failed to process transaction", "details": str(e)}), 500

    return jsonify({
        "message": "Wallet funded successfully",
        "amount": amount,
        "wallet_balance": wallet.balance
    }), 200
