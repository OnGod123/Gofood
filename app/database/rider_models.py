from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from app.extensions import db

class Rider(db.Model):
    __tablename__ = "riders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    status = Column(String(32), default="inactive")  # active, busy, offline
    current_lat = Column(Float, nullable=True)
    current_lng = Column(Float, nullable=True)
    current_address = Column(String(255), nullable=True)
    is_available = Column(Boolean, default=True)
    last_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "current_lat": self.current_lat,
            "current_lng": self.current_lng,
            "current_address": self.current_address,
            "is_available": self.is_available,
            "last_update": self.last_update.strftime("%Y-%m-%d %H:%M:%S") if self.last_update else None,
        }

