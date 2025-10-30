from datetime import datetime
from app.extensions import db
import uuid

class Wallet(db.Model):
    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False, unique=True)
    balance = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="wallet")

    def credit(self, amount: float):
        """Add funds to wallet"""
        self.balance += amount

    def debit(self, amount: float):
        """Deduct funds if balance is sufficient"""
        if self.balance < amount:
            raise ValueError("Insufficient wallet balance")
        self.balance -= amount

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendors.id"))
    amount = db.Column(db.Float)
    type = db.Column(db.String(32))
    reference = db.Column(db.String(128), unique=True)
    status = db.Column(db.String(32), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
