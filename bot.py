import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from analyzer import analyze_market
from market_data import get_market_data

TOKEN = __import__("os").getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 SAMANDER AI\n\n"
        "MULTI-MARKET ANALYZER\n\n"
        "Select a market:\n\n"
        "₿ Crypto: /analyze BTC\n"
        "💱 Forex: /analyze EURUSD\n"
        "📈 Stocks: /analyze AAPL\n\n"
        "Other symbols:\n"
        "ETH, GBPUSD, TSLA\n\n"
        "Timeframe: 1 Minute"
    )


async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Example: /analyze BTC"
        )
        return

    symbol = context.args[0].upper()

    await update.message.reply_text(
        f"🔍 SAMANDER AI\nAnalyzing {symbol}..."
    )

    data = await asyncio.to_thread(get_market_data, symbol)

    if data is None or data.empty:
        await update.message.reply_text(
            "Market data unavailable. Try again later."
        )
        return

    result = analyze_market(data)

    if result.get("status") != "Analysis complete":
        await update.message.reply_text(result["status"])
        return

    patterns = ", ".join(result["patterns"])

    message = (
        f"🔥 SAMANDER AI\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: 1 Minute\n"
        f"Price: {result['price']}\n"
        f"Market: {result['market']}\n"
        f"RSI: {result['rsi']}\n"
        f"EMA 20: {result['ema20']}\n"
        f"EMA 50: {result['ema50']}\n\n"
        f"Patterns: {patterns}\n\n"
        f"Candles checked: {result['candles_checked']}\n"
        f"Educational chart analysis only."
    )

    await update.message.reply_text(message)


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))

    print("SAMANDER AI starting...")

    app.run_polling()


if __name__ == "__main__":
    main()
