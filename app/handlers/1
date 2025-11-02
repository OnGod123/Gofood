from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User, CentralAccount, FullName

central_bp = Blueprint("central", __name__, url_prefix="/central")

@central_bp.route("/fund_wallet", methods=["POST"])
def fund_wallet_instructions():
    """
    Provide instructions to user on how to fund their wallet via central account.
    User sends full name + phone, receives central account details + narration format.
    """
    data = request.get_json()
    phone = data.get("phone")
    full_name = data.get("full_name")

    if not phone or not full_name:
        return jsonify({"error": "Both phone and full_name are required"}), 400

    # Find user
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Ensure FullName exists or create
    fullname_record = FullName.query.filter_by(user_id=user.id).first()
    if not fullname_record:
        fullname_record = FullName(user_id=user.id, full_name=full_name)
        db.session.add(fullname_record)
        db.session.commit()

    # Get central account info
    central = CentralAccount.query.first()
    if not central:
        return jsonify({"error": "Central account not configured"}), 500

    # Provide instructions for user to fund wallet
    instructions = {
        "message": "Use the following details to fund your GoFood wallet",
        "central_account_number": central.account_number,
        "bank_name": central.bank_name,
        "amount": "Enter amount you wish to fund",
        "narration": f"{full_name} | {phone}",  # required for matching SMS
        "note": "Ensure you put your full name and phone in the narration/remark field so it can be auto-credited."
    }

    return jsonify(instructions), 200
