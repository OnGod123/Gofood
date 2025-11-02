import requests
from flask import current_app
from .base_provider import PaymentProvider

class PaystackProvider(PaymentProvider):
    def __init__(self):
        self.secret_key = current_app.config.get("PAYSTACK_SECRET_KEY")
        self.base_url = "https://api.paystack.co"

    def _headers(self):
        return {"Authorization": f"Bearer {self.secret_key}", "Content-Type": "application/json"}

    def initialize_payment(self, user, amount: float):
        url = f"{self.base_url}/transaction/initialize"
        payload = {"email": getattr(user, "email", "no-reply@example.com"), "amount": int(float(amount) * 100)}
        r = requests.post(url, json=payload, headers=self._headers(), timeout=10)
        resp = r.json()
        if not resp.get("status"):
            raise Exception(f"Paystack init failed: {resp}")
        return {"authorization_url": resp["data"]["authorization_url"], "reference": resp["data"]["reference"]}

    def verify_payment(self, reference: str):
        url = f"{self.base_url}/transaction/verify/{reference}"
        r = requests.get(url, headers=self._headers(), timeout=10)
        resp = r.json()
        if not resp.get("status"):
            raise Exception(f"Paystack verify failed: {resp}")
        amount = resp["data"]["amount"] / 100.0
        status = resp["data"]["status"]
        return {"status": status, "amount": amount, "reference": reference}

