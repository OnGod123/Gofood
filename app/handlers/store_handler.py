from flask import Blueprint, jsonify, request, render_template
from app.extensions import db
from app.database.models import FoodItem
from app.utils.minio_utils import upload_to_minio, get_minio_file_url
from cachetools import TTLCache
from datetime import datetime
import base64

store_bp = Blueprint("store_bp", __name__, template_folder="../../templates")

# In-memory cache: max 200 items, 5 minutes TTL
store_cache = TTLCache(maxsize=200, ttl=300)

def get_cached_data(key):
    return store_cache.get(key)

def set_cached_data(key, value):
    store_cache[key] = value

def clear_cache():
    store_cache.clear()


def wants_json_response():
    """
    Detect if the client expects JSON.
    (Used to automatically switch between HTML and JSON.)
    """
    return "application/json" in request.headers.get("Accept", "")


@store_bp.route("/store", methods=["GET", "POST"])
def store_handler():
    """
    Main store handler for retrieving or adding food items.
    Includes MinIO image logic + page rendering.
    """
    if request.method == "GET":
        cached = get_cached_data("all_items")
        if cached:
            data = cached
        else:
            items = FoodItem.query.filter_by(is_available=True).all()
            data = []
            for item in items:
                item_dict = item.to_dict()
                try:
                    image_url = get_minio_file_url(item.vendor_name, item.picture_filename)
                    item_dict["image_url"] = image_url
                except Exception as e:
                    print(f"[MINIO ERROR] {e}")
                    item_dict["image_url"] = None
                data.append(item_dict)
            set_cached_data("all_items", data)

        # 🧠 Render HTML or return JSON automatically
        if wants_json_response():
            return jsonify({"source": "cache" if cached else "db", "data": data}), 200
        else:
            return render_template("store.html", items=data)

    elif request.method == "POST":
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "Missing JSON data"}), 400

        try:
            vendor_name = payload.get("vendor_name")
            picture_filename = payload.get("picture_filename")
            picture_type = payload.get("picture_type")
            picture_data = payload.get("picture_data")

            if not all([vendor_name, picture_filename, picture_type, picture_data]):
                return jsonify({"error": "Missing image data"}), 400

            file_bytes = base64.b64decode(picture_data)
            upload_to_minio(vendor_name, file_bytes, picture_filename, picture_type)
            image_url = get_minio_file_url(vendor_name, picture_filename)

            new_item = FoodItem(
                vendor_id=payload["vendor_id"],
                merchant_id=payload["merchant_id"],
                name=payload["name"],
                description=payload.get("description"),
                price=float(payload["price"]),
                picture_filename=picture_filename,
                picture_type=picture_type,
                image_url=image_url,
                is_available=True,
                available_from=datetime.strptime(payload["available_from"], "%H:%M").time()
                    if payload.get("available_from") else None,
                available_to=datetime.strptime(payload["available_to"], "%H:%M").time()
                    if payload.get("available_to") else None,
            )
            db.session.add(new_item)
            db.session.commit()
            clear_cache()
            return jsonify({"message": "Item added successfully", "item": new_item.to_dict()}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Failed to add item: {str(e)}"}), 500


@store_bp.route("/store/diary", methods=["GET"])
def store_diary():
    """
    Sub-handler for diary items (cached, with MinIO URLs, and page rendering).
    """
    cached = get_cached_data("diary_items")
    if cached:
        data = cached
    else:
        items = FoodItem.query.filter(
            FoodItem.is_available == True,
            FoodItem.name.ilike("%milk%") | FoodItem.name.ilike("%cheese%") | FoodItem.name.ilike("%butter%")
        ).all()
        data = []
        for item in items:
            item_dict = item.to_dict()
            try:
                item_dict["image_url"] = get_minio_file_url(item.vendor_name, item.picture_filename)
            except:
                item_dict["image_url"] = None
            data.append(item_dict)
        set_cached_data("diary_items", data)

    if wants_json_response():
        return jsonify({"source": "cache" if cached else "db", "data": data}), 200
    else:
        return render_template("store_diary.html", items=data)


@store_bp.route("/store/food", methods=["GET"])
def store_food():
    """
    Sub-handler for general food items (cached, with MinIO URLs, and page rendering).
    """
    cached = get_cached_data("food_items")
    if cached:
        data = cached
    else:
        items = FoodItem.query.filter(
            FoodItem.is_available == True,
            ~FoodItem.name.ilike("%milk%"),
            ~FoodItem.name.ilike("%cheese%"),
            ~FoodItem.name.ilike("%butter%")
        ).all()
        data = []
        for item in items:
            item_dict = item.to_dict()
            try:
                item_dict["image_url"] = get_minio_file_url(item.vendor_name, item.picture_filename)
            except:
                item_dict["image_url"] = None
            data.append(item_dict)
        set_cached_data("food_items", data)

    if wants_json_response():
        return jsonify({"source": "cache" if cached else "db", "data": data}), 200
    else:
        return render_template("store_food.html", items=data)

