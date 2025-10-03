import requests
import pandas as pd
import yfinance as yf
from typing import List, Dict, Any
from .config import NEWSAPI_KEY, TWITTER_BEARER_TOKEN

# ---------- Price / Technical base: yfinance ----------
def fetch_price_history(symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()
    df = df.rename(columns=str.lower)
    return df

def fetch_fundamentals_snapshot(symbol: str) -> Dict[str, Any]:
    """
    Light fundamentals snapshot via yfinance Ticker. Fields availability can vary.
    """
    t = yf.Ticker(symbol)
    info = {}
    try:
        # fast_info is lighter and faster if available
        info = getattr(t, "fast_info", {})
        if hasattr(info, "__dict__"):
            info = info.__dict__
    except Exception:
        info = {}
    # Fallback to .info (slower / may be deprecated in future)
    if not info:
        try:
            info = t.info
        except Exception:
            info = {}
    # Normalize interesting keys if present
    keys = ["marketCap", "trailingPE", "forwardPE", "priceToBook", "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "currency"]
    snap = {k: info.get(k) for k in keys}
    return snap

# ---------- News via NewsAPI ----------
def fetch_news_headlines(query: str, max_articles: int = 30) -> List[Dict[str, Any]]:
    if not NEWSAPI_KEY:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": min(max_articles, 100),
        "apiKey": NEWSAPI_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data.get("articles", [])
    except Exception:
        return []

# ---------- Twitter/X search (v2 recent search) ----------
def fetch_twitter_recent(query: str, max_results: int = 50) -> List[Dict[str, Any]]:
    if not TWITTER_BEARER_TOKEN:
        return []
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    params = {
        "query": query,
        "max_results": max(10, min(max_results, 100)),
        "tweet.fields": "created_at,lang,public_metrics",
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data.get("data", [])
    except Exception:
        return []
