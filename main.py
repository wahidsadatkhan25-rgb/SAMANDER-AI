import logging
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 SAMANDER AI\n\n"
        "Multi-Market Chart Analyzer\n\n"
        "Select a market:\n"
        "/crypto\n"
        "/forex\n"
        "/stocks\n"
        "/help"
    )


async def crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "₿ CRYPTO ANALYZER\n"
        "Market: Cryptocurrency\n"
        "Timeframe: 1 minute\n"
        "Waiting for market selection..."
    )


async def forex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💱 FOREX ANALYZER\n"
        "Market: Forex\n"
        "Timeframe: 1 minute\n"
        "Waiting for market selection..."
    )


async def stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 STOCK ANALYZER\n"
        "Market: Stocks\n"
        "Timeframe: 1 minute\n"
        "Waiting for market selection..."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "SAMANDER AI Help\n\n"
        "This bot studies real market candles,\n"
        "patterns, trends and confirmations."
    )


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("crypto", crypto))
    app.add_handler(CommandHandler("forex", forex))
    app.add_handler(CommandHandler("stocks", stocks))
    app.add_handler(CommandHandler("help", help_command))

    print("SAMANDER AI is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
