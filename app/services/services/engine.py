import uuid
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.merchants.Database.vendors_data_base import Vendor
from app.merchants.Database.Vendors_payment_service import Vendor_Payment
from app.services.payout.provider_paystack import paystack_charge_bank
from app.services.payout.provider_flutter import flutterwave_charge_bank
from app.services.payout.provider_monnify import monnify_charge
from app.handlers.wallet import Wallet
import concurrent.futures


class PayoutError(Exception):
    pass


def provider_worker(provider, vendor, reference, vendor_amount):
    if provider == "paystack":
        return provider, paystack_charge_bank(
            email=vendor.email,
            amount=vendor_amount,
            bank_code=vendor.bank_code,
            account_number=vendor.bank_account
        )
    elif provider == "flutterwave":
        return provider, flutterwave_charge_bank(
            tx_ref=reference,
            amount=vendor_amount,
            bank_code=vendor.bank_code,
            account_number=vendor.bank_account,
            email=vendor.email
        )
    elif provider == "monnify":
        return provider, monnify_charge(
            account_number=vendor.bank_account,
            bank_code=vendor.bank_code,
            amount=vendor_amount,
            customer_name=vendor.name,
            customer_email=vendor.email
        )
    else:
        raise ValueError("Unknown provider")



def process_vendor_payout(*, user_id: int, vendor_id: int, order_id: int, amount: float, provider: str):
    """
    MASTER FUNCTION:
    ----------------
    Your original logic + automatic fallback to parallel provider execution.
    """

    # vendor validation
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        raise PayoutError("Vendor not found")

    # wallet validation
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        raise PayoutError("Wallet not found")

    if wallet.balance < amount:
        raise PayoutError("Insufficient wallet balance")

    # compute payout
    fee = vendor.platform_fee if hasattr(vendor, "platform_fee") else 700
    vendor_amount = amount - fee
    reference = f"TRX-{uuid.uuid4().hex[:12]}"

    # create payment row
    payment = Vendor_Payment(
        id=uuid.uuid4(),
        user_id=user_id,
        vendor_id=vendor_id,
        order_id=order_id,
        amount=amount,
        fee=fee,
        vendor_amount=vendor_amount,
        payment_gateway=provider,
        status="processing",
        vendor_bank_code=vendor.bank_code,
        vendor_account_number=vendor.bank_account,
        reference=reference,
        created_at=datetime.utcnow()
    )

    db.session.add(payment)
    db.session.commit()

    # debit wallet
    wallet.debit(amount)
    db.session.commit()

    # route to provider
    try:
        if provider == "paystack":
            provider_resp = paystack_charge_bank(
                email=vendor.email,
                amount=vendor_amount,
                bank_code=vendor.bank_code,
                account_number=vendor.bank_account
            )

        elif provider == "flutterwave":
            provider_resp = flutterwave_charge_bank(
                tx_ref=reference,
                amount=vendor_amount,
                bank_code=vendor.bank_code,
                account_number=vendor.bank_account,
                email=vendor.email
            )

        elif provider == "monnify":
            provider_resp = monnify_charge(
                account_number=vendor.bank_account,
                bank_code=vendor.bank_code,
                amount=vendor_amount,
                customer_name=vendor.name,
                customer_email=vendor.email
            )

        else:
            raise PayoutError("Unsupported payout provider")
    except Exception as e:

        providers = ["paystack", "flutterwave", "monnify"]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_provider = {
                executor.submit(provider_worker, p, vendor, reference, vendor_amount): p 
                for p in providers
            }

            for future in concurrent.futures.as_completed(future_to_provider):
                p = future_to_provider[future]
                try:
                    p, provider_resp = future.result()

                    # update success
                    payment.status = "completed"
                    payment.payment_gateway = p
                    payment.metadata = provider_resp
                    db.session.commit()

                    return {
                        "status": "success",
                        "reference": reference,
                        "amount": amount,
                        "vendor_amount": vendor_amount,
                        "fee": fee,
                        "provider": p,
                        "provider_response": provider_resp,
                        "wallet_balance": wallet.balance
                    }

                except Exception:
                    continue

        # If all failed
        payment.status = "failed"
        payment.metadata = {"error": str(e)}
        db.session.commit()
        raise PayoutError(f"All providers failed: {e}")

    payment.status = "completed"
    payment.metadata = provider_resp
    db.session.commit()

    return {
        "status": "success",
        "reference": reference,
        "amount": amount,
        "vendor_amount": vendor_amount,
        "fee": fee,
        "provider": provider,
        "provider_response": provider_resp,
        "wallet_balance": wallet.balance
    }

