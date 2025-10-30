# app/merchant/Database/delivery.py
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.extensions import Base

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_single_id = Column(Integer, ForeignKey("order_single.id"), nullable=True)
    order_multiple_id = Column(Integer, ForeignKey("order_multiple.id"), nullable=True)
    address = Column(String(255), nullable=False)
    delivery_fee = Column(Float, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="deliveries")
    order_single = relationship("OrderSingle", backref="delivery", uselist=False)
    order_multiple = relationship("OrderMultiple", backref="delivery", uselist=False)

    user = relationship("User", backref="deliveries")
    order_single = relationship("OrderSingle", backref="delivery", uselist=False)
    order_multiple = relationship("OrderMultiple", backref="delivery", uselist=False)

