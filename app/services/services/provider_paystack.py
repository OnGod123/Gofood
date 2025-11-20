import requests
from flask import current_app

PAYSTACK_CHARGE_URL = "https://api.paystack.co/charge"

def paystack_charge_bank(*, email, amount, bank_code, account_number):
    payload = {
        "email": email,
        "amount": int(amount * 100),  # Paystack uses kobo
        "bank": {
            "code": bank_code,
            "account_number": account_number
        }
    }

    headers = {
        "Authorization": f"Bearer {current_app.config['PAYSTACK_SECRET_KEY']}",
        "Content-Type": "application/json",
    }

    response = requests.post(PAYSTACK_CHARGE_URL, json=payload, headers=headers)
    data = response.json()

    if not response.ok:
        raise Exception(f"Paystack error: {data}")

    return data

