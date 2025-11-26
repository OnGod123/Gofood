
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import Base as base 
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Wallet(base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="wallet")

    def debit(self, amount: float):
        if self.balance < amount:
            raise ValueError("Insufficient wallet balance")
        self.balance -= amount

    # credit only in memory (optional)
    def credit(self, amount: float):
        self.balance += amount
        db.commit()          
        db.refresh(self)

    
    @staticmethod
    def debit_from_db(user_id: int, amount: float):
        """
        Atomically decrement wallet balance in DB.
        Raises ValueError if insufficient funds.
        """
        wallet = Wallet.query.filter_by(user_id=user_id).with_for_update().first()
        if not wallet:
            raise ValueError("Wallet not found")
        if wallet.balance < amount:
            raise ValueError("Insufficient wallet balance")

        # Deduct from DB
        wallet.balance -= amount
        db.session.add(wallet)
        db.session.commit()
        return wallet.balance

class Transaction(base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    amount = Column(Float)
    type = Column(String(32))
    reference = Column(String(128), unique=True)
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


    @classmethod
def process_vendor_payout(cls, *, user_id: int, vendor_id: int, amount: float):
    """
    Try Paystack → Flutterwave → Monnify.
    If ANY provider succeeds:
        - Debit user's wallet
        - Mark transaction as completed
    If all fail:
        - Transaction stays failed
    """

    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return {"error": "Vendor not found"}

    reference = f"TRX-{uuid.uuid4().hex[:12]}"
    tx = cls(
        user_id=user_id,
        vendor_id=vendor_id,
        amount=amount,
        type="vendor_payout",
        status="processing",
        reference=reference,
    )
    db.session.add(tx)
    db.session.commit()

    providers = ["paystack", "flutterwave", "monnify"]

    provider_response = None
    provider_used = None

    for provider in providers:
        try:
            if provider == "paystack":
                provider_response = paystack_charge_bank(
                    email=vendor.email,
                    amount=amount,
                    bank_code=vendor.bank_code,
                    account_number=vendor.bank_account,
                )

            elif provider == "flutterwave":
                provider_response = flutterwave_charge_bank(
                    tx_ref=reference,
                    amount=amount,
                    bank_code=vendor.bank_code,
                    account_number=vendor.bank_account,
                    email=vendor.email,
                )

            elif provider == "monnify":
                provider_response = monnify_charge(
                    account_number=vendor.bank_account,
                    bank_code=vendor.bank_code,
                    amount=amount,
                    customer_name=vendor.name,
                    customer_email=vendor.email,
                )

            provider_used = provider
            break  # SUCCESS → stop loop

        except Exception:
            continue  

    if not provider_used:
        tx.status = "failed"
        db.session.commit()

        return {
            "error": "All payout providers failed. Possibly insufficient funds.",
            "reference": reference,
        }

    try:
        new_balance = Wallet.debit_from_db(user_id=user_id, amount=amount)
    except Exception as e:
        # Wallet debit failed: mark payout as failed
        tx.status = "failed"
        db.session.commit()

        return {
            "error": "Wallet debit failed after payout.",
            "reference": reference,
            "details": str(e),
        }

    tx.status = "completed"
    db.session.commit()

    return {
        "status": "success",
        "provider": provider_used,
        "reference": reference,
        "amount": amount,
        "provider_response": provider_response,
        "wallet_balance": new_balance,
    }

