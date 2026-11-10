import yfinance as yf
import pandas as pd

SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "AAPL": "AAPL",
    "TSLA": "TSLA"
}


def get_market_data(symbol):
    ticker = SYMBOLS.get(symbol.upper())

    if not ticker:
        return None

    try:
        data = yf.download(
            ticker,
            period="5d",
            interval="1m",
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            return None

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data.columns = [
            str(column).lower()
            for column in data.columns
        ]

        return data.dropna()

    except Exception as error:
        print("Market data error:", error)
        return None
