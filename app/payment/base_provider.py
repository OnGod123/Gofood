from abc import ABC, abstractmethod

class PaymentProvider(ABC):
    """Base interface for all payment providers."""

    @abstractmethod
    def initialize_payment(self, user, amount: float) -> dict:
        """Initiate payment (returns a dict with at least authorization_url and reference)."""
        pass

    @abstractmethod
    def verify_payment(self, reference: str) -> dict:
        """Verify payment status via provider API.
        Should return a dict with at least: {'status': 'success'|'failed', 'amount': float, 'reference': str}
        """
        pass

