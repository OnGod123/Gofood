@wallet_payment_bp.route("/wallet/fund", methods=["POST"])
@verify_jwt_token
def fund_wallet(current_user):
    """
    Add test funds to wallet (for demonstration).
    """
    try:
        data = request.get_json()
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        wallet = Wallet.query.filter_by(user_id=current_user.id).first()
        if not wallet:
            wallet = Wallet(user_id=current_user.id, balance=0.0)
            db.session.add(wallet)

        wallet.credit(amount)
        db.session.commit()

        return jsonify({
            "message": f"Wallet funded with ₦{amount}",
            "new_balance": wallet.balance
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to fund wallet", "details": str(e)}), 500

