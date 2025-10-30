from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route("/dashboard")
def dashboard():
    user_data = {
        "id": 1,
        "name": "Vincent",
        "role": "admin",
        "notifications": 3
    }

    # --- If request comes from mobile app (JSON expected)
    if request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']:
        return jsonify(user_data)
    
    # --- Otherwise render HTML (for browser)
    return render_template("dashboard.html", user=user_data)

