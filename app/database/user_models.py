from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, JSON, Index, UniqueConstraint
)
from app.extensions import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(320), nullable=True, index=True)
    phone = Column(String(32), nullable=True, index=True)
    password_hash = Column(String(256), nullable=True)
    name = Column(String(120), nullable=True)

    google_id = Column(String(256), nullable=True, index=True)
    facebook_id = Column(String(256), nullable=True, index=True)

    # track IP (for guest or last seen). Not unique; multiple users may share IP historically,
    # but guest accounts will have is_guest=True
    last_ip = Column(String(45), nullable=True)

    is_guest = Column(Boolean, default=False, nullable=False)

    # metadata: email_verified, phone_verified, provider data etc.
    extra_data = Column(JSON, nullable=True, default={})

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        # optional strict uniqueness: if you want strict uniqueness at DB level
        UniqueConstraint('email', name='uq_users_email', sqlite_on_conflict='IGNORE'),
        UniqueConstraint('phone', name='uq_users_phone', sqlite_on_conflict='IGNORE'),
        UniqueConstraint('google_id', name='uq_users_google_id', sqlite_on_conflict='IGNORE'),
        UniqueConstraint('facebook_id', name='uq_users_facebook_id', sqlite_on_conflict='IGNORE'),
    )
    wallets = db.relationship("Wallet", backref="user", uselist=False)
    vendors = db.relationship("Vendor", backref="user", lazy=True)
    orders = db.relationship("OrderSingle", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "name": self.name,
            "google_id": self.google_id,
            "facebook_id": self.facebook_id,
            "is_guest": self.is_guest,
            "last_ip": self.last_ip,
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

