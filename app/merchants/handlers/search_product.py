from flask import Blueprint, jsonify, request
from app.extensions import db, r
from app.database.models import FoodItem
from app.utils.minio_utils import get_minio_file_url
import json
from datetime import timedelta

search_bp = Blueprint("search_bp", __name__)

@search_bp.route("/searchbyproduct", methods=["GET"])
def search_by_product():
    """
    Search food items by product name.
    Cached by search term.
    Returns paginated list of items with MinIO image URLs.
    """
    search_query = request.args.get("q", "").strip().lower()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    if not search_query:
        return jsonify({"error": "Missing search term ?q=<product_name>"}), 400

    cache_key = f"search:{search_query}:page:{page}:per_page:{per_page}"

    cached_data = r.get(cache_key)
    if cached_data:
        print(f"[CACHE HIT] Returning '{search_query}' page {page} from Redis.")
        return jsonify(json.loads(cached_data)), 200

    print(f"[CACHE MISS] Querying DB for '{search_query}' page {page}...")

    query = (
        FoodItem.query
        .filter(FoodItem.name.ilike(f"%{search_query}%"))
        .filter(FoodItem.is_available == True)
        .order_by(FoodItem.created_at.desc())
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items

    # --- Build result list with MinIO URLs ---
    result_items = []
    for item in items:
        item_dict = item.to_dict()
        try:
            # Assuming vendor_name and picture_filename are columns
            minio_url = get_minio_file_url(item.vendor_name, item.picture_filename)
            item_dict["image_url"] = minio_url
        except Exception as e:
            print(f"[MINIO ERROR] {e}")
            item_dict["image_url"] = None

        result_items.append(item_dict)

    result = {
        "search_term": search_query,
        "page": page,
        "per_page": per_page,
        "total_items": pagination.total,
        "total_pages": pagination.pages,
        "items": result_items,
    }

    r.setex(cache_key, timedelta(minutes=5), json.dumps(result))
    return jsonify(result), 200

