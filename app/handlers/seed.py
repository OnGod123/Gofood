from datetime import datetime
from app.extensions import db
from app.models import CentralAccount

def seed_central_account():
    """Create Moniepoint central account if missing"""
    existing = CentralAccount.query.filter_by(provider="moniepoint").first()
    if existing:
        return

    account = CentralAccount(
        provider="moniepoint",
        account_number="0021223344",
        bank_name="Moniepoint MFB",
        balance=500000.00,  # seed with demo float
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.session.add(account)
    db.session.commit()
    print("✅ Moniepoint central account seeded.")

