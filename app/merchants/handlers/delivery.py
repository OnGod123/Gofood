from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app.extensions import db
from app.merchant.Database.delivery import Delivery

@delivery_bp.route("/delivery/<int:delivery_id>/bargain")
def bargain_page(delivery_id):
    return render_template("bargain.html", delivery_id=delivery_id)


