import requests
from flask import current_app

FLUTTERWAVE_TRANSFER_URL = "https://api.flutterwave.com/v3/transfers"

def flutterwave_charge_bank(*, tx_ref, amount, bank_code, account_number, email):
    payload = {
        "account_bank": bank_code,
        "account_number": account_number,
        "amount": amount,
        "narration": f"Payout for {email}",
        "currency": "NGN",
        "reference": tx_ref
    }

    headers = {
        "Authorization": f"Bearer {current_app.config['FLW_SECRET_KEY']}",
        "Content-Type": "application/json",
    }

    response = requests.post(FLUTTERWAVE_TRANSFER_URL, json=payload, headers=headers)
    data = response.json()

    if not response.ok:
        raise Exception(f"Flutterwave error: {data}")

    return data

