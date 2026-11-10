
import yfinance as yf
import pandas as pd
import time

SYMBOLS = {
    # Crypto
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
    "DOGE": "DOGE-USD",
    "ADA": "ADA-USD",
    "TRX": "TRX-USD",
    "AVAX": "AVAX-USD",
    "LINK": "LINK-USD",
    "DOT": "DOT-USD",
    "LTC": "LTC-USD",
    "BCH": "BCH-USD",
    "TON": "TON11419-USD",
    "SHIB": "SHIB-USD",
    "PEPE": "PEPE24478-USD",
    "SUI": "SUI20947-USD",
    "NEAR": "NEAR-USD",
    "APT": "APT21794-USD",
    "UNI": "UNI-USD",

    # Forex
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "USDCHF": "USDCHF=X",
    "USDCAD": "USDCAD=X",
    "AUDUSD": "AUDUSD=X",
    "NZDUSD": "NZDUSD=X",
    "EURJPY": "EURJPY=X",
    "GBPJPY": "GBPJPY=X",
    "EURGBP": "EURGBP=X",
    "AUDJPY": "AUDJPY=X",
    "EURAUD": "EURAUD=X",
    "GBPAUD": "GBPAUD=X",
    "CADJPY": "CADJPY=X",
    "CHFJPY": "CHFJPY=X",
    "EURNZD": "EURNZD=X",
    "GBPCAD": "GBPCAD=X",
    "AUDCAD": "AUDCAD=X",
    "NZDCAD": "NZDCAD=X",
    "EURCHF": "EURCHF=X",

    # Stocks
    "AAPL": "AAPL",
    "TSLA": "TSLA",
    "NVDA": "NVDA",
    "MSFT": "MSFT",
    "AMZN": "AMZN",
    "GOOGL": "GOOGL",
    "META": "META",
    "NFLX": "NFLX",
    "AMD": "AMD",
    "INTC": "INTC",
    "COIN": "COIN",
    "PLTR": "PLTR",
    "ORCL": "ORCL",
    "IBM": "IBM",
    "DIS": "DIS"
}


def clean_market_data(data, ticker):
    if data is None or data.empty:
        return None

    if isinstance(data.columns, pd.MultiIndex):
        # Handle different yfinance column layouts
        for level in range(data.columns.nlevels):
            values = data.columns.get_level_values(level)

            if ticker in values:
                data = data.xs(ticker, axis=1, level=level)
                break
        else:
            for level in range(data.columns.nlevels):
                values = set(
                    str(value).lower()
                    for value in data.columns.get_level_values(level)
                )

                if {"open", "high", "low", "close"}.issubset(values):
                    data.columns = data.columns.get_level_values(level)
                    break

    data.columns = [str(col).lower() for col in data.columns]

    required = ["open", "high", "low", "close"]

    if not all(col in data.columns for col in required):
        return None

    data = data.dropna(subset=required)
    data = data[~data.index.duplicated(keep="last")]
    data = data.sort_index()

    if data.empty:
        return None

    return data


def get_market_data(symbol):
    symbol = symbol.upper().strip()
    ticker = SYMBOLS.get(symbol)

    if not ticker:
        print(f"Unknown symbol: {symbol}")
        return None

    # Try Yahoo Finance download first
    for attempt in range(2):
        try:
            data = yf.download(
                ticker,
                period="5d",
                interval="1m",
                progress=False,
                auto_adjust=True,
                threads=False,
                timeout=20
            )

            cleaned = clean_market_data(data, ticker)

            if cleaned is not None and len(cleaned) >= 2:
                print(f"{symbol}: received {len(cleaned)} candles")
                return cleaned

        except Exception as error:
            print(f"Download attempt {attempt + 1} failed for {symbol}: {error}")

        time.sleep(1)

    # Second method: ticker history
    try:
        data = yf.Ticker(ticker).history(
            period="5d",
            interval="1m",
            auto_adjust=True,
            timeout=20
        )

        cleaned = clean_market_data(data, ticker)

        if cleaned is not None and len(cleaned) >= 2:
            print(f"{symbol}: received {len(cleaned)} candles using fallback")
            return cleaned

    except Exception as error:
        print(f"History fallback failed for {symbol}: {error}")

    print(f"{symbol}: no usable 1-minute data available")
    return None
                               
