from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.extensions import Base as base

class FullName(base):
    """
    Link user -> the full official name used in banking transfers.
    A user may have multiple names (rare) but we'll keep one for now.
    """
    __tablename__ = "fullnames"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = Column(String(255), nullable=False, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="fullname", uselist=False)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "full_name": self.full_name}


class CentralAccount(base):
    """
    Record representing the system's central account (Moniepoint account)
    where customers deposit funds into before distribution.
    """
    __tablename__ = "central_accounts"
    id = Column(Integer, primary_key=True)
    provider = Column(String(64), nullable=False)  # e.g., "moniepoint"
    account_number = Column(String(64), nullable=False)
    bank_name = Column(String(128), nullable=True)
    balance = Column(Float, default=0.0)  # system tracked balance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Payment_API_database_Transaction(base):
    """
    Authoritative transaction log for monies flowing into central account,
    distributions to users, and payouts to vendors.
    """
    __tablename__ = "payment_transactions"
    id = Column(Integer, primary_key=True)
    provider = Column(String(64), nullable=False)  # 'moniepoint'
    provider_txn_id = Column(String(128), nullable=True, index=True)  # from provider
    amount = Column(Float, nullable=False)
    currency = Column(String(8), default="NGN")
    direction = Column(String(16), nullable=False)  # 'in' | 'out' | 'distribute' | 'payout'
    central_account_id = Column(Integer, ForeignKey("central_accounts.id"), nullable=True)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    meta = Column(JSON, nullable=True)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    central_account = relationship("CentralAccount", backref="transactions")
    user = relationship("User")
    verified_payment = Column(Boolean, default=False)

