
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
