from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import Base

class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    mimetype = Column(String(64), nullable=False)
    filesize = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # relationship back to user
    user = relationship("User", backref="pictures")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "mimetype": self.mimetype,
            "filesize": self.filesize,
            "uploaded_at": self.uploaded_at.isoformat(),
            "user_id": self.user_id,
        }

