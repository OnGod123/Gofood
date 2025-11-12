from flask import Blueprint, request, jsonify
from app.extensions import db
from app.database.models import Wishlist, FoodItem
from flask_login import current_user  # or however you manage auth

wishlist_bp = Blueprint("wishlist_bp", __name__)

@wishlist_bp.route("/wishlist", methods=["POST"])
def add_to_wishlist():
    """
    Add selected items from user dashboard to wishlist.
    Expects form-urlencoded data: item_ids=1&item_ids=2&item_ids=3
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    item_ids = request.form.getlist("item_ids")

    if not item_ids:
        return jsonify({"error": "No items selected"}), 400

    added_items = []
    for item_id in item_ids:
        existing = Wishlist.query.filter_by(user_id=current_user.id, item_id=item_id).first()
        if not existing:
            wishlist_item = Wishlist(user_id=current_user.id, item_id=item_id)
            db.session.add(wishlist_item)
            added_items.append(item_id)

    db.session.commit()

    return jsonify({
        "message": "Wishlist updated successfully.",
        "added_items": added_items
    }), 201

@wishlist_bp.route("/wishlist", methods=["GET"])
def get_wishlist():
    """
    Display user's wishlist items.
    """
    if not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401

    wishlist_items = (
        Wishlist.query
        .filter_by(user_id=current_user.id)
        .join(FoodItem)
        .add_entity(FoodItem)
        .all()
    )

    data = [
        {
            "item_id": food_item.id,
            "name": food_item.name,
            "price": food_item.price,
            "vendor": food_item.vendor.name,
            "image": food_item.image_url,
        }
        for _, food_item in wishlist_items
    ]

    return jsonify(data), 200

