from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from app.extensions import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Vendor_Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("order_single.id"), nullable=False)

    amount = Column(Float, nullable=False)
    fee = Column(Float, default=700.0)
    vendor_amount = Column(Float, nullable=False)

    payment_gateway = Column(String(32), default="wallet")
    status = Column(String(32), default="pending")

    vendor_bank_code = Column(String(16))
    vendor_account_number = Column(String(32))

    reference = Column(String(64), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

