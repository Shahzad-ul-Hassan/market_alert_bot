from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Tuple
import os

from . import data_sources as ds
from . import signals as sg
from . import analysis as an

# ---------- Helpers ----------
def _pct(a: float, b: float) -> float:
    try:
        return round((a - b) / b * 100.0, 2) if b else 0.0
    except Exception:
        return 0.0

def _now_pk() -> datetime:
    tz = os.getenv("PK_TZ", "Asia/Karachi")
    return datetime.now(ZoneInfo(tz))

# ---------- Core ----------
def build_daily_summary(symbols: List[str]) -> Tuple[str, int, int, int]:
    """
    Returns (message, n_buy, n_sell, n_neutral)
    """
    rows = []
    n_buy = n_sell = n_neutral = 0

    for sym in symbols:
        df = ds.fetch_price_history(sym)
        if df is None or df.empty or len(df) < 2:
            continue
        last = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        chg = _pct(last, prev)

        # quick decision via same pipeline
        tech = sg.compute_technicals(df)
        tech_signal = float(tech.get("signal", 0.0))
        sentiment   = an.sentiment_from_texts(an.get_recent_news_and_tweets(sym))
        fund        = float(sg.fundamentals_to_score(sym))
        score       = sg.aggregate_scores(tech_signal, sentiment, fund)
        decision    = sg.decision_from_score(score)
        if decision.startswith("🟢"): n_buy += 1
        elif decision.startswith("🔴"): n_sell += 1
        else: n_neutral += 1

        rows.append((sym, chg, decision))

    # sort by change
    rows.sort(key=lambda r: r[1], reverse=True)
    top_up   = rows[:3]
    top_down = rows[-3:][::-1] if len(rows) >= 3 else rows[::-1]

    now = _now_pk()
    head = f"📊 *Daily Summary*  —  {now.strftime('%Y-%m-%d %H:%M')} PKT"

    lines = [head, ""]
    if top_up:
        lines.append("🟢 *Top Gainers (24h)*")
        for sym, chg, dec in top_up:
            lines.append(f"• {sym}: +{chg:.2f}%  {dec}")
        lines.append("")
    if top_down:
        lines.append("🔴 *Top Losers (24h)*")
        for sym, chg, dec in top_down:
            sign = "+" if chg >= 0 else ""
            lines.append(f"• {sym}: {sign}{chg:.2f}%  {dec}")
        lines.append("")
    lines.append(f"Signals — 🟢Buy: {n_buy}   🔴Sell: {n_sell}   🟡Neutral: {n_neutral}")

    return "\n".join(lines), n_buy, n_sell, n_neutral

def maybe_send_daily_summary(symbols: List[str], send_func):
    """
    Sends summary once per day at DAILY_SUMMARY_HOUR_PK (default 21 i.e. 9pm PKT)
    Guard file: /tmp/daily_summary_sent.txt (stores YYYY-MM-DD)
    """
    enabled = os.getenv("DAILY_SUMMARY_ENABLED", "true").lower() in ("1","true","yes","on")
    if not enabled:
        return

    hour_pk = int(os.getenv("DAILY_SUMMARY_HOUR_PK", "21"))
    now = _now_pk()
    if now.hour != hour_pk:
        return

    guard = "/tmp/daily_summary_sent.txt"
    today = now.date().isoformat()
    try:
        if os.path.exists(guard):
            last = open(guard).read().strip()
            if last == today:
                return
    except Exception:
        pass

    msg, nb, ns, nn = build_daily_summary(symbols)
    try:
        send_func(msg)
        open(guard, "w").write(today)
    except Exception as e:
        print(f"❌ Daily summary send failed: {e}")
