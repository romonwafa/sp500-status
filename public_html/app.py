from flask import Flask, jsonify, render_template
from flask_cors import CORS
import yfinance as yf
import time

app = Flask(__name__)
CORS(app)

cached_data = {
    "timestamp": 0,
    "status": None,
    "percent_change": None
}

CACHE_DURATION = 300  # 5 minutes in seconds

def get_percent_change():
    ticker = yf.Ticker("^GSPC")
    data = ticker.history(period="2d")

    if len(data) < 2:
        raise ValueError("Not enough data to calculate change")

    prev_close = data['Close'].iloc[-2]
    latest_close = data['Close'].iloc[-1]
    percent_change = ((latest_close - prev_close) / prev_close) * 100
    return round(percent_change, 2)

def get_cached_status():
    now = time.time()
    if now - cached_data["timestamp"] > CACHE_DURATION:
        percent_change = get_percent_change()
        status = "up" if percent_change >= 0 else "down"
        cached_data["timestamp"] = now
        cached_data["percent_change"] = percent_change
        cached_data["status"] = status
    return cached_data["status"], cached_data["percent_change"]

@app.route('/status')
def market_status():
    try:
        status, percent_change = get_cached_status()
        return jsonify({"status": status, "percent": percent_change})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    try:
        status, percent_change = get_cached_status()
        return render_template('index.html', status=status, percent_change=percent_change)
    except Exception as e:
        return f"Error loading page: {e}", 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
