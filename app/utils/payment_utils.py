import requests
import uuid
from flask import current_app

def generate_moniepoint_payment_link(full_name: str, amount: float):
    """
    Simulate Moniepoint API call to create a top-up link.
    """
    try:
        payload = {
            "reference": str(uuid.uuid4()),
            "amount": amount,
            "currency": "NGN",
            "customer_name": full_name,
            "redirect_url": f"{current_app.config['BASE_URL']}/moniepoint/webhook"
        }

        # Example simulated API endpoint (would be actual Moniepoint sandbox endpoint)
        api_url = current_app.config.get("MONIEPOINT_API_URL", "https://api.moniepoint.com/payments/create")
        headers = {
            "Authorization": f"Bearer {current_app.config.get('MONIEPOINT_SECRET_KEY', 'test_key')}",
            "Content-Type": "application/json"
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("payment_url", "")
        return None
    except Exception:
        return None

