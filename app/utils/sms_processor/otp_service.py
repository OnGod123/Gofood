import random
from app.extensions import r

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def store_otp(phone: str, otp: str, context="payment", ttl=300):
    r.setex(f"otp:{context}:{phone}", ttl, otp)

def generate_and_store_otp(phone: str, context="payment", ttl=300):
    otp = generate_otp()
    store_otp(phone, otp, context, ttl)
    return otp

