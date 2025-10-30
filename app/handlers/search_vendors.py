from flask import Blueprint, jsonify, request
from app.extensions import db, r
from app.database.models import Vendor  # adjust import path as needed
import json
from datetime import timedelta

vendor_bp = Blueprint("vendor_bp", __name__)

@vendor_bp.route("/vendors/dashboard", methods=["GET"])
def vendor_dashboard():
    """
    Vendor Dashboard (cached for 5 minutes)
    Shows all open vendors with optional search and pagination.
    """
    search = request.args.get("search", "").strip().lower()
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    cache_key = f"vendors_dashboard:{search or 'all'}:page:{page}:limit:{limit}"

    # --- 1. Check cache first ---
    cached_data = r.get(cache_key)
    if cached_data:
        print("[CACHE HIT] Returning paginated vendors from Redis cache.")
        return jsonify(json.loads(cached_data)), 200

    # --- 2. Cache miss → query DB ---
    print("[CACHE MISS] Fetching vendors from DB...")
    query = Vendor.query.filter_by(is_open=True)
    if search:
        query = query.filter(Vendor.name.ilike(f"%{search}%"))

    total_vendors = query.count()
    vendors = query.offset(offset).limit(limit).all()

    result = {
        "page": page,
        "limit": limit,
        "total_vendors": total_vendors,
        "total_pages": (total_vendors + limit - 1) // limit,
        "vendors": [
            {
                "vendor_id": v.id,
                "vendor_name": v.name,
                "status": "open" if v.is_open else "closed",
                "location": v.location,
                "category": v.category,
                "average_rating": v.average_rating,
                "banner_image": v.banner_image,
            }
            for v in vendors
        ],
    }

    # --- 3. Store in Redis with TTL (5 min) ---
    r.setex(cache_key, timedelta(minutes=5), json.dumps(result))

    return jsonify(result), 200

