
from .paystack_provider import PaystackProvider

def get_provider(name: str):
    name = (name or "paystack").lower().strip()
    if name == "paystack":
        return PaystackProvider()
    if name == "moniepoint":
        from .moniepoint_provider import MoniepointProvider
        return MoniepointProvider()
    raise ValueError(f"Unknown provider: {name}")

