from __future__ import annotations
from typing import List
import os

# اس ماڈیول میں صرف دو فنکشن مین کو چاہئیں:
# 1) sentiment_from_texts(texts: List[str]) -> float
# 2) get_recent_news_and_tweets(symbol: str) -> List[str]

def _get_vader():
    """Lazy-init VADER; اگر نہ ملا تو None لوٹادے۔"""
    try:
        import nltk
        from nltk.sentiment import SentimentIntensityAnalyzer
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
        return SentimentIntensityAnalyzer()
    except Exception:
        return None

def sentiment_from_texts(texts: List[str]) -> float:
    """texts کی compound polarity کا اوسط (−1…+1)؛ خالی ہو تو 0.0"""
    if not texts:
        return 0.0
    vader = _get_vader()
    if vader:
        vals = []
        for t in texts:
            try:
                vals.append(vader.polarity_scores((t or "").strip()).get("compound", 0.0))
            except Exception:
                vals.append(0.0)
        return float(sum(vals) / len(vals)) if vals else 0.0
    # fallback: neutral
    return 0.0

def get_recent_news_and_tweets(symbol: str) -> List[str]:
    """
    News + Tweets سے مختصر لائنیں لوٹا دیں (ہیڈ لائن/ٹیکسٹ truncate کر کے) —
    تاکہ main.py ان پر sentiment بنا سکے۔
    """
    # data_sources کو relative import سے لائیں (main.py ایسے ہی expect کرتا ہے)
    try:
        from . import data_sources as ds
    except Exception:
        # اگر relative ناکام ہو تو absolute کی کوشش (لوکل ٹیسٹ کے لیے)
        import src.data_sources as ds  # type: ignore

    texts: List[str] = []

    # News titles
    try:
        news_items = ds.get_news(symbol) or []
        for item in news_items[:10]:
            title = ""
            if isinstance(item, dict):
                title = item.get("title") or item.get("headline") or ""
            elif isinstance(item, str):
                title = item
            title = (title or "").strip()
            if title:
                if len(title) > 200:
                    title = title[:197] + "..."
                texts.append(title)
    except Exception:
        pass

    # Tweets text
    try:
        tweets = ds.get_tweets(symbol) or []
        for tw in tweets[:10]:
            txt = ""
            if isinstance(tw, dict):
                txt = tw.get("text") or ""
            elif isinstance(tw, str):
                txt = tw
            txt = (txt or "").strip()
            if txt:
                if len(txt) > 200:
                    txt = txt[:197] + "..."
                texts.append(txt)
    except Exception:
        pass

    if not texts:
        texts = [f"No recent news/tweets for {symbol}"]

    return texts
