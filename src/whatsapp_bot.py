from twilio.rest import Client
from .config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, WHATSAPP_FROM, WHATSAPP_TO

def send_whatsapp_message(text: str) -> None:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and WHATSAPP_TO):
        print("WhatsApp not configured (missing SID/TOKEN/TO).")
        return
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    msg = client.messages.create(
        from_=WHATSAPP_FROM,
        body=text,
        to=WHATSAPP_TO
    )
    print("WhatsApp Message SID:", msg.sid)

if __name__ == "__main__":
    send_whatsapp_message("🚀 Test: WhatsApp alert from Market Bot!")

