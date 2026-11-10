
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


MARKETS = {
    "crypto": ["BTC", "ETH", "SOL"],
    "forex": ["EURUSD", "GBPUSD", "USDJPY"],
    "stocks": ["AAPL", "TSLA", "NVDA"]
}


def market_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("₿ CRYPTO", callback_data="market:crypto"),
            InlineKeyboardButton("💱 FOREX", callback_data="market:forex")
        ],
        [
            InlineKeyboardButton("📈 STOCKS", callback_data="market:stocks")
        ]
    ])


def symbol_keyboard(market):
    buttons = []
    for symbol in MARKETS[market]:
        buttons.append([
            InlineKeyboardButton(
                symbol,
                callback_data=f"symbol:{symbol}"
            )
        ])

    buttons.append([
        InlineKeyboardButton("⬅️ BACK", callback_data="back")
    ])

    return InlineKeyboardMarkup(buttons)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 SAMANDER AI\n\n"
        "MULTI-MARKET CHART ANALYZER\n\n"
        "Select a market:",
        reply_markup=market_keyboard()
    )


async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    action = query.data

    if action.startswith("market:"):
        market = action.split(":")[1]

        await query.edit_message_text(
            f"🔥 SAMANDER AI\n\n"
            f"Selected: {market.upper()}\n\n"
            "Select a symbol:",
            reply_markup=symbol_keyboard(market)
        )
        return

    if action == "back":
        await query.edit_message_text(
            "🔥 SAMANDER AI\n\nSelect a market:",
            reply_markup=market_keyboard()
        )
        return

    if action.startswith("symbol:"):
        symbol = action.split(":")[1]

        await query.edit_message_text(
            f"Analyzing {symbol}...\nPlease wait."
        )

        try:
            data = await asyncio.to_thread(
                get_market_data, symbol
            )

            if data is None or data.empty:
                await query.message.reply_text(
                    "Market data unavailable. Please try again later."
                )
                return

            result = analyze_market(data)

            if result.get("status") != "Analysis complete":
                await query.message.reply_text(result["status"])
                return

            patterns = ", ".join(result["patterns"])

            message = (
                "🔥 SAMANDER AI\n\n"
                f"Symbol: {symbol}\n"
                "Timeframe: 1 Minute\n"
                f"Price: {result['price']}\n"
                f"Market: {result['market']}\n"
                f"RSI: {result['rsi']}\n"
                f"EMA20: {result['ema20']}\n"
                f"EMA50: {result['ema50']}\n"
                f"Patterns: {patterns}\n\n"
                "Educational chart analysis — "
                "not a trading instruction."
            )

            await query.message.reply_text(message)

        except Exception:
            logging.exception("Analysis failed")
            await query.message.reply_text(
                "Analysis failed. Please try again."
            )


def main():
    if not TOKEN or not PUBLIC_URL:
        raise RuntimeError(
            "BOT_TOKEN or RENDER_EXTERNAL_URL missing"
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

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
            
