from flask import Blueprint, request, jsonify, session
from app.database.order import OrderSingle
from app.database.food_item import FoodItem
from app.database.wallet import Wallet
from app.database.vendor import Vendor
from app.extensions import db
from datetime import datetime

whatsapp_bp = Blueprint("whatsapp", __name__)

@whatsapp_bp.route("/whatsapp_order", methods=["POST"])
def whatsapp_order():
    # --- Get user_id from session ---
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    # --- Get vendor name and items from payload ---
    data = request.get_json()
    vendor_name = data.get("vendor_name")
    items_data = data.get("items", [])

    if not (vendor_name and items_data):
        return jsonify({"error": "Missing vendor name or items"}), 400

    # --- Fetch vendor by name ---
    vendor = Vendor.query.filter_by(name=vendor_name).first()
    if not vendor:
        return jsonify({"error": f"Vendor '{vendor_name}' not found"}), 404

    # --- Fetch food items ---
    food_names = [item["food_name"] for item in items_data]
    food_items = FoodItem.query.filter(
        FoodItem.name.in_(food_names),
        FoodItem.vendor_id == vendor.id,
        FoodItem.is_available == True
    ).all()

    if not food_items:
        return jsonify({"error": "No available items found for this vendor"}), 404

    total_amount = 0.0
    order_details = []

    for item in items_data:
        food = next((f for f in food_items if f.name == item["food_name"]), None)
        if not food:
            continue
        qty = item.get("quantity", 1)
        subtotal = food.price * qty
        total_amount += subtotal
        order_details.append({
            "food_id": food.id,
            "name": food.name,
            "price": food.price,
            "quantity": qty,
            "subtotal": subtotal
        })

    # --- Check wallet ---
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404

    if wallet.balance < total_amount:
        return jsonify({
            "error": "Insufficient balance",
            "wallet_balance": wallet.balance,
            "total_amount": total_amount
        }), 400

    # --- Automatic billing ---
    try:
        wallet.debit(total_amount)
        db.session.add(wallet)

        order = OrderSingle(
            user_id=user_id,
            item_data=order_details,
            total=total_amount,
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Payment failed", "details": str(e)}), 500

    # --- Return success ---
    return jsonify({
        "message": "Order placed successfully",
        "vendor_name": vendor.name,
        "order_id": order.id,
        "total_amount": total_amount,
        "remaining_balance": wallet.balance,
        "items": order_details
    })

