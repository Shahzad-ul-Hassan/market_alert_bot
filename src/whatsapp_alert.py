# src/whatsapp_alert.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

def _clean(v): return (v or "").strip()

# --- Env variables ---
ACCOUNT_SID   = _clean(os.getenv("TWILIO_ACCOUNT_SID"))
AUTH_TOKEN    = _clean(os.getenv("TWILIO_AUTH_TOKEN"))       # fallback
API_KEY       = _clean(os.getenv("TWILIO_API_KEY"))
API_SECRET    = _clean(os.getenv("TWILIO_API_SECRET"))
WHATSAPP_FROM = _clean(os.getenv("WHATSAPP_FROM"))
WHATSAPP_TO   = _clean(os.getenv("WHATSAPP_TO"))

# --- Get client automatically ---
def _get_client():
    if API_KEY and API_SECRET and ACCOUNT_SID:
        print("🔑 Using API Key/Secret auth")
        return Client(API_KEY, API_SECRET, ACCOUNT_SID)
    elif ACCOUNT_SID and AUTH_TOKEN:
        print("🔑 Using SID + Auth Token auth")
        return Client(ACCOUNT_SID, AUTH_TOKEN)
    raise Exception("❌ Twilio credentials not configured properly")

def verify_twilio_auth():
    try:
        _get_client().api.accounts(ACCOUNT_SID).fetch()
        print("✅ Twilio auth OK")
        return True
    except Exception as e:
        print("❌ Twilio auth FAILED:", str(e))
        return False

def send_whatsapp_alert(message_text: str):
    if not verify_twilio_auth():
        print("⚠️ Not sending due to failed auth.")
        return
    try:
        msg = _get_client().messages.create(
            from_=WHATSAPP_FROM,
            to=WHATSAPP_TO,
            body=message_text,
        )
        print("✅ WhatsApp Message Sent:", msg.sid)
    except Exception as e:
        print("❌ Error sending WhatsApp message:", str(e))
