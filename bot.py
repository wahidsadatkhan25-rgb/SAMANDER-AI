
import os
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from analyzer import analyze_market
from market_data import get_market_data

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_URL = os.getenv("RENDER_EXTERNAL_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("₿ CRYPTO", callback_data="market:crypto")],
        [InlineKeyboardButton("💱 FOREX", callback_data="market:forex")],
        [InlineKeyboardButton("📈 STOCKS", callback_data="market:stocks")]
    ]

    await update.message.reply_text(
        "🔥 SAMANDER AI\n\n"
        "MULTI-MARKET LIVE ANALYZER\n\n"
        "Choose your market:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def market_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    markets = {
        "crypto": ["BTC", "ETH", "SOL"],
        "forex": ["EURUSD", "GBPUSD"],
        "stocks": ["AAPL", "TSLA", "NVDA"]
    }

    selected = query.data.split(":")[1]

    keyboard = [
        [InlineKeyboardButton(
            symbol,
            callback_data=f"analyze:{symbol}"
        )]
        for symbol in markets[selected]
    ]

    keyboard.append([
        InlineKeyboardButton("⬅️ BACK", callback_data="back")
    ])

    await query.edit_message_text(
        f"Select {selected.upper()} symbol:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def analyze_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    symbol = query.data.split(":")[1]

    await query.edit_message_text(f"Analyzing {symbol}...")

    try:
        data = await asyncio.to_thread(get_market_data, symbol)

        if data is None or data.empty:
            await query.message.reply_text("Market data unavailable.")
            return

        result = analyze_market(data)

        if result.get("status") != "Analysis complete":
            await query.message.reply_text(result["status"])
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
            "Educational market analysis."
        )

        await query.message.reply_text(message)

    except Exception:
        logging.exception("Analysis failed")
        await query.message.reply_text(
            "Analysis error. Please try again."
        )


async def back_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("₿ CRYPTO", callback_data="market:crypto")],
        [InlineKeyboardButton("💱 FOREX", callback_data="market:forex")],
        [InlineKeyboardButton("📈 STOCKS", callback_data="market:stocks")]
    ]

    await query.edit_message_text(
        "🔥 SAMANDER AI\n\nChoose your market:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def main():
    if not TOKEN or not PUBLIC_URL:
        raise RuntimeError("BOT_TOKEN or RENDER_EXTERNAL_URL missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(market_buttons, pattern=r"^market:"))
    app.add_handler(CallbackQueryHandler(analyze_button, pattern=r"^analyze:"))
    app.add_handler(CallbackQueryHandler(back_button, pattern=r"^back$"))

    port = int(os.getenv("PORT", "10000"))

    print("SAMANDER AI starting...")

    await app.bot.set_webhook(
        url=f"{PUBLIC_URL}/{TOKEN}"
    )

    await app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=TOKEN,
        webhook_url=f"{PUBLIC_URL}/{TOKEN}"
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    
