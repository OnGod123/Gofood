import uuid
import requests
from flask import current_app

MONNIFY_TRANSFER_URL = "https://api.monnify.com/api/v2/disbursements/single"

def monnify_charge(*, account_number, bank_code, amount, customer_name, customer_email):
    payload = {
        "amount": amount,
        "reference": f"MNF-{uuid.uuid4().hex[:10]}",
        "narration": f"Payout to {customer_name}",
        "bankCode": bank_code,
        "accountNumber": account_number,
        "walletId": current_app.config["MONNIFY_WALLET_ID"]
    }

    headers = {
        "Authorization": f"Bearer {current_app.config['MONNIFY_ACCESS_TOKEN']}",
        "Content-Type": "application/json",
    }

    response = requests.post(MONNIFY_TRANSFER_URL, json=payload, headers=headers)
    data = response.json()

    if not response.ok:
        raise Exception(f"Monnify error: {data}")

    return data

