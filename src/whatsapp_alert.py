# src/whatsapp_alert.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

def _clean(v): return (v or "").strip()

ACCOUNT_SID      = _clean(os.getenv("TWILIO_ACCOUNT_SID"))
AUTH_TOKEN       = _clean(os.getenv("TWILIO_AUTH_TOKEN"))
API_KEY          = _clean(os.getenv("TWILIO_API_KEY"))
API_SECRET       = _clean(os.getenv("TWILIO_API_SECRET"))
WHATSAPP_FROM    = _clean(os.getenv("WHATSAPP_FROM"))
WHATSAPP_TO      = _clean(os.getenv("WHATSAPP_TO"))

def _get_client():
    # Prefer API Key/Secret if provided, else fall back to SID/Token
    if API_KEY and API_SECRET and ACCOUNT_SID:
        return Client(API_KEY, API_SECRET, ACCOUNT_SID)
    return Client(ACCOUNT_SID, AUTH_TOKEN)

def verify_twilio_auth():
    print(
        "Twilio creds → SID set:", bool(ACCOUNT_SID),
        "SID last4:", (ACCOUNT_SID[-4:] if ACCOUNT_SID else None),
        "| FROM:", WHATSAPP_FROM, "| TO:", WHATSAPP_TO,
        "| Using:", "API_KEY" if API_KEY else "AUTH_TOKEN"
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
            from_=WHATSAPP_FROM,  # must be 'whatsapp:+14155238886' for sandbox
            to=WHATSAPP_TO,       # must be your joined number like 'whatsapp:+92300...'
            body=message_text,
        )
        print("✅ WhatsApp Message Sent:", msg.sid)
    except Exception as e:
        print("❌ Error sending WhatsApp message:", str(e))
