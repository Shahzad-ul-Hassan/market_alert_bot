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
# ───────────────────────────────
# 🎯 TRADE LEVELS: Entry / Stop / Targets
# ATR-based levels with configurable risk-reward
# ───────────────────────────────
import math
from typing import Dict, Optional

def _round_price(x: float) -> float:
    """
    Round price smartly based on magnitude to get clean levels for crypto.
    """
    if x <= 0:
        return x
    if x >= 1000:
        return round(x, 1)
    if x >= 100:
        return round(x, 2)
    if x >= 10:
        return round(x, 3)
    if x >= 1:
        return round(x, 4)
    return round(x, 6)

def compute_trade_levels(df: pd.DataFrame,
                         decision_text: str,
                         atr_window: int = 14,
                         atr_mult: float = 1.5,
                         rr1: float = 1.0,
                         rr2: float = 2.0) -> Optional[Dict[str, float]]:
    """
    Calculates ATR-based entry/stop-loss/targets.
    - decision_text: use first emoji to infer long/short (🟢 long, 🔴 short). 🟡 returns None.
    - entry = last close
    - stop = entry ± atr_mult * ATR(14)
    - tp1, tp2 = R:R × risk distance
    """
    try:
        # decision guard
        if not decision_text or decision_text.strip().startswith("🟡"):
            return None

        # Check data
        if df is None or df.empty:
            return None
        for col in ("High", "Low", "Close"):
            if col not in df.columns:
                return None

        close = float(df["Close"].iloc[-1])

        # ATR(14)
        atr = ta.volatility.AverageTrueRange(
            high=df["High"], low=df["Low"], close=df["Close"], window=atr_window
        ).average_true_range().iloc[-1]
        atr = float(atr) if not math.isnan(atr) else 0.0
        if atr <= 0:
            return None

        long_side = decision_text.strip().startswith("🟢")
        short_side = decision_text.strip().startswith("🔴")

        entry = close

        if long_side:
            stop = entry - atr_mult * atr
            risk_per_unit = entry - stop
            tp1 = entry + rr1 * risk_per_unit
            tp2 = entry + rr2 * risk_per_unit
        elif short_side:
            stop = entry + atr_mult * atr
            risk_per_unit = stop - entry
            tp1 = entry - rr1 * risk_per_unit
            tp2 = entry - rr2 * risk_per_unit
        else:
            return None

        levels = {
            "entry": _round_price(entry),
            "stop": _round_price(stop),
            "tp1": _round_price(tp1),
            "tp2": _round_price(tp2),
            "atr": round(atr, 4),
            "rr": f"{rr1}:{rr2}",
            "direction": "LONG" if long_side else "SHORT",
        }
        return levels
    except Exception as e:
        print(f"⚠️ Trade levels error: {e}")
        return None

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



def risk_level_from_factors(tech_signal: float, sentiment: float, fundamentals: float) -> str:
    """
    Evaluates combined risk level using volatility and sentiment balance.
    Returns human-readable string with emojis for WhatsApp alerts.
    """
    try:
        # Volatility indicator (difference in signals)
        volatility = abs(tech_signal - fundamentals)

        # Sentiment contribution
        mood = abs(sentiment)

        # Risk score combines volatility + sentiment
        risk_score = (volatility * 0.6) + (mood * 0.4)

        if risk_score < 0.25:
            return "🔹 *Low Risk* — Market relatively stable 🧊"
        elif risk_score < 0.55:
            return "🟠 *Medium Risk* — Moderate fluctuations ⚙️"
        else:
            return "🔴 *High Risk* — Volatile market ahead ⚡️"
    except Exception as e:
        return f"⚠️ Risk calculation error: {e}"
# ───────────────────────────────
# 🎯 TRADE ENGINE: Entry / Stop / Targets / Trailing / Reversal
# ───────────────────────────────
import math
from typing import Dict, Optional
import numpy as np
import pandas as pd
import ta

def compute_trailing_stop(current_price: float,
                          trade_info: Dict[str, float],
                          trail_pct: float = 0.8) -> Optional[float]:
    """
    Dynamically adjusts stop-loss after TP1 hit.
    trail_pct = 0.8 means stop follows 80% of move after TP1.
    """
    try:
        if not trade_info:
            return None

        entry = trade_info.get("entry")
        stop = trade_info.get("stop")
        tp1 = trade_info.get("tp1")
        direction = trade_info.get("direction")

        if not all([entry, stop, tp1, direction]):
            return None

        if direction == "LONG":
            if current_price > tp1:
                move = current_price - entry
                new_stop = entry + trail_pct * move
                return _round_price(new_stop)
        elif direction == "SHORT":
            if current_price < tp1:
                move = entry - current_price
                new_stop = entry - trail_pct * move
                return _round_price(new_stop)
        return None
    except Exception as e:
        print(f"⚠️ Trailing stop error: {e}")
        return None

# ───────────────────────────────
# 3️⃣ Reversal Probability
# ───────────────────────────────
def compute_reversal_probability(df: pd.DataFrame,
                                 decision_text: str,
                                 atr_mult: float = 1.5) -> Optional[float]:
    """
    Estimates probability (0–100%) that price will reverse soon.
    Factors:
    - Distance to ATR band
    - RSI extremes (>=70 or <=30)
    - Candle size vs ATR
    """
    try:
        if df is None or df.empty:
            return None
        close = float(df["Close"].iloc[-1])
        high = float(df["High"].iloc[-1])
        low = float(df["Low"].iloc[-1])

        atr = ta.volatility.AverageTrueRange(
            high=df["High"], low=df["Low"], close=df["Close"], window=14
        ).average_true_range().iloc[-1]
        atr = float(atr) if not math.isnan(atr) else 0.0
        if atr <= 0:
            return None

        # RSI for overbought/oversold
        rsi = ta.momentum.RSIIndicator(df["Close"], window=14).rsi().iloc[-1]
        rsi = float(rsi) if not math.isnan(rsi) else 50.0

        # Candle range and position
        range_size = high - low
        distance_from_close = abs(close - (high + low) / 2)

        # Reversal pressure
        pressure = 0.0
        if range_size > atr * 1.2:
            pressure += 25
        if rsi >= 70 or rsi <= 30:
            pressure += 35
        if distance_from_close > 0.5 * atr:
            pressure += 20
        if "🟢" in decision_text and rsi >= 65:
            pressure += 10
        if "🔴" in decision_text and rsi <= 35:
            pressure += 10

        return round(min(100, pressure), 1)
    except Exception as e:
        print(f"⚠️ Reversal probability error: {e}")
        return None
# ───────────────────────────────
# 🎯 TRADE ENGINE: Entry / Stop / Targets / Trailing / Reversal
# ───────────────────────────────
import math
from typing import Dict, Optional
import numpy as np
import pandas as pd
import ta




