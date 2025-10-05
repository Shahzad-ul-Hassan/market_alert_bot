from __future__ import annotations
import os, time, argparse

# Safe logger (fallback)
try:
    from .logger import info, warn, err
except Exception:
    def info(msg): print(f"✅ {msg}")
    def warn(msg): print(f"⚠️ {msg}")
    def err(msg):  print(f"❌ {msg}")

# Project modules
from . import data_sources as ds
from . import signals as sg
from . import analysis as an
from .whatsapp_alert import send_whatsapp_alert

MIN_CONF = float(os.getenv("CONFIDENCE_MIN", "70"))

def analyze_symbol(symbol):
    info(f"Analyzing {symbol}...")
    df = ds.fetch_price_history(symbol)
    if df is None:
        warn(f"No price data for {symbol}. Skipping.")
        return None

    tech = sg.compute_technicals(df)
    tech_signal = float(tech.get("signal", 0.0))
    rsi        = tech.get("rsi", None)
    macd_hist  = tech.get("macd_hist", 0.0)
    sma_trend  = tech.get("sma_trend", 0.0)

    sentiment = an.sentiment_from_texts(an.get_recent_news_and_tweets(symbol))
    fund      = float(sg.fundamentals_to_score(symbol))

    score     = sg.aggregate_scores(tech_signal, sentiment, fund)
    decision  = sg.decision_from_score(score)
    risk      = sg.risk_level_from_factors(tech_signal, sentiment, fund)

    if sma_trend > 0.02 and macd_hist > 0:
        trend = "📊 Uptrend forming — buyers in control 💪"; tflag = 1
    elif sma_trend < -0.02 and macd_hist < 0:
        trend = "📊 Downtrend likely — sellers dominating 📉"; tflag = 1
    else:
        trend = "⚖️ Sideways / Consolidation — wait for breakout"; tflag = 0

    strength    = min(1.0, abs(score))
    base_conf   = 60.0 * strength
    trend_bonus = 20.0 * tflag
    rows        = len(df)
    data_bonus  = 10.0 if rows >= 120 else (5.0 if rows >= 60 else 0.0)
    confidence  = max(0.0, min(100.0, round(base_conf + trend_bonus + data_bonus, 1)))

    levels_block = []
    trade = sg.compute_trade_levels(df, decision)
    if trade:
        last_close = float(df["Close"].iloc[-1])
        trail   = sg.compute_trailing_stop(last_close, trade)
        revprob = sg.compute_reversal_probability(df, decision)

        levels_block += [
            f"🎯 Entry: {trade['entry']}",
            f"🛡️ Stop: {trade['stop']}",
            f"🎯 TP1: {trade['tp1']} | 🎯 TP2: {trade['tp2']}",
            f"🧮 ATR(14): {trade['atr']} | {trade['direction']} | R:R {trade['rr']}",
        ]
        if trail:              levels_block.append(f"📉 Trailing Stop: {trail}")
        if revprob is not None: levels_block.append(f"�� Reversal Probability: {revprob:.1f}%")

    lines = [
        f"📈 *{symbol}*",
        f"Tech Signal: {tech_signal:+.2f}",
        f"RSI: {rsi} | MACD Hist: {macd_hist} | SMA Trend: {sma_trend:+.2f}",
        f"Sentiment: {sentiment:+.2f} | Fundamentals: {fund:+.2f}",
        "",
        f"👉 Decision: {decision}",
        f"⚖️ Risk: {risk}",
        f"{trend}",
        f"✅ Confidence: {confidence:.1f}%",
    ]
    if levels_block:
        lines += [""] + levels_block

    return "\n".join(lines), decision, confidence

def should_alert(decision_text, confidence_pct, min_conf=MIN_CONF):
    if not decision_text:
        return False
    if decision_text.strip().startswith("🟡"):
        return False
    return float(confidence_pct) >= float(min_conf)

def run_once(symbols, send_whatsapp=True):
    info(f"Symbols: {', '.join(symbols)}")
    for sym in symbols:
        try:
            result = analyze_symbol(sym)
            if not result:
                continue
            msg, decision, conf = result
            print(msg)

            if send_whatsapp and should_alert(decision, conf, MIN_CONF):
                try:
                    send_whatsapp_alert(msg)
                except Exception as e:
                    err(f"WhatsApp send failed: {e}")
            else:
                print(f"ℹ️ Skipping {sym}: decision='{decision[:12]}...', confidence={conf:.1f}% (< {MIN_CONF:.1f}% یا neutral)")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            err(f"Error analyzing {sym}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", default="", help="Comma-separated e.g. BTC-USD,ETH-USD")
    parser.add_argument("--symbols-file", default="sample_symbols.txt")
    parser.add_argument("--interval", type=int, default=1800)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    symbols = []
    if args.symbols_file and os.path.exists(args.symbols_file):
        with open(args.symbols_file) as f:
            symbols = [l.strip() for l in f if l.strip() and not l.strip().startswith("#")]
    if not symbols and args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    if not symbols:
        warn("No symbols found — using defaults BTC-USD,ETH-USD")
        symbols = ["BTC-USD", "ETH-USD"]

    if args.once:
        run_once(symbols, send_whatsapp=True)
    else:
        while True:
            run_once(symbols, send_whatsapp=True)
            time.sleep(max(60, args.interval))
