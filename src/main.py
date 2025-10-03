import argparse
import datetime
import time
from typing import List

import pytz

from . import signals as sg
from . import analysis as an
from . import data_sources as ds

# Notifiers & config
from .whatsapp_alert import send_whatsapp_alert
from .config import (
    DEFAULT_SYMBOLS,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    WHATSAPP_TO,
)

# Telegram (optional): اگر telegram_bot.py موجود ہے تو import ہو جائے گا ورنہ safe fallback رہے گا
try:
    from .telegram_bot import send_telegram_message  # type: ignore
except Exception:
    def send_telegram_message(*args, **kwargs):
        print("[Telegram not available] Fallback to print/WhatsApp.")


def _fmt_technical(tech: dict) -> str:
    """
    tech = {
      'rsi': float|None,
      'macd_hist': float|None,
      'sma_trend': float,
      'signal': float
    }
    """
    if not tech or not isinstance(tech, dict):
        return "N/A"
    parts = []
    if "signal" in tech and tech["signal"] is not None:
        parts.append(f"{tech['signal']:+.2f}")
    if "rsi" in tech and tech["rsi"] is not None:
        parts.append(f"RSI={tech['rsi']:.1f}")
    if "macd_hist" in tech and tech["macd_hist"] is not None:
        parts.append(f"MACD={tech['macd_hist']:+.3f}")
    if "sma_trend" in tech:
        parts.append(f"Trend={int(tech['sma_trend'])}")
    return ", ".join(parts) if parts else "N/A"


def analyze_symbol(symbol: str) -> str:
    """Analyze one symbol and return a formatted WhatsApp/Telegram-friendly message."""
    print(f"Analyzing {symbol}...")

    # --- Fetch data (robust even if sources return little/none) ---
    df = ds.fetch_price_history(symbol, period="6mo", interval="1d")
    fundamentals = ds.fetch_fundamentals_snapshot(symbol) or {}
    news = ds.fetch_news_headlines(symbol, max_articles=5) or []
    tweets = ds.fetch_twitter_recent(symbol, max_results=20) or []

    # --- Compute scores ---
    tech = sg.compute_technicals(df) or {}
    tech_score = float(tech.get("signal", 0.0)) if isinstance(tech, dict) else 0.0

    texts = []
    try:
        texts += [n.get("title", "") for n in news]
    except Exception:
        pass
    try:
        texts += [t.get("text", "") for t in tweets]
    except Exception:
        pass
    sentiment = float(an.sentiment_from_texts(texts)) if texts else 0.0

    fund_score = float(sg.fundamentals_to_score(fundamentals))

    score = float(sg.aggregate_scores(tech_score, sentiment, fund_score))
    decision = sg.decision_from_score(score)

    # --- Pretty formatting (PKT time + emojis) ---
    emoji_map = {"BUY": "🟢", "SELL": "🔴", "NEUTRAL": "⚪"}
    tz = pytz.timezone("Asia/Karachi")
    now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M")

    tech_line = _fmt_technical(tech)
    msg = (
        f"📊 *Market Alert* ({now} PKT)\n\n"
        f"💰 *Symbol:* `{symbol}`\n"
        f"📈 *Decision:* {emoji_map.get(decision, '❔')} {decision}\n"
        f"⚖️ *Score:* {score:+.2f}\n\n"
        f"🔹 *Technical:* {tech_line}\n"
        f"🔹 *Sentiment:* {sentiment:+.2f}\n"
        f"🔹 *Fundamentals:* {fund_score:+.2f}"
    )
    return msg


def run_once(symbols: List[str], notify: bool = True) -> None:
    """Run analysis once over a list of symbols and notify based on configured channels."""
    for sym in symbols:
        sym = sym.strip()
        if not sym:
            continue
        msg = analyze_symbol(sym)

        if notify:
            # Prefer Telegram if configured, else WhatsApp, else print
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg)
            elif TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and WHATSAPP_TO:
                send_whatsapp_alert(msg)
            else:
                print("[No notifier configured] Printed locally.\n")
                print(msg)
        else:
            print(msg)


def main():
    parser = argparse.ArgumentParser(description="Market Alert Bot (WhatsApp/Telegram)")
    parser.add_argument(
        "--symbols",
        type=str,
        default="",
        help="Comma-separated symbols (e.g., BTC-USD,ETH-USD)",
    )
    parser.add_argument(
        "--symbols-file",
        type=str,
        default="",
        help="Path to a file with one symbol per line.",
    )
    parser.add_argument(
        "--no-telegram",
        action="store_true",
        help="Do not send Telegram; allows WhatsApp/print fallback.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit.",
    )
    parser.add_argument(
        "--interval-min",
        type=int,
        default=0,
        help="If >0, run forever with this many minutes between runs.",
    )
    args = parser.parse_args()

    # Resolve symbol list
    symbols: List[str] = []
    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    elif args.symbols_file:
        try:
            with open(args.symbols_file, "r", encoding="utf-8") as f:
                symbols = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print("Failed to read symbols file:", e)
    if not symbols:
        symbols = list(DEFAULT_SYMBOLS)

    # Notify flag: we still allow WhatsApp even if --no-telegram is passed
    notify = True  # overall notification switch
    if args.once:
        run_once(symbols, notify=notify)
        return

    # Looping mode
    interval = int(args.interval_min) if args.interval_min and args.interval_min > 0 else 30
    print(f"Running in loop mode every {interval} minutes. Press Ctrl+C to stop.")
    while True:
        try:
            run_once(symbols, notify=notify)
        except Exception as e:
            print("Run error:", e)
        time.sleep(interval * 60)


if __name__ == "__main__":
    main()
