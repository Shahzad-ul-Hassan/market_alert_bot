# src/whatsapp_alert.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

def _clean(v): return (v or "").strip()

# Read envs (both modes allowed)
ACCOUNT_SID   = _clean(os.getenv("TWILIO_ACCOUNT_SID"))
AUTH_TOKEN    = _clean(os.getenv("TWILIO_AUTH_TOKEN"))       # optional fallback
API_KEY       = _clean(os.getenv("TWILIO_API_KEY"))
API_SECRET    = _clean(os.getenv("TWILIO_API_SECRET"))
WHATSAPP_FROM = _clean(os.getenv("WHATSAPP_FROM"))
WHATSAPP_TO   = _clean(os.getenv("WHATSAPP_TO"))

def _get_client():
    if API_KEY and API_SECRET and ACCOUNT_SID:
        print("🔑 Auth mode: API KEY/SECRET")
        return Client(API_KEY, API_SECRET, ACCOUNT_SID)
    if ACCOUNT_SID and AUTH_TOKEN:
        print("🔑 Auth mode: SID + AUTH TOKEN")
        return Client(ACCOUNT_SID, AUTH_TOKEN)
    raise Exception("❌ Twilio credentials missing: need (API_KEY+API_SECRET+ACCOUNT_SID) or (ACCOUNT_SID+AUTH_TOKEN)")

def verify_twilio_auth():
    print(
        "DEBUG env →",
        "SID set:", bool(ACCOUNT_SID),
        "SID last4:", (ACCOUNT_SID[-4:] if ACCOUNT_SID else None),
        "| API_KEY set:", bool(API_KEY),
        "| API_SECRET set:", bool(API_SECRET),
        "| AUTH_TOKEN set:", bool(AUTH_TOKEN),
        "| FROM:", WHATSAPP_FROM,
        "| TO:", WHATSAPP_TO,
    )
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

if __name__ == "__main__":
    send_whatsapp_alert("🚀 Test from Railway (env debug)")
