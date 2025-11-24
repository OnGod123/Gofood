import json
from flask import Blueprint, request, jsonify, current_app, render_template, url_for
from app.extensions import db, r
from app.database.payment_models import CentralAccount, PaymentTransaction, FullName
from app.database.models import Wallet, User, Vendor
from datetime import datetime

monie_bp = Blueprint("monie", __name__, template_folder="../../templates")

# Utility: load or create central account record
def get_central_account(provider="moniepoint"):
    acct = CentralAccount.query.filter_by(provider=provider).first()
    if not acct:
        acct = CentralAccount(provider=provider, account_number=current_app.config.get("CENTRAL_ACCOUNT_NUMBER", "000000"), bank_name=current_app.config.get("CENTRAL_ACCOUNT_BANK", "Moniepoint"))
        db.session.add(acct)
        db.session.commit()
    return acct

@monie_bp.route("/wallet/topup", methods=["GET"])
def topup_view():
    """
    View the instructions and the full name the user must use while transferring.
    We expect client to show their full bank name (FullName) — user must set it in profile.
    """
    # For server-side rendering: get current_user via jwt/session
    # But for now just render static instructions; client will handle token and call API.
    return render_template("wallet_topup.html")

@wallet_bp.route("/wallet/load", methods=["GET"])
def load_wallet_get():
    """
    Initialize a wallet payment via GET request.
    Example: /wallet/load?phone=08012345678&amount=5000&provider=monnify
    """
    phone = request.args.get("phone")
    amount = request.args.get("amount")
    provider_name = request.args.get("provider", "monnify")  # default to Monnify
    full_name = request.args.get("full_name", phone)

    if not phone or not amount:
        return jsonify({"error": "phone and amount are required"}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({"error": "amount must be a number"}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        provider = get_provider(provider_name)
        payment_info = provider.initialize_payment(user, amount)
    except Exception as e:
        return jsonify({"error": "Payment initialization failed", "details": str(e)}), 500

    # Log the transaction
    txn = PaymentTransaction(
        provider=provider_name,
        provider_txn_id=payment_info["reference"],
        amount=amount,
        direction="in",
        target_user_id=user.id,
        processed=False,
        created_at=datetime.utcnow()
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({
        "message": "Payment initialized via GET",
        "payment_link": payment_info["payment_link"],
        "reference": payment_info["reference"]
    }), 201


@monnify_bp.route("/api/monnify/payment-complete", methods=["POST"])
def monnify_payment_complete():
    """
    DIRECT FLOW:
      1. Frontend sends Monnify SDK response to backend
      2. Save incoming payment into central account
      3. Try to match user using customer name
      4. If matched → debit central & credit user wallet
      5. If NOT matched → leave money in central (manual reconciliation)
    """

    # -------------------------------------------
    # Read JSON payload
    # -------------------------------------------
    payload = request.get_json(force=True)
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    tx_ref = payload.get("transactionReference")
    amount = float(payload.get("amountPaid", 0))
    status = payload.get("paymentStatus", "").lower()
    customer_name = payload.get("customerName", "").strip()

    # -------------------------------------------
    # Only successful payments matter
    # -------------------------------------------
    if status != "paid":
        return jsonify({"message": "Ignored non-paid transaction"}), 200

    # -------------------------------------------
    # Prevent duplicates (idempotency)
    # -------------------------------------------
    exists = PaymentTransaction.query.filter_by(
        provider="monnify",
        provider_txn_id=tx_ref
    ).first()

    if exists:
        return jsonify({"message": "duplicate"}), 200

    central = get_central_account("monnify")

    incoming_tx = PaymentTransaction(
        provider="monnify",
        provider_txn_id=tx_ref,
        amount=amount,
        currency="NGN",
        direction="in",
        central_account_id=central.id,
        metadata=payload,
        processed=False,
        created_at=datetime.utcnow()
    )

    db.session.add(incoming_tx)

    # Update central balance
    central.balance = float(central.balance) + amount
    db.session.add(central)
    db.session.commit()

    matched = FullName.query.filter(
        FullName.full_name.ilike(f"%{customer_name}%")
    ).first()

    if not matched:
        # Unmatched → Leave money in central account
        incoming_tx.processed = False
        db.session.commit()

        # Notify admin
        r.publish("payments", json.dumps({
            "event": "unmatched_payment",
            "customer_name": customer_name,
            "amount": amount,
            "tx_id": incoming_tx.id
        }))

        return jsonify({
            "message": "Payment received but not matched",
            "tx_id": incoming_tx.id,
            "central_balance": central.balance
        }), 200

    user = matched.user
    wallet = Wallet.query.filter_by(user_id=user.id).first()
    if not wallet:
        wallet = Wallet(user_id=user.id, balance=0.0)
        db.session.add(wallet)

    wallet.credit(amount)
    db.session.add(wallet)

    dist_tx = PaymentTransaction(
        provider="internal",
        provider_txn_id=f"dist:{tx_ref}:{user.id}",
        amount=amount,
        currency="NGN",
        direction="distribute",
        central_account_id=central.id,
        target_user_id=user.id,
        metadata={"source_tx": tx_ref},
        processed=True,
        created_at=datetime.utcnow(),
        processed_at=datetime.utcnow()
    )
    db.session.add(dist_tx)

    # Mark incoming payment as processed
    incoming_tx.processed = True
    incoming_tx.processed_at = datetime.utcnow()

    # Deduct amount from central since it's now moved to user wallet
    central.balance = float(central.balance) - amount

    db.session.commit()

    r.publish("payments", json.dumps({
        "event": "wallet_topup",
        "user_id": user.id,
        "amount": amount,
        "wallet_balance": wallet.balance
    }))

    return jsonify({
        "message": "Wallet credited successfully",
        "user_id": user.id,
        "wallet_balance": wallet.balance

}), 200



