# inside app/handlers/payouts.py (or moniepoint.py)
import requests

def payout_to_vendor(order_id, amount, vendor_bank_account, vendor_bank_name, vendor_name):
    central = get_user_wallet("moniepoint")
    if wallet.balance < amount:
        raise ValueError("Insufficient central funds to pay vendor")

    # Prepare provider API call (Moniepoint)
    payload = {
        "amount": amount,
        "beneficiary_account": vendor_bank_account,
        "beneficiary_name": vendor_name,
        "bank_name": vendor_bank_name,
        "narration": f"Payout for order {order_id}"
    }
    # call provider (replace with actual Moniepoint endpoint)
    resp = requests.post(current_app.config["MONIEPOINT_PAYOUT_URL"], json=payload, headers={"Authorization": f"Bearer {current_app.config['MONIEPOINT_SECRET']}"})
    data = resp.json()
    if resp.status_code not in (200,201) or data.get("status") != "success":
        # record failed transaction
        tx = PaymentTransaction(
            provider="moniepoint",
            provider_txn_id=data.get("reference"),
            amount=amount,
            direction="payout",
            processed=False,
            metadata=data
        )
        db.session.add(tx)
        db.session.commit()
        raise RuntimeError("Payout failed")

    # success: adjust central balance and record transaction
    central.balance -= amount
    db.session.add(central)

    tx = PaymentTransaction(
        provider="moniepoint",
        provider_txn_id=data.get("reference") or data.get("id"),
        amount=amount,
        direction="payout",
        target_vendor_id=vendor_id,
        central_account_id=central.id,
        processed=True,
        processed_at=datetime.utcnow(),
        metadata=data
    )
    db.session.add(tx)
    db.session.commit()
    return tx

