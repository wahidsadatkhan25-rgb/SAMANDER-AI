
import yfinance as yf
import pandas as pd

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

        if data is None or data.empty:
            return None

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data.columns = [str(c).lower() for c in data.columns]

        required = ["open", "high", "low", "close"]

        if not all(col in data.columns for col in required):
            return None

        return data.dropna(subset=required)

    except Exception as error:
        print(f"Market data error for {symbol}: {error}")
        return None
        
