import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

DEFAULT_SYMBOLS = [
    "BTC-USD",
    "BCH-USD",
    "BSV-USD",
    "LTC-USD",
    "DGB-USD",
    "ETH-USD",
    "ETC-USD",
    "OP-USD",
    "ARB-USD",
    "MATIC-USD"]

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC4d3c44fd970bc3f2adc704cbe9678c1e")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "873ffa00cbf25d31affe1662c16cd127")
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM", "whatsapp:+14155238886")
WHATSAPP_TO = os.getenv("WHATSAPP_TO", "")
DEFAULT_SYMBOLS = [
    # BTC + followers
    "BTC-USD",
    "BCH-USD", "BSV-USD", "BTG-USD", "LTC-USD", "DASH-USD",

    # ETH + followers
    "ETH-USD",
    "ETC-USD", "MATIC-USD", "OP-USD", "ARB-USD", "LDO-USD",
]
