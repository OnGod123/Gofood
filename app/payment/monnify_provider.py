import requests
import uuid
from flask import current_app
from .base_provider import PaymentProvider

class MonnifyProvider(PaymentProvider):
    """
    Monnify payment provider integration.
    """

    def __init__(self):
        self.api_key = current_app.config.get("MONNIFY_API_KEY")
        self.secret = current_app.config.get("MONNIFY_SECRET")
        self.base_url = current_app.config.get("MONNIFY_BASE_URL", "https://sandbox.monnify.com/api/v1")

        if not self.api_key or not self.secret:
            raise RuntimeError("Monnify API credentials not set")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}:{self.secret}",
            "Content-Type": "application/json"
        }

    def initialize_payment(self, user, amount: float, currency: str = "NGN", redirect_url: str = None) -> dict:
        """
        Initialize Monnify payment.
        Returns dict with at least: {'payment_link', 'reference'}
        """
        reference = str(uuid.uuid4())
        payload = {
            "tx_ref": reference,
            "amount": float(amount),
            "currency": currency,
            "customer_name": getattr(user, "name", getattr(user, "phone", "Unknown")),
            "customer_email": getattr(user, "email", f"{getattr(user,'phone','no-reply')}@example.local")
        }

        if redirect_url:
            payload["redirect_url"] = redirect_url
        elif current_app.config.get("PAYMENT_REDIRECT_URL"):
            payload["redirect_url"] = current_app.config.get("PAYMENT_REDIRECT_URL")

        url = f"{self.base_url}/payments/init"
        resp = requests.post(url, json=payload, headers=self._headers(), timeout=15)
        data = resp.json()

        if not data.get("success"):
            raise RuntimeError(f"Monnify init failed: {data}")

        payment_link = data["data"].get("payment_url") or data["data"].get("checkout_link")
        return {"payment_link": payment_link, "reference": reference}

    def verify_payment(self, reference: str) -> dict:
        """
        Verify Monnify payment status.
        Returns dict: {'status': 'successful'|'failed', 'amount': float, 'reference': str}
        """
        url = f"{self.base_url}/payments/{reference}/verify"
        resp = requests.get(url, headers=self._headers(), timeout=15)
        data = resp.json()

        if not data.get("success"):
            raise RuntimeError(f"Monnify verify failed: {data}")

        return {
            "status": data["data"].get("status", "failed"),
            "amount": float(data["data"].get("amount", 0)),
            "reference": reference
        }

