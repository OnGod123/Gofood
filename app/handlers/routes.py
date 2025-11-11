
from flask import Blueprint
from app.handlers.phone_login import request_login_token, verify_login_token

auth_phone = Blueprint("auth_mobile", __name__)

auth_phone.add_url_rule("/auth/request", view_func=request_login_token, methods=["POST"])
auth_phone.add_url_rule("/auth/verify", view_func=verify_login_token, methods=["POST"])

