from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.extensions import base

class FullName(base):
    """
    Link user -> the full official name used in banking transfers.
    A user may have multiple names (rare) but we'll keep one for now.
    """
    __tablename__ = "fullnames"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = db.Column(db.String(255), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="fullname", uselist=False)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "full_name": self.full_name}


class CentralAccount(Base):
    """
    Record representing the system's central account (Moniepoint account)
    where customers deposit funds into before distribution.
    """
    __tablename__ = "central_accounts"
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(64), nullable=False)  # e.g., "moniepoint"
    account_number = db.Column(db.String(64), nullable=False)
    bank_name = db.Column(db.String(128), nullable=True)
    balance = db.Column(db.Float, default=0.0)  # system tracked balance
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaymentTransaction(Base):
    """
    Authoritative transaction log for monies flowing into central account,
    distributions to users, and payouts to vendors.
    """
    __tablename__ = "payment_transactions"
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(64), nullable=False)  # 'moniepoint'
    provider_txn_id = db.Column(db.String(128), nullable=True, index=True)  # from provider
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(8), default="NGN")
    direction = db.Column(db.String(16), nullable=False)  # 'in' | 'out' | 'distribute' | 'payout'
    central_account_id = db.Column(db.Integer, db.ForeignKey("central_accounts.id"), nullable=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    target_vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"), nullable=True)
    metadata = db.Column(db.JSON, nullable=True)
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)

    central_account = db.relationship("CentralAccount", backref="transactions")
    user = db.relationship("User")

