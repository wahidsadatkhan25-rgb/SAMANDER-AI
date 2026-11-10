import pandas as pd
import numpy as np


def analyze_market(data):
    if data is None or len(data) < 60:
        return {"status": "Not enough candle data"}

    df = data.copy()

    df.columns = [str(c).lower() for c in df.columns]

    required = ["open", "high", "low", "close"]

    if not all(c in df.columns for c in required):
        return {"status": "Invalid candle data"}

    df = df.dropna(subset=required)

    if len(df) < 60:
        return {"status": "Not enough valid candles"}

    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()

    delta = df["close"].diff()

    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()

    rs = gain / loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))

    last = df.iloc[-1]
    previous = df.iloc[-2]

    body = abs(last["close"] - last["open"])
    candle_range = last["high"] - last["low"]

    upper_wick = last["high"] - max(
        last["open"], last["close"]
    )

    lower_wick = min(
        last["open"], last["close"]
    ) - last["low"]

    patterns = []

    if (
        previous["close"] < previous["open"]
        and last["close"] > last["open"]
        and last["close"] > previous["open"]
        and last["open"] < previous["close"]
    ):
        patterns.append("Bullish Engulfing")

    if (
        previous["close"] > previous["open"]
        and last["close"] < last["open"]
        and last["close"] < previous["open"]
        and last["open"] > previous["close"]
    ):
        patterns.append("Bearish Engulfing")

    if (
        lower_wick > body * 2
        and upper_wick < body
        and body > 0
    ):
        patterns.append("Hammer")

    if (
        upper_wick > body * 2
        and lower_wick < body
        and body > 0
    ):
        patterns.append("Shooting Star")

    recent = df.tail(20)

    ema_difference = abs(
        last["ema20"] - last["ema50"]
    ) / last["close"]

    if ema_difference < 0.001:
        market = "Possible Range"
    elif last["ema20"] > last["ema50"]:
        market = "Uptrend"
    else:
        market = "Downtrend"

    return {
        "status": "Analysis complete",
        "market": market,
        "price": round(float(last["close"]), 6),
        "rsi": round(float(last["rsi"]), 2)
        if pd.notna(last["rsi"]) else None,
        "ema20": round(float(last["ema20"]), 6),
        "ema50": round(float(last["ema50"]), 6),
        "patterns": patterns or ["No recognized pattern"],
        "candles_checked": len(df)
    }
