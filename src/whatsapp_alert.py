from __future__ import annotations
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

def send_whatsapp_alert(body: str) -> str:
    """
    Twilio WhatsApp پر ایک سادہ ٹیکسٹ میسج بھیجتا ہے۔
    Env: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, TWILIO_WHATSAPP_TO
    """
    sid  = (os.getenv("TWILIO_ACCOUNT_SID") or "").strip()
    tok  = (os.getenv("TWILIO_AUTH_TOKEN") or "").strip()
    from_ = (os.getenv("TWILIO_WHATSAPP_FROM") or "").strip()
    to    = (os.getenv("TWILIO_WHATSAPP_TO") or "").strip()

    if not (sid and tok and from_ and to):
        raise RuntimeError("Twilio env not configured (SID/TOKEN/FROM/TO)")

    client = Client(sid, tok)
    msg = client.messages.create(from_=from_, body=body, to=to)
    print(f"✅ WhatsApp Message Sent: {msg.sid}")
    return msg.sid
