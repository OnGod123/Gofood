from datetime import datetime, time
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey,
    DateTime, Time, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.extensions import Base
from app.database.user_models import User


# ---------------------- Vendor ----------------------
class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    Business_name = Column(String(255), nullable=False, index=True)
    Business_address = Column(String(255), nullable=False)

    is_open = Column(Boolean, default=True)  # whether vendor currently open or closed
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)
    Bussiness_account = Column (Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", backref="fullname", uselist=False)
    user = relationship("User", back_populates="vendor", cascade="all, delete-orphan")

    menu_items = relationship("FoodItem", back_populates="vendor", cascade="all, delete-orphan")
    merchants = relationship("ProfileMerchant", backref="vendor", cascade="all, delete-orphan")

    def to_dict(self, include_menu=False):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "is_open": self.is_open,
            "opening_time": self.opening_time.strftime("%H:%M") if self.opening_time else None,
            "closing_time": self.closing_time.strftime("%H:%M") if self.closing_time else None,
            "created_at": self.created_at.isoformat(),
        }
        if include_menu:
            data["menu"] = [item.to_dict() for item in self.menu_items]
        return data


# ---------------------- Merchant ----------------------
class Profile_Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)

    password_hash = Column(String(256), nullable=False)
    account_number = Column(String(64), nullable=True)
    order_tracker = Column(String(128), nullable=True, unique=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user  = relationship("User", backref="merchant_account", uselist=False)
    vendor  = relationship("Vendor", back_populates="merchants")
    

    __table_args__ = (
        UniqueConstraint("user_id", "vendor_id", name="uq_user_vendor"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vendor_id": self.vendor_id,
            "vendor_name": self.vendor.name if self.vendor else None,
            "account_number": self.account_number,
            "order_tracker": self.order_tracker,
            "is_active": self.is_active,
        }


# ---------------------- Food Item (Menu Table) ----------------------
class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(String(512), nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(512), nullable=True)  # path or URL to item picture

    available_from = Column(Time, nullable=True)
    available_to = Column(Time, nullable=True)
    is_available = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    price = Column(Float, nullable=False)

    vendor = relationship("Vendor", backref="food_items", lazy="joined")
    merchant = relationship("Merchant", backref="food_items", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "merchant_id": self.merchant_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "image_url": self.image_url,
            "available_from": self.available_from.strftime("%H:%M") if self.available_from else None,
            "available_to": self.available_to.strftime("%H:%M") if self.available_to else None,
            "is_available": self.is_available,
        }

