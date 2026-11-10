
from flask import Flask, jsonify, request
import pandas as pd

from market_data import get_market_data
from analyzer import analyze_market

app = Flask(__name__)

ALLOWED_SYMBOLS = [
    "BTC", "ETH", "EURUSD",
    "GBPUSD", "AAPL", "TSLA"
]


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response


@app.route("/")
def home():
    return jsonify({
        "name": "SAMANDER AI API",
        "status": "online"
    })


@app.route("/api/analyze", methods=["GET"])
def analyze():
    symbol = request.args.get("symbol", "").upper()

    if symbol not in ALLOWED_SYMBOLS:
        return jsonify({
            "error": "Unsupported symbol"
        }), 400

    try:
        data = get_market_data(symbol)

        if data is None or data.empty:
            return jsonify({
                "error": "Market data unavailable"
            }), 503

        result = analyze_market(data)

        if result.get("status") != "Analysis complete":
            return jsonify(result), 503

        candles = []

        for timestamp, row in data.tail(30).iterrows():
            candles.append({
                "time": pd.Timestamp(timestamp).isoformat(),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"])
            })

        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": "1m",
            "price": result["price"],
            "market": result["market"],
            "rsi": result["rsi"],
            "ema20": result["ema20"],
            "ema50": result["ema50"],
            "patterns": result["patterns"],
            "candles": candles,
            "last_candle_time": candles[-1]["time"]
        })

    except Exception as error:
        app.logger.exception("Analysis error")
        return jsonify({
            "error": "Analysis failed"
        }), 500
      
