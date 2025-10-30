from app.extensions import Base
from datetime import datetime

class Wishlist(Base):
    __tablename__ = "wishlists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey("food_items.id"), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="wishlist_items")
    item = db.relationship("FoodItem")

# Add this relationship in User model:
# wishlist_items = db.relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")

