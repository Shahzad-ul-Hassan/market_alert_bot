# --- NLTK (VADER) robust setup ---
import os, nltk
from nltk.sentiment import SentimentIntensityAnalyzer

NLTK_DIR = os.getenv("NLTK_DATA", "/tmp/nltk_data")
os.makedirs(NLTK_DIR, exist_ok=True)
if NLTK_DIR not in nltk.data.path:
    nltk.data.path.append(NLTK_DIR)

try:
    # اگر پہلے سے موجود نہیں تو صرف ایک بار ڈاؤن لوڈ
    nltk.data.find("sentiment/vader_lexicon")
except LookupError:
    try:
        nltk.download("vader_lexicon", download_dir=NLTK_DIR, quiet=True)
        print("[INFO] Downloaded VADER lexicon to", NLTK_DIR)
    except Exception as e:
        print("[WARN] VADER download failed:", e)

_sia = None
try:
    _sia = SentimentIntensityAnalyzer()
except Exception as e:
    print("[WARN] SentimentIntensityAnalyzer init failed:", e)

def sentiment_from_texts(texts):
    if not texts or _sia is None:
        return 0.0
    vals = []
    for t in texts:
        if not t:
            continue
        s = _sia.polarity_scores(str(t))
        vals.append(s.get("compound", 0.0))
    return sum(vals) / len(vals) if vals else 0.0
# Add this at the END of src/analysis.py

import src.data_sources as ds

def get_recent_news_and_tweets(symbol: str):
    """
    Collects recent news headlines and tweets for a given symbol (e.g. BTC-USD)
    Returns a list of text strings for sentiment analysis.
    """
    try:
        news_items = ds.get_news(symbol)
    except Exception as e:
        print(f"[WARN] News fetch failed for {symbol}: {e}")
        news_items = []

    try:
        tweets = ds.get_tweets(symbol)
    except Exception as e:
        print(f"[WARN] Tweets fetch failed for {symbol}: {e}")
        tweets = []

    texts = [item['title'] for item in news_items if isinstance(item, dict) and 'title' in item]
    texts += [tw['text'] for tw in tweets if isinstance(tw, dict) and 'text' in tw]

    if not texts:
        texts = [f"No recent news or tweets for {symbol}"]

    return texts
# Add this refined version at the END of src/analysis.py

import src.data_sources as ds
from textblob import TextBlob

def get_recent_news_and_tweets(symbol: str):
    """
    Collects recent news + tweets for a given symbol (e.g. BTC-USD)
    Returns a short summarized sentiment text instead of full articles.
    """
    try:
        news_items = ds.get_news(symbol)
    except Exception as e:
        print(f"[WARN] News fetch failed for {symbol}: {e}")
        news_items = []

    try:
        tweets = ds.get_tweets(symbol)
    except Exception as e:
        print(f"[WARN] Tweets fetch failed for {symbol}: {e}")
        tweets = []

    texts = [item.get("title", "") for item in news_items if isinstance(item, dict)]
    texts += [tw.get("text", "") for tw in tweets if isinstance(tw, dict)]

    if not texts:
        return [f"No significant market sentiment detected for {symbol}."]

    # Summarize overall sentiment
    polarity_scores = [TextBlob(t).sentiment.polarity for t in texts if t]
    avg_polarity = sum(polarity_scores) / len(polarity_scores) if polarity_scores else 0

    if avg_polarity > 0.2:
        summary = f"📈 Bullish sentiment seen for {symbol} — traders optimistic."
    elif avg_polarity < -0.2:
        summary = f"📉 Bearish sentiment seen for {symbol} — cautious outlook."
    else:
        summary = f"⚖️ Neutral mood for {symbol} — mixed expert opinions."

    return [summary]
# Add this enhanced version at the END of src/analysis.py

import src.data_sources as ds
import src.signals as sg
from textblob import TextBlob
import numpy as np

def get_recent_news_and_tweets(symbol: str):
    """
    Collects recent news + tweets for a given symbol (e.g. BTC-USD)
    Returns a summarized sentiment + technical range outlook.
    """
    try:
        news_items = ds.get_news(symbol)
    except Exception as e:
        print(f"[WARN] News fetch failed for {symbol}: {e}")
        news_items = []

    try:
        tweets = ds.get_tweets(symbol)
    except Exception as e:
        print(f"[WARN] Tweets fetch failed for {symbol}: {e}")
        tweets = []

    texts = [item.get("title", "") for item in news_items if isinstance(item, dict)]
    texts += [tw.get("text", "") for tw in tweets if isinstance(tw, dict)]

    if not texts:
        texts = [f"No strong sentiment detected for {symbol}."]
        avg_polarity = 0
    else:
        polarity_scores = [TextBlob(t).sentiment.polarity for t in texts if t]
        avg_polarity = np.mean(polarity_scores) if polarity_scores else 0

    # Determine market sentiment summary
    if avg_polarity > 0.2:
        sentiment_summary = f"📈 Bullish — traders optimistic."
    elif avg_polarity < -0.2:
        sentiment_summary = f"📉 Bearish — cautious outlook."
    else:
        sentiment_summary = f"⚖️ Neutral — mixed expert opinions."

    # Get recent technicals (support/resistance)
    try:
        tech = sg.compute_technicals(symbol)
        support = tech.get("support", None)
        resistance = tech.get("resistance", None)
    except Exception as e:
        print(f"[WARN] Technicals unavailable for {symbol}: {e}")
        support, resistance = None, None

    range_summary = ""
    if support and resistance:
        range_summary = f"Support: {support:.0f} | Resistance: {resistance:.0f}"
    else:
        range_summary = "Technical range unavailable"

    # Determine short-term bias
    if avg_polarity > 0.2:
        bias = "Likely move towards resistance"
    elif avg_polarity < -0.2:
        bias = "Possible test of support"
    else:
        bias = "Range-bound movement expected"

    final_summary = [
        f"Sentiment: {sentiment_summary}",
        f"{range_summary}",
        f"Range: {bias}"
    ]

    return final_summary
cat >> ~/Desktop/market_alert_bot/src/analysis.py <<'PY'

# ─────────────────────────────────────────────────────────
# Summary + Support/Resistance + Range + Confidence (PK)
# ─────────────────────────────────────────────────────────
from textblob import TextBlob
import numpy as np
import pandas as pd
import src.data_sources as ds
import src.signals as sg

def get_recent_news_and_tweets(symbol: str):
    """
    Returns a SHORT summary list for sentiment & alert body:
    - Sentiment summary (bullish/bearish/neutral)
    - Support / Resistance (last 50 bars highs/lows)
    - Range bias (towards S/R)
    - Confidence % (from tech + sentiment + fund, same logic as main)
    Note: We return short lines (not full news/tweets) to avoid spam.
    """
    # 1) fetch texts (titles + tweets)
    try:
        news_items = ds.get_news(symbol)
    except Exception as e:
        print(f"[WARN] News fetch failed for {symbol}: {e}")
        news_items = []
    try:
        tweets = ds.get_tweets(symbol)
    except Exception as e:
        print(f"[WARN] Tweets fetch failed for {symbol}: {e}")
        tweets = []

    texts = [n.get("title","") for n in news_items if isinstance(n, dict)]
    texts += [t.get("text","") for t in tweets if isinstance(t, dict)]
    if not texts:
        texts = [f"No strong sentiment detected for {symbol}."]

    # 2) build price/technicals for S/R + confidence
    df = ds.fetch_price_history(symbol) or pd.DataFrame()
    support = resistance = None
    sma_trend = macd_hist = 0.0
    tech_signal = 0.0
    rows = len(df)

    if not df.empty and all(c in df.columns for c in ("High","Low","Close")):
        last50 = df.tail(50)
        if not last50.empty:
            try:
                support = float(last50["Low"].min())
                resistance = float(last50["High"].max())
            except Exception:
                support = resistance = None

        try:
            tech = sg.compute_technicals(df)
            tech_signal = float(tech.get("signal", 0.0))
            sma_trend   = float(tech.get("sma_trend", 0.0))
            macd_hist   = float(tech.get("macd_hist", 0.0))
        except Exception as e:
            print(f"[WARN] compute_technicals failed for {symbol}: {e}")

    # 3) sentiment score (avg polarity via TextBlob)
    polarities = [TextBlob(t).sentiment.polarity for t in texts if t]
    avg_pol = float(np.mean(polarities)) if polarities else 0.0
    if avg_pol > 0.2:
        sent_summary = "📈 Bullish — traders optimistic."
    elif avg_pol < -0.2:
        sent_summary = "📉 Bearish — cautious outlook."
    else:
        sent_summary = "⚖️ Neutral — mixed expert opinions."

    # 4) fundamentals + aggregate score → confidence (same style as main)
    try:
        fund = float(sg.fundamentals_to_score(symbol))
    except Exception:
        fund = 0.0

    try:
        score = sg.aggregate_scores(tech_signal, avg_pol, fund)
    except Exception:
        score = tech_signal + 0.5*avg_pol + 0.3*fund

    strength = min(1.0, abs(score))
    base_conf = 60.0 * strength
    trend_bonus = 20.0 if (sma_trend > 0.02 and macd_hist > 0) or (sma_trend < -0.02 and macd_hist < 0) else 0.0
    data_bonus  = 10.0 if rows >= 120 else (5.0 if rows >= 60 else 0.0)
    confidence  = max(0.0, min(100.0, round(base_conf + trend_bonus + data_bonus, 1)))

    # 5) range bias
    if avg_pol > 0.2:
        bias = "Likely move towards resistance"
    elif avg_pol < -0.2:
        bias = "Possible test of support"
    else:
        bias = "Range-bound movement expected"

    sr_line = "Technical range unavailable"
    if support is not None and resistance is not None:
        sr_line = f"Support: {support:.0f} | Resistance: {resistance:.0f}"

    return [
        f"Sentiment: {sent_summary}",
        sr_line,
        f"Range: {bias}",
        f"Confidence: {confidence:.1f}%"
    ]
PY
