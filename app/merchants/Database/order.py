from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from app.extensions import Base


class OrderSingle(Base):
    __tablename__ = "order_single"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_data = Column(JSON, nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    vendor_name = Column(DateTime, default=datetime.utcnow)
    product_name = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", backref="single_orders")
    reciepient_address = Column(String(50), nullabe = False)


class OrderMultiple(Base):
    __tablename__ = "order_multiple"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    items_data = Column(JSON, nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    vendor_name = Column(DateTime, default=datetime.utcnow)
    product_name = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", backref="multiple_orders")
    reciepient_address = Column(String(50), nullabe = False)

