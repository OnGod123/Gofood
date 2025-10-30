from flask import Blueprint, request, jsonify, redirect, url_for, current_app, render_template
from flask import Flask
from app.extensions import db, migrate, socketio, oauth, r
from app.database.user_models import User
from werkzeug.security import generate_password_hash
from datetime import datetime
import re

signup_bp = Blueprint("auth_signup", __name__)

@signup_bp.route("/signup", methods=["GET"])
def signup_get():
    """Render the signup form (signup.html)."""
    return render_template("signup.html")

        
@signup_bp.route("/signup", methods=["POST"])
def signup_post():
    """
    Robust JSON-based signup endpoint with redirect to dashboard.
    Expected JSON payload:
    {
        "email": "user@example.com",
        "phone": "+1234567890",
        "password": "mypassword",
        "name": "John Doe",
        "metadata": { "referral": "friend", "country": "NG" }
    }
    """
    try:
        # --- Step 1: Parse JSON input ---
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid or missing JSON payload"}), 400

        email = (data.get("email") or "").strip().lower()
        phone = (data.get("phone") or "").strip()
        password = data.get("password")
        name = (data.get("name") or "").strip()
        metadata = data.get("metadata") or {}
        ip_address = request.remote_addr

        # --- Step 2: Validate input ---
        if not email or not password or not name:
            return jsonify({"error": "Missing required fields (email, password, name)"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email format"}), 400

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        # --- Step 3: Check for duplicates ---
        existing_user = db.session.query(User).filter(
            (User.email == email) | (User.phone == phone)
        ).first()
        if existing_user:
            return jsonify({"error": "User with this email or phone already exists"}), 409

        # --- Step 4: Hash password ---
        password_hash = generate_password_hash(password)

        # --- Step 5: Create new user ---
        new_user = User(
            email=email,
            phone=phone or None,
            password_hash=password_hash,
            name=name,
            last_ip=ip_address,
            is_guest=False,
            metadata=metadata,
        )
        db.session.add(new_user)
        db.session.commit()

        # --- Step 6: Redirect to dashboard ---
        dashboard_url = url_for("user.dashboard", user_id=new_user.id)
        response = jsonify({
            "message": "Signup successful",
            "user": new_user.to_dict(),
            "redirect": dashboard_url
        })
        response.status_code = 201

        # Optionally perform an actual redirect if the client expects it
        if request.args.get("redirect") == "true":
            return redirect(dashboard_url)

        return response

    except Exception as e:
        current_app.logger.exception("Signup error")
        db.session.rollback()
        return jsonify({"error": "Server error", "details": str(e)}), 500

