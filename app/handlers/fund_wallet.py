
from flask import Blueprint, request, jsonify
from threading import Timer
from datetime import datetime
from app.extensions import db
from app.database.user_models import User 
from app.database.payment_models import FullName, CentralAccount
from app.sms_processor import process_incoming_sms  
from app.utils.services import send_sms

central_bp = Blueprint("central", __name__, url_prefix="/central")

@central_bp.route("/fund_wallet", methods=["POST"])
def fund_wallet_instructions():
    """
    Provide instructions to user on how to fund their wallet via central account.
    Then automatically trigger SMS processor after 1 minute to simulate credit alert.
    """
    data = request.get_json()
    phone = data.get("phone")
    full_name = data.get("full_name")

    if not phone or not full_name:
        return jsonify({"error": "Both phone and full_name are required"}), 400

    # --- Step 1: Ensure user exists ---
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # --- Step 2: Ensure FullName record exists ---
    fullname_record = FullName.query.filter_by(user_id=user.id).first()
    if not fullname_record:
        fullname_record = FullName(user_id=user.id, full_name=full_name)
        db.session.add(fullname_record)
        db.session.commit()

    # --- Step 3: Get central account info ---
    central = CentralAccount.query.first()
    if not central:
        return jsonify({"error": "Central account not configured"}), 500

    # --- Step 4: Prepare funding instruction ---
    instructions = {
        "message": "Use the following details to fund your GoFood wallet",
        "central_account_number": central.account_number,
        "bank_name": central.bank_name,
        "amount": "Enter amount you wish to fund",
        "narration": f"{full_name} | {phone}",
        "note": "Ensure you put your full name and phone in the narration field."
    }

    # --- Step 5: Send user SMS instruction ---
    send_sms(phone, f"Deposit funds to {central.bank_name} ({central.account_number}) with narration '{full_name} | {phone}'")

    # --- Step 6: Trigger SMS processor after 1 minute ---
    def delayed_sms_process():
        print("📩 Auto-triggering SMS processor after 1 minute...")
        process_incoming_sms()

    Timer(60, delayed_sms_process).start()

    return jsonify({
        "message": "Funding instructions sent successfully. System will verify in 1 minute.",
        "instructions": instructions
    }), 200

