from flask import Blueprint, jsonify, request
from app.extensions import db
from app.database.wallet import Wallet, Transaction
from app.utils.jwt_utils import verify_jwt
import uuid

wallet_bp = Blueprint("wallet_bp", __name__, url_prefix="/wallet")

@wallet_bp.route("/balance", methods=["GET"])
@verify_jwt
def get_balance(user):
    wallet = Wallet.query.filter_by(user_id=user.id).first()
    return jsonify({"balance": wallet.balance if wallet else 0})

@wallet_bp.route("/transfer", methods=["POST"])
@verify_jwt
def transfer_funds(user):
    data = request.json
    vendor_id = data.get("vendor_id")
    amount = float(data.get("amount"))
    
    wallet = Wallet.query.filter_by(user_id=user.id).first()
    if not wallet or wallet.balance < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    # ---------------------------------------------
    # 1. CALL PAYMENT PROCESSOR BEFORE RECORDING TXN
    # ---------------------------------------------
    try:
        provider = data.get("provider", "paystack")

        payout_result = process_vendor_payout(
            user_id=user.id,
            vendor_id=vendor_id,
            order_id=data.get("order_id", None),
            amount=amount,
            provider=provider
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # --------------------------------------------------
    # 2. YOUR ORIGINAL LOGIC (UNCHANGED)
    # --------------------------------------------------
    txn = Transaction(
        user_id=user.id,
        vendor_id=vendor_id,
        amount=amount,
        type="payout",
        reference=str(uuid.uuid4()),
        status="completed"
    )

    wallet.balance -= amount
    db.session.add(txn)
    db.session.commit()

    # --------------------------------------------------
    # 3. RETURN BOTH (YOUR RESPONSE + PAYMENT DETAILS)
    # --------------------------------------------------
    return jsonify({
        "status": "success",
        "txn_id": txn.reference,
        "payout": payout_result
    })


