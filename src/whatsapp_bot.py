from __future__ import annotations
from .whatsapp_alert import send_whatsapp_alert

def send_whatsapp_message(text: str):
    return send_whatsapp_alert(text)

if __name__ == "__main__":
    send_whatsapp_message("🚀 Test: WhatsApp alert from Market Bot!")
