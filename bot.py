import os
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from analyzer import analyze_market
from market_data import get_market_data

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_URL = os.getenv("RENDER_EXTERNAL_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 SAMANDER AI\n\n"
        "MULTI-MARKET CHART ANALYZER\n\n"
        "Crypto: /analyze BTC\n"
        "Forex: /analyze EURUSD\n"
        "Stocks: /analyze AAPL\n\n"
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
        f"Analyzing {symbol}..."
    )

    data = await asyncio.to_thread(
        get_market_data, symbol
    )

    if data is None or data.empty:
        await update.message.reply_text(
            "Market data unavailable."
        )
        return

    result = analyze_market(data)

    if result.get("status") != "Analysis complete":
        await update.message.reply_text(result["status"])
        return

    message = (
        f"🔥 SAMANDER AI\n\n"
        f"Symbol: {symbol}\n"
        f"Timeframe: 1 Minute\n"
        f"Price: {result['price']}\n"
        f"Market: {result['market']}\n"
        f"RSI: {result['rsi']}\n"
        f"EMA20: {result['ema20']}\n"
        f"EMA50: {result['ema50']}\n"
        f"Patterns: {', '.join(result['patterns'])}\n\n"
        "Educational chart analysis."
    )

    await update.message.reply_text(message)


def main():
    if not TOKEN or not PUBLIC_URL:
        raise RuntimeError(
            "BOT_TOKEN or RENDER_EXTERNAL_URL missing"
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("analyze", analyze))

    port = int(os.getenv("PORT", "10000"))

    print("SAMANDER AI webhook starting...")

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"{PUBLIC_URL}/{TOKEN}"
    )


if __name__ == "__main__":
    main()
