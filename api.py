
from flask import Flask, jsonify, request
from flask_cors import CORS

from market_data import get_market_data, SYMBOLS
from analyzer import analyze_market

app = Flask(__name__)
CORS(app)

ALLOWED_SYMBOLS = list(SYMBOLS.keys())


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "name": "SAMANDER AI API",
        "status": "online",
        "supported_symbols": len(ALLOWED_SYMBOLS),
        "symbols": ALLOWED_SYMBOLS,
        "markets": ["Crypto", "Forex", "Stocks"]
    })


@app.route("/api/analyze", methods=["GET"])
def analyze():
    symbol = request.args.get("symbol", "BTC").upper().strip()

    if symbol not in ALLOWED_SYMBOLS:
        return jsonify({
            "status": "error",
            "message": "Unsupported symbol"
        }), 400

    data = get_market_data(symbol)

    if data is None or data.empty:
        return jsonify({
            "status": "error",
            "symbol": symbol,
            "message": "Market data is currently unavailable"
        }), 503

    try:
        result = analyze_market(data)

        if not isinstance(result, dict):
            result = {"analysis": result}

        result["status"] = "success"
        result["symbol"] = symbol
        result["timeframe"] = "1m"
        result["price"] = float(data["close"].iloc[-1])

        result["candles"] = [
            {
                "time": str(index),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"])
            }
            for index, row in data.tail(30).iterrows()
        ]

        result["last_candle_time"] = str(data.index[-1])

        return jsonify(result)

    except Exception as error:
        print("Analysis error:", error)

        return jsonify({
            "status": "error",
            "symbol": symbol,
            "message": "Analysis could not be completed"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
    
