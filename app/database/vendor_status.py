from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import Enum as SQLEnum
from app.extensions import Base, db

# If you use db.Model instead of Base, change Base -> db.Model and imports accordingly

class VendorStatusLog(Base):
    __tablename__ = "vendor_status_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    old_status = Column(String(32), nullable=False)    # "open" or "closed"
    new_status = Column(String(32), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.changed_by,
            "changed_at": self.changed_at.isoformat(),
        }

