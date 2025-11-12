
from flask import Blueprint, request, jsonify
from app.models.food_item import FoodItem
from app.models.order_multiple import OrderMultiple
from app.extensions import db
from minio import Minio
from minio.error import S3Error
import base64
from datetime import datetime

food_bp = Blueprint("food_bp", __name__, url_prefix="/vendor")

# MinIO client config
minio_client = Minio(
    "minio:9000",  # replace with your MinIO host
    access_key="minioaccesskey",
    secret_key="miniosecretkey",
    secure=False  # True if using HTTPS
)
bucket_name = "food-files"
# Ensure bucket exists
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)

def validate_item(data):
    required = ["item", "food", "picture_data", "picture_filename", "picture_type"]
    missing = [key for key in required if key not in data or not data[key]]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    return True, None

def upload_to_minio(vendor_name: str, file_bytes: bytes, filename: str, content_type: str):
    """Upload file to MinIO under vendor_name folder"""
    object_name = f"{vendor_name}/{filename}"
    minio_client.put_object(
        bucket_name=bucket_name,
        object_name=object_name,
        data=file_bytes,
        length=len(file_bytes),
        content_type=content_type
    )
    return object_name  # return path in MinIO

# --- Single item upload ---
@food_bp.route("/item", methods=["POST"])
def upload_single_item():
    try:
        data = request.get_json(force=True)
        valid, error = validate_item(data)
        if not valid:
            return jsonify({"error": error}), 400

        vendor_name = "vendor1"  # replace with actual vendor name / fetch from DB
        file_bytes = base64.b64decode(data["picture_data"])
        minio_path = upload_to_minio(vendor_name, file_bytes, data["picture_filename"], data["picture_type"])

        # Simulate vendor_id / merchant_id
        vendor_id = 1
        merchant_id = 1

        food = FoodItem(
            vendor_id=vendor_id,
            merchant_id=merchant_id,
            name=data["item"],
            description=data["food"],
            image_url=minio_path,
            price=data.get("price", 0.0),
        )
        db.session.add(food)
        db.session.commit()

        return jsonify({"message": "Food item uploaded successfully", "item": food.to_dict()}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Multiple items upload ---
@food_bp.route("/items", methods=["POST"])
def upload_multiple_items():
    try:
        data = request.get_json(force=True)
        user_id = data.get("user_id")
        items = data.get("items", [])

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        if not isinstance(items, list) or not items:
            return jsonify({"error": "Items must be a non-empty list"}), 400

        saved_items = []
        errors = []
        total_price = 0.0
        vendor_id = 1
        merchant_id = 1
        vendor_name = "vendor1"  # replace with actual vendor name / fetch from DB

        for i, item in enumerate(items, start=1):
            valid, error = validate_item(item)
            if not valid:
                errors.append({"index": i, "error": error})
                continue

            try:
                file_bytes = base64.b64decode(item["picture_data"])
                minio_path = upload_to_minio(vendor_name, file_bytes, item["picture_filename"], item["picture_type"])
            except Exception as fe:
                errors.append({"index": i, "error": f"File upload error: {str(fe)}"})
                continue

            food = FoodItem(
                vendor_id=vendor_id,
                merchant_id=merchant_id,
                name=item["item"],
                description=item["food"],
                image_url=minio_path,
                price=item.get("price", 0.0)
            )
            db.session.add(food)
            saved_items.append(food)
            total_price += item.get("price", 0.0)

        if not saved_items:
            return jsonify({"error": "No valid items", "details": errors}), 400

        db.session.commit()

        # Optional: save as OrderMultiple
        order = OrderMultiple(
            user_id=user_id,
            items_data=[{
                "item": f.name,
                "description": f.description,
                "price": f.price,
                "image_url": f.image_url
            } for f in saved_items],
            total=total_price,
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.commit()

        return jsonify({
            "message": f"{len(saved_items)} items uploaded successfully",
            "saved_items": [f.to_dict() for f in saved_items],
            "order_id": order.id,
            "errors": errors
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# --- GET: List all items ---
@food_bp.route("/fooditem", methods=["GET"])
def list_food_items():
    try:
        vendor_id = request.args.get("vendor_id", type=int, default=1)
        items = FoodItem.query.filter_by(vendor_id=vendor_id).all()
        return jsonify([i.to_dict() for i in items]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@food_bp.route("/vendor/fooditem", methods=["GET"])
def get_food_upload_form():
    """
    Render the vendor food item upload form.
    """
    return render_template("food_item.html")

