import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Ensure VADER lexicon is available on new machines/containers (Railway, etc.)
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

_sia = SentimentIntensityAnalyzer()

def sentiment_from_texts(texts):
    if not texts:
        return 0.0
    vals = []
    for t in texts:
        if not t:
            continue
        s = _sia.polarity_scores(str(t))
        vals.append(s.get("compound", 0.0))
    return sum(vals) / len(vals) if vals else 0.0
