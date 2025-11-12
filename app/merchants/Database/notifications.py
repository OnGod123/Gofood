from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean
from app.extensions import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(String(64), nullable=False)
    type = Column(String(64), nullable=False)  # e.g. order_created, offer_sent
    payload = Column(JSON, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "order_id": self.order_id,
            "type": self.type,
            "payload": self.payload,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }


class BargainMessage(Base):
    __tablename__ = "bargain_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String(512), nullable=False)
    metadata = Column(JSON, nullable=True)
    sequence_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message": self.message,
            "metadata": self.metadata,
            "sequence_id": self.sequence_id,
            "created_at": self.created_at.isoformat(),
        }

