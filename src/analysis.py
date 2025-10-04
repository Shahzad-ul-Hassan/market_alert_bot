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
