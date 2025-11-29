import uuid
from app.database import db
from app.database.models import Wallet, Vendor, Transaction
from app.payments.payout import process_vendor_payout


def pay_vendor_by_name(*, user_id: int, vendor_name: str, amount: float, order_id=None, provider="paystack"):
    vendor = Vendor.query.filter(Vendor.name.ilike(vendor_name)).first()
    if not vendor:
        return {"error": f"Vendor '{vendor_name}' not found"}, 404

    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return {"error": "User wallet not found"}, 404

    if wallet.balance < amount:
        return {"error": "Insufficient balance"}, 400

    try:
        payout_result = process_vendor_payout(
            user_id=user_id,
            vendor_id=vendor.id,
            order_id=order_id,
            amount=amount,
            provider=provider
        )
    except Exception as e:
        return {"error": str(e)}, 400

    reference = str(uuid.uuid4())

    txn = Transaction(
        user_id=user_id,
        vendor_id=vendor.id,
        amount=amount,
        type="payout",
        reference=reference,
        status="completed",
        order_id=order_id
    )

    wallet.balance -= amount

    db.session.add(txn)
    db.session.commit()

    return {
        "status": "success",
        "vendor": vendor.name,
        "vendor_id": vendor.id,
        "amount": amount,
        "transaction_reference": reference,
        "payout": payout_result
    }, 200

