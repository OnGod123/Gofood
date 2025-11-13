# app/models.py
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import Base as base 

class Wallet(base):
    __tablename__ = "wallets"
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.UUID(as_uuid=True), db.ForeignKey("users.id"), nullable=False, unique=True)
    balance = Column(db.Float, default=0.0)
    updated_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="wallet")

    def credit(self, amount: float):
        self.balance = float(self.balance) + float(amount)

    def debit(self, amount: float):
        if float(self.balance) < float(amount):
            raise ValueError("Insufficient wallet balance")
        self.balance = float(self.balance) - float(amount)

class Transaction(base):
    __tablename__ = "transactions"
    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey("users.id"))
    vendor_id = Column(db.Integer, db.ForeignKey("vendors.id"))
    amount = Column(db.Float)
    type = Column(db.String(32))
    reference = Column(db.String(128), unique=True)
    status = Column(db.String(32), default="pending")
    created_at = Column(db.DateTime, default=datetime.utcnow)
