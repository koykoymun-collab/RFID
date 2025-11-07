from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your phone front-end if needed

# Accounts data (RFID UID -> name and balance)
accounts = {
    "MAANGAS": {"name": "Jarred Pablo", "balance": 150.0},
    "5678EFGH": {"name": "Student 2", "balance": 75.0}
}

# Food menu (barcode -> item name & price)
menu = {
    "886467100079": {"item": "Pringles", "price": 137.0},
    "222222": {"item": "Fries", "price": 25.0},
    "333333": {"item": "Soda", "price": 20.0}
}

# Transaction log
transactions = []

# Home page (web interface)
@app.route("/")
def home():
    return render_template("index.html")  # This will be the phone interface

# Scan RFID endpoint (optional: if you have an RFID reader that POSTs here)
@app.route("/scan_rfid", methods=["POST"])
def scan_rfid():
    data = request.json or {}
    uid = data.get("uid")
    if not uid:
        return jsonify({"status": "error", "message": "Missing uid"}), 400

    if uid in accounts:
        return jsonify({
            "status": "success",
            "name": accounts[uid]["name"],
            "balance": accounts[uid]["balance"]
        })
    else:
        return jsonify({"status": "error", "message": "RFID not found"}), 404

# Purchase endpoint (scan barcode)
@app.route("/purchase", methods=["POST"])
def purchase():
    data = request.json or {}
    uid = data.get("uid")
    barcode = data.get("barcode")

    if not uid or not barcode:
        return jsonify({"status": "error", "message": "Missing uid or barcode"}), 400

    if uid not in accounts:
        return jsonify({"status": "error", "message": "RFID not found"}), 404
    if barcode not in menu:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    item = menu[barcode]["item"]
    price = menu[barcode]["price"]

    if accounts[uid]["balance"] < price:
        return jsonify({"status": "error", "message": "Insufficient balance"}), 400

    accounts[uid]["balance"] -= price
    tx = {
        "uid": uid,
        "name": accounts[uid]["name"],
        "item": item,
        "price": price,
        "time": datetime.datetime.now().isoformat()
    }
    transactions.append(tx)

    return jsonify({
        "status": "success",
        "item": item,
        "price": price,
        "new_balance": accounts[uid]["balance"],
        "transactions": [t for t in transactions if t["uid"] == uid]
    })

# Add balance endpoint (supervisor)
@app.route("/add_balance", methods=["POST"])
def add_balance():
    data = request.json or {}
    uid = data.get("uid")
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid amount"}), 400

    if uid not in accounts:
        return jsonify({"status": "error", "message": "RFID not found"}), 404

    accounts[uid]["balance"] += amount
    return jsonify({
        "status": "success",
        "name": accounts[uid]["name"],
        "new_balance": accounts[uid]["balance"]
    })

if __name__ == "__main__":
    # For development only. Use a proper WSGI server in production.
    app.run(host="0.0.0.0", port=5000, debug=True)
