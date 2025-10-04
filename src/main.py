# src/main.py
from __future__ import annotations
import os, sys, argparse, time, warnings, logging
from typing import List, Optional

# 🔇 make logs quiet & clean
warnings.filterwarnings("ignore")
logging.basicConfig(
    level=logging.ERROR,  # only errors in console
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ── Project imports
from . import data_sources as ds
from . import analysis as an
from . import signals as sg
from .whatsapp_alert import send_whatsapp_alert

# ── Small helpers
def info(msg: str) -> None:
    # neat, single-line progress messages
    print(f"✅ {msg}")

def warn(msg: str) -> None:
    print(f"⚠️  {msg}")

def err(msg: str) -> None:
    print(f"❌ {msg}")

# ── Symbol helpers
def load_symbols_from_file(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            symbols = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
        return symbols
    except Exception as e:
        err(f"Could not read symbols file '{path}': {e}")
        return []

def resolve_symbols(args) -> List[str]:
    if args.symbols:
        return [s.strip() for s in args.symbols.split(",") if s.strip()]
    if args.symbols_file:
        syms = load_symbols_from_file(args.symbols_file)
        if syms:
            return syms
    # fallback
    sample = os.path.join(os.path.dirname(__file__), "..", "sample_symbols.txt")
    syms = load_symbols_from_file(os.path.abspath(sample))
    if not syms:
        syms = ["BTC-USD", "ETH-USD"]
        warn("Using fallback symbols: BTC-USD, ETH-USD")
    return syms

# ── One-symbol analysis → text message
def analyze_symbol(symbol: str) -> Optional[str]:
    info(f"Analyzing {symbol}...")
    df = ds.fetch_price_history(symbol)
    if df is None:
        warn(f"No price data for {symbol}. Skipping.")
        return None

    # technicals (guarded inside sg)
    tech = sg.compute_technicals(df)

    # sentiment / fundamentals (guard inside 'analysis' and 'signals')
    sentiment = an.sentiment_from_texts(an.get_recent_news_and_tweets(symbol))
    fund = sg.fundamentals_to_score(symbol)  # light, mocked or real depending on your impl

    score = sg.aggregate_scores(tech_signal=tech.get("signal", 0.0),
                                sentiment=sentiment,
                                fundamentals=fund)

    decision = sg.decision_from_score(score)

    # pretty WhatsApp-friendly message
    lines = [
        f"📈 *{symbol}*",
        f"Tech Signal: {tech.get('signal', 0.0):+.2f}",
        f"RSI: {tech.get('rsi', None)} | MACD Hist: {tech.get('macd_hist', None)} | SMA Trend: {tech.get('sma_trend', 0.0):+.2f}",
        f"Sentiment: {sentiment:+.2f} | Fundamentals: {fund:+.2f}",
        "",
        f"👉 Decision: {decision}",
    ]
    return "\n".join(lines)

# ── One pass over symbol list
def run_once(symbols: List[str], send_whatsapp: bool = True) -> None:
    info(f"Symbols: {', '.join(symbols)}")
    for sym in symbols:
        try:
            msg = analyze_symbol(sym)
            if not msg:
                continue
            print(msg)  # always print analysis to logs

            if send_whatsapp:
                try:
                    send_whatsapp_alert(msg)
                except Exception as e:
                    err(f"WhatsApp send failed: {e}")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            err(f"Error analyzing {sym}: {e}")

# ── CLI
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Market Alert Bot runner (clean logs)"
    )
    p.add_argument("--symbols", help="Comma-separated symbols, e.g. BTC-USD,ETH-USD")
    p.add_argument("--symbols-file", help="File with one symbol per line")
    p.add_argument("--once", action="store_true", help="Run one pass and exit")
    p.add_argument("--no-telegram", action="store_true",
                   help="(Historical flag) Disable messaging; also disables WhatsApp")
    p.add_argument("--interval-min", type=int, default=30,
                   help="Only used if you create your own Python loop. Railway uses shell loop.")
    return p

def main() -> None:
    args = build_parser().parse_args()
    symbols = resolve_symbols(args)
    send_flag = not args.no_telegram

    if args.once:
        run_once(symbols, send_whatsapp=send_flag)
        return

    # If someone runs locally without Railway shell loop:
    interval = max(1, int(args.interval_min)) * 60
    info(f"Local loop mode active (interval {interval//60}m).")
    while True:
        run_once(symbols, send_whatsapp=send_flag)
        info(f"Sleeping {interval} seconds…")
        time.sleep(interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
