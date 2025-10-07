from __future__ import annotations
import os
from dotenv import load_dotenv

# .env لوڈ کریں (لوکل میں) — Railway پر ENV ویری ایبلز پہلے سے ہوتے ہیں
load_dotenv()

# Public APIs (optional)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Twilio / WhatsApp
TWILIO_ACCOUNT_SID   = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # Sandbox default
TWILIO_WHATSAPP_TO   = os.getenv("TWILIO_WHATSAPP_TO", "")  # e.g., whatsapp:+9230XXXXXXXXX

# Defaults
DEFAULT_SYMBOLS_FILE = os.getenv("SYMBOLS_FILE", "sample_symbols.txt")
CONFIDENCE_MIN       = float(os.getenv("CONFIDENCE_MIN", "70"))
