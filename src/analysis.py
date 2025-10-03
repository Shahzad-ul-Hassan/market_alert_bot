from typing import List
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np

_sia = None
def get_sia():
    global _sia
    if _sia is None:
        _sia = SentimentIntensityAnalyzer()
    return _sia

def sentiment_score_texts(texts: List[str]) -> float:
    """Returns a normalized sentiment score in range [-1, 1]."""
    if not texts:
        return 0.0
    sia = get_sia()
    scores = []
    for t in texts:
        try:
            s = sia.polarity_scores(t or "")
            scores.append(s.get("compound", 0.0))
        except Exception:
            scores.append(0.0)
    if not scores:
        return 0.0
    return float(np.clip(np.mean(scores), -1.0, 1.0))

def normalize_value(x, lo, hi):
    if x is None:
        return 0.0
    try:
        x = float(x)
    except Exception:
        return 0.0
    if hi == lo:
        return 0.0
    return float(np.clip((x - lo) / (hi - lo), 0, 1))
