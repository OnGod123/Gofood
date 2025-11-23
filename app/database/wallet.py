
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
