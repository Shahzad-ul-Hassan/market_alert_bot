import os
from twilio.rest import Client
from dotenv import load_dotenv

# .env سے environment variables لوڈ کریں
load_dotenv()

# Twilio credentials اور WhatsApp numbers
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM", "whatsapp:+14155238886")
WHATSAPP_TO = os.getenv("WHATSAPP_TO")

def send_whatsapp_alert(message_text: str):
    if not (ACCOUNT_SID and AUTH_TOKEN and WHATSAPP_TO):
        print("⚠️ WhatsApp not configured correctly (SID/TOKEN/TO missing).")
        return

    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    try:
        message = client.messages.create(
            from_=WHATSAPP_FROM,
            body=message_text,
            to=WHATSAPP_TO
        )
        print("✅ WhatsApp Message Sent! SID:", message.sid)
    except Exception as e:
        print("❌ Error sending WhatsApp message:", str(e))

if __name__ == "__main__":
    send_whatsapp_alert("🚀 Test: WhatsApp alert from Market Bot!")
