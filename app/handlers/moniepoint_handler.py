# app/handlers/moniepoint.py
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


@monie_bp.route("/webhook/moniepoint", methods=["POST"])
def moniepoint_webhook():
    """
    Webhook endpoint Moniepoint will call when a payment is made to the central account.
    Expected payload (example, adapt to provider):
    {
      "tx_ref": "abc123",
      "amount": 2000,
      "currency": "NGN",
      "status": "SUCCESS",
      "narration": "Payment for topup",
      "payer_name": "John Doe",
      "provider_account": "0812345678",
      ...
    }
    """
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid payload"}), 400

    # TODO: validate signature using provider's shared secret
    # if not validate_moniepoint_signature(request): return 403

    provider_txn_id = payload.get("tx_ref") or payload.get("id") or payload.get("reference")
    amount = float(payload.get("amount", 0))
    status = payload.get("status", "").lower()
    payer_name = (payload.get("payer_name") or payload.get("narration") or "").strip()

    if status != "success" and status != "successful":
        # Ignore pending / failed for now
        current_app.logger.info("monie webhook non-success status: %s", status)
        return jsonify({"message": "ignored non-successful status"}), 200

    # idempotency: check if provider_txn_id processed
    existing = PaymentTransaction.query.filter_by(provider="moniepoint", provider_txn_id=provider_txn_id).first()
    if existing:
        current_app.logger.info("duplicate webhook received: %s", provider_txn_id)
        return jsonify({"message": "duplicate"}), 200

    # create transaction record (incoming to central account)
    central = get_central_account("moniepoint")
    pt = PaymentTransaction(
        provider="moniepoint",
        provider_txn_id=provider_txn_id,
        amount=amount,
        currency=payload.get("currency", "NGN"),
        direction="in",
        central_account_id=central.id,
        metadata=payload,
        processed=False,
        created_at=datetime.utcnow()
    )
    db.session.add(pt)

    # update central account balance
    central.balance = (central.balance or 0.0) + amount
    db.session.add(central)
    db.session.commit()

    # attempt to match payer_name with FullName table
    matched = None
    if payer_name:
        matched = FullName.query.filter(FullName.full_name.ilike(payer_name)).first()
        if not matched:
            # try fuzzy matching? For now exact-ish ilike
            matched = FullName.query.filter(FullName.full_name.ilike(f"%{payer_name}%")).first()

    if matched:
        # credit user's wallet immediately
        user = matched.user
        # get/create wallet
        wallet = Wallet.query.filter_by(user_id=user.id).first()
        if not wallet:
            wallet = Wallet(user_id=user.id, balance=0.0)
            db.session.add(wallet)

        wallet.credit(amount)
        db.session.add(wallet)

        # record distribution transaction
        dist = PaymentTransaction(
            provider="internal",
            provider_txn_id=f"dist:{provider_txn_id}:{user.id}",
            amount=amount,
            currency="NGN",
            direction="distribute",
            central_account_id=central.id,
            target_user_id=user.id,
            metadata={"source_provider_txn_id": provider_txn_id, "payer_name": payer_name},
            processed=True,
            created_at=datetime.utcnow(),
            processed_at=datetime.utcnow()
        )
        db.session.add(dist)

        # mark original tx processed
        pt.processed = True
        pt.processed_at = datetime.utcnow()
        db.session.commit()

        # Optionally publish to redis for frontends / reconciliation
        r.publish("payments", json.dumps({"event": "topup", "user_id": user.id, "amount": amount, "tx": pt.id}))

        return jsonify({"message": "credited user wallet", "user_id": user.id}), 200
    else:
        # not matched -> leave as central_account balance. mark txn for manual reconciliation.
        pt.processed = False
        db.session.commit()
        current_app.logger.warning("Unmatched incoming payment: %s, payer_name=%s", provider_txn_id, payer_name)
        # notify ops via pubsub or email
        r.publish("payments", json.dumps({"event": "unmatched_topup", "amount": amount, "payer_name": payer_name, "tx": pt.id}))
        return jsonify({"message": "received but not matched", "tx_id": pt.id}), 200

