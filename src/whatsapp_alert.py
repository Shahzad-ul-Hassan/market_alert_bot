# src/whatsapp_alert.py

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# --- sanitize: strip() removes hidden spaces/newlines ---
ACCOUNT_SID   = (os.getenv("TWILIO_ACCOUNT_SID") or "").strip()
AUTH_TOKEN    = (os.getenv("TWILIO_AUTH_TOKEN") or "").strip()
WHATSAPP_FROM = (os.getenv("WHATSAPP_FROM") or "").strip()
WHATSAPP_TO   = (os.getenv("WHATSAPP_TO") or "").strip()

def verify_twilio_auth():
    # safe print for logs (sensitive hide)
    print(
        "Twilio SID present:", bool(ACCOUNT_SID),
        "SID endswith:", (ACCOUNT_SID[-4:] if ACCOUNT_SID else None),
        "| FROM:", WHATSAPP_FROM, "| TO:", WHATSAPP_TO
    )
    try:
        # simple auth probe
        Client(ACCOUNT_SID, AUTH_TOKEN).api.accounts(ACCOUNT_SID).fetch()
        print("✅ Twilio auth OK")
        return True
    except Exception as e:
        print("❌ Twilio auth FAILED:", str(e))
        return False

def send_whatsapp_alert(message_text: str):
    if not verify_twilio_auth():
        print("⚠️ Not sending message due to failed auth.")
        return
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        msg = client.messages.create(
            from_=WHATSAPP_FROM,  # must be whatsapp:+14155238886 (sandbox)
            to=WHATSAPP_TO,       # must be your joined number, e.g., whatsapp:+923076551525
            body=message_text,
        )
        print("✅ WhatsApp Message Sent:", msg.sid)
    except Exception as e:
        print("❌ Error sending WhatsApp message:", str(e))
