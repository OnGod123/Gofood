from flask import Blueprint, render_template, request, redirect, url_for, make_response, current_app, g
import jwt, datetime, redis
from functools import wraps
from app.database.user_models import User
from app.database.signinmodels import Signin
from flask import Flask
from app.extensions import db, migrate, socketio, oauth, r


auth_bp = Blueprint("auth", __name__)

def jwt_required(f):
    """
    Protect routes and inject `g.current_user`
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("jwt")
        if not token:
            return redirect(url_for("auth.signin"))

        try:
            # Decode JWT
            data = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            email = data.get("email")

            # Verify Redis session is still valid
            if not r.exists(f"session:{email}"):
                return redirect(url_for("auth.signin"))

            # Attach the user to Flask's global context
            user = db.session.query(User).filter_by(email=email).first()
            if not user:
                return redirect(url_for("auth.signin"))
            g.current_user = user

        except jwt.ExpiredSignatureError:
            return redirect(url_for("auth.signin"))
        except jwt.InvalidTokenError:
            return redirect(url_for("auth.signin"))

        return f(*args, **kwargs)
    return decorated

@auth_bp.route("/signin", methods=["POST"])
def signin_post():
    email = request.form.get("email")
    password = request.form.get("password")
    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    user = db.session.query(User).filter_by(email=email).first()

    if user and password == "1234":  # TODO: replace with proper password check
        # ✅ Log successful signin
        signin_log = Signin(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            method="password",
            success=True
        )
        db.session.add(signin_log)
        db.session.commit()

        # Generate JWT and Redis session
        exp_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        token = jwt.encode(
            {"email": email, "exp": exp_time},
            current_app.config["JWT_SECRET"],
            algorithm="HS256"
        )

        # Store short-lived session in Redis
        r.setex(f"session:{email}", current_app.config["SESSION_EXPIRE"], "active")

        # Return cookie
        resp = make_response(redirect(url_for("home.dashboard")))
        resp.set_cookie("jwt", token, httponly=True, max_age=900)
        return resp

    else:
        
        signin_log = Signin(
            user_id=user.id if user else None,
            ip_address=ip_address,
            user_agent=user_agent,
            method="password",
            success=False,
            message="Invalid credentials"
        )
        db.session.add(signin_log)
        db.session.commit()

        return render_template("signin.html", error="Invalid credentials")


from flask import Blueprint, request, redirect, url_for, jsonify, make_response, current_app
from flask import Flask
from app.extensions import db, migrate, socketio, oauth, r
from app.database.user_models import User
from app.database.signinmodels import Signin
from authlib.integrations.flask_client import OAuth
import jwt, datetime, redis, os

auth_bp = Blueprint("auth", __name__)

# --- Google OAuth Setup ---
oauth = OAuth()
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID", "your-google-client-id"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", "your-google-client-secret"),
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    userinfo_endpoint="https://www.googleapis.com/oauth2/v2/userinfo",
    client_kwargs={"scope": "openid email profile"},
)

# --- Step 1: Redirect user to Google ---
@auth_bp.route("/google/login")
def google_login():
    redirect_uri = url_for("auth.google_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

# --- Step 2: Handle Google OAuth callback ---
@auth_bp.route("/auth/google/callback")
def google_callback():
    token = google.authorize_access_token()
    user_info = google.get("userinfo").json()

    user_email = user_info.get("email")
    user_name = user_info.get("name")
    user_google_id = user_info.get("id")
    ip_address = request.remote_addr
    user_agent = request.headers.get("User-Agent")

    if not user_email:
        return jsonify({"error": "Unable to retrieve Google account email"}), 400

    # Check if user already exists
    user = db.session.query(User).filter_by(email=user_email).first()

    # If not, create a new one
    if not user:
        user = User(
            email=user_email,
            name=user_name,
            google_id=user_google_id,
            is_guest=False,
        )
        db.session.add(user)
        db.session.commit()

    # --- Log the sign-in event ---
    signin_log = Signin(
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
        method="google",
        success=True
    )
    db.session.add(signin_log)
    db.session.commit()

    # --- Create JWT Token ---
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    jwt_token = jwt.encode(
        {"email": user.email, "exp": exp_time},
        current_app.config["JWT_SECRET"],
        algorithm="HS256"
    )

    # --- Store active session in Redis ---
    r.setex(f"session:{user.email}", current_app.config["SESSION_EXPIRE"], "active")

    # --- Set secure cookie and redirect ---
    resp = make_response(redirect(url_for("home.dashboard")))
    resp.set_cookie("jwt", jwt_token, httponly=True, max_age=900)
    return resp

