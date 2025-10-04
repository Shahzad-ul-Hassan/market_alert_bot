import pandas as pd
import numpy as np
from typing import Dict, Any
import ta

def _pick_close_series(df: pd.DataFrame) -> pd.Series:
    """Return a clean 'close' price series (case/space tolerant), or empty series."""
    if df is None or not hasattr(df, "columns"):
        return pd.Series(dtype=float)

    # صاف ناموں کا میپ (case + spaces ignore)
    norm_map = {str(c).lower().replace(" ", ""): c for c in df.columns}

    for key in ("close", "adjclose", "closingprice"):
        if key in norm_map:
            return pd.to_numeric(df[norm_map[key]], errors="coerce").dropna()

    # بعض دفعہ yfinance auto_adjust=False ہو تو 'Adj Close' آتا ہے
    for raw in ("Close", "Adj Close"):
        if raw in df.columns:
            return pd.to_numeric(df[raw], errors="coerce").dropna()

    return pd.Series(dtype=float)

def compute_technicals(df: pd.DataFrame) -> Dict[str, Any]:
    defaults = {"rsi": None, "macd_hist": None, "sma_trend": 0.0, "signal": 0.0}

    if df is None or not hasattr(df, "empty") or df.empty:
        return defaults

    close = _pick_close_series(df)
    if close.empty or len(close) < 20:
        return defaults  # indicators کے لیے کم از کم ڈیٹا چاہیے

    # RSI
    try:
        rsi = float(ta.momentum.RSIIndicator(close).rsi().iloc[-1])
    except Exception:
        rsi = None

    # MACD histogram
    macd_hist = None
    try:
        macd = ta.trend.MACD(close)
        macd_hist = macd.macd_diff().tail(3).mean()
        macd_hist = float(macd_hist) if pd.notna(macd_hist) else None
    except Exception:
        macd_hist = None

    # 20/50 MA trend
    sma_trend = 0.0
    try:
        sma_fast = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else None
        sma_slow = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None
        if sma_fast is not None and sma_slow is not None:
            sma_trend = float(np.sign((sma_fast or 0) - (sma_slow or 0)))
    except Exception:
        sma_trend = 0.0

    # aggregate in [-1, 1]
    tech_signal = 0.0
    if rsi is not None:
        if rsi < 30:   tech_signal += 0.4
        elif rsi > 70: tech_signal -= 0.4
    if macd_hist is not None:
        tech_signal += 0.3 * float(np.tanh(macd_hist))
    tech_signal += 0.3 * sma_trend
    tech_signal = float(np.clip(tech_signal, -1.0, 1.0))

    return {
        "rsi": rsi if rsi is not None and not np.isnan(rsi) else None,
        "macd_hist": macd_hist if macd_hist is not None else None,
        "sma_trend": sma_trend,
        "signal": tech_signal,
    }
def fundamentals_to_score(fundamentals: dict) -> float:
    """
    Convert fundamentals dict (PE, EPS, etc) into a score between -1 and 1.
    Right now just a stub — returns 0.0 if nothing useful.
    """
    if not fundamentals:
        return 0.0

    score = 0.0
    pe = fundamentals.get("pe_ratio")
    eps = fundamentals.get("eps")
    if pe is not None:
        if pe < 15: score += 0.3
        elif pe > 30: score -= 0.3
    if eps is not None and eps > 0:
        score += 0.2

    # clamp in [-1, 1]
    return float(max(-1.0, min(1.0, score)))
def fundamentals_to_score(fundamentals: dict) -> float:
    """
    Convert fundamentals dict (PE, EPS, etc) into a score between -1 and 1.
    Right now just a basic scoring model.
    """
    if not fundamentals:
        return 0.0

    score = 0.0
    pe = fundamentals.get("pe_ratio")
    eps = fundamentals.get("eps")

    # PE ratio logic
    if pe is not None:
        if pe < 15:
            score += 0.3   # undervalued = positive
        elif pe > 30:
            score -= 0.3   # overvalued = negative

    # EPS logic
    if eps is not None:
        if eps > 0:
            score += 0.2   # profitable = positive
        else:
            score -= 0.2   # loss-making = negative

    # Clamp to [-1, 1]
    return float(max(-1.0, min(1.0, score)))
def fundamentals_to_score(snapshot: dict) -> float:
    """
    Score fundamentals to [-1, 1].
    Works with yfinance keys: trailingPE, forwardPE, fiftyTwoWeekHigh/Low.
    Keeps it simple & robust if fields are missing.
    """
    if not snapshot or not isinstance(snapshot, dict):
        return 0.0

    score = 0.0

    # --- PE (prefer trailing, else forward) ---
    pe = snapshot.get("trailingPE") or snapshot.get("forwardPE")
    try:
        pe = float(pe) if pe is not None else None
    except Exception:
        pe = None

    if pe is not None:
        if pe < 12:
            score += 0.40     # very cheap
        elif pe < 20:
            score += 0.20     # reasonable
        elif pe > 35:
            score -= 0.20     # expensive

    # --- 52-week range context (if close to low → slight positive; near high → slight negative) ---
    hi = snapshot.get("fiftyTwoWeekHigh")
    lo = snapshot.get("fiftyTwoWeekLow")
    try:
        hi = float(hi) if hi is not None else None
        lo = float(lo) if lo is not None else None
    except Exception:
        hi = lo = None

    if hi is not None and lo is not None and hi > lo:
        # neutral point mid-range
        # we don't have current price here, so keep a tiny neutral nudge only if range looks healthy
        score += 0.05  # light bias

    # clamp
    if score > 1.0: score = 1.0
    if score < -1.0: score = -1.0
    return float(score)
def aggregate_scores(tech: float, sentiment: float, fundamentals: float) -> float:
    """
    Combine technical, sentiment, and fundamentals scores into a single number [-1, 1].
    """
    parts = [p for p in (tech, sentiment, fundamentals) if p is not None]
    if not parts:
        return 0.0

    score = sum(parts) / len(parts)

    # Clamp to [-1, 1]
    if score > 1.0:
        score = 1.0
    if score < -1.0:
        score = -1.0
    return float(score)
def aggregate_scores(tech: float, sentiment: float, fundamentals: float) -> float:
    """
    Combine technical, sentiment, and fundamentals scores into a single number [-1, 1].
    Simple average of available scores.
    """
    parts = []
    if tech is not None:
        parts.append(float(tech))
    if sentiment is not None:
        parts.append(float(sentiment))
    if fundamentals is not None:
        parts.append(float(fundamentals))

    if not parts:
        return 0.0

    score = sum(parts) / len(parts)

    # clamp between -1 and 1
    if score > 1.0:
        score = 1.0
    if score < -1.0:
        score = -1.0

    return score
def decision_from_score(score: float, buy_th: float = 0.25, sell_th: float = -0.25) -> str:
    """
    Map the aggregate score to a decision label.
    Returns one of: 'BUY', 'SELL', 'NEUTRAL'
    """
    if score is None:
        return "NEUTRAL"
    try:
        s = float(score)
    except Exception:
        return "NEUTRAL"

    if s >= buy_th:
        return "BUY"
    if s <= sell_th:
        return "SELL"
    return "NEUTRAL"

def fundamentals_to_score(snapshot: dict) -> float:
    """Convert fundamentals snapshot (like PE, EPS, 52-week) to a score."""
    if not snapshot or not isinstance(snapshot, dict):
        return 0.0
    score = 0.0
    pe = snapshot.get("trailingPE") or snapshot.get("forwardPE")
    try:
        pe = float(pe) if pe is not None else None
    except Exception:
        pe = None
    if pe is not None:
        if pe < 12:
            score += 0.40
        elif pe < 20:
            score += 0.20
        elif pe > 35:
            score -= 0.20
    hi = snapshot.get("fiftyTwoWeekHigh")
    lo = snapshot.get("fiftyTwoWeekLow")
    try:
        hi = float(hi) if hi is not None else None
        lo = float(lo) if lo is not None else None
    except Exception:
        hi = lo = None
    if hi and lo and hi > lo:
        score += 0.05
    return max(-1.0, min(1.0, score))

def aggregate_scores(tech: float, sentiment: float, fundamentals: float) -> float:
    """Average of technical, sentiment and fundamentals [-1,1]."""
    parts = [p for p in (tech, sentiment, fundamentals) if p is not None]
    if not parts:
        return 0.0
    score = sum(parts) / len(parts)
    return max(-1.0, min(1.0, score))

def decision_from_score(score: float, buy_th: float = 0.25, sell_th: float = -0.25) -> str:
    """Convert score to BUY/SELL/NEUTRAL."""
    if score is None:
        return "NEUTRAL"
    s = float(score)
    if s >= buy_th:
        return "BUY"
    if s <= sell_th:
        return "SELL"
    return "NEUTRAL"
# ───────────────────────────────
# ❤️ FINAL DECISION SECTION (with emojis)
# ───────────────────────────────
def decision_from_score(score: float) -> str:
    """
    Converts numeric score into a clear emoji-based decision.
    """
    try:
        if score >= 0.35:
            return "🟢 *BUY* — Momentum looks strong, trend upward 📈"
        elif score <= -0.35:
            return "🔴 *SELL* — Bearish momentum, trend downward 📉"
        else:
            return "🟡 *WAIT* — Market uncertain, stay cautious ⚖️"
    except Exception as e:
        return f"⚠️ Decision error: {e}"
