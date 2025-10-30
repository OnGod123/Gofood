from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, func
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.extensions import Base   # assuming your user model is in user.py


class Signin(Base):
    __tablename__ = "signins"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key to user table
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # IP, user agent, and method (e.g. password, google, facebook)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(256), nullable=True)
    method = Column(String(50), nullable=False, default="password")

    # Track sign-in result
    success = Column(Boolean, default=True, nullable=False)
    message = Column(String(255), nullable=True)

    # Optional JSON for extra context (e.g., geolocation or device info)
    extra_data = Column(JSON, default={}, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to User
    user = relationship("User", backref="signins", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "method": self.method,
            "success": self.success,
            "message": self.message,
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

