import requests
from flask import current_app

def initiate_vendor_payout(vendor_account_number: str, bank_code: str, amount: float, narration: str):
    """
    Call Monnify's payout (settlement) API to pay vendor.
    """
    url = current_app.config["MONNIFY_PAYOUT_URL"]
    headers = {
        "Authorization": f"Bearer {current_app.config['MONNIFY_SECRET_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": amount,
        "accountNumber": vendor_account_number,
        "bankCode": bank_code,
        "narration": narration,
        "reference": generate_unique_reference()
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    return resp.json()

