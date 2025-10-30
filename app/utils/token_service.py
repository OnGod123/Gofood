import random, datetime, jwt
from app.extensions import r as  redis_client
from flask import current_app

def generate_otp(phone: str) -> str:
    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"otp:{phone}", 300, otp)  # expires in 5 min
    return otp

def verify_otp(phone: str, otp: str) -> bool:
    saved = redis_client.get(f"otp:{phone}")
    return saved == otp

def generate_jwt(email: str):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    payload = {"email": email, "exp": exp_time}
    token = jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")
    return token

