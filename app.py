from flask import Flask, jsonify, request, abort
import os, time, hmac, hashlib, requests
from urllib.parse import urlencode

app = Flask(__name__)

API_KEY = os.environ.get('BINANCE_API_KEY')
SECRET = os.environ.get('BINANCE_SECRET_KEY')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN', 'troque-este-token')

BASE = "https://api.binance.com"

def sign_params(params: dict):
    query = urlencode(params)
    signature = hmac.new(SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    return f"{query}&signature={signature}"

@app.route('/balances', methods=['GET'])
def balances():
    auth = request.headers.get('Authorization')
    if auth != f"Bearer {ACCESS_TOKEN}":
        abort(401)
    ts = int(time.time() * 1000)
    qs = sign_params({"timestamp": ts})
    headers = {"X-MBX-APIKEY": API_KEY}
    r = requests.get(f"{BASE}/api/v3/account?{qs}", headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    result = []
    for b in data.get("balances", []):
        free = float(b.get("free", 0))
        locked = float(b.get("locked", 0))
        total = free + locked
        if total > 0:
            result.append({ "asset": b.get("asset"), "free": free, "locked": locked, "total": total })
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
