import requests
import uuid
from flask import current_app

from .base_provider import PaymentProvider

class FlutterwaveProvider(PaymentProvider):
    """
    Implements PaymentProvider for Flutterwave (v3).
    - initialize_payment -> POST /v3/payments (Standard checkout)
    - verify_payment     -> GET /v3/transactions/{id}/verify
    """

    def __init__(self):
        self.secret_key = current_app.config.get("FLUTTERWAVE_SECRET_KEY")
        # use sandbox or production base depending on config
        if current_app.config.get("FLUTTERWAVE_SANDBOX", True):
            self.base_url = "https://api.flutterwave.com/v3"
        else:
            self.base_url = "https://api.flutterwave.com/v3"

        if not self.secret_key:
            raise RuntimeError("FLUTTERWAVE_SECRET_KEY not set in config")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

    def initialize_payment(self, user, amount: float, currency: str = "NGN", redirect_url: str = None) -> dict:
        """
        Create a Flutterwave checkout link.
        Returns: {"payment_link": "...", "tx_ref": "...", "transaction_id": ...opt}
        """
        tx_ref = f"{uuid.uuid4().hex}:{user.id}"
        payload = {
            "tx_ref": tx_ref,
            "amount": float(amount),
            "currency": currency,
            "customer": {
                "email": getattr(user, "email", f"{getattr(user,'phone','no-reply')}@example.local"),
                "phonenumber": getattr(user, "phone", None),
                "name": getattr(user, "name", None) or getattr(user, "phone", "")
            },
            # optional: specify payment options, meta, customizations
            "meta": {"user_id": str(user.id)},
        }

        # redirect_url is recommended; set from app config if not provided
        redirect = redirect_url or current_app.config.get("PAYMENT_REDIRECT_URL")
        if redirect:
            payload["redirect_url"] = redirect

        url = f"{self.base_url}/payments"
        resp = requests.post(url, json=payload, headers=self._headers(), timeout=15)
        try:
            data = resp.json()
        except Exception:
            raise RuntimeError(f"Flutterwave init: invalid json response: {resp.text}")

        # check response structure
        if not data.get("status") or data.get("status").lower() != "success":
            raise RuntimeError(f"Flutterwave init failed: {data}")

        # Standard returns data.link (checkout)
        link = data["data"].get("link") or data["data"].get("checkout_link") or data["data"].get("authorization_url")
        reference = data["data"].get("id") or data["data"].get("tx_ref") or tx_ref

        return {"payment_link": link, "reference": reference, "tx_ref": tx_ref}

    def verify_payment(self, reference: str) -> dict:
        """
        Verify transaction by transaction id (the 'id' from Flutterwave) or by tx_ref using endpoint.
        We will try to use the transactions/{id}/verify endpoint. The webhook payload usually includes data.id.
        Returns dict: {"status": "successful"|"failed", "amount": float, "currency": str, "reference": str, "data": {...}}
        """
        # The verify endpoint expects the transaction id (an integer) most commonly.
        # Sometimes you have tx_ref; you can call GET /transactions?tx_ref=... but official verify uses id.
        url_by_id = f"{self.base_url}/transactions/{reference}/verify"
        r = requests.get(url_by_id, headers=self._headers(), timeout=15)
        try:
            body = r.json()
        except Exception:
            raise RuntimeError(f"Flutterwave verify: invalid json response: {r.text}")

        # If it returns 404 or similar and reference is not id, try search by tx_ref
        if r.status_code == 404 or not body.get("status"):
            # fallback: try search by tx_ref
            # GET /transactions?tx_ref=your_tx_ref
            url_search = f"{self.base_url}/transactions?tx_ref={reference}"
            r2 = requests.get(url_search, headers=self._headers(), timeout=15)
            try:
                body = r2.json()
            except Exception:
                raise RuntimeError(f"Flutterwave verify fallback: invalid response: {r2.text}")
            # If still invalid, raise
            if not body.get("status"):
                raise RuntimeError(f"Flutterwave verify failed: {body}")

        # body['data'] contains transaction details when success
        data = body.get("data", {})
        status = data.get("status") or body.get("status")
        amount = data.get("amount") or data.get("charged_amount") or 0.0
        currency = data.get("currency") or "NGN"
        return {
            "status": (status or "").lower(),
            "amount": float(amount),
            "currency": currency,
            "reference": reference,
            "data": data
        }

